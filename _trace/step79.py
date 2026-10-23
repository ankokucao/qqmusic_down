import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

SHOW="""() => {
  document.querySelectorAll('.mod_list_menu').forEach(m=>{ m.style.opacity='1'; m.style.visibility='visible'; m.style.pointerEvents='auto'; m.style.zIndex='9999'; });
  document.querySelectorAll('.list_menu__play').forEach(p=>{ p.style.pointerEvents='auto'; p.style.zIndex='10000'; });
  document.querySelectorAll('.songlist__songname').forEach(s=>{ s.style.pointerEvents='none'; });
  return {ok:true};
}"""

DIAG="""() => {
  const out={};
  out.frames = Array.from(document.querySelectorAll('iframe')).map(f=>({src:f.src, cls:f.className}));
  out.audios = document.querySelectorAll('audio').length;
  out.videos = document.querySelectorAll('video').length;
  out.audioTags = Array.from(document.querySelectorAll('audio')).map(a=>a.outerHTML.slice(0,200));
  // 全局播放器相关
  const keys=Object.keys(window).filter(k=>/player|Player|music|Music|spd|SPD|qqmusic/i.test(k));
  out.gkeys=keys.slice(0,40);
  // 底部播放器 DOM
  const bp=document.querySelector('.btn_bottom_player');
  out.bottom = bp? bp.outerHTML.slice(0,400):null;
  const pl=document.querySelector('#playermodule, .playermodule, [id*=player], [class*=player]');
  out.playerHtml = pl? pl.outerHTML.slice(0,600):null;
  // resource entries
  out.res = performance.getEntriesByType('resource').map(r=>r.name).filter(n=>/player|spd|audio|media|stream/i.test(n)).slice(0,20);
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":SHOW,"confirm":True,"mainWorld":True})
r=m.call("click_element",{"selector":"i.list_menu__icon_play","index":1,"confirm":True})
print("CLICK ok=",r.get('ok'))
time.sleep(6)
d=m.call("evaluate_script",{"function":DIAG,"confirm":True,"mainWorld":True})
print(json.dumps(d,ensure_ascii=False)[:4000])
# frames
fr=m.call("select_frame",{"frameId":0})
print("frames:",json.dumps(fr,ensure_ascii=False)[:800])
m.kill()
