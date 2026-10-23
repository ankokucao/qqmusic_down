import json,subprocess,os,sys,threading,queue,time

class MCP:
    def __init__(self, args=None, cwd=None, isolated=False):
        # isolated=True: 使用临时独立 profile, 避免与其它 js-reverse-mcp 实例
        # 争抢同一个 cloak browser user-data-dir 而互相 kill
        if args is None:
            args = ["-y","js-reverse-mcp@latest","--cloak"]
            if isolated:
                args.append("--isolated")
        env=dict(os.environ)
        self.p=subprocess.Popen(["C://Program Files//nodejs//npx.cmd"]+args,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            env=env,text=True,encoding="utf-8",cwd=cwd,bufsize=1)
        self.id=0
        rid=self._nid()
        self.send({"jsonrpc":"2.0","id":rid,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"drv","version":"1"}}})
        self.wait_id(rid)
        self.send({"jsonrpc":"2.0","method":"notifications/initialized"})
    def _nid(self):
        self.id+=1; return self.id
    _last=None
    def send(self,o):
        self.p.stdin.write(json.dumps(o)+"\n"); self.p.stdin.flush()
    def wait_id(self,rid,timeout=180):
        t0=time.time()
        while time.time()-t0<timeout:
            line=self.p.stdout.readline()
            if not line: break
            try: m=json.loads(line)
            except: continue
            if m.get("id")==rid: return m
        raise TimeoutError(f"id {rid} timeout")
    def call(self,name,args=None,timeout=180):
        rid=self._nid()
        self.send({"jsonrpc":"2.0","id":rid,"method":"tools/call","params":{"name":name,"arguments":args or {}}})
        m=self.wait_id(rid,timeout)
        r=m.get("result") or m.get("error")
        if isinstance(r,dict) and "structuredContent" in r:
            return r["structuredContent"]
        if isinstance(r,dict) and "content" in r:
            return r["content"]
        return r
    def tools(self):
        rid=self._nid()
        self.send({"jsonrpc":"2.0","id":rid,"method":"tools/list","params":{}})
        m=self.wait_id(rid)
        return m["result"]["tools"]
    def kill(self):
        try: self.p.kill()
        except: pass

if __name__=="__main__":
    m=MCP()
    for t in m.tools():
        print("###",t["name"])
        print(json.dumps(t.get("inputSchema",{}),ensure_ascii=False,indent=1)[:1200])
    m.kill()
