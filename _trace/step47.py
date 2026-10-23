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
r=m.call("evaluate_script",{"function":"() => ({workers: (()=>{try{return performance.getEntriesByType('resource').filter(e=>e.initiatorType==='other'||/worker|wasm/i.test(e.name)).map(e=>e.name.slice(0,120));}catch(e){return ['ERR']}})(), allRes: performance.getEntriesByType('resource').length})","confirm":True,"mainWorld":True})
print("RES:", json.dumps(r,ensure_ascii=False)[:3000])
m.kill()
