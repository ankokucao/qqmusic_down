import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
time.sleep(3)

# 找到首页的歌曲列表并点击其播放按钮
JS = """() => {
  const items = Array.from(document.querySelectorAll('[class*=songlist] li, [class*=song_item], [class*=songlist__item], [class*=list__item]'));
  const info = items.slice(0,10).map(e=>({cls:String(e.className).slice(0,70), txt:(e.innerText||'').trim().slice(0,50)}));
  return {count: items.length, info};
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("ITEMS:", json.dumps(r,ensure_ascii=False)[:2500])

r=m.call("list_console_messages",{"pageSize":30,"types":["error","warn"]})
print("CONSOLE:", json.dumps(r,ensure_ascii=False)[:2000])

# 全局搜索播放按钮
r=m.call("evaluate_script",{"function":"() => Array.from(document.querySelectorAll('i[class*=icon_play], span[class*=icon_play], [class*=play_icon]')).slice(0,10).map(e=>({cls:String(e.className), title:e.title||'', p:(e.parentElement&&e.parentElement.innerText||'').trim().slice(0,40)}))","confirm":True,"mainWorld":True})
print("PLAYICONS:", json.dumps(r,ensure_ascii=False)[:2500])
m.kill()
