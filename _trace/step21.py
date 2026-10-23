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
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; const a=row&&row.querySelector('.list_menu__play'); if(a){a.click(); return 'ok';} return 'no'; }","confirm":True,"mainWorld":True})
print("CLICK:",json.dumps(r,ensure_ascii=False)[:150])
time.sleep(12)

# 全量请求，不筛类型
r=m.call("list_network_requests",{"pageSize":200})
reqs=r['data']['requests']
print("TOTAL:",len(reqs))
for x in reqs:
    u=x['url']
    if any(k in u for k in ('.mp3','.flac','.m4a','.aac','stream','media','vkey','playurl','ws.','svr')) or x['resourceType']=='media':
        print(" HIT",x['reqid'],x['method'],x['resourceType'],x['status'],u[:220])
print("---- 全部 url 摘要 ----")
seen=set()
for x in reqs:
    base=x['url'].split('?')[0]
    if base not in seen:
        seen.add(base); print("  ",x['resourceType'],base[:130])
m.kill()
