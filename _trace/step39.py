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
# 找 qmfe-sdk-cgi 脚本与其导出的全局
r=m.call("list_scripts",{"filter":"qmfe-sdk-cgi","pageSize":10})
print("SCRIPTS:", json.dumps(r,ensure_ascii=False)[:1500])
r=m.call("evaluate_script",{"function":"() => { const ks=Object.keys(window).filter(k=>/sdk|cgi|qmfe|encrypt|crypt/i.test(k)); return ks.slice(0,40); }","confirm":True,"mainWorld":True})
print("GLOBALS:", json.dumps(r,ensure_ascii=False)[:1500])
# 在 vendor 里搜 re.encrypt 定义
r=m.call("search_in_sources",{"query":"re.encrypt","maxResults":6,"maxLineLength":400})
print("RE:", json.dumps(r,ensure_ascii=False)[:2500])
m.kill()
