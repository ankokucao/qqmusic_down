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
time.sleep(9)

# 悬停第一行并点击其播放按钮
JS = """() => {
  const row = document.querySelectorAll('.songlist__item')[0];
  if (!row) return 'norow';
  const a = row.querySelector('a.songlist__icon_play, i.songlist__icon_play, [class*=play]');
  if (a) { a.dispatchEvent(new MouseEvent('mouseover',{bubbles:true})); a.click(); return 'clicked ' + a.className; }
  row.dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));
  return 'rowonly';
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("CLICK:", json.dumps(r,ensure_ascii=False)[:400])
time.sleep(10)

r=m.call("list_network_requests",{"pageSize":100,"resourceTypes":["media","other","xhr","fetch"]})
for x in r['data']['requests']:
    print(" REQ",x['reqid'],x['method'],x['resourceType'],x['status'],x['url'][:150])
r=m.call("evaluate_script",{"function":"() => ({audios:Array.from(document.querySelectorAll('audio')).map(a=>({src:a.src,cls:a.className,id:a.id})), html:Array.from(document.querySelectorAll('audio')).map(a=>a.outerHTML.slice(0,300))})","confirm":True,"mainWorld":True})
print("AUDIO:", json.dumps(r,ensure_ascii=False)[:2500])
m.kill()
