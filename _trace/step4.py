import json,sys
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
INJECT = "(raw) => { const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
# 用 CDP 设 cookie 更可靠：这里先用 document.cookie
r=m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
print("INJECT:", json.dumps(r,ensure_ascii=False)[:200])
# evaluate_script 不支持参数传入，用 mainWorld 内嵌字符串
INJECT2 = "(raw) => { const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
# 直接在页面里用 JS 字符串字面量注入
lit = json.dumps(COOKIE)
js = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
r=m.call("evaluate_script",{"function":js,"confirm":True,"mainWorld":True})
print("INJECT2:", json.dumps(r,ensure_ascii=False)[:200])

# 校验登录态
chk = "() => ({qpsvr: localStorage.getItem('qpsvr'), cookies: document.cookie.includes('qm_keyst')})"
r=m.call("evaluate_script",{"function":chk,"confirm":True,"mainWorld":True})
print("STATE:", json.dumps(r,ensure_ascii=False)[:500])

# 打开歌曲播放页（晴天 mid: 晴天 = 003OUlho2HcRHC 需确认，先用首页）
r=m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/songDetail/003OUlho2HcRHC","timeout":30000})
print("NAV:", json.dumps(r,ensure_ascii=False)[:300])

# 列出网络请求
r=m.call("list_network_requests",{"pageSize":60,"resourceTypes":["xhr","fetch"]})
print("NET:", json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
