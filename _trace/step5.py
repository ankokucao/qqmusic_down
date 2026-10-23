import json,sys
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/003OUlho2HcRHC"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})

# vkeyProxyUrl 参数链
js = """async () => {
  const guid = document.cookie.match(/pgv_pvid=(\\d+)/)?.[1] || '';
  const body = {
    comm: {ct:24, cv:0, uin:'1152921504608413217', format:'json', platform:'yqq.json', needNewCode:0, g_tk_new_20200303:'140128255', g_tk:'140128255'},
    req_1: {module:'music.vkeyProxyUrl', method:'GetVkey', param:{guid, songmid:'003OUlho2HcRHC', songtype:0, uin:'1152921504608413217', loginflag:1, platform:'20', web_location:'0'}}
  };
  const r = await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json', {method:'POST', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const j = await r.json();
  return {guid, code:j.code, resp: JSON.stringify(j.req_1).slice(0,2500)};
}"""
r=m.call("evaluate_script",{"function":js,"confirm":True,"mainWorld":True,"timeout":40000})
print("VKEY:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
