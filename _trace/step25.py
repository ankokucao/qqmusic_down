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
  as.forEach(a => { const mid=(a.getAttribute('href')||'').split('/').pop(); if(mid&&/^[A-Za-z0-9]{10,20}$/.test(mid)&&!map.has(mid)) map.set(mid,{mid,title:(a.textContent||'').trim(),vip:false}); });
  document.querySelectorAll('.songlist__item, [class*=song_item]').forEach(row=>{ const a=row.querySelector('a[href*="songDetail"]'); if(!a)return; const mid=(a.getAttribute('href')||'').split('/').pop(); if(map.has(mid)&&row.querySelector('[class*=vip]')) map.get(mid).vip=true; });
  return [...map.values()];
}"""
r=m.call("evaluate_script",{"function":JS1,"confirm":True,"mainWorld":True})
songs=r['data']['value']
free=[s for s in songs if not s['vip']]
print("FREE:",free[:6])
mids=[s['mid'] for s in free[:5]] or [s['mid'] for s in songs[:3]]
print("MIDS:",mids)

JS2 = """async () => {
  const mids = MIDS, guid='3329277760', out={};
  const comm = {ct:24, cv:0, uin:'1152921504608413217', format:'json', platform:'yqq.json', needNewCode:0, g_tk_new_20200303:'140128255', g_tk:'140128255'};
  const mods=[['music.vkeyProxyUrl','GetVkey'],['music.streamProxyUrl','GetVkey'],['music.playUrl.vkey','GetVkey']];
  let i=0;
  for (const mid of mids){
    for (const [mod,meth] of mods){
      i++;
      const body={comm, ['req_'+i]:{module:mod,method:meth,param:{guid,songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20',web_location:'0'}}};
      try{
        const r=await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
        const j=await r.json();
        const s=JSON.stringify(j['req_'+i]||{});
        if(!/500003/.test(s)) out[mid+'|'+mod]=s.slice(0,900);
        else if(!out[mid+'|'+mod]) out[mid+'|'+mod]='500003';
      }catch(e){ out[mid+mod]='ERR'+e.message; }
    }
  }
  return out;
}""".replace('MIDS', json.dumps(mids))
r=m.call("evaluate_script",{"function":JS2,"confirm":True,"mainWorld":True,"timeout":60000})
print("VKEY:", json.dumps(r,ensure_ascii=False)[:5000])
m.kill()
