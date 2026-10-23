import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  const wj = window.webpackJsonp;
  const orig = wj.push.bind(wj);
  wj.push = function(arr){ const mods=arr[1]; if(mods){ for(const k in mods){ if(typeof mods[k]==='function'){ window.__WREQ=mods[k]; break; } } } return orig(arr); };
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push = orig;
  const R = window.__WREQ;
  const out = {ids:{}};
  for (const id of ['8','433']) {
    try {
      const ex = R(id);
      const keys = Object.keys(ex||{});
      const info = {};
      for (const k of keys) {
        const v = ex[k];
        info[k] = typeof v === 'function' ? 'fn:'+(v.length)+':'+String(v).slice(0,140) : (typeof v);
      }
      out.ids[id] = {keys: keys, info: info};
    } catch(e){ out.ids[id] = {err:String(e)}; }
  }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print(json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
