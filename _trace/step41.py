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
# 搜播放器取地址的模块名：常见 'playUrl'/'GetSongPlayUrl'/'music.playUrl' 等
for q in ['playUrl','PlayUrl','play_url','GetPlayUrl','getSongUrl','playinfo','play_info','PlayInfo','music.streamProxyUrl','vkey']:
    r=m.call("search_in_sources",{"query":q,"maxResults":6,"maxLineLength":200})
    d=r.get('data',{})
    if d.get('totalMatches'):
        print("###",q,d.get('totalMatches'))
        for mm in (d.get('matches') or [])[:4]:
            print("   ", mm['url'][:80],"|",mm['lineContent'][:200].replace("\n"," "))
m.kill()
