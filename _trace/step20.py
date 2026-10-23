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
time.sleep(9)

# 先 hook 全局：TextDecoder + JSON.parse + 常见音频相关
HOOK = """() => {
  window.__hits = [];
  const push = (k,v) => { try { window.__hits.push({k, v: String(v).slice(0,3000)}); } catch(e){} };
  const oj = JSON.parse;
  JSON.parse = function(t){ const v = oj.apply(this, arguments); try{ const s=typeof t==='string'?t:''; if(s.length>30) push('json', s.slice(0,3000)); }catch(e){} return v; };
  const od = TextDecoder.prototype.decode;
  TextDecoder.prototype.decode = function(b){ const v = od.apply(this, arguments); try{ if(v && v.length>50) push('td', v.slice(0,2000)); }catch(e){} return v; };
  const oa = window.atob;
  window.atob = function(s){ try{ if(s && s.length>200) push('b64', s.slice(0,600)); }catch(e){} return oa.apply(this, arguments); };
  const od2 = window.btoa;
  return 'ok';
}"""
r=m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("HOOK:",json.dumps(r,ensure_ascii=False)[:150])

JS = """() => {
  const row = document.querySelectorAll('.songlist__item')[0];
  const a = row && row.querySelector('.list_menu__play');
  if(a){a.click(); return 'ok';} return 'no';
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True})
print("CLICK:",json.dumps(r,ensure_ascii=False)[:200])
time.sleep(10)

r=m.call("evaluate_script",{"function":"() => window.__hits","confirm":True,"mainWorld":True})
txt=json.dumps(r,ensure_ascii=False)
print("HITS_LEN:", len(txt))
# 过滤出含 vkey / playurl / purl 的
try:
    hits=r['data']['value']
    for h in hits:
        if any(k in h['v'] for k in ('vkey','playurl','purl','filename','stream.qqmusic','.mp3','.flac')):
            print(">>>",h['k'],h['v'][:1200]); print()
    print("TOTAL_HITS",len(hits))
    for h in hits[:6]:
        print(" -",h['k'],h['v'][:200])
except Exception as e:
    print("ERR",e, txt[:3000])
m.kill()
