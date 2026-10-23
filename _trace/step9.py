import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/003OUlho2HcRHC"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":30000})
time.sleep(4)

# hook JSON.parse 捕获解密后明文；hook atob 捕获密文解码
HOOK = """() => {
  window.__vkeys = [];
  const oj = JSON.parse;
  JSON.parse = function(t, r) {
    const v = oj.apply(this, arguments);
    try {
      const s = typeof t === 'string' ? t : '';
      if (s.length > 40 && /vkey|playurl|filename|purl/i.test(s)) {
        window.__vkeys.push({len:s.length, snippet: s.slice(0, 4000)});
      }
    } catch(e){}
    return v;
  };
  const oa = window.atob;
  window.atob = function(s) {
    try { if (s && s.length > 100) window.__vkeys.push({b64len:s.length, b64:s.slice(0,300)}); } catch(e){}
    return oa.apply(this, arguments);
  };
  return 'ok';
}"""
r=m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("HOOK:", json.dumps(r,ensure_ascii=False)[:200])

# 找歌曲列表里的播放入口
JS = """() => {
  const rows = Array.from(document.querySelectorAll('li, tr, .song_item, [class*=songlist] [class*=item]')).slice(0,400);
  const out = [];
  rows.forEach(e=>{
    const t = (e.innerText||'').trim();
    if (t && t.length < 120 && /play/i.test(e.innerHTML)) out.push({t: t.slice(0,60), cls: String(e.className).slice(0,60)});
  });
  const audios = Array.from(document.querySelectorAll('audio')).map(a=>({src:a.src, id:a.id, cls:a.className}));
  return {rows: out.slice(0,12), audios};
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("DOM:", json.dumps(r,ensure_ascii=False)[:2500])

# 点击绿色播放按钮（列表中）
r=m.call("evaluate_script",{"function":"() => { const bs=document.querySelectorAll('i.mod_btn_green__icon_play'); let n=0; bs.forEach(b=>{try{b.click();n++}catch(e){}}); return n; }","confirm":True,"mainWorld":True})
print("CLICKED:", json.dumps(r,ensure_ascii=False)[:200])
time.sleep(10)

r=m.call("evaluate_script",{"function":"() => ({vkeys: window.__vkeys, audios: Array.from(document.querySelectorAll('audio')).map(a=>a.src)})","confirm":True,"mainWorld":True})
print("CAPTURED:", json.dumps(r,ensure_ascii=False)[:9000])
m.kill()
