/* QQ音乐取流下载工具 - 前端逻辑 */
(function () {
  "use strict";

  var $ = function (s) { return document.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };

  var state = { current: null, rows: [], busy: false };

  // ---------------- 主题 ----------------
  var saved = localStorage.getItem("qqm-theme");
  var prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
  document.documentElement.setAttribute("data-theme", saved || (prefersLight ? "light" : "dark"));
  $("#themeBtn").addEventListener("click", function () {
    var cur = document.documentElement.getAttribute("data-theme");
    var nxt = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nxt);
    localStorage.setItem("qqm-theme", nxt);
  });

  // ---------------- 工具 ----------------
  function fmtSize(n) {
    if (!n && n !== 0) return "-";
    if (n < 1024) return n + " B";
    if (n < 1048576) return (n / 1024).toFixed(1) + " KB";
    return (n / 1048576).toFixed(2) + " MB";
  }
  function fmtDur(s) {
    if (!s && s !== 0) return "-";
    var m = Math.floor(s / 60), x = s % 60;
    return m + ":" + (x < 10 ? "0" : "") + x;
  }
  function toast(msg, kind) {
    var t = $("#toast");
    t.textContent = msg;
    t.className = "toast show" + (kind ? " " + kind : "");
    clearTimeout(t._tm);
    t._tm = setTimeout(function () { t.className = "toast"; }, 3200);
  }
  function api(path, opt) {
    return fetch(path, opt).then(function (r) {
      return r.json().catch(function () { return { error: "HTTP " + r.status }; });
    });
  }
  function setStatus(text, kind) {
    $("#statusText").textContent = text;
    $("#status").className = "status" + (kind ? " " + kind : "");
  }

  // ---------------- 状态轮询 ----------------
  function pollStatus() {
    api("/api/status").then(function (d) {
      if (!d) return;
      if (d.ready) setStatus("浏览器会话就绪", "ok");
      else if (d.state && d.state.indexOf("启动") >= 0) setStatus(d.state, "busy");
      else if (d.state && d.state.indexOf("加载") >= 0) setStatus(d.state, "busy");
      else setStatus(d.state || "未知");
    }).catch(function () { setStatus("服务未连接", "err"); });
  }
  setInterval(pollStatus, 3000);
  pollStatus();

  // ---------------- 搜索 ----------------
  function doSearch() {
    var kw = $("#q").value.trim();
    if (!kw) { toast("请输入歌名或歌手"); return; }
    $("#searchBtn").disabled = true;
    $("#searchBtn").textContent = "搜索中…";
    api("/api/search?q=" + encodeURIComponent(kw))
      .then(function (d) {
        if (d.error) { toast(d.error, "err"); return; }
        renderResults(d.list || []);
        $("#searchCount").textContent = d.total ? "共 " + d.total + " 首" : "";
      })
      .catch(function (e) { toast("搜索失败: " + e.message, "err"); })
      .finally(function () {
        $("#searchBtn").disabled = false;
        $("#searchBtn").textContent = "搜索";
      });
  }

  function renderResults(list) {
    var box = $("#results");
    box.innerHTML = "";
    if (!list.length) {
      box.innerHTML = '<div class="empty" style="padding:30px 0"><p>没有找到结果</p></div>';
      return;
    }
    list.forEach(function (s) {
      var el = document.createElement("div");
      el.className = "r-item";
      el.dataset.mid = s.songmid;
      var isVip = !!(s.size_320mp3 && s.size_flac);
      el.innerHTML =
        '<div class="r-title">' + esc(s.name || "?") +
        (s.songmid ? "" : '<span class="badge dim">无ID</span>') + '</div>' +
        '<div class="r-sub">' + esc(s.singer || "") +
        (s.album ? " · " + esc(s.album) : "") + " · " + fmtDur(s.duration) + "</div>";
      el.addEventListener("click", function () {
        $$(".r-item").forEach(function (x) { x.classList.remove("active"); });
        el.classList.add("active");
        loadDetail(s);
      });
      box.appendChild(el);
    });
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------------- 详情 ----------------
  function loadDetail(s) {
    state.current = s;
    $("#empty").classList.add("hidden");
    $("#detail").classList.remove("hidden");
    $("#sName").textContent = s.name || "—";
    $("#sSinger").textContent = s.singer || "—";
    $("#cover").textContent = "♫";
    var tags = [];
    tags.push('<span class="tag">时长 ' + fmtDur(s.duration) + "</span>");
    if (s.size_128mp3) tags.push('<span class="tag">128k ' + fmtSize(s.size_128mp3) + "</span>");
    if (s.size_320mp3) tags.push('<span class="tag">320k ' + fmtSize(s.size_320mp3) + "</span>");
    if (s.size_flac) tags.push('<span class="tag">FLAC ' + fmtSize(s.size_flac) + "</span>");
    $("#sTags").innerHTML = tags.join("");
    $("#rows").innerHTML = "";
    $("#resolveHint").textContent = "选择音质后点击获取";
  }

  // ---------------- 取流 ----------------
  function resolve() {
    if (!state.current || !state.current.songmid) { toast("请先选择歌曲", "err"); return; }
    var quals = $$("#qualities input:checked").map(function (i) { return i.value; });
    if (!quals.length) { toast("请至少选择一个音质", "err"); return; }
    if (state.busy) return;
    state.busy = true;
    var btn = $("#resolveBtn");
    btn.disabled = true; btn.textContent = "取流中…（首次约需 20 秒）";
    setStatus("取流中…", "busy");
    $("#rows").innerHTML = "";

    api("/api/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ songmid: state.current.songmid, qualities: quals })
    }).then(function (d) {
      if (d.error) { toast("取流失败: " + d.error, "err"); return; }
      state.rows = d.rows || [];
      renderRows();
      var ok = state.rows.filter(function (r) { return r.url; }).length;
      toast("成功获取 " + ok + " 条可用地址", ok ? "ok" : "err");
    }).catch(function (e) {
      toast("请求失败: " + e.message, "err");
    }).finally(function () {
      state.busy = false;
      btn.disabled = false; btn.textContent = "获取下载地址";
      pollStatus();
    });
  }

  var ICONS = {
    rs02: "▶", c400: "♪", m500: "♫", m800: "♬", f000: "❖", a000: "♫"
  };

  function renderRows() {
    var box = $("#rows");
    box.innerHTML = "";
    if (!state.rows.length) {
      box.innerHTML = '<div class="empty" style="padding:26px 0"><p>未返回结果</p></div>';
      return;
    }
    state.rows.forEach(function (r) {
      var el = document.createElement("div");
      el.className = "row" + (r.url ? "" : " bad");
      var statusPill = r.url
        ? '<span class="pill ok">可用</span>'
        : (r.result === 104003
          ? '<span class="pill no">需 VIP</span>'
          : '<span class="pill wait">result ' + (r.result == null ? "?" : r.result) + "</span>");
      var actions = r.url
        ? '<button class="mini go" data-act="dl">下载</button>' +
          '<button class="mini" data-act="copy">复制地址</button>'
        : '<button class="mini" disabled>不可用</button>';
      el.innerHTML =
        '<div class="row-ic">' + (ICONS[r.quality] || "♪") + "</div>" +
        '<div class="row-main">' +
        '<div class="row-t">' + esc(r.label || r.quality) + " " + statusPill + "</div>" +
        '<div class="row-s">' + esc(r.filename || "") + (r.expiration ? " · 有效期 " + Math.round(r.expiration / 3600) + "h" : "") + "</div>" +
        "</div>" +
        '<div class="row-act">' + actions + "</div>";

      if (r.url) {
        el.querySelector('[data-act="copy"]').addEventListener("click", function () {
          copy(r.url);
        });
        el.querySelector('[data-act="dl"]').addEventListener("click", function (e) {
          doDownload(r, e.currentTarget);
        });
      }
      box.appendChild(el);
    });
  }

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { toast("地址已复制", "ok"); },
        function () { fallbackCopy(text); });
    } else { fallbackCopy(text); }
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); toast("地址已复制", "ok"); }
    catch (e) { toast("复制失败，请手动选取", "err"); }
    document.body.removeChild(ta);
  }

  // ---------------- 下载 ----------------
  function doDownload(row, btn) {
    var old = btn.textContent;
    btn.disabled = true; btn.textContent = "下载中…";
    var song = (state.current && state.current.name) || "audio";
    var fname = song + "_" + (row.filename || (row.quality + ".mp3"));
    api("/api/download?url=" + encodeURIComponent(row.url) +
        "&name=" + encodeURIComponent(fname))
      .then(function (d) {
        if (d.error) { toast("下载失败: " + d.error, "err"); return; }
        toast("已保存 " + d.file + " (" + fmtSize(d.bytes) + ")", "ok");
        loadFiles();
        // 触发浏览器保存到默认下载目录
        var a = document.createElement("a");
        a.href = "/api/file?name=" + encodeURIComponent(d.file);
        a.download = d.file;
        document.body.appendChild(a); a.click(); a.remove();
      })
      .catch(function (e) { toast("下载失败: " + e.message, "err"); })
      .finally(function () { btn.disabled = false; btn.textContent = old; });
  }

  // ---------------- 已下载列表 ----------------
  function loadFiles() {
    api("/api/files").then(function (d) {
      var box = $("#files");
      box.innerHTML = "";
      var fs = d.files || [];
      $("#fileCount").textContent = fs.length ? fs.length + " 个文件" : "";
      if (!fs.length) {
        box.innerHTML = '<div class="r-sub" style="padding:6px 2px">暂无下载</div>';
        return;
      }
      fs.slice(0, 30).forEach(function (f) {
        var el = document.createElement("div");
        el.className = "f-item";
        el.innerHTML =
          '<span class="fn" title="' + esc(f.name) + '">' + esc(f.name) + "</span>" +
          '<span class="fs">' + fmtSize(f.bytes) + "</span>" +
          '<a href="/api/file?name=' + encodeURIComponent(f.name) + '" download>保存</a>';
        box.appendChild(el);
      });
    });
  }

  // ---------------- 事件 ----------------
  $("#searchBtn").addEventListener("click", doSearch);
  $("#q").addEventListener("keydown", function (e) { if (e.key === "Enter") doSearch(); });
  $("#resolveBtn").addEventListener("click", resolve);
  loadFiles();
  setInterval(loadFiles, 15000);
})();
