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
JS = """() => {
  const out={};
  try{
    const arr = window.webpackJsonp;
    // webpack4: webpackJsonp.push 覆盖以捕获 require
    let req=null;
    const origPush = arr.push;
    arr.push = function(chunk){
      const result = origPush.apply(this, arguments);
      try{ if(chunk && chunk.length>1) req = chunk[1]; }catch(e){}
      return result;
    };
    // 触发一次动态 chunk 加载以捕获 require：直接 push 一个假 chunk 不行，改为从已有 chunk 里找
    // 已知 require 存在于 runtime chunk；尝试常见路径
    out.captured = !!req;
    arr.push = origPush;
    // 直接搜索 runtime 中的 require 名字
    out.hint = 'need runtime';
  }catch(e){ out.err=e.message; }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("CAP:", json.dumps(r,ensure_ascii=False)[:1500])
# runtime chunk 里通常有 window.webpackJsonp.push([[chunkIds],{...}]) 形式；读取 runtime 源码找 require 名
r=m.call("get_script_source",{"url":"https://y.qq.com/ryqq/js/runtime~Page.2ef1b1e081a519a5bb2f.js","startLine":1,"endLine":40})
print("RUNTIME:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
