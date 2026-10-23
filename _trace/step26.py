import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":30000})
time.sleep(10)
for q in ['musics.fcg','encoding=ag-1','"sign"','vkey','GetVkey','spd']:
    r=m.call("search_in_sources",{"query":q,"maxResults":10,"maxLineLength":300,"excludeMinified":False})
    d=r.get('data',{})
    print("###",q,"total",d.get('totalMatches'))
    for mm in (d.get('matches') or [])[:6]:
        print("   ",mm['url'][:90],"|",mm['lineContent'][:260].replace("\n"," "))
    print()
m.kill()
