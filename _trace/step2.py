import json,sys
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip() if __import__('os').path.exists('cookie.txt') else None

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})

# 1) 探测 cookie
r=m.call("evaluate_script",{"function":"() => document.cookie","confirm":True,"mainWorld":True})
print("COOKIE_LEN:", json.dumps(r,ensure_ascii=False)[:300])

# 2) 用 musicu.fcg 搜索一首歌，拿到 songmid
js = """async () => {
  const body = {
    comm: {ct:11, cv:'20180101', uin:'0', format:'json', platform:'yqq.json', needNewCode:0},
    req: {module:'music.search.SearchCgiService', method:'DoSearchForQQMusicDesktop',
      param:{query:'周杰伦 晴天', num_per_page:5, page_num:1, search_type:0, remoteplace:'txt.yqq.top'}}
  };
  const r = await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json', {
    method:'POST', credentials:'include',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  const j = await r.json();
  const list = j?.req?.data?.body?.song?.list || [];
  return {code:j.code, n:list.length, top: list.slice(0,3).map(s=>({mid:s.mid,title:s.title,singer:(s.singer||[]).map(x=>x.name)}))};
}"""
r=m.call("evaluate_script",{"function":js,"confirm":True,"mainWorld":True,"timeout":30000})
print("SEARCH:", json.dumps(r,ensure_ascii=False)[:1500])
m.kill()
