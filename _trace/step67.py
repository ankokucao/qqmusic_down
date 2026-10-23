import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push=orig;
  const R=window.__WREQ, M8=R(8);
  window.__cap=[];
  // hook 低层 ur (export c)
  if(typeof M8.c==='function'){
    const Ou=M8.c;
    M8.c=function(e){ try{ if(e && e.data) window.__cap.push({t:'ur', url:e.url, data:String(e.data).slice(0,3000)}); }catch(x){} return Ou.apply(this, arguments); };
    window.__cap.push({t:'hook-ur'});
  }
  // hook 高层 request
  try{
    const P=M8.a.prototype;
    if(P && typeof P.request==='function'){
      const Or=P.request;
      P.request=function(reqs){ try{ window.__cap.push({t:'req', data:JSON.stringify(reqs).slice(0,3000)}); }catch(x){} return Or.apply(this, arguments); };
      window.__cap.push({t:'hook-request'});
    }
  }catch(x){ window.__cap.push({t:'err-req',e:String(x)}); }
  // 也 hook 全局 XHR send 记录 URL
  const osend=XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send=function(b){ try{ window.__cap.push({t:'xhr', url:this.__u||'', len: b&&b.length}); }catch(x){} return osend.apply(this, arguments); };
  const oopen=XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open=function(m,u){ this.__u=u; return oopen.apply(this, arguments); };
  return {ok:true, cap: window.__cap.length};
}"""

# 触发播放：JS 直接 .click()（不受遮挡影响），并列出候选元素
TRIG="""async () => {
  const cands=[];
  const sels=['i.mod_cover__icon_play','.play-btn','.icon_play','.mod_cover__icon_play',
    'a.list_menu__play','.songlist__play','.play_ico','.icon-play','.btn_play',
    '[class*=play]','.iconfont.icon-play'];
  for(const s of sels){
    try{ const els=document.querySelectorAll(s); if(els.length) cands.push(s+' -> '+els.length); }catch(x){}
  }
  // 通用：找带 play 的类名元素
  const all=document.querySelectorAll('*');
  const hits=[];
  let n=0;
  for(const el of all){
    if(n>8) break;
    const cn=(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className)||'';
    if(typeof cn==='string' && /play/i.test(cn) && el.tagName!=='SCRIPT' && el.tagName!=='STYLE'){
      const r=el.getBoundingClientRect();
      hits.push({tag:el.tagName, cls:cn.slice(0,60), w:Math.round(r.width), h:Math.round(r.height), top:Math.round(r.top)});
      n++;
    }
  }
  // 点击所有可点的 play 元素
  let clicked=0;
  for(const el of all){
    if(clicked>6) break;
    const cn=(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className)||'';
    if(typeof cn==='string' && /play/i.test(cn)){
      const r=el.getBoundingClientRect();
      if(r.width>0&&r.height>0){ try{ el.click(); clicked++; }catch(x){} }
    }
  }
  await new Promise(r=>setTimeout(r,6000));
  return {cands, hits: hits.slice(0,12), clicked, cap:(window.__cap||[]).length};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
print("HOOK:", json.dumps(m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:600])
print("TRIG:", json.dumps(m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:1500])
time.sleep(3)
GET="() => JSON.stringify(window.__cap||[])"
r=m.call("evaluate_script",{"function":GET,"confirm":True,"mainWorld":True})
val=r.get('data',{}).get('value') if isinstance(r,dict) else None
open('cap1.json','w',encoding='utf-8').write(val or '')
print("CAP len",len(val or ''))
print((val or '')[:3000])
m.kill()
