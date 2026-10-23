import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

CALL="""async () => {
  const wj=window.webpackJsonp, orig=wj.push.bind(wj);
  wj.push=function(arr){const m=arr[1]; if(m){for(const k in m){if(typeof m[k]==='function'){window.__WREQ=m[k];break;}}} return orig(arr);};
  wj.push([[999999],{999999:(m,e,r)=>{window.__WREQ=r;}},[[999999]]]);
  wj.push=orig;
  const R=window.__WREQ;
  const out={};
  // 1) 导出含 vkey 的模块源码
  const defs=R.m||{};
  const vmods={};
  for(const k of Object.keys(defs)){
    const s=String(defs[k]);
    if(/vkey|GetVkey|purl|playUrl/i.test(s)) vmods[k]={len:s.length, ctx:(function(){
       const i=Math.max(s.search(/vkey/i), s.search(/purl/i), s.search(/playUrl/i));
       return i>=0? s.slice(Math.max(0,i-400), i+400):'';
    })()};
  }
  out.vmods=vmods;
  // 2) 暴力枚举模块
  const M8=R(8);
  const mid='000NBVdP3wg95P', fn='C400000NBVdP3wg95P.mp3';
  const guid=(document.cookie.match(/qqmusic_guid=([^;]+)/)||[])[1]||'1000000000';
  const param={guid:guid,songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20',filename:fn};
  const mods=['music.vkeyProxyUrl','music.vkey','music.getVkey','music.playUrl','music.playUrlV2','music.vkeyProxyUrlV2',
    'music.streamUrl','music.fileUrl','music.downloadUrl','music.songUrl','music.musicUrl','music.audioUrl','music.tryUrl',
    'music.urlProxy','music.purlProxyUrl','music.sip','music.vkeyProxy','music.vkeyUrl','music.playurl','music.play_url',
    'music.vkeyProxyUrlNew','music.music.vkey','music.getPlayUrl','music.getUrl','music.fileKey','music.mediaUrl',
    'music.fcgiPlayUrl','music.playUrlProxy','music.vkeyNew','music.newVkey'];
  const meths=['GetVkey','getVkey','GetPlayUrl','getPlayUrl','GetUrl','getUrl','GetMusicUrl','Get'];
  const inst=new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg',type:'POST',needSign:true});
  const hits=[];
  for(const mo of mods){
    for(const me of meths){
      try{
        const r=await inst.request([{module:mo,method:me,param:Object.assign({},param)}]);
        const j=r&&r[0];
        const s=JSON.stringify(j||'');
        if(j && j.code===0 && !/500003/.test(s) && /vkey|purl|sip|filename/i.test(s)) hits.push({mo,me,r:j});
        else if(j && j.code!==0 && j.subcode!==860100005) hits.push({mo,me,r:j});
      }catch(e){}
    }
  }
  out.hits=hits;
  out.guid=guid;
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(12)
r=m.call("evaluate_script",{"function":CALL,"confirm":True,"mainWorld":True})
v=r.get('data',{}).get('value',{}) if isinstance(r,dict) else {}
open('dump65.json','w',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=1))
print("guid",v.get('guid'))
print("vmods keys:",list((v.get('vmods') or {}).keys()))
print("HITS:",json.dumps(v.get('hits'),ensure_ascii=False)[:3000])
m.kill()
