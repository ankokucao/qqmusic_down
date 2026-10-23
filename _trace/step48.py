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
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; if(!row) return 'norow'; const html=row.outerHTML; return {html: html.slice(0,1500), playBtns: Array.from(row.querySelectorAll('a,i,span')).map(e=>({tag:e.tagName, cls:String(e.className).slice(0,60), title:e.title||'', txt:(e.textContent||'').trim().slice(0,10)})).slice(0,15)}; }","confirm":True,"mainWorld":True})
print("ROW:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
