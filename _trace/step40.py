import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/toplist","timeout":30000})
time.sleep(12)
JS = """() => {
  const c = window.crypto;
  const out = {cryptoKeys: Object.keys(c||{}), windowCrypto: typeof c};
  // 常见的 SDK 全局
  const names = Object.keys(window).filter(k=>typeof window[k]==='object' && window[k] && /sdk|qmfe|cgi/i.test(k));
  out.sdkGlobals = names.slice(0,20);
  const detail = {};
  names.slice(0,20).forEach(k=>{ try{ detail[k]=Object.keys(window[k]).slice(0,25);}catch(e){} });
  out.detail = detail;
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("SDK:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
