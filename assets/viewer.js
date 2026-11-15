// Board viewer: shows one board from window.BOARD_SET (assets/boards.js), chosen by the URL hash.
(function () {
  'use strict';

  var set = window.BOARD_SET;
  var boards = set.boards;
  var $ = function (id) { return document.getElementById(id); };
  var stage = $('stage');
  var box = $('board-box');
  var frame = $('board-frame');
  var prev = $('board-prev');
  var next = $('board-next');
  var zoomButtons = document.querySelectorAll('[data-zoom]');

  var index = 0;
  var zoom = 'fit';

  function indexFromHash() {
    var slug = decodeURIComponent(location.hash.slice(1));
    for (var i = 0; i < boards.length; i++) {
      if (boards[i].slug === slug) return i;
    }
    return 0;
  }

  function layout() {
    var b = boards[index];
    var scale = 1;
    if (zoom === 'fit') {
      var cs = getComputedStyle(stage);
      var availW = stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      var availH = stage.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      scale = Math.max(0.1, Math.min(availW / b.w, availH / b.h));
    }
    frame.style.width = b.w + 'px';
    frame.style.height = b.h + 'px';
    frame.style.transform = scale === 1 ? '' : 'scale(' + scale + ')';
    box.style.width = Math.round(b.w * scale) + 'px';
    box.style.height = Math.round(b.h * scale) + 'px';
  }

  function show() {
    index = indexFromHash();
    var b = boards[index];
    var src = 'boards/' + b.slug + '.html';
    if (frame.getAttribute('src') !== src) frame.setAttribute('src', src);
    frame.title = b.code + ' · ' + b.title;
    $('board-code').textContent = b.code;
    $('board-title').textContent = b.title;
    $('board-title').title = b.title;
    $('board-open').href = src;
    $('board-pos').textContent = (index + 1) + ' / ' + boards.length;
    prev.disabled = index === 0;
    next.disabled = index === boards.length - 1;
    document.title = b.code + ' · ' + b.title + ' · ' + set.set;
    stage.scrollTo(0, 0);
    layout();
  }

  function go(delta) {
    var i = index + delta;
    if (i < 0 || i >= boards.length) return;
    location.hash = boards[i].slug;
  }

  function setZoom(value) {
    zoom = value;
    for (var i = 0; i < zoomButtons.length; i++) {
      zoomButtons[i].setAttribute('aria-pressed', String(zoomButtons[i].getAttribute('data-zoom') === zoom));
    }
    layout();
  }

  prev.addEventListener('click', function () { go(-1); });
  next.addEventListener('click', function () { go(1); });
  for (var i = 0; i < zoomButtons.length; i++) {
    zoomButtons[i].addEventListener('click', function () { setZoom(this.getAttribute('data-zoom')); });
  }

  document.addEventListener('keydown', function (e) {
    // At 1:1 the arrow keys keep scrolling the board; paging is on the buttons.
    if (zoom !== 'fit' || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.key === 'ArrowLeft') { go(-1); e.preventDefault(); }
    else if (e.key === 'ArrowRight') { go(1); e.preventDefault(); }
  });

  window.addEventListener('hashchange', show);
  if (window.ResizeObserver) new ResizeObserver(layout).observe(stage);
  else window.addEventListener('resize', layout);

  show();
})();
