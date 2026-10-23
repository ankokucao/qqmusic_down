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
# 直接下载 qmfe-sdk-cgi 脚本，查看它暴露什么
r=m.call("evaluate_script",{"function":"async () => { const t=await (await fetch('https://y.qq.com/component/m/qmfe-sdk-cgi/iife/index.js?max_age=2592000')).text(); return {len:t.length, head:t.slice(0,1200), tail:t.slice(-1500)}; }","confirm":True,"mainWorld":True,"timeout":30000})
print("SDKJS:", json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
