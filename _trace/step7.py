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
time.sleep(4)

# 点击封面播放按钮
r=m.call("click_element",{"selector":"i.mod_cover__icon_play","confirm":True})
print("CLICK:", json.dumps(r,ensure_ascii=False)[:400])
time.sleep(6)

# 抓媒体请求
r=m.call("list_network_requests",{"pageSize":100,"resourceTypes":["media","xhr","fetch"]})
txt=json.dumps(r,ensure_ascii=False)
print("NET:", txt[:9000])
# 导出所有 musics.fcg 请求体
reqids=[x['reqid'] for x in r['data']['requests'] if 'musics.fcg' in x['url']]
print("MUSICS_REQIDS:", reqids)
for rid in reqids:
    out=f"musics_{rid}.txt"
    rr=m.call("list_network_requests",{"reqid":rid,"outputFile":os.path.abspath(out),"outputPart":"all"})
    print("EXPORT",rid,json.dumps(rr,ensure_ascii=False)[:300])
m.kill()
