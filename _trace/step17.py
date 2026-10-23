import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
time.sleep(4)
r=m.call("list_network_requests",{"pageSize":40,"resourceTypes":["xhr","fetch"]})
ids=[x['reqid'] for x in r['data']['requests'] if 'musics.fcg' in x['url']]
print("IDS:",ids)
for rid in ids[:3]:
    rr=m.call("get_request_initiator",{"requestId":rid})
    print("INIT",rid,json.dumps(rr,ensure_ascii=False)[:2500]); print()
m.kill()
