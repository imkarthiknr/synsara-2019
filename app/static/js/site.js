// SYNSARA site behaviour. Progressive enhancement only: every page works without JS.
(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Text scramble (the 2019 "shuffle letters" effect, without jQuery).
  const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&';
  function scramble(el) {
    const target = el.dataset.scramble || el.textContent;
    if (reduceMotion) { el.textContent = target; return; }
    const total = 22;
    let frame = 0;
    const tick = () => {
      frame += 1;
      const revealed = Math.floor((frame / total) * target.length);
      el.textContent = [...target]
        .map((ch, i) => (i < revealed || ch === ' ' ? ch : GLYPHS[(Math.random() * GLYPHS.length) | 0]))
        .join('');
      if (frame < total) requestAnimationFrame(() => setTimeout(tick, 35));
      else el.textContent = target;
    };
    tick();
  }
  document.querySelectorAll('[data-scramble]').forEach(scramble);

  // Countdown to the symposium (or a note once it's over).
  const cd = document.querySelector('[data-countdown]');
  if (cd) {
    const start = new Date(cd.dataset.countdown).getTime();
    const end = new Date(cd.dataset.ends).getTime();
    const render = () => {
      const now = Date.now();
      if (now >= end) {
        cd.innerHTML = '<p class="past">This edition has concluded. Thank you for being part of it!</p>';
        return false;
      }
      if (now >= start) {
        cd.innerHTML = '<p class="past">Happening now. See you at the venue!</p>';
        return false;
      }
      let s = Math.floor((start - now) / 1000);
      const parts = [['days', 86400], ['hours', 3600], ['mins', 60], ['secs', 1]].map(([label, n]) => {
        const v = Math.floor(s / n); s -= v * n; return [label, v];
      });
      cd.innerHTML = parts.map(([l, v]) => `<div class="unit"><b>${String(v).padStart(2, '0')}</b><span>${l}</span></div>`).join('');
      return true;
    };
    if (render()) setInterval(render, 1000);
  }

  // Mobile menu.
  const menu = document.querySelector('[data-menu]');
  const nav = document.getElementById('nav');
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', (e) => { if (e.target.closest('a')) { nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); } });
  }

  // Event choice limits: disable the rest once the maximum is ticked (the server enforces it too).
  document.querySelectorAll('fieldset[data-limit]').forEach((fs) => {
    const max = Number(fs.dataset.limit);
    const boxes = [...fs.querySelectorAll('input[type=checkbox]')];
    const status = fs.querySelector('[data-limit-status]');
    const update = () => {
      const n = boxes.filter((b) => b.checked).length;
      boxes.forEach((b) => { b.disabled = !b.checked && n >= max; });
      if (status) status.textContent = n >= max ? `Maximum of ${max} selected.` : `${n} of ${max} selected.`;
    };
    boxes.forEach((b) => b.addEventListener('change', update));
    update();
  });

  // Confirm destructive admin actions.
  document.querySelectorAll('form[data-confirm]').forEach((f) => {
    f.addEventListener('submit', (e) => { if (!window.confirm(f.dataset.confirm)) e.preventDefault(); });
  });
})();
