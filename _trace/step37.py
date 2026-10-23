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
  const mid='000NBVdP3wg95P', out={};
  // 试不同 host 组合，play_single_song 可能返回 sip 需带 ftype/guid
  const urls=[
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json&guid=3329277760&ftype=mp3',
    'https://i.y.qq.com/v8/playsong.html?songmid='+mid+'&format=json&guid=3329277760',
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json&filename=M800'+mid+'.mp3',
    'https://ws.stream.qqmusic.qq.com/'
  ];
  for(const u of urls){ try{const r=await fetch(u,{credentials:'include'}); const t=await r.text(); out[u.slice(8,75)]=r.status+' :: '+t.slice(0,350);}catch(e){out[u.slice(8,75)]='ERR '+e.message;} }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("SIP:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
