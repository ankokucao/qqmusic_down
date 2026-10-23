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
  const mid='0039MnYb0qxYhV';
  const r=await fetch('https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json',{credentials:'include'});
  const j=await r.json();
  const d=j.data[0];
  return {keys:Object.keys(d), file:d.file, sip:d.sip, filename:d.filename, songmid:d.songmid, action:d.action};
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("FULL:", json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
