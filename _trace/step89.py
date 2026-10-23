import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq_v2/player","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(20)
ls=m.call("list_scripts",{"pageSize":100})
items=ls.get('data',{}).get('scripts',ls.get('scripts',[])) if isinstance(ls,dict) else []
for s in items: print(s.get('scriptId'),(s.get('url') or '(inline)')[:130])
print("=== search vkey in loaded sources")
for q in ["vkey","GetVkey","playUrl","fileKey","media_mid"]:
    r=m.call("search_in_sources",{"query":q,"maxResults":12})
    d=r.get('data',{}) if isinstance(r,dict) else {}
    print("---",q,d.get('totalMatches'))
    for mm in d.get('matches',[]): print("   ",(mm.get('url') or '(inline)')[:100],"|",(mm.get('lineContent') or '')[:140].replace("\n"," "))
m.kill()
