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
time.sleep(10)
# 断点设在 'a=r.data' —— 明文 body 变量
r=m.call("set_breakpoint_on_text",{"text":"a=r.data","urlFilter":"vendor.chunk"})
print("BP:", json.dumps(r,ensure_ascii=False)[:400])
# 触发：点击播放
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; const a=row&&row.querySelector('.list_menu__play'); if(a){a.click(); return 'ok';} return 'no'; }","confirm":True,"mainWorld":True})
print("CLICK:",json.dumps(r,ensure_ascii=False)[:200])
for k in range(10):
    pi=m.call("get_paused_info",{"includeScopes":True,"maxScopeDepth":3})
    if pi.get('ok'):
        d=pi['data']
        print("PAUSED_KEYS:", list(d.keys()))
        print(json.dumps(d,ensure_ascii=False)[:5000])
        m.call("pause_or_resume",{"action":"resume"})
        break
    time.sleep(1)
else:
    print("NO PAUSE")
m.kill()
