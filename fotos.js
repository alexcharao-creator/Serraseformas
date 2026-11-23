/* Serras & Formas — moldura para fotos externas que não carregarem
   (ex.: na prévia do Claude, que bloqueia imagens de outros sites).
   No site publicado as fotos carregam normalmente e nada disto aparece. */
(function () {
  function externa(img) {
    var s = img.getAttribute('src') || '';
    return /^https?:\/\//i.test(s);
  }
  function trocar(img) {
    if (!img || img.dataset.semFoto || !externa(img)) return;
    img.dataset.semFoto = '1';
    var mini = img.classList.contains('mini');
    var box = document.createElement('span');
    box.className = 'foto-ausente' + (mini ? ' mini' : '');
    box.setAttribute('role', 'img');
    box.setAttribute('aria-label', img.alt || 'Foto');
    box.innerHTML =
      '<svg viewBox="0 0 48 36" aria-hidden="true"><rect x="2" y="4" width="44" height="28" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>' +
      '<circle cx="14" cy="14" r="4" fill="currentColor"/><path d="M6 29l12-11 9 8 6-5 9 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>' +
      (mini ? '' : '<span class="fa-txt"></span><small>Foto visível no site publicado</small>');
    if (!mini && img.alt) box.querySelector('.fa-txt').textContent = img.alt;
    img.replaceWith(box);
  }
  document.addEventListener('error', function (e) {
    if (e.target && e.target.tagName === 'IMG') trocar(e.target);
  }, true);
  function revisar() {
    var imgs = document.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
      var im = imgs[i];
      if (im.complete && im.naturalWidth === 0 && externa(im)) trocar(im);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', revisar);
  else revisar();
  window.addEventListener('load', revisar);
})();
