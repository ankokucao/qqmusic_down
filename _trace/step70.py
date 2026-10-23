import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){
    let s; try{ s=os.apply(this,arguments); }catch(e){ return os.apply(this,arguments); }
    try{ if(typeof s==='string' && s.length>150 && s.indexOf('req_')>=0) window.__cap.push(s); }catch(x){}
    return s;
  };
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string' && t.length>150 && /vkey|purl|"sip"|play_url|file/i.test(t)) window.__cap.push('RESP:'+t); }catch(x){} return r; };
  return {ok:true};
}"""

TRIG="""async () => {
  const all=document.querySelectorAll('*');
  let clicked=0;
  for(const el of all){
    if(clicked>6) break;
    const cn=(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className)||'';
    if(typeof cn==='string' && /play/i.test(cn)){
      const r=el.getBoundingClientRect();
      if(r.width>0&&r.height>0){ try{ el.click(); clicked++; }catch(x){} }
    }
  }
  await new Promise(r=>setTimeout(r,9000));
  return {clicked, n:(window.__cap||[]).length, total:(window.__cap||[]).reduce((a,b)=>a+b.length,0)};
}"""

READ="() => { const c=window.__cap||[]; const i=window.__i||0; const s=c[i]||''; return s.slice(0,2500); }"
ADVI="() => { window.__i=(window.__i||0)+1; return window.__i; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("TRIG:", json.dumps(m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:300])
time.sleep(2)
# 用 evaluate_script 读出长度，再逐条读
rr=m.call("evaluate_script",{"function":"() => (window.__cap||[]).map(s=>s.length)","confirm":True,"mainWorld":True})
lens=rr.get('data',{}).get('value') if isinstance(rr,dict) else None
print("lens",lens)
outs=[]
for i in range(30):
    m.call("evaluate_script",{"function":"() => { window.__i=%d; return 1; }"%i,"confirm":True,"mainWorld":True})
    got=False
    off=0
    while True:
        r=m.call("evaluate_script",{"function":"() => { const c=window.__cap||[]; const s=c[%d]||''; return s.slice(%d,%d); }"%(i,off,off+2500),"confirm":True,"mainWorld":True})
        v=r.get('data',{}).get('value') if isinstance(r,dict) else None
        if not isinstance(v,str) or not v: break
        outs.append(v); off+=2500; got=True
        if len(v)<2500: break
    if not got: break
cap="".join(outs)
open('cap_full.txt','w',encoding='utf-8').write(cap)
print("total len",len(cap))
import re
for m2 in re.finditer(r'"module":"([^"]+)"',cap):
    print("MOD:",m2.group(1))
print("vkey hits:",len(re.findall(r'vkey',cap)), "purl:",len(re.findall(r'purl',cap)))
m.kill()
