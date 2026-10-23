import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

HOOK="""() => {
  window.__cap=[];
  const os=JSON.stringify;
  JSON.stringify=function(v){ let s; try{s=os.apply(this,arguments);}catch(e){return os.apply(this,arguments);} try{ if(typeof s==='string'&&s.length>150&&s.indexOf('req_')>=0) window.__cap.push('R:'+s);}catch(x){} return s; };
  const op=JSON.parse;
  JSON.parse=function(t){ const r=op.apply(this,arguments); try{ if(typeof t==='string'&&t.length>150&&/vkey|purl|"sip"|"filename"/i.test(t)) window.__cap.push('P:'+t);}catch(x){} return r; };
  return {ok:true};
}"""

# 枚举所有可能持有播放器实例的全局
ENUM="""() => {
  const out={};
  const all=[];
  for(const k in window){
    try{
      const v=window[k];
      if(v && (typeof v==='object'||typeof v==='function')){
        let tag='';
        try{ tag=Object.keys(v).slice(0,25).join(','); }catch(x){}
        if(/play|song|audio|media|track|queue|current/i.test(k+' '+tag)) all.push({k, tag:tag.slice(0,150)});
      }
    }catch(x){}
  }
  out.cands=all.slice(0,60);
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
m.call("evaluate_script",{"function":HOOK,"confirm":True,"mainWorld":True})
e=m.call("evaluate_script",{"function":ENUM,"confirm":True,"mainWorld":True})
print("ENUM:",json.dumps(e,ensure_ascii=False)[:4000])
m.kill()
