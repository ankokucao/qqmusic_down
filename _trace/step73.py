import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){ let s; try{ s=os.apply(this,arguments);}catch(e){ return os.apply(this,arguments);} try{ if(typeof s==='string'&&s.length>150&&s.indexOf('req_')>=0) window.__cap.push('R:'+s);}catch(x){} return s; };
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string'&&t.length>150&&/vkey|purl|"sip"|play_url|"filename"|"url":/i.test(t)) window.__cap.push('P:'+t);}catch(x){} return r; };
  return {ok:true};
}"""

# 在歌手页找到歌曲行播放按钮并点击
TRIG="""async () => {
  const info=[];
  const sels=['.list_menu__play','.songlist__play','i.list_menu__icon_play','.icon_play','.play-icon','.mod_cover__icon_play','[class*=play]'];
  for(const s of sels){ try{ const e=document.querySelectorAll(s); if(e.length) info.push(s+'='+e.length);}catch(x){} }
  const btn=document.querySelector('.list_menu__play')||document.querySelector('[class*=play]');
  let clicked=false, txt='';
  if(btn){ const r=btn.getBoundingClientRect(); txt=JSON.stringify({cls:String(btn.className).slice(0,60),w:r.width,h:r.height,top:r.top,left:r.left});
    btn.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,400));
    btn.click(); clicked=true; }
  await new Promise(r=>setTimeout(r,9000));
  return {info, clicked, txt, n:(window.__cap||[]).length};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
r=m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True})
print("TRIG:",json.dumps(r,ensure_ascii=False)[:1200])
time.sleep(2)
# 读回捕获
lens=m.call("evaluate_script",{"function":"() => (window.__cap||[]).map(s=>s.length)","confirm":True,"mainWorld":True})
lv=lens.get('data',{}).get('value') if isinstance(lens,dict) else None
print("lens",lv)
out=[]
import re
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
open('cap_singer.txt','w',encoding='utf-8').write(cap)
print("caplen",len(cap))
for mm in re.finditer(r'"module":"([^"]+)"',cap): print("MOD:",mm.group(1))
print("vkey",len(re.findall(r'vkey',cap,re.I)),"purl",len(re.findall(r'"purl"',cap)),"sip",len(re.findall(r'"sip"',cap)))
m.kill()
