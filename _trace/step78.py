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

# 强制显示所有 mod_list_menu，使播放按钮可点击
SHOW="""() => {
  const menus=document.querySelectorAll('.mod_list_menu');
  let n=0;
  menus.forEach(m=>{ m.style.opacity='1'; m.style.visibility='visible'; m.style.pointerEvents='auto'; m.style.zIndex='9999'; n++; });
  // 也把播放项本身放大便于点击
  document.querySelectorAll('.list_menu__play').forEach(p=>{ p.style.pointerEvents='auto'; p.style.zIndex='10000'; });
  // 解除歌名区遮挡：给歌名区加 pointer-events none
  document.querySelectorAll('.songlist__songname').forEach(s=>{ s.style.pointerEvents='none'; });
  // 验证
  const el=document.querySelectorAll('i.list_menu__icon_play')[1];
  let top=null;
  if(el){ const r=el.getBoundingClientRect(); const cx=r.left+r.width/2, cy=r.top+r.height/2;
    const t=document.elementFromPoint(cx,cy);
    top={tag:t&&t.tagName, cls:t?String(t.className&&t.className.baseVal!==undefined?t.className.baseVal:t.className).slice(0,60):null, isIcon: t===el}; }
  return {menus:n, top};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("SHOW:",json.dumps(m.call("evaluate_script",{"function":SHOW,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:600])
for sel in ["i.list_menu__icon_play",".list_menu__play"]:
    r=m.call("click_element",{"selector":sel,"index":1,"confirm":True})
    print("CLICK",sel,"ok=",r.get('ok') if isinstance(r,dict) else None,json.dumps(r,ensure_ascii=False)[:300])
    if isinstance(r,dict) and r.get('ok'): break
    time.sleep(2)
time.sleep(10)
st=m.call("evaluate_script",{"function":"() => ({n:(window.__cap||[]).length, audio:Array.from(document.querySelectorAll('audio')).map(a=>({s:a.src,c:a.currentSrc})), html: (document.querySelector('.player')||{}).outerHTML? document.querySelector('.player').outerHTML.slice(0,300):null})","confirm":True,"mainWorld":True})
print("state:",json.dumps(st,ensure_ascii=False)[:900])
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
open('cap_click3.txt','w',encoding='utf-8').write(cap)
print("caplen",len(cap))
for mm in re.finditer(r'"module":"([^"]+)"',cap): print("MOD:",mm.group(1))
print("vkey",len(re.findall(r'vkey',cap,re.I)),"purl",len(re.findall(r'"purl"',cap)))
m.kill()
