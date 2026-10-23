import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/search?w=%E6%99%B4%E5%A4%A9%20%E5%91%A8%E6%9D%B0%E4%BC%A6&t=0&size=30","timeout":30000})
time.sleep(8)
r=m.call("evaluate_script",{"function":"() => ({url:location.href, title:document.title, bodyLen:document.body.innerText.length, snippet:document.body.innerText.slice(0,1200)})","confirm":True,"mainWorld":True})
print("PAGE:", json.dumps(r,ensure_ascii=False)[:3000])
r=m.call("list_network_requests",{"pageSize":60,"resourceTypes":["xhr","fetch"],"methods":["POST","GET"]})
txt=json.dumps(r,ensure_ascii=False)
print("NET:", txt[:7000])
m.kill()
