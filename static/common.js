/* common.js - shared helpers for all pages (loaded in <head>, so DOM-dependent code waits for DOMContentLoaded) */
(function () {
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  window.$ = $; window.$$ = $$;

  window.esc = v => String(v == null ? '' : v).replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* fetch wrapper -> {ok, status, data}; never throws */
  window.api = async function (url, opts) {
    opts = opts || {};
    if (opts.json !== undefined) {
      opts.method = opts.method || 'POST';
      opts.headers = { 'Content-Type': 'application/json' };
      opts.body = JSON.stringify(opts.json);
      delete opts.json;
    }
    let res;
    try { res = await fetch(url, opts); }
    catch (e) { return { ok: false, status: 0, data: { detail: 'Network error: ' + e.message } }; }
    let data = null;
    try { data = await res.json(); } catch (e) { /* not json */ }
    return { ok: res.ok, status: res.status, data: data || {} };
  };

  /* readable error text from a FastAPI / _run() error response */
  window.errText = function (r) {
    const d = r.data && r.data.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d.map(x => ((x.loc || []).slice(1).join('.') || 'input') + ': ' + x.msg).join('\n');
    return d ? JSON.stringify(d) : 'Request failed (HTTP ' + r.status + ')';
  };

  /* kind: ok | err | info ; empty text hides the box */
  window.showMsg = function (el, kind, text) {
    if (!el) return;
    if (!text) { el.className = 'msg hidden'; el.textContent = ''; return; }
    el.className = 'msg ' + kind;
    el.textContent = text;
  };

  /* list of dicts -> HTML table (a "DataFrame") */
  window.cellHtml = function (v) {
    if (v === null || v === undefined) return '<span class="null">None</span>';
    if (typeof v === 'object') return esc(JSON.stringify(v));
    return esc(v);
  };
  window.tableHtml = function (rows, caption) {
    if (!rows || !rows.length) return '<p class="muted">' + esc(caption ? caption + ': ' : '') + 'no rows.</p>';
    const cols = [];
    rows.forEach(r => Object.keys(r).forEach(k => { if (!cols.includes(k)) cols.push(k); }));
    return '<div class="df"><table>' + (caption ? '<caption>' + esc(caption) + '</caption>' : '') +
      '<thead><tr>' + cols.map(c => '<th>' + esc(c) + '</th>').join('') + '</tr></thead><tbody>' +
      rows.map(r => '<tr>' + cols.map(c => '<td>' + cellHtml(r[c]) + '</td>').join('') + '</tr>').join('') +
      '</tbody></table></div>';
  };

  /* modal: returns {el (body element), close()} */
  window.openModal = function (title, bodyHtml) {
    const back = document.createElement('div');
    back.className = 'modal-back';
    back.innerHTML = '<div class="modal" role="dialog" aria-modal="true"><div class="modal-head"><h3>' + esc(title) +
      '</h3><button class="x" aria-label="Close">&times;</button></div><div class="modal-body">' + bodyHtml + '</div></div>';
    document.body.appendChild(back);
    const onKey = e => { if (e.key === 'Escape') close(); };
    const close = () => { back.remove(); document.removeEventListener('keydown', onKey); };
    document.addEventListener('keydown', onKey);
    $('.x', back).onclick = close;
    back.addEventListener('mousedown', e => { if (e.target === back) close(); });
    return { el: $('.modal-body', back), close };
  };

  /* flying sunset dots */
  function sky() {
    const s = document.getElementById('sky');
    if (!s) return;
    for (let i = 0; i < 40; i++) {
      const d = document.createElement('span');
      const z = 2 + Math.random() * 5;
      d.className = 'dot';
      d.style.cssText = 'width:' + z + 'px;height:' + z + 'px;left:' + (Math.random() * 100) + '%;--dx:' +
        (Math.random() * 160 - 80) + 'px;animation-duration:' + (14 + Math.random() * 22) + 's;animation-delay:-' +
        (Math.random() * 30) + 's';
      s.appendChild(d);
    }
  }

  /* highlight the tab whose section is on screen */
  function activeTabs() {
    const links = $$('nav.tabs a[href^="#"]');
    if (!links.length) return;
    const update = () => {
      let cur = null;
      links.forEach(a => {
        const sec = $(a.getAttribute('href'));
        if (sec && sec.getBoundingClientRect().top <= 120) cur = a;
      });
      links.forEach(a => a.classList.toggle('active', a === cur));
    };
    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  document.addEventListener('DOMContentLoaded', () => { sky(); activeTabs(); });
})();
