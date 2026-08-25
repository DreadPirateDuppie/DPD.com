/* Matrix rain + category filtering. Both degrade to nothing if unsupported. */
(function () {
  "use strict";

  var reduce = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- katakana rain ---- */
  var GLYPHS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789".split("");

  function rain(cv) {
    var ctx = cv.getContext && cv.getContext("2d");
    if (!ctx) return;
    var cols, drops, size = 14, raf;

    function resize() {
      var r = cv.getBoundingClientRect();
      cv.width = Math.max(1, r.width);
      cv.height = Math.max(1, r.height);
      cols = Math.ceil(cv.width / size);
      drops = new Array(cols);
      for (var i = 0; i < cols; i++) drops[i] = Math.random() * -50;
    }

    function frame() {
      ctx.fillStyle = "rgba(0,0,0,0.09)";
      ctx.fillRect(0, 0, cv.width, cv.height);
      ctx.font = size + "px 'Courier New', monospace";
      for (var i = 0; i < cols; i++) {
        var ch = GLYPHS[(Math.random() * GLYPHS.length) | 0];
        var y = drops[i] * size;
        ctx.fillStyle = Math.random() > 0.985 ? "#ccffcc" : "rgba(0,255,7,0.55)";
        ctx.fillText(ch, i * size, y);
        if (y > cv.height && Math.random() > 0.975) drops[i] = 0;
        drops[i] += 0.5;
      }
      raf = requestAnimationFrame(frame);
    }

    resize();
    addEventListener("resize", resize);
    if (reduce) {
      // one static pass, no animation
      ctx.font = size + "px 'Courier New', monospace";
      for (var i = 0; i < cols; i++) {
        for (var j = 0; j < cv.height / size; j++) {
          if (Math.random() > 0.88) {
            ctx.fillStyle = "rgba(0,255,7,0.28)";
            ctx.fillText(GLYPHS[(Math.random() * GLYPHS.length) | 0], i * size, j * size);
          }
        }
      }
      return;
    }
    frame();
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-rain]"), rain);

  /* ---- category filter ---- */
  var cards = [].slice.call(document.querySelectorAll(".card"));
  if (!cards.length) return;
  var bar = document.querySelector(".catbar");
  var shown = document.getElementById("shown");
  var empty = document.getElementById("empty");

  function apply(cat) {
    var n = 0;
    cards.forEach(function (c) {
      var hit = cat === "all" ||
        (" " + c.getAttribute("data-cats") + " ").indexOf(" " + cat + " ") > -1;
      c.hidden = !hit;
      if (hit) n++;
    });
    if (shown) shown.textContent = n;
    if (empty) empty.hidden = n !== 0;
    if (bar) {
      [].forEach.call(bar.querySelectorAll(".cat"), function (a) {
        a.classList.toggle("on", a.getAttribute("data-cat") === cat);
      });
    }
  }

  // a chip followed from a post page arrives as ?cat=...
  try {
    var q = /[?&]cat=([^&#]+)/.exec(location.search);
    apply(q ? decodeURIComponent(q[1]) : "all");
  } catch (err) { apply("all"); }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-cat]");
    if (!a) return;
    var onIndex = !!document.querySelector(".grid");
    if (!onIndex) return;           // chips on post pages navigate to the index instead
    e.preventDefault();
    apply(a.getAttribute("data-cat"));
    document.getElementById("blog").scrollIntoView({ block: "start" });
  });
})();

/* ---- BTEK set search ---- */
(function () {
  "use strict";
  var q = document.getElementById("q");
  if (!q) return;
  var sets = [].slice.call(document.querySelectorAll(".set"));
  var count = document.getElementById("setcount");
  var none = document.getElementById("noresult");

  function run() {
    var term = q.value.trim().toLowerCase(), n = 0;
    sets.forEach(function (s) {
      var hit = !term || s.getAttribute("data-title").indexOf(term) > -1;
      s.hidden = !hit;
      if (hit) n++;
    });
    if (count) count.textContent = n;
    if (none) none.hidden = n !== 0;
  }
  q.addEventListener("input", run);
})();

/* ---- photography lightbox ---- */
(function () {
  "use strict";
  var lb = document.getElementById("lb");
  if (!lb) return;
  var tiles = [].slice.call(document.querySelectorAll(".shot-t")),
      img = document.getElementById("lbimg"),
      cnt = document.getElementById("lbc"),
      cur = 0;

  function show(i) {
    cur = (i + tiles.length) % tiles.length;
    img.src = tiles[cur].getAttribute("data-full");
    cnt.textContent = (cur + 1) + " / " + tiles.length;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
  }
  function hide() {
    lb.hidden = true;
    img.src = "";
    document.body.style.overflow = "";
  }

  tiles.forEach(function (t, i) {
    t.addEventListener("click", function () { show(i); });
  });
  document.getElementById("lbx").addEventListener("click", hide);
  document.getElementById("lbp").addEventListener("click", function (e) {
    e.stopPropagation(); show(cur - 1);
  });
  document.getElementById("lbn").addEventListener("click", function (e) {
    e.stopPropagation(); show(cur + 1);
  });
  lb.addEventListener("click", function (e) { if (e.target === lb) hide(); });
  document.addEventListener("keydown", function (e) {
    if (lb.hidden) return;
    if (e.key === "Escape") hide();
    else if (e.key === "ArrowLeft") show(cur - 1);
    else if (e.key === "ArrowRight") show(cur + 1);
  });
})();
