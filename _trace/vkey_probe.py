import json,urllib.request,urllib.parse,itertools,os,sys

COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEAD={"User-Agent":UA,"Referer":"https://y.qq.com/","Cookie":COOKIE,
      "Accept":"application/json, text/plain, */*"}

def get(url,data=None,extra=None):
    h=dict(HEAD)
    if extra:h.update(extra)
    body=None
    if data is not None:
        body=json.dumps(data).encode()
        h["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=body,headers=h)
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            return r.status,r.read()
    except Exception as e:
        return -1,str(e).encode()

def show(tag,b):
    s=b.decode('utf-8','replace')
    if 'vkey' in s or 'sip' in s or 'purl' in s:
        print("!! HIT",tag)
        print(s[:1500]); return True
    return False

# 免费歌 + VIP歌
SONGS={"vip":"0039MnYb0qxYhV","free":"000NBVdP3wg95P"}
MEDIAMID={"0039MnYb0qxYhV":"003Qui1q2u1Zho","000NBVdP3wg95P":None}

def fnames(mid,media_mid):
    out=[]
    if media_mid:
        for p in ["C400","C500","M500","F000","C100","C128","M500","M800","C32"]:
            for e in ["mp3","flac","m4a","aac","ogg"]:
                out.append(p+media_mid+"."+e)
    out.append("C100"+mid+".m4a")
    out.append("M500"+mid+".mp3")
    out.append("F000"+mid+".flac")
    return out

for host in ["u.y.qq.com","u6.y.qq.com","c.y.qq.com","i.y.qq.com","y.qq.com"]:
    for mod in ["music.vkeyProxyUrl","music.vkey","music.playUrl","music.getVkey","vkey.getVkey","music.vkeyProxy"]:
        for sname,mid in SONGS.items():
            fn=fnames(mid,MEDIAMID[mid])[0]
            param={"guid":"1000000000","songmid":mid,"songtype":0,"uin":"1152921504608413217",
                   "loginflag":1,"platform":"20","filename":fn,"file":{"filename":fn},
                   "song_type":0,"qsec":1}
            data={"comm":{"ct":11,"cv":1000000},"req_0":{"module":mod,"method":"GetVkey","param":param}}
            st,b=get("https://%s/cgi-bin/musicu.fcg"%host,data)
            s=b.decode('utf-8','replace')
            code=re_code=None
            try:
                j=json.loads(s); code=j.get("code")
            except Exception:
                pass
            tag="%s|%s|%s"%(host,mod,sname)
            if show(tag,b): sys.exit(0)
            if code not in (0,None) and code!=0:
                print("%-46s code=%s %s"%(tag,code,s[:110].replace("\n"," ")))
print("no hit")
