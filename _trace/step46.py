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

# 用 evaluate_script 注入在页面 script 之前不可能；但可以改 XMLHttpRequest 构造器本身
HOOK = """() => {
  const RealXHR = window.XMLHttpRequest;
  window.__calls = [];
  function Wrapped(){ const x = new RealXHR(); const self=this;
    const oOpen = x.open.bind(x);
    x.open = function(m,u){ self.__u=u; self.__m=m; return oOpen.apply(x, arguments); };
    const oSend = x.send.bind(x);
    x.send = function(b){ try{ window.__calls.push({u:self.__u, m:self.__m, b:(typeof b==='string')?b.slice(0,4000):String(b)}); }catch(e){} return oSend.apply(x, arguments); };
    return x;
  }
  Wrapped.prototype = RealXHR.prototype;
  Object.setPrototypeOf(Wrapped, RealXHR);
  window.XMLHttpRequest = Wrapped;
  return 'wrapped';
}"""
r=m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("HOOK:", json.dumps(r,ensure_ascii=False)[:200])
# 触发播放
r=m.call("evaluate_script",{"function":"() => { const row=document.querySelectorAll('.songlist__item')[0]; const a=row&&row.querySelector('.list_menu__play'); if(a){a.click(); return 'ok';} return 'no'; }","confirm":True,"mainWorld":True})
time.sleep(8)
r=m.call("evaluate_script",{"function":"() => window.__calls","confirm":True,"mainWorld":True})
calls=r['data']['value']
print("CALLS:",len(calls))
for c in calls:
    if 'music' in (c['u'] or ''):
        print(" >",c['m'],c['u'][:90],"| BODY:",c['b'][:1500]); print()
m.kill()
