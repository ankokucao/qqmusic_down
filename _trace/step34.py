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
  const r=await fetch('https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json',{credentials:'include'});
  const d=(await r.json()).data[0];
  out.pay=d.pay; out.isonly=d.isonly; out.status=d.status; out.url=d.url; out.sip=d.sip; out.media_mid=d.file.media_mid; out.size_try=d.file.size_try;
  // 试 legacy playsong 的 sip 列表接口
  const urls=[
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json&guid=3329277760',
    'https://c.y.qq.com/base/fcgi-bin/fcg_qmusic_base.fcg?songmid='+mid+'&format=json&filename=M800'+d.file.media_mid+'.mp3&guid=3329277760'
  ];
  for(const u of urls){ try{ const rr=await fetch(u,{credentials:'include'}); const t=await rr.text(); out[u.slice(30,90)]=t.slice(0,300);}catch(e){out[u.slice(30,90)]='ERR'+e.message;} }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("INFO:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
