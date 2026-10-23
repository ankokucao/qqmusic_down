import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

GETREQ="""() => {
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push=orig;
  const R=window.__WREQ, defs=R.m||{};
  const s8=String(defs['8']);
  const out={};
  // 导出整个 module8 到分段
  window.__m8 = s8;
  out.len = s8.length;
  const names=['lr','gr','ur','hr','Br','sr','_o','fr','O','$'];
  out.fndefs={};
  for(const n of names){
    const i=s8.indexOf('function '+n+'(');
    out.fndefs[n]= i>=0 ? s8.slice(i, i+260) : null;
  }
  // re / ie 定义
  const iRe=s8.indexOf('re=');
  out.re_ctx = iRe>=0 ? s8.slice(Math.max(0,iRe-200), iRe+300) : null;
  const iIe=s8.indexOf('ie=');
  out.ie_ctx = iIe>=0 ? s8.slice(Math.max(0,iIe-200), iIe+300) : null;
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":GETREQ,"confirm":True,"mainWorld":True})
v=r.get('data',{}).get('value',{}) if isinstance(r,dict) else {}
print(json.dumps(v,ensure_ascii=False)[:5000])
# 分段导出 module8
CH=12000
n=int(v.get('len',0))
out=[]
for st in range(0,n,CH):
    res=m.call("evaluate_script",{"function":"() => window.__m8.slice(%d,%d)"%(st,st+CH),"confirm":True,"mainWorld":True})
    val=res.get('data',{}).get('value') if isinstance(res,dict) else None
    if not isinstance(val,str): print("chunk fail",st,repr(val)[:200]); break
    out.append(val)
src=''.join(out)
open('module8.js','w',encoding='utf-8').write(src)
print("saved module8.js len",len(src))
m.kill()
