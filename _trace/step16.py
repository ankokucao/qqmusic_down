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
time.sleep(9)

r=m.call("evaluate_script",{"function":"() => { const h=document.documentElement.outerHTML; const mids=[...new Set([...h.matchAll(/songDetail\\/([A-Za-z0-9]{10,20})/g)].map(x=>x[1]))]; return {htmlLen:h.length, mids:mids.slice(0,15), txt:document.body.innerText.slice(0,400)}; }","confirm":True,"mainWorld":True})
print("MIDS:", json.dumps(r,ensure_ascii=False)[:3000])

# 同时看搜索页的 network，找承载结果的加密请求
r=m.call("list_network_requests",{"pageSize":40,"resourceTypes":["xhr","fetch"]})
for x in r['data']['requests']:
    print(" REQ", x['reqid'], x['method'], x['url'][:110], x['status'])
m.kill()
