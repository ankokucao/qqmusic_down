"""
QQ音乐 逆向溯源 - 取流地址下载器 (最终版)
=========================================
用法:
    python qqmusic_url.py <songmid> [音质...]
    python qqmusic_url.py 0039MnYb0qxYhV rs02 c400 m500 f000

音质:
    rs02  试听片段  RS02<media_mid>.mp3
    c400  128k m4a   C400<media_mid>.m4a
    m500  320k mp3   M500<media_mid>.mp3
    f000  FLAC       F000<media_mid>.flac
    (不带参数则只请求一次"默认流", 用于观察服务端默认行为)

原理 (JS 逆向溯源结论):
    1. 复用浏览器(js-reverse-mcp)加载的 y.qq.com 页面自身的加密 CGI 通道
       - 劫持 window.webpackJsonp.push 拿到 __webpack_require__
       - R(8) 即 CGI 核心模块(module 8), export 'a' = lr (批量请求类)
         内部: getSecuritySign -> encrypt -> musics.fcg?encoding=ag-1&sign=... -> decrypt
    2. 调用现行取流模块: music.vkey.GetEVkey / GetUrl
       param: {guid, songmid:[], songtype:[], uin, loginflag:1, platform:"20", xcdn:1, filename?}
    3. 响应 data.midurlinfo[].purl 即带 vkey 的相对路径, 拼 data.sip[0] 即完整地址
"""
import json, os, sys, time, base64, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mcpdrv import MCP

COOKIE_FILE = os.path.join(HERE, "cookie.txt")
PAGE = "https://y.qq.com/n/ryqq_v2/player"
PLAYER_ORIGIN = "https://y.qq.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 音质 -> filename 模板
# 实测结论(2026-10, 登录态):
#   C400<media_mid>.m4a  -> 96k AAC  (字节数 == 明文接口 size_96aac)
#   M500<media_mid>.mp3  -> 128k MP3 (字节数 == 明文接口 size_128mp3)
#   RS02<media_mid>.mp3  -> 60 秒试听片段 (仅 VIP 曲, 免费曲 404)
#   M800 / F000          -> result=104003 (无 VIP 权限)
# 注意: 后缀(.m4a/.mp3)必须与前缀匹配, 否则 CDN 404;
#       服务端会按前缀把 filename 归一化, 传 .mp3 后缀取 C400 会得到 404
QUALITY_MAP = {
    "rs02": ("RS02{media_mid}.mp3", "试听片段 60s (仅VIP曲)"),
    "c400": ("C400{media_mid}.m4a", "96k AAC / m4a"),
    "m500": ("M500{media_mid}.mp3", "128k MP3"),
    "m800": ("M800{media_mid}.mp3", "320k MP3 (需VIP)"),
    "f000": ("F000{media_mid}.flac", "FLAC 无损 (需VIP)"),
    "a000": ("A000{media_mid}.m4a", "192k AAC (需VIP)"),
}

# 页面内执行的取流脚本 (在页面 realm 中, 走页面自身的 sign/encrypt/decrypt 通道)
# 注意: 只回传精简字段, 避免 MCP 对超大返回值截断
FETCH_JS = r"""
async (songmid, qualities) => {
  // 劫持 webpackJsonp.push 捕获 __webpack_require__
  // 注意: chunk id 必须每次唯一 —— 同一 id 第二次 push 时模块已缓存,
  //       工厂不再执行, __WREQ 会停留在假工厂上导致 R(8) 返回 undefined
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  const cid=900000000+Math.floor(Math.random()*90000000);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  const mod={}; mod[cid]=(m,e,r)=>{window.__WREQ=r;};
  wj.push([[cid],mod,[[cid]]]);
  wj.push=orig;
  const R=window.__WREQ;
  if(typeof R!=='function'){ return {res:[{q:'',err:'webpack require 捕获失败'}]}; }
  let M8;
  try{ M8=R(8); }catch(e){ return {res:[{q:'',err:'R(8) 失败: '+String(e)}]}; }
  if(!M8||!M8.a){ return {res:[{q:'',err:'module 8 不可用'}]}; }
  const uin=(document.cookie.match(/wxuin=(\d+)/)||[])[1]||'';
  const mkguid=()=>String(Math.round(2147483647*Math.random())*new Date().getUTCMilliseconds()%1e10);
  const jobs = qualities.map(q => (async () => {
      const param={guid:mkguid(), songmid:[songmid], songtype:[0], uin:uin, loginflag:1, platform:'20', xcdn:1};
      if(q) param.filename=[q];
      try{
        const inst=new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg',type:'POST',needSign:true});
        const r=await inst.request([{module:'music.vkey.GetEVkey',method:'GetUrl',param:param}]);
        const a0=(r&&r[0])||{}; const d=a0.data||{}; const mi=(d.midurlinfo||[])[0]||{};
        return {q:q, code:a0.code, retcode:d.retcode, msg:d.msg,
          songmid:mi.songmid, filename:mi.filename, purl:mi.purl, vkey:mi.vkey,
          xcdnurl:mi.xcdnurl, result:mi.result, errtype:mi.errtype,
          sip:d.sip, expiration:d.expiration};
      }catch(e){ return {q:q, err:String(e)}; }
  })());
  const out = await Promise.all(jobs);
  return {res: out};
}
"""

# 兜底: 把结果写进页面数组, 分片读回 (规避 MCP 返回值截断)
STORE_JS = "() => { window.__RES=[]; return true; }"
PUSH_JS = "async (songmid, qualities) => { const fn = " + FETCH_JS + "; const r = await fn(songmid,qualities); window.__RES.push(r); return window.__RES.length; }"
READ_JS = "(i,n) => { const s=JSON.stringify(window.__RES[i]||null); return s.slice(n, n+1800); }"

# 页面内执行的下载探测 (Range 请求, 用于判断 vkey 是否绑定发起环境)
PROBE_JS = r"""
async (url, range) => {
  try{
    const opt={credentials:'include'};
    if(range) opt.headers={Range:range};
    const r=await fetch(url,opt);
    const b=await r.blob();
    return {status:r.status, ok:r.ok, type:r.headers.get('content-type'),
            len:b.size, cr:r.headers.get('content-range')};
  }catch(e){ return {err:String(e)}; }
}
"""


def _inject_js(cookie):
    lit = json.dumps(cookie)
    return (
        "() => { const raw = " + lit + "; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean);"
        " ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');"
        "document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';}));"
        " return document.cookie.length; }"
    )


def _cookie():
    if not os.path.exists(COOKIE_FILE):
        raise RuntimeError(
            "缺少登录 cookie: 请将 y.qq.com 的登录 cookie 保存到 %s" % COOKIE_FILE)
    c = open(COOKIE_FILE, encoding="utf-8").read().strip()
    if not c:
        raise RuntimeError("cookie.txt 为空: 请先从浏览器复制登录 cookie")
    return c


READY_JS = ("() => { const w=window; return !!(w.webpackJsonp && w.webpackJsonp.push && "
            "document.readyState==='complete'); }")


def wait_ready(mcp, timeout=40, interval=0.5):
    """等待页面加载完成且 webpackJsonp 可用 (代替固定 sleep, 首次加载更快更稳)"""
    import time as _t
    t0 = _t.time()
    while _t.time() - t0 < timeout:
        try:
            v = _eval(mcp, READY_JS)
        except Exception:
            v = None
        if v is True:
            return True
        _t.sleep(interval)
    return False


def open_ready_page(mcp, cookie, timeout=45):
    """打开播放器页 + 注入 cookie + 等待就绪 (就绪检测代替固定 sleep)"""
    mcp.call("new_page", {"url": PAGE, "timeout": 45000})
    mcp.call("evaluate_script", {"function": _inject_js(cookie), "confirm": True, "mainWorld": True})
    mcp.call("navigate_page", {"type": "reload", "timeout": 45000})
    if not wait_ready(mcp, timeout=timeout):
        # 未完全就绪也继续, 让上层走兜底/重建逻辑
        pass


def get_song_info(songmid, cookie=None):
    """明文接口查歌曲基础信息 (media_mid / 试听过 / VIP 标记 / 各音质大小)"""
    if cookie is None:
        cookie = _cookie()
    h = {"User-Agent": UA, "Referer": PLAYER_ORIGIN + "/", "Cookie": cookie}
    url = ("https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid=%s&format=json" % songmid)
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20)
                       .read().decode("utf-8", "ignore"))
    except Exception as e:
        return {"err": str(e)}
    item = (d.get("data") or [{}])[0]
    f = item.get("file") or {}
    pay = item.get("pay") or {}
    return {
        "songmid": item.get("mid") or item.get("songmid"),
        "media_mid": f.get("media_mid"),
        "songname": item.get("title") or item.get("name"),
        "singer": [s.get("name") for s in (item.get("singer") or [])],
        "interval": item.get("interval"),
        "pay_play": pay.get("pay_play"),
        "is_vip": (pay.get("pay_play") == 1),
        "price_track": pay.get("price_track"),
        "size_try": item.get("size_try"),
        "b_30s": item.get("b_30s"),
        "size_128mp3": f.get("size_128mp3"),
        "size_320mp3": f.get("size_320mp3"),
        "size_flac": f.get("size_flac"),
        "filename_all": f.get("filename"),
    }


def build_filenames(songmid, qualities=None, cookie=None):
    """songmid + 音质key -> {q: filename}  (自动用 media_mid 拼 filename)"""
    info = get_song_info(songmid, cookie)
    mm = info.get("media_mid")
    if not mm:
        return info, None
    if not qualities:
        qualities = ["rs02", "c400", "m500", "f000"]
    out = {}
    for q in qualities:
        tpl = QUALITY_MAP.get(q.lower())
        if tpl:
            out[q.lower()] = tpl[0].format(media_mid=mm)
    return info, out


def _eval(mcp, fn):
    r = mcp.call("evaluate_script", {"function": fn, "confirm": True, "mainWorld": True})
    if isinstance(r, dict):
        return r.get("data", {}).get("value")
    return r


def _read_sharded(mcp, idx=0, chunk=1800):
    """把 window.__RES[idx] 分片读回并拼成 JSON 字符串"""
    buf = ""
    n = 0
    while True:
        s = _eval(mcp, "() => { const s = JSON.stringify(window.__RES[%d]||null); return s.slice(%d,%d); }" % (idx, n, n + chunk))
        if s is None:
            break
        if not isinstance(s, str):
            s = str(s)
        buf += s
        n += len(s)
        if len(s) < chunk:
            break
    return buf


def fetch_urls(songmid, qualities=None, cookie=None, mcp=None, keep=False, reinit=True):
    """返回 {quality: {purl, vkey, sip, filename, xcdnurl, result, ...}}

    reinit=True  : 新建页面 + 注入 cookie + reload (首次使用)
    reinit=False : 复用当前已加载页面 (会话常驻, 约 2 秒)
    """
    if cookie is None:
        cookie = _cookie()
    if qualities is None:
        qualities = [""]

    own = mcp is None
    if own:
        mcp = MCP()
    raw = None
    try:
        if reinit:
            open_ready_page(mcp, cookie)

        # 主通道: 页面内写数组
        _eval(mcp, STORE_JS)
        js = ("async () => { const fn = " + PUSH_JS + "; return await fn("
              + json.dumps(songmid) + ", " + json.dumps(qualities) + "); }")
        _eval(mcp, js)
        s = _read_sharded(mcp, 0)
        try:
            raw = json.loads(s)
        except Exception:
            raw = None

        # 兜底: 直接返回
        if raw is None:
            js2 = ("async () => { const fn = " + FETCH_JS + "; return await fn("
                   + json.dumps(songmid) + ", " + json.dumps(qualities) + "); }")
            v = _eval(mcp, js2)
            if isinstance(v, str):
                try: v = json.loads(v)
                except Exception: v = None
            raw = v
    finally:
        if own and not keep:
            mcp.kill()

    res = {}
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except Exception: raw = None
    if isinstance(raw, dict): raw = raw.get("res") or []
    if isinstance(raw, dict): raw = [raw]
    for item in raw or []:
        if not isinstance(item, dict): continue
        q = item.get("q") or "default"
        if item.get("err"):
            res[q] = {"err": item["err"]}
            continue
        res[q] = {
            "songmid": item.get("songmid"),
            "filename": item.get("filename"),
            "purl": item.get("purl"),
            "vkey": item.get("vkey"),
            "xcdnurl": item.get("xcdnurl"),
            "sip": item.get("sip"),
            "result": item.get("result"),
            "errtype": item.get("errtype"),
            "expiration": item.get("expiration"),
            "msg": item.get("msg"),
            "retcode": item.get("retcode"),
        }
    return res


def build_url(info, base=None):
    """把 purl / xcdnurl 拼成完整可下载 URL"""
    if not info:
        return None
    purl = info.get("purl") or ""
    if not purl:
        return None
    if purl.startswith("http"):
        return purl
    host = (base or (info.get("sip") or ["http://aqqmusic.tc.qq.com/"])[0])
    if not host.endswith("/"):
        host += "/"
    return host + purl


def download(url, cookie=None, out=None, referer=PLAYER_ORIGIN + "/"):
    """独立下载(curl 风格) —— 失败时抛异常"""
    h = {"User-Agent": UA, "Referer": referer}
    if cookie is None:
        cookie = _cookie()
    h["Cookie"] = cookie
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        ct = r.headers.get("Content-Type")
        st = r.status
    if out:
        with open(out, "wb") as f:
            f.write(data)
    return len(data), ct, st


def probe_in_browser(url, mcp, cookie=None, range_="bytes=0-4095"):
    """在浏览器会话内用 fetch 取流(与取流请求同源同IP), 判断 vkey 是否绑定环境"""
    js = ("async () => { const fn = " + PROBE_JS + "; return await fn("
          + json.dumps(url) + ", " + json.dumps(range_) + "); }")
    r = mcp.call("evaluate_script", {"function": js, "confirm": True, "mainWorld": True})
    v = r.get("data", {}).get("value") if isinstance(r, dict) else None
    if isinstance(v, str):
        try: v = json.loads(v)
        except Exception: pass
    return v


def probe_curl(url, cookie=None, referer=PLAYER_ORIGIN + "/"):
    """独立探测: 只取 Range 前 2KB, 看状态码"""
    h = {"User-Agent": UA, "Referer": referer, "Range": "bytes=0-2047"}
    if cookie is None:
        cookie = _cookie()
    h["Cookie"] = cookie
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
            body = r.read()
            return {"status": r.status, "len": len(body), "type": r.headers.get("Content-Type"),
                    "cr": r.headers.get("Content-Range")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "err": str(e)}
    except Exception as e:
        return {"err": str(e)}


if __name__ == "__main__":
    mid = sys.argv[1] if len(sys.argv) > 1 else "000NBVdP3wg95P"
    qs = sys.argv[2:] or None
    info, fns = build_filenames(mid, qs)
    print("=" * 72)
    print("歌曲:", info.get("songname"), "|", "/".join(info.get("singer") or []))
    print("songmid :", info.get("songmid"), " media_mid:", info.get("media_mid"))
    print("VIP     :", info.get("is_vip"), " pay_play:", info.get("pay_play"),
          " 试听过长度:", info.get("size_try"))
    if not fns:
        print("!! 无法取得 media_mid:", info)
        sys.exit(1)
    print("目标 filename:", fns)

    res = fetch_urls(mid, list(fns.values()))
    print("=" * 72)
    rev = {v: k for k, v in fns.items()}
    for q, d in res.items():
        print("[%s]  %s" % (rev.get(q, q), q))
        if d.get("err"):
            print("   ERR:", d["err"]); continue
        print("   filename :", d["filename"])
        print("   result   :", d["result"], " errtype:", d["errtype"], " msg:", d.get("msg"))
        print("   purl     :", (d["purl"] or "")[:150])
        print("   url      :", build_url(d))
        print("   xcdn     :", d.get("xcdnurl"))
        print("   有效期(s):", d.get("expiration"))
    print("=" * 72)
