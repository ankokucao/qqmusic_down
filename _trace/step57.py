import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

EXPLORE="""() => {
  const keys = Object.keys(window).filter(k => /webpack|chunk|spd|music|player|cgi|qmusic|qmfe/i.test(k));
  const vals = {};
  for (const k of keys.slice(0,60)) {
    try { const v = window[k]; vals[k] = (typeof v) + (typeof v === 'function' ? '/fn' : (Array.isArray(v)?'/arr':'')); } catch(e){ vals[k]='err'; }
  }
  return { keys: keys, vals: vals, ua: navigator.userAgent.slice(0,60) };
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(10)
r=m.call("evaluate_script",{"function":EXPLORE,"confirm":True,"mainWorld":True})
print(json.dumps(r,ensure_ascii=False)[:4000])
print("---- scripts")
ls=m.call("list_scripts",{"pageSize":100})
items=ls.get('data',{}).get('scripts',ls.get('scripts',[])) if isinstance(ls,dict) else []
for s in items:
    print(s.get('scriptId'), (s.get('url') or '(inline)')[:130])
m.kill()
