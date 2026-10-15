(function(){
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* menu mobile : s'ouvre en 200 ms, se ferme avec Échap, un lien ou un clic ailleurs */
  var mb = document.querySelector('.menu-btn'), menu = document.getElementById('menu'), small = matchMedia('(max-width: 899px)');
  function setMenu(open){
    mb.setAttribute('aria-expanded', String(open));
    menu.hidden = small.matches && !open;
    if(open && !reduce){ menu.classList.remove('anim'); void menu.offsetWidth; menu.classList.add('anim'); }
  }
  if(mb && menu){
    setMenu(false);
    small.addEventListener('change', function(){ setMenu(false); });
    mb.addEventListener('click', function(){ setMenu(mb.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function(e){ if(e.target.closest('a') && small.matches) setMenu(false); });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && mb.getAttribute('aria-expanded') === 'true'){ setMenu(false); mb.focus(); }
    });
    document.addEventListener('click', function(e){
      if(mb.getAttribute('aria-expanded') === 'true' && !e.target.closest('.nav')) setMenu(false);
    });
  }

  /* pop-up newsletter : au clic sur « Newsletter » ; sur l'accueil, aussi après 10 s. Rien n'est mémorisé. */
  var d = document.getElementById('nl'), vu = false;
  if(d && typeof d.showModal === 'function'){
    var ouvrir = function(){ if(!d.open){ vu = true; setMenu && mb && setMenu(false); d.showModal(); } };
    document.querySelectorAll('[data-nl]').forEach(function(b){
      b.addEventListener('click', function(e){ e.preventDefault(); ouvrir(); });
    });
    d.addEventListener('click', function(e){ if(e.target === d) d.close(); });
    d.querySelectorAll('[data-close]').forEach(function(b){ b.addEventListener('click', function(){ d.close(); }); });
    if(document.body.hasAttribute('data-home')) setTimeout(function(){ if(!vu) ouvrir(); }, 10000);
  }

  /* lecteur YouTube : créé seulement au clic, à la place exacte de la vignette (pas de saut de mise en page) */
  document.addEventListener('click', function(e){
    var b = e.target.closest('.play'); if(!b) return;
    var box = b.parentNode, f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(box.dataset.yt) + '?autoplay=1';
    f.title = 'Lecteur YouTube : ' + box.dataset.title;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    box.replaceChild(f, b);
    f.focus();
  });

  /* entrées à l'écran, une fois par élément ; balayage de la pill quand son titre entre */
  var els = [].slice.call(document.querySelectorAll('[data-in], .pill[data-sweep]'));
  function show(x){ x.classList.add(x.matches('.pill') ? 'on' : 'in'); }
  if(reduce || !('IntersectionObserver' in window)){ els.forEach(show); return; }
  var io = new IntersectionObserver(function(list){
    var batch = list.filter(function(en){ return en.isIntersecting; }).map(function(en){ return en.target; });
    batch.forEach(function(x, k){
      io.unobserve(x);
      x.style.transitionDelay = x.matches('.pill') ? '120ms' : (Math.min(k, 6) * 40) + 'ms';
      show(x);
      x.addEventListener('transitionend', function(){ x.style.transitionDelay = ''; }, { once: true });
    });
  }, { rootMargin: '0px 0px -6% 0px' });
  els.forEach(function(x){ io.observe(x); });
})();
