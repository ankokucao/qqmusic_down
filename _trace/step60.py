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
  const kw=['musics.fcg','vkeyProxyUrl','GetVkey','cgiEncrypt','musicu.fcg'];
  for(const k of Object.keys(defs)){
    const s=String(defs[k]);
    const found=kw.filter(w=>s.indexOf(w)>=0);
    if(found.length) res[k]=found;
  }
  // dump module 8 关键片段
  const s8=String(defs['8']);
  const i=s8.indexOf('cgiEncrypt');
  res.m8_ctx = i>=0 ? s8.slice(Math.max(0,i-2500), i+1500) : s8.slice(0,1500);
  res.m8_len = s8.length;
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
open('mod8.txt','w',encoding='utf-8').write(json.dumps({k:v.get(k) for k in v if k!='m8_ctx'},ensure_ascii=False,indent=1))
print("MODULE HITS:", json.dumps({k:v.get(k) for k in v if k not in('m8_ctx',)},ensure_ascii=False)[:3000])
print("=== m8_ctx ===")
print(v.get('m8_ctx','')[:3500])
m.kill()
