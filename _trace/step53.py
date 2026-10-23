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
for q in ['__webpack_require__','webpackJsonp.push','installedModules','function r(e)','encrypt:function','decrypt']:
    r=m.call("search_in_sources",{"query":q,"maxResults":5,"maxLineLength":300,"urlFilter":"runtime"})
    d=r.get('data',{})
    if d.get('totalMatches'):
        print("###",q,d['totalMatches'])
        for mm in d['matches'][:3]:
            print("   ",mm['lineContent'][:280].replace("\n"," "))
# 找 encrypt 的定义位置（vendor）
r=m.call("search_in_sources",{"query":"encrypt","maxResults":10,"maxLineLength":300,"urlFilter":"vendor.chunk"})
d=r.get('data',{})
print("### encrypt in vendor:", d.get('totalMatches'))
for mm in (d.get('matches') or [])[:8]:
    print("   ",mm['lineContent'][:260].replace("\n"," "))
m.kill()
