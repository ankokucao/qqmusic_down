import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

# 拦截 __TmeWebSec_* 的赋值
HOOK="""() => {
  window.__sec={};
  const names=['__TmeWebSec_seccgi','__TmeWebSec_sign','__TmeWebSec_U','__TmeWebSec_I','__TmeWebSec_M','__TmeWebSec_x','__TmeWebSec_D','__TmeWebSec_fingerprint','__TmeWebSec_report'];
  for(const n of names){
    try{
      let val;
      Object.defineProperty(window, n, {
        configurable: true, enumerable: true,
        get(){ return val; },
        set(v){ val=v; window.__sec[n]=v; }
      });
    }catch(e){ window.__sec['err_'+n]=String(e); }
  }
  // 同时记录 XHR 明文 body（含加密前）与 url
  window.__xhr=[];
  const oopen=XMLHttpRequest.prototype.open, osend=XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open=function(m,u,...a){ this.__m=m; this.__u=u; return oopen.call(this,m,u,...a); };
  XMLHttpRequest.prototype.send=function(b){ try{ window.__xhr.push({m:this.__m,u:this.__u,len:b&&b.length}); }catch(e){} return osend.call(this,b); };
  return {ok:true, hooked:Object.keys(window.__sec)};
}"""

TRIG="""async () => {
  const all=document.querySelectorAll('*');
  let clicked=0;
  for(const el of all){
    if(clicked>8) break;
    const cn=(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className)||'';
    if(typeof cn==='string' && /play/i.test(cn)){
      const r=el.getBoundingClientRect();
      if(r.width>0&&r.height>0){ try{ el.click(); clicked++; }catch(x){} }
    }
  }
  await new Promise(r=>setTimeout(r,10000));
  const sec=window.__sec||{};
  const o={};
  for(const k of Object.keys(sec)){ const v=sec[k]; o[k]= (typeof v==='function')? 'fn:'+String(v).slice(0,200) : (typeof v)+':'+String(v).slice(0,120); }
  return {clicked, secKeys:Object.keys(sec), sec:o, xhr:(window.__xhr||[]).slice(-12)};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(14)
print("HOOK:",json.dumps(m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:500])
r=m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True})
print("TRIG:",json.dumps(r,ensure_ascii=False)[:3000])
m.kill()
