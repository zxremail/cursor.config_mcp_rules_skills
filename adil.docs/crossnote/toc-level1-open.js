(function () {
  if (window.__mpeSidebarToc350) {
    return;
  }
  window.__mpeSidebarToc350 = true;

  var TOC_WIDTH_PX = 350;
  var MIN_WIDTH = 200;
  var REPLACEABLE_WIDTHS = { 280: 1, 420: 1, 500: 1, 620: 1 };
  var OPEN_KEY_PREFIX = "crossnote.sidebarTocOpen.";
  var restoring = false;

  function clampWidth(px) {
    var max = Math.max(MIN_WIDTH, window.innerWidth - 120);
    return Math.max(MIN_WIDTH, Math.min(px, max));
  }

  function setSidebarWidth(px) {
    var w = clampWidth(px);
    document.documentElement.style.setProperty("--sidebar-toc-width", w + "px");
    var el = document.querySelector(".md-sidebar-toc");
    if (el) {
      el.style.width = w + "px";
    }
    try {
      localStorage.setItem("crossnote.sidebarTocWidth", String(w));
    } catch (e) {}
    return w;
  }

  function seedWidthOnce() {
    var stored = null;
    try {
      stored = localStorage.getItem("crossnote.sidebarTocWidth");
    } catch (e) {}
    var n = Number(stored);
    if (stored && Number.isFinite(n) && !REPLACEABLE_WIDTHS[n]) {
      setSidebarWidth(n);
      return;
    }
    setSidebarWidth(TOC_WIDTH_PX);
  }

  function bindDrag() {
    var sidebar = document.querySelector(".md-sidebar-toc");
    if (!sidebar) {
      return;
    }
    var handle = sidebar.querySelector(".md-sidebar-toc-resize-handle");
    if (!handle || handle.__mpeDragBound) {
      return;
    }
    handle.__mpeDragBound = true;
    handle.addEventListener(
      "mousedown",
      function (e) {
        if (e.button !== 0) {
          return;
        }
        e.preventDefault();
        e.stopPropagation();
        if (e.stopImmediatePropagation) {
          e.stopImmediatePropagation();
        }
        var dragging = true;
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
        function move(ev) {
          if (!dragging) {
            return;
          }
          ev.preventDefault();
          setSidebarWidth(window.innerWidth - ev.clientX);
        }
        function up() {
          dragging = false;
          document.body.style.cursor = "";
          document.body.style.userSelect = "";
          document.removeEventListener("mousemove", move, true);
          document.removeEventListener("mouseup", up, true);
        }
        document.addEventListener("mousemove", move, true);
        document.addEventListener("mouseup", up, true);
      },
      true
    );
  }

  function isFirstLevel(details) {
    var summary = details.querySelector(":scope > summary.md-toc-link-wrapper");
    var level = summary && summary.getAttribute("data-level");
    if (level != null) {
      return level === "0";
    }
    var p = details.parentElement;
    while (p) {
      if (p.matches && p.matches("details.md-toc-details")) {
        return false;
      }
      p = p.parentElement;
    }
    return !!details.closest(".md-sidebar-toc");
  }

  function docKey() {
    var title = (document.title || "").trim();
    if (title) {
      return title;
    }
    return "default";
  }

  function storageKey() {
    return OPEN_KEY_PREFIX + docKey();
  }

  function detailsKey(details) {
    var a = details.querySelector(":scope > summary a.md-toc-link");
    var href = a && a.getAttribute("href");
    if (href) {
      return href;
    }
    var text = details.querySelector(":scope > summary");
    return (text && text.textContent ? text.textContent : "").trim();
  }

  function readSavedOpen() {
    try {
      var raw = localStorage.getItem(storageKey());
      if (!raw) {
        return null;
      }
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        return parsed;
      }
    } catch (e) {}
    return null;
  }

  function persistOpenState() {
    if (restoring) {
      return;
    }
    var items = document.querySelectorAll(
      ".md-sidebar-toc details.md-toc-details"
    );
    if (!items.length) {
      return;
    }
    var map = {};
    for (var i = 0; i < items.length; i++) {
      var key = detailsKey(items[i]);
      if (key) {
        map[key] = !!items[i].open;
      }
    }
    try {
      localStorage.setItem(storageKey(), JSON.stringify(map));
    } catch (e) {}
  }

  function bindToggle() {
    var sidebar = document.querySelector(".md-sidebar-toc");
    if (!sidebar || sidebar.__mpeToggleBound) {
      return;
    }
    sidebar.__mpeToggleBound = true;
    sidebar.addEventListener(
      "toggle",
      function (e) {
        var t = e.target;
        if (
          restoring ||
          !t ||
          !t.matches ||
          !t.matches("details.md-toc-details")
        ) {
          return;
        }
        persistOpenState();
      },
      true
    );
  }

  function applyLevel() {
    var items = document.querySelectorAll(
      ".md-sidebar-toc details.md-toc-details"
    );
    if (!items.length) {
      return;
    }
    var saved = readSavedOpen();
    restoring = true;
    try {
      for (var i = 0; i < items.length; i++) {
        var details = items[i];
        var key = detailsKey(details);
        if (saved && Object.prototype.hasOwnProperty.call(saved, key)) {
          details.open = !!saved[key];
        } else {
          details.open = isFirstLevel(details);
        }
      }
    } finally {
      restoring = false;
    }
  }

  function applyLevelSoon() {
    applyLevel();
    requestAnimationFrame(applyLevel);
    setTimeout(applyLevel, 50);
    setTimeout(applyLevel, 200);
  }

  function tocWasRebuilt(mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var m = mutations[i];
      if (m.type === "attributes" && m.attributeName === "class") {
        var t = m.target;
        if (t && t.classList && t.classList.contains("show-sidebar-toc")) {
          return true;
        }
      }
      var nodes = m.addedNodes;
      for (var j = 0; j < nodes.length; j++) {
        var n = nodes[j];
        if (n.nodeType !== 1) {
          continue;
        }
        if (
          (n.matches &&
            n.matches(
              "details.md-toc-details, .md-toc, .md-sidebar-toc, .md-sidebar-toc-resize-handle"
            )) ||
          (n.querySelector &&
            n.querySelector("details.md-toc-details, .md-sidebar-toc-resize-handle"))
        ) {
          return true;
        }
      }
    }
    return false;
  }

  function onTocChrome() {
    seedWidthOnce();
    bindDrag();
    bindToggle();
    applyLevelSoon();
  }

  onTocChrome();
  new MutationObserver(function (mutations) {
    if (tocWasRebuilt(mutations)) {
      bindDrag();
      bindToggle();
      applyLevelSoon();
    } else {
      bindDrag();
      bindToggle();
    }
  }).observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["class"]
  });
})();
