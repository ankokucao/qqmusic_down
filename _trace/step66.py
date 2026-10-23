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
  const R=window.__WREQ, M8=R(8);
  const out={};
  const mid='000NBVdP3wg95P';
  const inst=new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg',type:'POST',needSign:true});
  const tries=[
    ['music.pf_song_detail_svr','GetSongDetail',{song_mid:mid}],
    ['music.pf_song_detail_svr','GetSongDetail',{songmid:mid}],
    ['music.pf_song_detail_svr','GetPfSongDetail',{song_mid:mid}],
    ['music.musichallSong.PlayLyricInfo','GetPlayLyricInfo',{song_mid:mid}],
    ['music.trackInfo.UniformRuleCtrl','GetUniformRuleCtrl',{song_mid:mid}],
  ];
  out.res=[];
  for(const [mo,me,pr] of tries){
    try{
      const r=await inst.request([{module:mo,method:me,param:pr}]);
      out.res.push({mo,me,r:JSON.stringify(r).slice(0,2500)});
    }catch(e){ out.res.push({mo,me,err:String(e)}); }
  }
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
open('dump66.json','w',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=1))
for x in v.get('res',[]):
    print("###",x['mo'],x['me'])
    print((x.get('r') or x.get('err'))[:2200]); print()
m.kill()
