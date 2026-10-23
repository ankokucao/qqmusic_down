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
time.sleep(12)

JS1 = """() => {
  const as = Array.from(document.querySelectorAll('a[href*="songDetail"]'));
  const map = new Map();
  as.forEach(a => {
    const mid=(a.getAttribute('href')||'').split('/').pop();
    if(!mid||!/^[A-Za-z0-9]{10,20}$/.test(mid)) return;
    if(!map.has(mid)) map.set(mid, {mid, title:(a.textContent||'').trim(), vip:false});
  });
  // vip 标记：在同一条 songlist__item 内
  document.querySelectorAll('.songlist__item, [class*=song_item], [class*=list__item]').forEach(row=>{
    const a=row.querySelector('a[href*="songDetail"]');
    if(!a) return; const mid=(a.getAttribute('href')||'').split('/').pop();
    if(map.has(mid) && row.querySelector('[class*=vip]')) map.get(mid).vip=true;
  });
  return {n:map.size, list:[...map.values()].slice(0,40)};
}"""
r=m.call("evaluate_script",{"function":JS1,"confirm":True,"mainWorld":True})
songs=r['data']['value']
print("N:",songs['n'])
for s in songs['list'][:20]: print("  ",s)
mids=[s['mid'] for s in songs['list']]
json.dump(songs,open('songs.json','w',encoding='utf-8'),ensure_ascii=False)
m.kill()
