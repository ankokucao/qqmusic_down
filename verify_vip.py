"""综合验证: 晴天(VIP) 试听取流 + 浏览器内fetch vs 独立下载 对比"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qqmusic_url as Q
from mcpdrv import MCP

MID = "0039MnYb0qxYhV"   # 晴天

info, fns = Q.build_filenames(MID, ["rs02", "c400", "m500"])
print("=" * 72)
print("歌曲:", info.get("songname"), "/".join(info.get("singer") or []))
print("songmid:", info.get("songmid"), "media_mid:", info.get("media_mid"))
print("pay_play:", info.get("pay_play"), "is_vip:", info.get("is_vip"),
      "size_try:", info.get("size_try"), "b_30s:", info.get("b_30s"))
print("目标:", fns)

mcp = MCP()
try:
    res = Q.fetch_urls(MID, list(fns.values()), mcp=mcp, keep=True)
    print("=" * 72)
    rev = {v: k for k, v in fns.items()}
    for q, d in res.items():
        print("[%s] %s  result=%s errtype=%s" % (rev.get(q, q), q, d.get("result"), d.get("errtype")))
        print("   filename:", d.get("filename"), " purl:", (d.get("purl") or "")[:90])
        u = Q.build_url(d)
        if u:
            print("   浏览器内fetch:", Q.probe_in_browser(u, mcp))
            print("   独立download  :", Q.probe_curl(u))
finally:
    mcp.kill()
print("=" * 72)
