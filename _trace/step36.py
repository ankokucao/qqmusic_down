import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE = open('cookie.txt',encoding='utf-8').read().strip()
lit = json.dumps(COOKIE)
INJECT = "() => { const raw = " + lit + "; const parts = raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"
m=MCP()
m.call("new_page",{"url":"https://y.qq.com/"})
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})

# 经典明文 vkey 接口：musicu.fcg (u.y.qq.com) 与 base/fcg_qmusic_base.fcg
JS = """async () => {
  const mid='000NBVdP3wg95P', out={};
  const tries = [
    ['u_musicu','https://u.y.qq.com/cgi-bin/musicu.fcg'],
    ['c_base','https://c.y.qq.com/base/fcgi-bin/fcg_qmusic_base.fcg'],
    ['c_play','https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg']
  ];
  // 尝试 1: 老 base 接口带 filename
  const u1='https://c.y.qq.com/base/fcgi-bin/fcg_qmusic_base.fcg?songmid='+mid+'&format=json&filename=M800'+mid+'.mp3&guid=3329277760';
  try{const r=await fetch(u1,{credentials:'include'}); out.base= (await r.text()).slice(0,500);}catch(e){out.base='ERR'+e.message;}
  // 尝试 2: musicu.fcg 加 filename + 完整 comm（含 qqmusic_key 登录态）
  const comm={ct:24,cv:0,uin:'1152921504608413217',format:'json',platform:'yqq.json',needNewCode:0,g_tk_new_20200303:'140128255',g_tk:'140128255'};
  const body={comm,req_1:{module:'music.vkeyProxyUrl',method:'GetVkey',param:{guid:'3329277760',songmid:mid,songtype:0,uin:'1152921504608413217',loginflag:1,platform:'20',web_location:'0',filename:'M800'+mid+'.mp3'}}};
  try{const r=await fetch('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); out.musicu=(await r.text()).slice(0,600);}catch(e){out.musicu='ERR'+e.message;}
  return out;
}"""
r=m.call("evaluate_script",{"function":JS,"confirm":True,"mainWorld":True,"timeout":40000})
print("VKEYTRY:", json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
