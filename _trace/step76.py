import json,sys,os,time
sys.path.insert(0,'.')
from mcpdrv import MCP
COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
lit=json.dumps(COOKIE)
INJECT="() => { const raw = "+lit+"; const parts=raw.split(';').map(s=>s.trim()).filter(Boolean); ['.qq.com','.y.qq.com'].forEach(dom=>parts.forEach(p=>{const i=p.indexOf('=');document.cookie=p.slice(0,i)+'='+p.slice(i+1)+'; domain='+dom+'; path=/; max-age=2592000';})); return document.cookie.length; }"

PROBE="""() => {
  const els=document.querySelectorAll('.list_menu__play');
  const out=[];
  for(let i=0;i<Math.min(3,els.length);i++){
    const el=els[i], r=el.getBoundingClientRect();
    const cx=r.left+r.width/2, cy=r.top+r.height/2;
    const top=document.elementFromPoint(cx,cy);
    out.push({i, rect:{x:Math.round(cx),y:Math.round(cy),w:Math.round(r.width),h:Math.round(r.height)},
      topTag:top&&top.tagName, topCls: top?String(top.className&&top.className.baseVal!==undefined?top.className.baseVal:top.className).slice(0,80):null,
      isSelf: top===el || el.contains(top)});
  }
  // 找覆盖层
  const overlays=[];
  document.querySelectorAll('*').forEach(el=>{
    const cs=getComputedStyle(el);
    if((cs.position==='fixed'||cs.position==='absolute') && parseInt(cs.zIndex||'0')>50){
      const r=el.getBoundingClientRect();
      if(r.width>200&&r.height>200) overlays.push({tag:el.tagName, cls:String(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className).slice(0,60), z:cs.zIndex, op:cs.opacity, w:Math.round(r.width),h:Math.round(r.height)});
    }
  });
  return {out, overlays: overlays.slice(0,10)};
}"""

m=MCP()
m.call("new_page",{"url":"https://y.qq.com/n/ryqq/singer/0025NhlN2yWrP4","timeout":45000})
time.sleep(3)
m.call("evaluate_script",{"function":INJECT,"confirm":True,"mainWorld":True})
m.call("navigate_page",{"type":"reload","timeout":45000})
time.sleep(16)
r=m.call("evaluate_script",{"function":PROBE,"confirm":True,"mainWorld":True})
print(json.dumps(r,ensure_ascii=False)[:4000])
m.kill()
