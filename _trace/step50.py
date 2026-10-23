import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":30000})
time.sleep(12)
# 抓 webpack chunk 里的 module exports：站点请求用的 axios 实例
JS = """() => {
  const out={};
  // webpackJsonp 全局
  const keys=Object.keys(window).filter(k=>/webpack/i.test(k));
  out.webpackKeys=keys;
  try{
    const wj = window.webpackJsonp || window.webpackChunkYqqMusic;
    out.wjType = typeof wj;
    if(wj && wj.length){ out.chunkNums = wj.map(c=>c[0]); }
  }catch(e){ out.err=e.message; }
  // 常见全局暴露
  ['__webpack_require__','webpackJsonp','webpackChunk','__NEXT_DATA__'].forEach(k=>{ out[k]= typeof window[k]; });
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("WP:", json.dumps(r,ensure_ascii=False)[:3000])
m.kill()
