import json,urllib.request,urllib.parse

COOKIE=open('cookie.txt',encoding='utf-8').read().strip()
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
   "Referer":"https://y.qq.com/","Cookie":COOKIE}

def fetch(url,data=None,hdr=None):
    h=dict(H)
    if hdr:h.update(hdr)
    body=None
    if data is not None:
        body=json.dumps(data).encode(); h["Content-Type"]="application/json"
    try:
        r=urllib.request.Request(url,data=body,headers=h)
        with urllib.request.urlopen(r,timeout=15) as resp:
            return resp.status,resp.read()
    except Exception as e:
        return -1,str(e).encode()

def rep(tag,b):
    s=b.decode('utf-8','replace')
    if 'vkey' in s or 'purl' in s or 'sip' in s:
        print("### HIT",tag); print(s[:1200]); return True
    if s.strip():
        print("---",tag,len(s),s[:220].replace("\n"," "))
    return False

MID="000NBVdP3wg95P"   # 免费歌
MM=MID
FN="C400%s.mp3"%MM
GUID="1000000000"

# 1) 各类遗留 vkey 端点
urls=[
 "https://i.y.qq.com/qianmusic/vkey?guid=%s&songmid=%s&filename=%s&size=128"%(GUID,MID,FN),
 "https://i.y.qq.com/qianmusic/vkey?guid=%s&songmid=%s&filename=%s"%(GUID,MID,FN),
 "https://c.y.qq.com/fcgi-bin/fcg_outer_playurl.fcg?songmid=%s&songid=734825099&format=json"%MID,
 "https://c.y.qq.com/base/fcgi-bin/fcg_bin_single_song.fcg?songmid=%s&format=json"%MID,
 "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid=%s&filename=%s&format=json"%(MID,FN),
 "https://ws.stream.qqmusic.qq.com/C400%s.mp3?guid=%s&vkey=&fromtag=38"%(MM,GUID),
 "https://c.y.qq.com/base/fcgi-bin/fcg_play_single_song_new.fcg?songmid=%s&format=json"%MID,
 "https://c.y.qq.com/base/fcgi-bin/fcg_outer_playurl.fcg?songmid=%s&format=json"%MID,
 "https://i.y.qq.com/qianmusic/fcgi-bin/fcg_outer_playurl.fcg?songmid=%s&format=json"%MID,
]
for u in urls:
    st,b=fetch(u)
    rep(u[:90],b)

# 2) u6 明文 musicu.fcg 通道 + 各 vkey 模块
def probe(host,mod,method,param,ct=11):
    data={"comm":{"ct":ct,"cv":1000000,"uin":"1152921504608413217"},
          "req_0":{"module":mod,"method":method,"param":param}}
    st,b=fetch("https://%s/cgi-bin/musicu.fcg"%host,data)
    return b

base_param={"guid":GUID,"songmid":MID,"songtype":0,"uin":"1152921504608413217",
            "loginflag":1,"platform":"20","filename":FN,"song_type":0}
for host in ["u.y.qq.com","u6.y.qq.com","c.y.qq.com","i.y.qq.com","h5.y.qq.com","y.qq.com"]:
    for mod,meth in [("music.vkeyProxyUrl","GetVkey"),("music.vkey","GetVkey"),
                     ("music.playUrl","GetPlayUrl"),("music.getVkey","GetVkey"),
                     ("vkey.getVkey","GetVkey"),("music.vkeyGetVkey","GetVkey"),
                     ("music.streamUrl","GetUrl"),("music.musicUrl","GetUrl")]:
        for ct in (11,24):
            b=probe(host,mod,meth,dict(base_param),ct)
            s=b.decode('utf-8','replace')
            if '"code":0' in s and ('vkey' in s or 'purl' in s):
                print("### HIT",host,mod,meth,ct); print(s[:1200])
            elif '"code":0' in s:
                sub=s[:200].replace("\n"," ")
                if '500003' not in s:
                    print("--- code0 but no vkey:",host,mod,meth,ct,sub)
print("done")
