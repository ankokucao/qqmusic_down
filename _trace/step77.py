import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){ let s; try{s=os.apply(this,arguments);}catch(e){return os.apply(this,arguments);} try{ if(typeof s==='string'&&s.length>150&&s.indexOf('req_')>=0) window.__cap.push('R:'+s);}catch(x){} return s; };
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string'&&t.length>150&&/vkey|purl|"sip"|"filename"/i.test(t)) window.__cap.push('P:'+t);}catch(x){} return r; };
  return {ok:true};
}"""

# 先 hover 出行，再真实点击图标
HOVER="""async () => {
  const row=document.querySelectorAll('.songlist__songname')[1]||document.querySelector('.songlist__songname');
  if(row) row.scrollIntoView({block:'center'});
  await new Promise(r=>setTimeout(r,500));
  return {ok:!!row, html: row? row.outerHTML.slice(0,600):null};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("HOVER:",json.dumps(m.call("evaluate_script",{"function":HOVER,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:1200])
# 真实鼠标移动到行内播放按钮位置
for sel in ["i.list_menu__icon_play",".list_menu__play i",".list_menu__play .icon_play"]:
    r=m.call("click_element",{"selector":sel,"index":1,"confirm":True})
    ok=r.get('ok') if isinstance(r,dict) else None
    print("CLICK",sel,json.dumps(r,ensure_ascii=False)[:300])
    if ok: break
    time.sleep(2)
time.sleep(8)
st=m.call("evaluate_script",{"function":"() => ({n:(window.__cap||[]).length, audio:Array.from(document.querySelectorAll('audio')).map(a=>a.src||a.currentSrc)})","confirm":True,"mainWorld":True})
print("state:",json.dumps(st,ensure_ascii=False)[:600])
import re
out=[]
for i in range(30):
    got=False; off=0
    while True:
        rr=m.call("evaluate_script",{"function":"() => { const c=window.__cap||[]; const s=c[%d]||''; return s.slice(%d,%d);}"%(i,off,off+2500),"confirm":True,"mainWorld":True})
        v=rr.get('data',{}).get('value') if isinstance(rr,dict) else None
        if not isinstance(v,str) or not v: break
        out.append(v); off+=2500; got=True
        if len(v)<2500: break
    if not got: break
cap="".join(out)
open('cap_click2.txt','w',encoding='utf-8').write(cap)
print("caplen",len(cap))
for mm in re.finditer(r'"module":"([^"]+)"',cap): print("MOD:",mm.group(1))
print("vkey",len(re.findall(r'vkey',cap,re.I)),"purl",len(re.findall(r'"purl"',cap)))
m.kill()
