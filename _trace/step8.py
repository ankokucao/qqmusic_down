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

HOOK = """() => {
  window.__log = [];
  const of = window.fetch;
  window.fetch = async function(input, init) {
    try {
      const url = typeof input === 'string' ? input : input.url;
      let body = init && init.body ? String(init.body) : '';
      window.__log.push({t:'fetch', url, body: body.slice(0,3000), ct: init&&init.headers&&(init.headers['Content-Type']||init.headers.get&&init.headers.get('Content-Type'))});
    } catch(e){}
    return of.apply(this, arguments);
  };
  const oo = XMLHttpRequest.prototype.open, os_ = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m,u){ this.__m=m; this.__u=u; return oo.apply(this,arguments); };
  XMLHttpRequest.prototype.send = function(b){
    try { window.__log.push({t:'xhr', m:this.__m, url:this.__u, body: b?String(b).slice(0,3000):''}); } catch(e){}
    this.addEventListener('load', ()=>{ try{ window.__log.push({t:'xhr-resp', url:this.__u, resp:String(this.responseText||this.response||'').slice(0,6000)}); }catch(e){} });
    return os_.apply(this, arguments);
  };
  return 'hooked';
}"""
r=m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
print("HOOK:", json.dumps(r,ensure_ascii=False)[:200])

# 播放底部条
r=m.call("click_element",{"selector":"i.mod_btn_green__icon_play","confirm":True})
print("CLICK_BTN:", json.dumps(r,ensure_ascii=False)[:300])
time.sleep(3)
# 也有可能需要点击列表
r=m.call("evaluate_script",{"function":"() => { const b=document.querySelector('i.mod_btn_green__icon_play'); if(b) b.click(); return !!b; }","confirm":True,"mainWorld":True})
time.sleep(8)

r=m.call("evaluate_script",{"function":"() => window.__log","confirm":True,"mainWorld":True})
print("LOG:", json.dumps(r,ensure_ascii=False)[:9000])
m.kill()
