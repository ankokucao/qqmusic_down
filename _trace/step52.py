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
time.sleep(12)
r=m.call("list_scripts",{"filter":"runtime","pageSize":10})
print("RT:", json.dumps(r,ensure_ascii=False)[:1200])
urls=[s.get('url') for s in r['data']['scripts'] if s.get('url')]
if urls:
    r=m.call("get_script_source",{"url":urls[0],"startLine":1,"endLine":30})
    s=json.dumps(r,ensure_ascii=False)
    print("SRC:", s[:5000])
m.kill()
