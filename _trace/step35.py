import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
# 排行榜页的歌曲多为免费
m.call("navigate_page",{"type":"url","url":"https://y.qq.com/n/ryqq/toplist","timeout":30000})
time.sleep(10)
JS1 = """() => {
  const as = Array.from(document.querySelectorAll('a[href*="songDetail"]'));
  const map=new Map();
  as.forEach(a=>{const mid=(a.getAttribute('href')||'').split('/').pop(); if(mid&&/^[A-Za-z0-9]{10,20}$/.test(mid)&&!map.has(mid)) map.set(mid,{mid,title:(a.textContent||'').trim()});});
  return [...map.values()].slice(0,12);
}"""
r=m.call("evaluate_script",{"function":JS1,"confirm":True,"mainWorld":True})
cands=r['data']['value']
print("CANDS:",cands[:6])
mids=[c['mid'] for c in cands[:8]]
JS2 = """async () => {
  const mids=MIDS, out=[];
  for(const mid of mids){
    try{
      const r=await fetch('https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json',{credentials:'include'});
      const j=await r.json(); if(!j.data||!j.data.length){out.push({mid,err:'nodata'}); continue;}
      const d=j.data[0];
      out.push({mid, title:d.title, pay_play:d.pay&&d.pay.pay_play, pay_status:d.pay&&d.pay.pay_status, price_track:d.pay&&d.pay.price_track, media_mid:d.file.media_mid, size_try:d.file.size_try, size_128mp3:d.file.size_128mp3, url:d.url, has_sip:!!d.sip});
    }catch(e){out.push({mid,err:e.message});}
  }
  return out;
}""".replace('MIDS', json.dumps(mids))
r=m.call("evaluate_script",{"function":JS2,"confirm":True,"mainWorld":True,"timeout":60000})
print("PAY:", json.dumps(r,ensure_ascii=False)[:5000])
m.kill()
