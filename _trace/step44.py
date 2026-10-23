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
  const hosts=['https://u.y.qq.com/cgi-bin/musicu.fcg','https://u6.y.qq.com/cgi-bin/musicu.fcg','https://c.y.qq.com/cgi-bin/musicu.fcg','https://y.qq.com/cgi-bin/musicu.fcg','https://u6.y.qq.com/cgi-bin/musics.fcg'];
  const comms=[
    {ct:11,cv:'20180101',uin:'0',format:'json',platform:'yqq.json',needNewCode:0},
    {ct:24,cv:0,uin:'0',format:'json',platform:'yqq.json',needNewCode:0},
    {ct:11,cv:'20180101',uin:'1152921504608413217',format:'json',platform:'yqq.json',needNewCode:0,g_tk_new_20200303:'140128255',g_tk:'140128255'}
  ];
  let n=0;
  for(const h of hosts){
    for(const c of comms){
      n++;
      const body={comm:c, req_1:{module:'music.vkeyProxyUrl',method:'GetVkey',param:{guid:'3329277760',songmid:mid,songtype:0,uin:'0',loginflag:0,platform:'20',web_location:'0'}}};
      try{
        const r=await fetch(h+'?format=json',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
        const t=await r.text();
        const key=h.split('/')[2]+'|ct'+c.ct+'|uin'+c.uin;
        out[key]=t.slice(0,220);
      }catch(e){ out[h.split('/')[2]+'|ct'+c.ct+'|uin'+c.uin]='ERR '+e.message; }
    }
  }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":90000})
print("MATRIX:", json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
