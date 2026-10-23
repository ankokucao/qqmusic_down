import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})

# 1) smartbox 搜索拿真实 mid
JS = """async () => {
  const r = await fetch('https://c.y.qq.com/splcloud/fcgi-bin/fcgi_bin_smartbox_new.fcg?key=' + encodeURIComponent('周杰伦 晴天') + '&format=json', {credentials:'include'});
  const j = await r.json();
  const l = j?.data?.song?.list || [];
  return {n: l.length, list: l.slice(0,6).map(s=>({mid:s.mid, title:s.name, s:(s.singer||[]).map(x=>x.name)}))};
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":30000})
print("SMARTBOX:", json.dumps(r,ensure_ascii=False)[:2000])

# 2) 找 GetGuid / guid 生成
r=m.call("search_in_sources",{"query":"GetGuid","maxResults":15,"maxLineLength":200})
print("GETGUID:", json.dumps(r,ensure_ascii=False)[:3000])
r=m.call("search_in_sources",{"query":"vkeyProxyUrl","maxResults":15,"maxLineLength":250})
print("VKEYSRC:", json.dumps(r,ensure_ascii=False)[:3000])
m.kill()
