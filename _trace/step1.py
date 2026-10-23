import json,sys
sys.path.insert(0,'.')
from mcpdrv import MCP

COOKIE = "pgv_pvid=3329277760; fqm_pvqid=420278c5-0915-49c3-a9fd-3cd7d0821efb; fqm_sessionid=be4ef1c1-ebf1-462f-a5a7-e261786e50e0; _tme_did=secid_v1_ecf405d013cc0657fefd28942df27a691035; _tme_cid=cid_v1_3c261edd84baac3fa104d2d59702a5aa66d7; pgv_info=ssid=s2643671652; ts_last=y.qq.com/; ts_refer=www.google.com/; ts_uid=3396806898; _qpsvr_localtk=0.6795685303380659; qlogin_uid=281dabf9afb70b6739eaa8492168ce9d; qqmusic_key=W_X_63B0aEDr_0nhpBK7xBut2M-JXvv3mQK1KVNK2KrqGva8pUBqF-QBSOdXzyQOKp20W78GZhRVnafpZ6oU1XXdp68Hrjd1bbg; euin=oK6kowEAoK4z7eCzNev5oi-57z**; qm_keyst=W_X_63B0aEDr_0nhpBK7xBut2M-JXvv3mQK1KVNK2KrqGva8pUBqF-QBSOdXzyQOKp20W78GZhRVnafpZ6oU1XXdp68Hrjd1bbg; psrf_qqaccess_token=; tmeLoginType=1; wxunionid=oqFLxsqtYevP6AF3Me0JcKJnzaAQ; psrf_qqopenid=; psrf_qqrefresh_token=; psrf_qqunionid=; wxuin=1152921504608413217; wxopenid=opCFJw1tc3uxexsmrVtPh_R2QCJs; wxuin=1152921504608413217; login_type=2"

m=MCP()
print("STEP1 open y.qq.com")
print(json.dumps(m.call("new_page",{"url":"https://y.qq.com/"}),ensure_ascii=False)[:600])

# 注入 cookie（分 domain 投放：主站 .qq.com / .y.qq.com）
inject = f"""() => {{
  const raw = {json.dumps(COOKIE)};
  const parts = raw.split(';').map(s=>s.trim()).filter(Boolean);
  const setOn = (domain, path) => {{
    parts.forEach(p => {{
      const i = p.indexOf('=');
      const k = p.slice(0,i), v = p.slice(i+1);
      document.cookie = k + '=' + v + '; domain=' + domain + '; path=/; max-age=2592000';
    }});
  }};
  setOn('.qq.com','/'); setOn('.y.qq.com','/');
  return document.cookie.length;
}}"""
print("STEP2 inject cookies")
print(json.dumps(m.call("evaluate_script",{"function":inject,"confirm":True,"mainWorld":True}),ensure_ascii=False)[:600])
print("STEP3 cookie now")
print(json.dumps(m.call("evaluate_script",{"function":"() => document.cookie","mainWorld":True}),ensure_ascii=False)[:2000])
m.kill()
