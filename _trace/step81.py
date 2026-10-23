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

LS="""() => {
  const out={};
  for(const k of Object.keys(localStorage)){
    if(/play|player|song/i.test(k)) out[k]=(localStorage.getItem(k)||'').slice(0,1500);
  }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
print("LS-BEFORE:",json.dumps(m.call("evaluate_script",{"function":LS,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:2500])
m.call("evaluate_script",{"function":SHOW,"confirm":True,"mainWorld":True})
r=m.call("click_element",{"selector":"i.list_menu__icon_play","index":1,"confirm":True})
print("CLICK ok=",r.get('ok'))
time.sleep(10)
print("LS-AFTER:",json.dumps(m.call("evaluate_script",{"function":LS,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:3000])
m.kill()
