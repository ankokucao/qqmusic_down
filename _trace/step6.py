import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/003OUlho2HcRHC"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":30000})
time.sleep(3)

# 触发播放：点击播放按钮
js = """() => {
  const cands = Array.from(document.querySelectorAll('[class*=play],[class*=btn]'));
  const hits = cands.filter(e => /播放|play/i.test(e.getAttribute('title')||e.getAttribute('aria-label')||e.className||'')).slice(0,8);
  return hits.map(e=>({tag:e.tagName, cls:String(e.className).slice(0,80), title:e.getAttribute('title')}));
}"""
r=m.call("evaluate_script",{"function":js,"confirm":True,"mainWorld":True})
print("BUTTONS:", json.dumps(r,ensure_ascii=False)[:1500])

# 直接用页面内音频播放器触发
js2 = """() => {
  // 尝试找到全局播放器并调用 play
  const keys = Object.keys(window).filter(k=>/player|audio|music/i.test(k)).slice(0,40);
  return keys;
}"""
r=m.call("evaluate_script",{"function":js2,"confirm":True,"mainWorld":True})
print("GLOBALS:", json.dumps(r,ensure_ascii=False)[:1200])

# 抓网络
r=m.call("list_network_requests",{"pageSize":80,"resourceTypes":["xhr","fetch"]})
print("NET:", json.dumps(r,ensure_ascii=False)[:8000])
m.kill()
