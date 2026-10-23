import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

CALL="""async () => {
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push=orig;
  const R=window.__WREQ;
  const M8=R(8);
  const out={exports:Object.keys(M8)};
  // 尝试用 export 'c'(ur) 发请求
  const mid = '000NBVdP3wg95P';
  const fn = 'C400000NBVdP3wg95P.mp3';
  const param = {guid:'1000000000', songmid:mid, songtype:0, uin:'1152921504608413217',
                 loginflag:1, platform:'20', filename:fn};
  const req = {module:'music.vkeyProxyUrl', method:'GetVkey', param: param};
  const opts = {url:'https://u.y.qq.com/cgi-bin/musicu.fcg', type:'POST', needSign:true, dataType:'json'};
  try {
    const fnC = M8.c;
    const r = await fnC(opts, req);
    out.via_c = r;
  } catch(e){ out.err_c = String(e); }
  try {
    const inst = new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg', type:'POST', needSign:true});
    const res = await inst.request([req]);
    out.via_a = res;
  } catch(e){ out.err_a = String(e); }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":CALL,"confirm":True,"mainWorld":True})
print(json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
