import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/toplist","timeout":30000})
time.sleep(10)
# 找 decrypt / 响应解码处：搜 'arraybuffer' 附近的处理
for q in ['responseType="arraybuffer"','onload','arrayBuffer()','new Uint8Array']:
    r=m.call("search_in_sources",{"query":q,"maxResults":8,"maxLineLength":420,"urlFilter":"vendor.chunk"})
    d=r.get('data',{})
    print("###",q,"total",d.get('totalMatches'))
    for mm in (d.get('matches') or [])[:5]:
        print("  ", mm['lineContent'][:400].replace("\n"," "))
    print()
m.kill()
