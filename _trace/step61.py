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
  const s8=String(defs['8']);
  res.m8_len=s8.length;
  const grab=(kw,before,after)=>{const i=s8.indexOf(kw); return i<0?null:s8.slice(Math.max(0,i-before),i+after);};
  res.ctx_musics = grab('musics.fcg',1800,1200);
  res.ctx_encParam = grab('encParam',1500,1500);
  res.ctx_vkey = grab('vkey',600,600);
  res.has6151 = !!defs['6151'];
  res.has6151_src = defs['6151'] ? String(defs['6151']).slice(0,400) : null;
  // 搜所有模块里的 __cgiEncrypt 定义与 'ag-1'
  const kws=['__cgiEncrypt','ag-1','GetVkey','vkeyProxyUrl','qqmusic_guid'];
  for(const w of kws){
    const hits=[];
    for(const k of Object.keys(defs)){ const s=String(defs[k]); if(s.indexOf(w)>=0) hits.push(k); }
    res['mods_'+w]=hits;
  }
  // SPD
  try{ const spd=window.SPD; res.spd=Object.keys(spd||{}).slice(0,40); }catch(e){res.spd=String(e);}
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
open('dump61.json','w',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=1))
for k in v:
    if k.startswith('mods_') or k in ('has6151','has6151_src','spd','m8_len'):
        print(k,'=',json.dumps(v[k],ensure_ascii=False)[:600])
print('=== ctx_musics ==='); print((v.get('ctx_musics') or '')[:3000])
m.kill()
