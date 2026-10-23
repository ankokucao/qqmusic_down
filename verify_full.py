"""
最终端到端验证: 多首歌 x 多音质 -> 取流 -> 下载落盘 -> 校验
"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qqmusic_url as Q
from mcpdrv import MCP

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(OUT, exist_ok=True)

CASES = [
    ("000NBVdP3wg95P", ["rs02", "c400", "m500", "m800", "f000"]),
    ("0039MnYb0qxYhV", ["rs02", "c400", "m500"]),   # 晴天 VIP
    ("004Z8Ihr0JIu5s", ["rs02", "c400", "m500"]),   # 七里香 VIP
    ("001Qu4I30eVFYb", ["rs02", "c400", "m500"]),   # 演员 VIP
]

mcp = MCP()
report = []
try:
    for mid, qs in CASES:
        info, fns = Q.build_filenames(mid, qs)
        print("=" * 78)
        print("《%s》 %s  | songmid=%s media_mid=%s | VIP=%s | %ss" %
              (info.get("songname"), "/".join(info.get("singer") or []),
               info.get("songmid"), info.get("media_mid"),
               info.get("is_vip"), info.get("interval")))
        res = Q.fetch_urls(mid, list(fns.values()), mcp=mcp, keep=True)
        rev = {v: k for k, v in fns.items()}
        for q, d in res.items():
            name = rev.get(q, q)
            fn = d.get("filename")
            if d.get("err") or not d.get("purl"):
                print("   [%-5s] %-28s result=%-7s -> 无流(权限/资源不足)" % (name, fn, d.get("result")))
                report.append({"song": info.get("songname"), "quality": name,
                               "filename": fn, "result": d.get("result"), "status": "NO_STREAM"})
                continue
            u = Q.build_url(d)
            try:
                p = os.path.join(OUT, "%s_%s%s" % (info.get("songname"), name,
                                                   os.path.splitext(fn)[1]))
                n, ct, st = Q.download(u, out=p)
                md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
                print("   [%-5s] %-28s HTTP %s  %9d bytes  %-10s MD5=%s" %
                      (name, fn, st, n, ct, md5))
                report.append({"song": info.get("songname"), "quality": name, "filename": fn,
                               "result": d.get("result"), "url": u, "bytes": n,
                               "type": ct, "http": st, "md5": md5, "status": "OK",
                               "vkey_expire_s": d.get("expiration")})
            except Exception as e:
                print("   [%-5s] %-28s 下载失败: %s" % (name, fn, e))
                report.append({"song": info.get("songname"), "quality": name, "filename": fn,
                               "result": d.get("result"), "url": u, "status": "DL_FAIL",
                               "err": str(e)})
finally:
    mcp.kill()

print("=" * 78)
ok = sum(1 for r in report if r["status"] == "OK")
print("成功 %d / 共 %d" % (ok, len(report)))
json.dump(report, open(os.path.join(OUT, "report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("报告:", os.path.join(OUT, "report.json"))
