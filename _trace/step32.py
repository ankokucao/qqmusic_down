import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})

JS = """async () => {
  const mid='0039MnYb0qxYhV', out={};
  const urls = [
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json',
    'https://c.y.qq.com/base/fcgi-bin/fcg_qmusic_base.fcg?type=1&t=0&mid='+mid+'&format=json',
    'https://i.y.qq.com/v8/playsong.html?songmid='+mid+'&format=json',
    'https://c.y.qq.com/fcgi-bin/fcg_qmusic_base.fcg?mid='+mid+'&format=json'
  ];
  for (const u of urls){
    try{ const r=await fetch(u,{credentials:'include'}); const t=await r.text(); out[u.slice(0,60)]=r.status+' :: '+t.slice(0,400); }
    catch(e){ out[u.slice(0,60)]='ERR '+e.message; }
  }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("LEGACY:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
