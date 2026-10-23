import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

# 在 XHR.send 之前 hook JSON.stringify —— 加密前的明文 body 必经 JSON.stringify
HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){
    try{
      const s=os.apply(this,arguments);
      if(typeof s==='string' && s.length>200 && s.indexOf('req_')>=0){
        window.__cap.push({t:'json', len:s.length, data:s.slice(0,4000)});
      }
    }catch(x){}
    return os.apply(this,arguments);
  };
  // 同时 hook atob / TextDecoder 以捕获解密后明文
  const od=window.atob;
  window.atob=function(s){ try{ const r=od.apply(this,arguments); if(r.length>200) window.__cap.push({t:'atob',len:r.length,data:r.slice(0,3000)}); return r; }catch(x){ return od.apply(this,arguments); } };
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
  await new Promise(r=>setTimeout(r,8000));
  return {clicked, cap:(window.__cap||[]).length};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("TRIG:", json.dumps(m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:400])
time.sleep(2)
GET="() => JSON.stringify(window.__cap||[])"
r=m.call("evaluate_script",{"function":GET,"confirm":True,"mainWorld":True})
val=r.get('data',{}).get('value') if isinstance(r,dict) else None
open('cap2.json','w',encoding='utf-8').write(val or '')
print("CAP len",len(val or ''))
try:
    arr=json.loads(val)
    for x in arr:
        print("###",x.get('t'),x.get('len'))
        print((x.get('data') or '')[:2500]); print()
except Exception as e:
    print("parse err",e); print((val or '')[:2000])
m.kill()
