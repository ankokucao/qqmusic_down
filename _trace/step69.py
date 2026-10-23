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
    let s;
    try{ s=os.apply(this,arguments); }catch(e){ return os.apply(this,arguments); }
    try{
      if(typeof s==='string' && s.length>150 && s.indexOf('req_')>=0){
        window.__cap.push(s);
      }
    }catch(x){}
    return s;
  };
  // 捕获响应解密后的明文：hook 页面里 JSON.parse
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string' && t.length>200 && /vkey|purl|sip/i.test(t)) window.__cap.push('RESP:'+t.slice(0,4000)); }catch(x){} return r; };
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
  return {clicked, n:(window.__cap||[]).length};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("TRIG:", json.dumps(m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:300])
time.sleep(2)
# 分块取回，避免超长截断
allcap=[]
off=0
while True:
    r=m.call("evaluate_script",{"function":"() => JSON.stringify((window.__cap||[]).slice(%d,%d))"%(off,off+3),"confirm":True,"mainWorld":True})
    val=r.get('data',{}).get('value') if isinstance(r,dict) else None
    if not val or val=='[]': break
    try: arr=json.loads(val)
    except Exception: print("bad chunk",repr(val)[:100]); break
    if not arr: break
    allcap.extend(arr); off+=3
    if len(arr)<3: break
open('cap_full.txt','w',encoding='utf-8').write("\n\n=====\n\n".join(allcap))
print("total captured:",len(allcap))
for i,s in enumerate(allcap):
    tag='RESP' if s.startswith('RESP:') else 'REQ'
    body=s[5:] if tag=='RESP' else s
    mods=re.findall(r'"module":"([^"]+)"',body) if tag=='REQ' else []
    print(i,tag,len(body),mods[:12] if mods else body[:200])
m.kill()
