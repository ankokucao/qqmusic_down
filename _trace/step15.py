import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/search?w=%E6%99%B4%E5%A4%A9&t=0&size=30","timeout":30000})
time.sleep(8)

r=m.call("evaluate_script",{"function":"() => { const items=Array.from(document.querySelectorAll('li')).filter(e=>/晴天/.test(e.innerText||'')&&e.innerText.length<300); return {n:items.length, first: items.slice(0,3).map(e=>({txt:(e.innerText||'').trim().slice(0,80), html:e.outerHTML.slice(0,700)}))}; }","confirm":True,"mainWorld":True})
print("SUNNY:", json.dumps(r,ensure_ascii=False)[:4500])
m.kill()
