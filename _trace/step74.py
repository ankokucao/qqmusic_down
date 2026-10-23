import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
def net(tag):
    r=m.call("list_network_requests",{"pageSize":100})
    s=json.dumps(r,ensure_ascii=False)
    print("###",tag,"len",len(s))
    # 找 musics.fcg / stream.qqmusic
    import re
    for m2 in re.finditer(r'"url":"([^"]*musics\.fcg[^"]*)"',s): print("  MUSICS:",m2.group(1)[:150])
    for m2 in re.finditer(r'"url":"([^"]*stream\.qqmusic[^"]*)"',s): print("  STREAM:",m2.group(1)[:200])
    return s
net("before")
# 点击行播放
TRIG="""async () => {
  const btn=document.querySelector('.list_menu__play');
  if(!btn) return {err:'no btn'};
  btn.scrollIntoView({block:'center'});
  await new Promise(r=>setTimeout(r,300));
  btn.click();
  await new Promise(r=>setTimeout(r,12000));
  return {ok:true, audio: Array.from(document.querySelectorAll('audio')).map(a=>({src:a.src, cur:a.currentSrc}))};
}"""
print("TRIG:",json.dumps(m.call("evaluate_script",{"function":TRIG,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:1500])
net("after")
m.kill()
