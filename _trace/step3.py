import json,sys
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})

inject = """(raw) => {
  const parts = raw.split(';').map(s=>s.trim()).filter(Boolean);
  const setOn = (domain) => parts.forEach(p => {
    const i = p.indexOf('=');
    document.cookie = p.slice(0,i)+'='+p.slice(i+1)+'; domain='+domain+'; path=/; max-age=2592000';
  });
  setOn('.qq.com'); setOn('.y.qq.com');
  return document.cookie.length;
}"""
r=m.call("evaluate_script",{"function":inject,"confirm":True,"mainWorld":True,"args":{"raw":COOKIE}} if False else {"function":"(raw) => { const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); const setOn = (domain) => parts.forEach(p => { const i = p.indexOf('='); document.cookie = p.slice(0,i)+'='+p.slice(i+1)+'; domain='+domain+'; path=/; max-age=2592000'; }); setOn('.qq.com'); setOn('.y.qq.com'); return document.cookie.length; }","confirm":True,"mainWorld":True,"args":None})
print("INJECT:",json.dumps(r,ensure_ascii=False)[:200])

# 直接用带 cookie 的 fetch（浏览器上下文，cookie 已进 document.cookie）
js = """async () => {
  const body = {
    comm: {ct:11, cv:'20180101', uin:'3396806898', format:'json', platform:'yqq.json', needNewCode:0},
    req: {module:'music.search.SearchCgiService', method:'DoSearchForQQMusicDesktop',
      param:{query:'周杰伦 晴天', num_per_page:5, page_num:1, search_type:0, remoteplace:'txt.yqq.top'}}
  };
  const r = await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json', {
    method:'POST', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const j = await r.json();
  return {code:j.code, raw: JSON.stringify(j).slice(0,600)};
}"""
r=m.call("evaluate_script",{"function":js,"confirm":True,"mainWorld":True,"timeout":30000})
print("SEARCH:",json.dumps(r,ensure_ascii=False)[:2000])
m.kill()
