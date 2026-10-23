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
  const mid='000NBVdP3wg95P', fn='C400000NBVdP3wg95P.mp3';
  const guid=(document.cookie.match(/qqmusic_guid=([^;]+)/)||[])[1]||'1000000000';
  const uin='1152921504608413217';
  const base={guid:guid,songmid:mid,songtype:0,uin:uin,loginflag:1,platform:'20',filename:fn};
  // 1) 尝试各种 CGI 端点（走 M8.c = ur，自带 sign/encrypt/decrypt）
  const eps=[
    'https://u6.y.qq.com/cgi-bin/musicu.fcg',
    'https://u.y.qq.com/cgi-bin/musicu.fcg',
    'https://c.y.qq.com/base/fcgi-bin/fcg_bin_single_song.fcg',
    'https://c.y.qq.com/fcgi-bin/fcg_outer_playurl.fcg',
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg',
    'https://u6.y.qq.com/cgi-bin/getsonginfo.fcg',
    'https://c.y.qq.com/splcloud/fcgi-bin/fcgi_bin_smartbox_new.fcg',
  ];
  const mods=['music.vkeyProxyUrl','music.vkey','music.getVkey','music.playUrl','music.music.vkey','music.songUrl','music.musicUrl','music.audioUrl','music.streamUrl','media.getUrl','music.getSongUrl','music.fileUrl','music.pf_song_detail_svr','music.musichallSong.PlayLyricInfo','music.vkeyProxy','music.playUrlV2','music.newVkey','music.vkeyUrl','music.musicUrlProxy','music.getPlayUrl'];
  const results=[];
  for(const ep of eps){
    for(const mo of mods){
      try{
        const inst=new M8.a({url:ep,type:'POST',needSign:true});
        const r=await inst.request([{module:mo,method:'GetVkey',param:Object.assign({},base)}]);
        const s=JSON.stringify(r);
        if(s && !/500003/.test(s) && !/"code":0,"subcode":860100005/.test(s)) results.push({ep,mo,s:s.slice(0,1200)});
      }catch(e){}
    }
  }
  out.results=results;
  // 2) GET 型：fcg_outer_playurl / vkey
  const getUrls=[
    'https://c.y.qq.com/fcgi-bin/fcg_outer_playurl.fcg?songmid='+mid+'&format=json',
    'https://c.y.qq.com/base/fcgi-bin/fcg_bin_single_song.fcg?songmid='+mid+'&format=json',
    'https://i.y.qq.com/qianmusic/vkey?guid='+guid+'&songmid='+mid+'&filename='+fn+'&size=128',
    'https://ws.stream.qqmusic.qq.com/'+fn+'?guid='+guid+'&vkey=&fromtag=38',
    'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid='+mid+'&format=json&filename='+fn
  ];
  out.get=[];
  for(const u of getUrls){
    try{
      const resp=await fetch(u,{credentials:'include'});
      const t=await resp.text();
      out.get.push({u:u.slice(0,90), code:resp.status, body:t.slice(0,700)});
    }catch(e){ out.get.push({u:u.slice(0,90), err:String(e)}); }
  }
  return out;
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/songDetail/0039MnYb0qxYhV","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(14)
r=m.call("evaluate_script",{"function":CALL,"confirm":True,"mainWorld":True})
v=r.get('data',{}).get('value',{}) if isinstance(r,dict) else {}
print("=== results (musicu modules x endpoints)")
for x in v.get('results',[])[:25]: print(x['ep'],x['mo'],x['s'][:500])
print("=== get endpoints")
for x in v.get('get',[]): print(x.get('u'),'->',x.get('code'),(x.get('body') or x.get('err') or '')[:400])
m.kill()
