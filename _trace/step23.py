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

# 从 DOM 抓歌曲 mid/title/vip
JS1 = """() => {
  const rows = Array.from(document.querySelectorAll('.songlist__item'));
  return rows.slice(0,30).map(r => {
    const a = r.querySelector('a.songlist__songname_txt');
    const vip = !!r.querySelector('.songlist__icon_vip');
    return {mid: a ? (a.getAttribute('href')||'').split('/').pop() : null, title: a?a.textContent.trim():'', vip};
  }).filter(x=>x.mid);
}"""
r=m.call("evaluate_script",{"function":JS1,"confirm":True,"mainWorld":True})
songs=r['data']['value']
free=[s for s in songs if not s['vip']]
print("TOTAL_SONGS",len(songs),"FREE",len(free))
for s in songs[:12]: print("  ",s)

mid = (free[0]['mid'] if free else songs[0]['mid'])
title = (free[0]['title'] if free else songs[0]['title'])
print("TRY:",mid,title)

JS2 = """async () => {
  const mid = MID, guid='3329277760';
  const comm = {ct:24, cv:0, uin:'1152921504608413217', format:'json', platform:'yqq.json', needNewCode:0, g_tk_new_20200303:'140128255', g_tk:'140128255'};
  const body={comm, req_1:{module:'music.vkeyProxyUrl',method:'GetVkey',param:{guid,songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20',web_location:'0'}}};
  const r=await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j=await r.json();
  return JSON.stringify(j.req_1).slice(0,3000);
}""".replace('MID', json.dumps(mid))
r=m.call("evaluate_script",{"function":JS2,"confirm":True,"mainWorld":True,"timeout":40000})
print("VKEY:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
