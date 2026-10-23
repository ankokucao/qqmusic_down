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
# 真实鼠标点击
r=m.call("click_element",{"selector":"a.list_menu__play","index":0,"confirm":True})
print("CLICK:", json.dumps(r,ensure_ascii=False)[:400])
time.sleep(12)
r=m.call("list_network_requests",{"pageSize":120,"resourceTypes":["media","xhr","fetch","other"]})
for x in r['data']['requests']:
    print(" ",x['reqid'],x['method'],x['resourceType'],x['status'],x['url'][:130])
r=m.call("evaluate_script",{"function":"() => ({audio:Array.from(document.querySelectorAll('audio')).map(a=>({src:a.src,paused:a.paused,cur:a.currentTime})), bottom: !!document.querySelector('[class*=player]')})","confirm":True,"mainWorld":True})
print("AUDIO:", json.dumps(r,ensure_ascii=False)[:2000])
m.kill()
