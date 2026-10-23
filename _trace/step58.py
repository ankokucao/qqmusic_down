import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  try {
    const wj = window.webpackJsonp;
    if (typeof wj.push !== 'function') return {err:'no push'};
    let req = null;
    const orig = wj.push.bind(wj);
    wj.push = function(arr){
      // arr = [chunkIds, modules, entry]
      const mods = arr[1];
      if (mods) { for (const k in mods) { if (typeof mods[k] === 'function') { req = mods[k]; break; } } }
      return orig(arr);
    };
    wj.push([[], {9999: function(module, exports, req2){ window.__req = req2; }}, [[9999]]]);
    wj.push = orig;
    if (!window.__req) return {err:'no req captured'};
    window.__req = null;
    return {ok:true, hasReq: !!req};
  } catch(e) { return {err: String(e)}; }
}"""

# 更稳的取 require 方法：webpack4 里 __webpack_require__ 通过 push 捕获
HOOK2="""() => {
  const out = {};
  try {
    const wj = window.webpackJsonp;
    const orig = wj.push.bind(wj);
    let got = null;
    wj.push = function(arr){
      const mods = arr[1];
      if (mods) { for (const k in mods) { if (typeof mods[k]==='function'){ got = mods[k]; break; } } }
      return orig(arr);
    };
    wj.push([[999999], {999999:(m,e,r)=>{ window.__WREQ = r; }}, [[999999]]]);
    wj.push = orig;
    out.hasWREQ = !!window.__WREQ;
    if (window.__WREQ) {
      const R = window.__WREQ;
      // 收集已注册 module 定义
      const defs = R.m || {};
      out.defCount = Object.keys(defs).length;
      const hits = [];
      for (const k of Object.keys(defs)) {
        const s = String(defs[k]);
        if (s.indexOf('__cgiEncrypt')>=0 || s.indexOf('musics.fcg')>=0) hits.push(k);
      }
      out.hits = hits;
      // 列出 chunk 数组长度
      out.wjLen = wj.length;
      out.wj0 = JSON.stringify(wj[0]).slice(0,200);
    }
  } catch(e){ out.err=String(e); }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":HOOK2,"confirm":True,"mainWorld":True})
print(json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
