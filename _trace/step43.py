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
r=m.call("evaluate_script",{"function":"() => Array.from(document.querySelectorAll('iframe')).map(f=>({src:f.src, cls:f.className, id:f.id, name:f.name, w:f.width,h:f.height}))","confirm":True,"mainWorld":True})
print("IFRAMES:", json.dumps(r,ensure_ascii=False)[:2000])
r=m.call("evaluate_script",{"function":"() => ({YQQ_IFRAME: (window.YQQ_IFRAME && window.YQQ_IFRAME.tagName) || null, src: window.YQQ_IFRAME && window.YQQ_IFRAME.src})","confirm":True,"mainWorld":True})
print("YQQ:", json.dumps(r,ensure_ascii=False)[:800])
# 点击播放后再看 iframe
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; const a=row&&row.querySelector('.list_menu__play'); if(a){a.click(); return 'ok';} return 'no'; }","confirm":True,"mainWorld":True})
time.sleep(8)
r=m.call("select_frame",{})
print("FRAMES2:", json.dumps(r,ensure_ascii=False)[:1500])
m.kill()
