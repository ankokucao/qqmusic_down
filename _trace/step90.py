import json,sys,os,time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
  const songs=[
    {name:'万里长风(免费)', mid:'000NBVdP3wg95P', media:'000NBVdP3wg95P', vip:0},
    {name:'晴天(VIP)', mid:'0039MnYb0qxYhV', media:'003Qui1q2u1Zho', vip:1},
  ];
  const uin=(document.cookie.match(/wxuin=(\d+)/)||[])[1]||'1152921504608413217';
  const mkguid=()=>String(Math.round(2147483647*Math.random())*new Date().getUTCMilliseconds()%1e10);
  out.res=[];
  for(const s of songs){
    for(const useFile of [true,false]){
      const param={guid:mkguid(), songmid:[s.mid], songtype:[0], uin:uin, loginflag:1, platform:'20', xcdn:1};
      if(useFile) param.filename=['RS02'+s.media+'.mp3'];
      try{
        const inst=new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg',type:'POST',needSign:true});
        const r=await inst.request([{module:'music.vkey.GetEVkey',method:'GetUrl',param:param}]);
        out.res.push({song:s.name, file:useFile, r:r});
      }catch(e){ out.res.push({song:s.name, file:useFile, err:String(e)}); }
    }
  }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq_v2/player","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
r=m.call("evaluate_script",{"function":CALL,"confirm":True,"mainWorld":True})
v=r.get('data',{}).get('value',{}) if isinstance(r,dict) else {}
open('getevkey.json','w',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=1))
for x in v.get('res',[]):
    print("###",x['song'],"file=",x['file'])
    print(json.dumps(x.get('r') or x.get('err'),ensure_ascii=False)[:2500]); print()
m.kill()
