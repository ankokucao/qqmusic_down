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
r=m.call("set_breakpoint_on_text",{"text":"c=P(r.data)","urlFilter":"vendor.chunk"})
print("BP:", json.dumps(r,ensure_ascii=False)[:300])
# 触发播放
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; const a=row&&row.querySelector('.list_menu__play'); if(a){a.click(); return 'ok';} return 'no'; }","confirm":True,"mainWorld":True})
print("CLICK:",json.dumps(r,ensure_ascii=False)[:200])
time.sleep(3)
# 断点应已暂停；读取作用域
for k in range(8):
    try:
        pi=m.call("get_paused_info",{"includeScopes":True,"maxScopeDepth":3})
    except Exception as e:
        print("ERR",e); break
    if pi.get('ok') and pi.get('data'):
        d=pi['data']
        s=json.dumps(d,ensure_ascii=False)
        print("PAUSED:", s[:4000])
        # 提取含 vkey/playurl 的文本
        def find(o,path=''):
            if isinstance(o,dict):
                for k2,v in o.items(): find(v,path+'/'+k2)
            elif isinstance(o,list):
                for i,v in enumerate(o): find(v,path+f'[{i}]')
            else:
                st=str(o)
                if any(x in st for x in ('vkey','playurl','purl','filename','req_','module','songmid')):
                    print("  HIT",path,"=",st[:800])
        find(d)
        m.call("pause_or_resume",{"action":"resume"})
        break
    else:
        print("NOT PAUSED yet", json.dumps(pi,ensure_ascii=False)[:300])
        time.sleep(1)
m.kill()
