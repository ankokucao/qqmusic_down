"""
QQ音乐取流下载工具 - 后端服务 (纯标准库, 免安装)
=================================================
启动:
    python server.py              # 默认 http://127.0.0.1:8770
    python server.py --port 9000 --open

设计要点:
  * 复用 qqmusic_url.py 已打通的取流链路 (webpack 劫持 -> R(8) -> GetEVkey)
  * 浏览器会话常驻复用: 首次取流需 ~20s 加载页面, 后续请求复用同一会话, 只需 ~2s
  * 下载走服务端代理, 自动带上正确的 UA/Referer/Cookie, 规避跨环境 403
"""
import os, sys, json, time, threading, queue, urllib.request, urllib.parse, urllib.error, hashlib
import http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import qqmusic_url as Q
from mcpdrv import MCP

PORT = 8770
HOST = "127.0.0.1"
DL_DIR = os.path.join(HERE, "downloads")
os.makedirs(DL_DIR, exist_ok=True)

UA = Q.UA

# SSRF 防护: /api/download 只允许代理 QQ音乐官方域名 (含其 CDN 子域)
ALLOWED_HOSTS = (".qq.com", ".y.qq.com", ".tc.qq.com", "isure6-stream-qqmusic.a.bdycdn.cn")


def _safe_url(url):
    """校验代理下载的目标是否为 QQ音乐官方域名"""
    try:
        n = urllib.parse.urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    except Exception:
        return False
    return any(n == h.lstrip(".") or n.endswith("." + h.lstrip(".")) or n == h
               for h in ALLOWED_HOSTS)


# --------------------------------------------------------------------------
# 浏览器会话管理器: 常驻 MCP + 复用页面
# --------------------------------------------------------------------------
class Session:
    def __init__(self):
        self.mcp = None
        # 必须是可重入锁: fetch() 持锁后调用 ensure(), ensure() 内部再次加锁
        self.lock = threading.RLock()
        self.ready = False
        self.state = "未启动"

    def _rebuild(self):
        """彻底重建浏览器会话 (MCP 实例与 cloak 浏览器进程一起重开)"""
        self.ready = False
        if self.mcp:
            try: self.mcp.kill()
            except Exception: pass
            self.mcp = None
        self.state = "启动浏览器中..."
        self.mcp = MCP(isolated=True)
        self.state = "加载播放器页面..."
        Q.open_ready_page(self.mcp, Q._cookie(), timeout=45)
        if not Q.wait_ready(self.mcp, timeout=5):
            time.sleep(3)  # 就绪检测未通过时兜底等待
        self.ready = True
        self.state = "就绪"

    def ensure(self):
        """确保浏览器会话就绪 (已注入 cookie 且页面已加载)"""
        with self.lock:
            if self.ready and self.mcp:
                return
            self._rebuild()

    def fetch(self, songmid, filenames):
        with self.lock:
            self.ensure()
            # 页面已就绪 -> 复用, 跳过重载 (约 0.2s)
            res = Q.fetch_urls(songmid, filenames, mcp=self.mcp, keep=True, reinit=False)
            if not any(d.get("purl") for d in res.values()):
                # 会话可能已失效(浏览器被外部关闭/超时): 彻底重建后再试
                self.state = "重建会话中..."
                try:
                    self._rebuild()
                except Exception:
                    pass
                res = Q.fetch_urls(songmid, filenames, mcp=self.mcp, keep=True, reinit=False)
            self.state = "就绪"
            return res

    def close(self):
        with self.lock:
            self.ready = False
            if self.mcp:
                try: self.mcp.kill()
                except Exception: pass
                self.mcp = None
            self.state = "已停止"


SESSION = Session()


# --------------------------------------------------------------------------
# 搜索 (明文接口, 免加密)
# --------------------------------------------------------------------------
def search_songs(keyword, page=1, num=20):
    cookie = Q._cookie()
    h = {"User-Agent": UA, "Referer": "https://y.qq.com/", "Cookie": cookie,
         "Content-Type": "application/json"}
    body = json.dumps({
        "comm": {"ct": 11, "cv": 170205},
        "req": {"method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {"query": keyword, "num_per_page": num,
                          "page_num": page, "search_type": 0}},
    }).encode()
    req = urllib.request.Request("https://u.y.qq.com/cgi-bin/musicu.fcg", data=body, headers=h)
    d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore"))
    lst = (((d.get("req") or {}).get("data") or {}).get("body") or {}).get("song") or {}
    items = lst.get("list") or []
    out = []
    for s in items:
        f = s.get("file") or {}
        out.append({
            "songmid": s.get("mid"),
            "media_mid": f.get("media_mid"),
            "name": s.get("title"),
            "singer": " / ".join(x.get("name", "") for x in (s.get("singer") or [])),
            "album": (s.get("album") or {}).get("name"),
            "duration": s.get("interval"),
            "size_96aac": f.get("size_96aac"),
            "size_128mp3": f.get("size_128mp3"),
            "size_320mp3": f.get("size_320mp3"),
            "size_flac": f.get("size_flac"),
        })
    return {"total": lst.get("totalnum", len(out)), "list": out}


def song_detail(songmid):
    info = Q.get_song_info(songmid)
    if info.get("err"):
        return {"error": info["err"]}
    return info


# --------------------------------------------------------------------------
# 下载代理 (服务端带正确头部拉流, 再回传给浏览器)
# --------------------------------------------------------------------------
_BAD_NAMES = {
    "con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5", "com6",
    "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6",
    "lpt7", "lpt8", "lpt9",
}


def _safe_fname(name_hint):
    """下载文件名安全化: 去非法字符/Windows 保留名/路径穿越/结尾空点"""
    safe = "".join(c for c in name_hint if c.isprintable() and c not in "\\/:*?\"<>|")
    base = os.path.basename(safe.replace("..", "_")).rstrip(" .")
    name, ext = os.path.splitext(base)
    if name.lower() in _BAD_NAMES:
        name = "_" + name
    safe = (name.rstrip(" .") or "audio") + ext
    return safe or ("audio_" + hashlib.md5(name_hint.encode()).hexdigest()[:12])


def fetch_to_file(url, referer="https://y.qq.com/", name_hint=None):
    """服务端拉流落盘, 返回 (路径, 字节数, content-type)

    name_hint: 形如 "歌名_C400000xxx.m4a", 用于给文件起可读名字
    """
    h = {"User-Agent": UA, "Referer": referer, "Cookie": Q._cookie()}
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=180) as r:
        ct = r.headers.get("Content-Type") or "application/octet-stream"
        cd = r.headers.get("Content-Disposition") or ""
        data = r.read()
    if name_hint:
        safe = _safe_fname(name_hint)
        path = os.path.join(DL_DIR, safe)
        # 同名不覆盖, 追加序号
        if os.path.exists(path):
            root, ext = os.path.splitext(path)
            i = 1
            while os.path.exists("%s_(%d)%s" % (root, i, ext)):
                i += 1
            path = "%s_(%d)%s" % (root, i, ext)
    else:
        ext = ".mp3"
        if "filename=" in cd:
            nm = cd.split("filename=")[-1].strip('"; ')
            ext = os.path.splitext(nm)[1] or ext
        path = os.path.join(DL_DIR, "audio_" + hashlib.md5(url.encode()).hexdigest()[:12] + ext)
    with open(path, "wb") as f:
        f.write(data)
    return path, len(data), ct


def download_stream(url, wfile, referer="https://y.qq.com/"):
    """边下边写给浏览器 (前端用 <a download> 触发)"""
    h = {"User-Agent": UA, "Referer": referer, "Cookie": Q._cookie()}
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=180) as r:
        ct = r.headers.get("Content-Type") or "application/octet-stream"
        total = r.headers.get("Content-Length")
        wfile.write(("HTTP/1.1 200 OK\r\nContent-Type: %s\r\n"
                     "Content-Disposition: attachment; filename=\"%s\"\r\n"
                     % (ct, _fname(url))).encode())
        if total:
            wfile.write(("Content-Length: %s\r\n" % total).encode())
        wfile.write(b"Connection: close\r\n\r\n")
        while True:
            chunk = r.read(64 * 1024)
            if not chunk:
                break
            wfile.write(chunk)
    return ct


def _fname(url):
    p = urllib.parse.urlparse(url).path
    return os.path.basename(p) or "audio.mp3"


# --------------------------------------------------------------------------
# HTTP 服务
# --------------------------------------------------------------------------
class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # 静默, 避免刷屏

    # ---- helpers ----
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def _static(self, name, ctype):
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            self._json({"error": "missing " + name}, 404); return
        data = open(p, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    # ---- routes ----
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path

        if path in ("/", "/index.html"):
            return self._static("index.html", "text/html; charset=utf-8")
        if path == "/app.js":
            return self._static("app.js", "application/javascript; charset=utf-8")
        if path == "/style.css":
            return self._static("style.css", "text/css; charset=utf-8")
        if path == "/api/status":
            return self._json({"state": SESSION.state, "ready": SESSION.ready})
        if path == "/api/search":
            kw = (q.get("q") or [""])[0].strip()
            if not kw:
                return self._json({"list": [], "total": 0})
            try:
                page = int((q.get("page") or ["1"])[0])
            except Exception:
                page = 1
            try:
                return self._json(search_songs(kw, page))
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if path == "/api/detail":
            mid = (q.get("songmid") or q.get("mid") or [""])[0]
            if not mid:
                return self._json({"error": "missing songmid"}, 400)
            try:
                return self._json(song_detail(mid))
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if path == "/api/download":
            url = (q.get("url") or [""])[0]
            if not url.startswith("http"):
                return self._json({"error": "bad url"}, 400)
            if not _safe_url(url):
                return self._json({"error": "仅允许代理 QQ音乐官方域名"}, 403)
            hint = (q.get("name") or [""])[0]
            try:
                p, n, ct = fetch_to_file(url, name_hint=hint or None)
                return self._json({"ok": True, "file": os.path.basename(p),
                                   "bytes": n, "type": ct, "dir": DL_DIR})
            except urllib.error.HTTPError as e:
                return self._json({"error": "HTTP %s %s" % (e.code, e.reason)}, 502)
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if path == "/api/files":
            fs = []
            for fn in sorted(os.listdir(DL_DIR)):
                fp = os.path.join(DL_DIR, fn)
                if os.path.isfile(fp):
                    fs.append({"name": fn, "bytes": os.path.getsize(fp),
                               "mtime": int(os.path.getmtime(fp))})
            fs.sort(key=lambda x: -x["mtime"])
            return self._json({"dir": DL_DIR, "files": fs})
        if path == "/api/file":
            fn = (q.get("name") or [""])[0]
            fp = os.path.join(DL_DIR, os.path.basename(fn))
            if not os.path.exists(fp):
                return self._json({"error": "not found"}, 404)
            size = os.path.getsize(fp)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition",
                             'attachment; filename="%s"' % os.path.basename(fn))
            self.end_headers()
            with open(fp, "rb") as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            return
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        b = self._body()
        if u.path == "/api/resolve":
            mid = (b.get("songmid") or b.get("mid") or "").strip()
            quals = b.get("qualities") or ["rs02", "c400", "m500"]
            if not mid:
                return self._json({"error": "missing songmid"}, 400)
            try:
                info, fns = Q.build_filenames(mid, quals)
                if not fns:
                    return self._json({"error": "无法获取 media_mid", "detail": info}, 500)
                res = SESSION.fetch(mid, list(fns.values()))
                rev = {v: k for k, v in fns.items()}
                rows = []
                for qk, d in res.items():
                    qname = rev.get(qk, qk)
                    tpl = Q.QUALITY_MAP.get(qname, ("", ""))[1]
                    rows.append({
                        "quality": qname,
                        "label": tpl,
                        "filename": d.get("filename"),
                        "result": d.get("result"),
                        "purl": d.get("purl"),
                        "url": Q.build_url(d),
                        "xcdnurl": d.get("xcdnurl"),
                        "expiration": d.get("expiration"),
                        "err": d.get("err"),
                        "msg": d.get("msg"),
                    })
                return self._json({"song": info, "rows": rows})
            except Exception as e:
                import traceback
                traceback.print_exc()
                return self._json({"error": str(e)}, 500)
        if u.path == "/api/shutdown":
            SESSION.close()
            return self._json({"ok": True})
        return self._json({"error": "not found"}, 404)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    global PORT, HOST
    args = sys.argv[1:]
    if "--port" in args:
        PORT = int(args[args.index("--port") + 1])
    if "--host" in args:
        HOST = args[args.index("--host") + 1]
    srv = Server((HOST, PORT), Handler)
    url = "http://%s:%d/" % (HOST, PORT)
    print("=" * 60)
    print("  QQ音乐取流下载工具")
    print("  服务地址: %s" % url)
    print("  下载目录: %s" % DL_DIR)
    print("  按 Ctrl+C 停止")
    print("=" * 60)
    try:
        Q._cookie()
        print("  登录 cookie: OK")
    except Exception as e:
        print("  !! %s\n  (搜索不可用; 取流/下载将失败)" % e)
    if "--open" in args:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        SESSION.close()
        srv.server_close()


if __name__ == "__main__":
    main()
