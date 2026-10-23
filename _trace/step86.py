import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  window.__log=[];
  const L=(t,d)=>{ try{ window.__log.push(t+' '+String(d).slice(0,1500)); }catch(e){} };
  // fetch
  const of=window.fetch;
  window.fetch=function(input,init){
    try{
      const u=(typeof input==='string')?input:(input&&input.url);
      const body=init&&init.body;
      L('FETCH '+u+' BODY='+(typeof body==='string'?body:'[nonstring]'));
      if(init&&init.body&&typeof init.body==='string'){
        try{ const p=JSON.parse(init.body); L('FETCH-PARSED '+JSON.stringify(p).slice(0,3000)); }catch(x){}
      }
    }catch(e){}
    return of.apply(this, arguments);
  };
  // XHR：记录 body（可能是明文）
  const oopen=XMLHttpRequest.prototype.open, osend=XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open=function(m,u,...a){ this.__m=m; this.__u=u; L('XHR-OPEN '+m+' '+u); return oopen.call(this,m,u,...a); };
  XMLHttpRequest.prototype.send=function(b){ L('XHR-SEND '+this.__m+' '+this.__u+' body='+(typeof b==='string'?b.slice(0,3000):'[bin '+((b&&b.byteLength)||0)+']')); return osend.call(this,b); };
  // JSON.stringify（明文）
  const os=JSON.stringify;
  JSON.stringify=function(v){ let s; try{s=os.apply(this,arguments);}catch(e){return os.apply(this,arguments);} try{ if(typeof s==='string'&&s.length>150&&s.indexOf('req_')>=0) L('JSON '+s);}catch(x){} return s; };
  // JSON.parse（明文响应）
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string'&&t.length>150&&/vkey|purl|"sip"|"filename"/i.test(t)) L('PARSE '+t);}catch(x){} return r; };
  return {ok:true};
}"""

SHOW="""() => {
  document.querySelectorAll('.mod_list_menu').forEach(m=>{ m.style.opacity='1'; m.style.visibility='visible'; m.style.pointerEvents='auto'; m.style.zIndex='9999'; });
  document.querySelectorAll('.list_menu__play').forEach(p=>{ p.style.pointerEvents='auto'; p.style.zIndex='10000'; });
  document.querySelectorAll('.songlist__songname').forEach(s=>{ s.style.pointerEvents='none'; });
  return {ok:true};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
m.call("evaluate_script",{"function":SHOW,"confirm":True,"mainWorld":True})
r=m.call("click_element",{"selector":"i.list_menu__icon_play","index":1,"confirm":True})
print("CLICK ok=",r.get('ok'))
time.sleep(12)
import re
out=[]
for i in range(60):
    got=False; off=0
    while True:
        rr=m.call("evaluate_script",{"function":"() => { const c=window.__log||[]; const s=c[%d]||''; return s.slice(%d,%d);}"%(i,off,off+2500),"confirm":True,"mainWorld":True})
        v=rr.get('data',{}).get('value') if isinstance(rr,dict) else None
        if not isinstance(v,str) or not v: break
        out.append(v); off+=2500; got=True
        if len(v)<2500: break
    if not got: break
log="".join(out)
open('hooklog.txt','w',encoding='utf-8').write(log)
print("loglen",len(log))
for line in log.split("\n"):
    if len(line)>200: print(line[:200],"...")
    else: print(line)
m.kill()
