import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); document.cookie='qqmusic_guid=3329277760; path=/; domain=.y.qq.com; max-age=2592000'; return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})

JS = """async () => {
  const mid = '0039MnYb0qxYhV';
  const guid = (document.cookie.match(/pgv_pvid=(\\d+)/)||[])[1] || '3329277760';
  const comm = {ct:24, cv:0, uin:'1152921504608413217', format:'json', platform:'yqq.json', needNewCode:0, g_tk_new_20200303:'140128255', g_tk:'140128255'};
  const out = {};
  const variants = [
    ['music.vkeyProxyUrl','GetVkey',{guid,songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20',web_location:'0'}],
    ['music.streamProxyUrl','GetVkey',{guid,songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20'}],
    ['music.vkeyProxyUrl','GetVkey',{guid,songmid:mid,songtype:0,uin:'0',loginflag:0,platform:'20',web_location:'0',filename:'M800'+mid+'.mp3'}],
  ];
  for (let i=0;i<variants.length;i++){
    const [mod,meth,param]=variants[i];
    const body={comm, ['req_'+(i+1)]:{module:mod,method:meth,param}};
    try{
      const r=await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const j=await r.json();
      out[mod+'|'+meth+'|'+(param.loginflag||0)]=JSON.stringify(j['req_'+(i+1)]).slice(0,1500);
    }catch(e){ out[mod+'_'+i]='ERR '+e.message; }
  }
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("VKEY:", json.dumps(r,ensure_ascii=False)[:6000])
m.kill()
