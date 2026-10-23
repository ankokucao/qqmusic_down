import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
for q in ["vkey","GetVkey","purl","stream.qqmusic","tryPlay","C400","filename"]:
    r=m.call("search_in_sources",{"query":q,"maxResults":15,"caseSensitive":False})
    d=r.get('data',{}) if isinstance(r,dict) else {}
    ms=d.get('matches',[])
    print("=== ",q," total",d.get('totalMatches'))
    for mm in ms:
        print("   ",mm.get('scriptId'),(mm.get('url') or '(inline)')[:90],"|",(mm.get('lineContent') or '')[:150].replace("\n"," "))
m.kill()
