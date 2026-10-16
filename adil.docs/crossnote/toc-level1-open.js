(function () {
  if (window.__mpeSidebarToc350) {
    return;
  }
  window.__mpeSidebarToc350 = true;

  var TOC_WIDTH_PX = 350;
  var MIN_WIDTH = 200;
  var REPLACEABLE_WIDTHS = { 280: 1, 420: 1, 500: 1, 620: 1 };

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
    if (summary && summary.getAttribute("data-level") != null) {
      return summary.getAttribute("data-level") === "0";
    }
    var root = details.closest(".md-toc");
    return !!(root && details.parentElement === root);
  }

  function applyLevel() {
    var items = document.querySelectorAll(".md-sidebar-toc details.md-toc-details");
    for (var i = 0; i < items.length; i++) {
      items[i].open = isFirstLevel(items[i]);
    }
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
    applyLevel();
  }

  onTocChrome();
  new MutationObserver(function (mutations) {
    if (tocWasRebuilt(mutations)) {
      bindDrag();
      applyLevel();
    } else {
      bindDrag();
    }
  }).observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["class"]
  });
})();
