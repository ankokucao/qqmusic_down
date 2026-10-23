import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

DUMP="""() => {
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push=orig;
  const R=window.__WREQ, defs=R.m||{};
  const res={};
  // 找提供 encrypt/decrypt 与 getSecuritySign 的模块
  const cands={};
  for(const k of Object.keys(defs)){
    const s=String(defs[k]);
    const f=[];
    if(/encrypt\s*[:=]/.test(s)) f.push('enc');
    if(/decrypt\s*[:=]/.test(s)) f.push('dec');
    if(/getSecuritySign/.test(s)) f.push('sign');
    if(/__TmeWebSec/.test(s)) f.push('tmews');
    if(f.length) cands[k]=f;
  }
  res.cands=cands;
  // module 8 里 re / ie 的定义
  const s8=String(defs['8']);
  const findVar=(v)=>{ const m=s8.match(new RegExp('[,;]([\\\\w$]+)=n\\\\((\\\\d+)\\\\)')); return null; };
  const m8=[];
  const re=/(?:^|[,;])\s*([\w$]+)\s*=\s*n\((\d+)\)/g; let mm;
  while((mm=re.exec(s8))){ if(m8.length<200) m8.push(mm[1]+'->'+mm[2]); }
  res.m8_requires=m8.join(',');
  const iRe=s8.search(/[,;]re\s*=\s*n\(\d+\)/);
  res.re_def = iRe>=0 ? s8.slice(iRe,iRe+120) : null;
  const iIe=s8.search(/[,;]ie\s*=\s*n\(\d+\)/);
  res.ie_def = iIe>=0 ? s8.slice(iIe,iIe+120) : null;
  res.m8_head = s8.slice(0,900);
  return res;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":DUMP,"confirm":True,"mainWorld":True})
v=r.get('data',{}).get('value',{}) if isinstance(r,dict) else {}
open('dump62.json','w',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=1))
print(json.dumps(v,ensure_ascii=False)[:4000])
m.kill()
