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
time.sleep(9)

r=m.call("evaluate_script",{"function":"() => { const h=document.documentElement.outerHTML; const mids=[...new Set([...h.matchAll(/songDetail\\/([A-Za-z0-9]{10,20})/g)].map(x=>x[1]))]; const rows=Array.from(document.querySelectorAll('[class*=songlist] li')).slice(0,4).map(e=>({txt:(e.innerText||'').trim().slice(0,40), h:e.outerHTML.slice(0,500)})); return {mids:mids.slice(0,10), rows, txt:document.body.innerText.slice(0,200)}; }","confirm":True,"mainWorld":True})
print("SINGER:", json.dumps(r,ensure_ascii=False)[:5000])
m.kill()
