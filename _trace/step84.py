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
  // 大量候选模块名（覆盖新旧命名）
  const mods=[
   'music.vkeyProxyUrl','music.vkey','music.getVkey','music.music.vkey','music.vkeyNew','music.vkey2',
   'music.playUrl','music.playUrlNew','music.getPlayUrl','music.playUrlV2','music.playurl',
   'music.songUrl','music.musicUrl','music.audioUrl','music.streamUrl','media.getUrl','media.playUrl',
   'music.fileUrl','music.downloadUrl','music.getFileUrl','music.songFileUrl',
   'music.pf_song_detail_svr','music.musichallSong.PlayLyricInfo','music.trackInfo.UniformRuleCtrl',
   'music.musicHallSong.PlaySongInfo','music.musichallSong.PlaySongInfo','musichall.song_play_server',
   'music.songPlayUrl','music.playbackUrl','music.getSongUrl','music.musicUrlProxy',
   'music.vkeyProxy','music.vkeyService','music.vkeyServer','vkey.vkeyServer','music.vkeyDetail',
   'music.musichallSong.PlaySongUrl','music.musichallSong.SongPlayUrl','music.player.PlayUrl',
   'music.qmplayer.GetPlayUrl','music.playerv2.GetPlayUrl','music.webplayer.GetPlayUrl',
   'music.musicPlatForm.PlayUrl','music.platform.PlayUrl','music.musichallAlbum.AlbumInfoServer'
  ];
  const meths=['GetVkey','GetPlayUrl','GetUrl','GetSongUrl','Get','getVkey','getPlayUrl','PlayUrl','GetMusicUrl','GetFileUrl'];
  const hits=[];
  const errs=[];
  for(const mo of mods){
    for(const me of meths){
      try{
        const inst=new M8.a({url:'https://u.y.qq.com/cgi-bin/musicu.fcg',type:'POST',needSign:true});
        const r=await inst.request([{module:mo,method:me,param:Object.assign({},base)}]);
        const s=JSON.stringify(r);
        if(!/500003/.test(s) && !/"code":0,"subcode":860100005/.test(s)){
          hits.push({mo,me,r:s.slice(0,1500)});
        }
      }catch(e){ errs.push(mo+'/'+me+':'+String(e).slice(0,60)); }
    }
  }
  out.hits=hits; out.nerr=errs.length; out.sampleErr=errs.slice(0,3);
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
print("hits:",len(v.get('hits',[])))
for h in v.get('hits',[])[:20]: print(h['mo'],h['me'],h['r'][:600])
print("errs",v.get('nerr'),v.get('sampleErr'))
m.kill()
