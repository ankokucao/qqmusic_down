import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
# 先 hook 明文
HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){ let s; try{s=os.apply(this,arguments);}catch(e){return os.apply(this,arguments);} try{ if(typeof s==='string'&&s.length>150&&s.indexOf('req_')>=0) window.__cap.push('R:'+s);}catch(x){} return s; };
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string'&&t.length>150&&/vkey|purl|"sip"|"filename"/i.test(t)) window.__cap.push('P:'+t);}catch(x){} return r; };
  return {ok:true};
}"""
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
# 真实鼠标点击第 2 行的播放按钮
for sel,idx in [(".list_menu__play",1),(".list_menu__play",0),("i.list_menu__icon_play",1)]:
    r=m.call("click_element",{"selector":sel,"index":idx,"confirm":True})
    print("CLICK",sel,idx,json.dumps(r,ensure_ascii=False)[:400])
    time.sleep(6)
    st=m.call("evaluate_script",{"function":"() => ({n:(window.__cap||[]).length, audio:Array.from(document.querySelectorAll('audio')).map(a=>a.src||a.currentSrc)})","confirm":True,"mainWorld":True})
    print("  state:",json.dumps(st,ensure_ascii=False)[:600])
    if isinstance(st,dict):
        v=st.get('data',{}).get('value',{})
        if v.get('n',0)>1 or v.get('audio'): break
# 读回
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
open('cap_click.txt','w',encoding='utf-8').write(cap)
print("caplen",len(cap))
for mm in re.finditer(r'"module":"([^"]+)"',cap): print("MOD:",mm.group(1))
print("vkey",len(re.findall(r'vkey',cap,re.I)),"purl",len(re.findall(r'"purl"',cap)),"sip",len(re.findall(r'"sip"',cap)))
m.kill()
