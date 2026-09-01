// Light/dark mode. Runs in <head> so the page never flashes the wrong theme.
(function () {
  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  var mq = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
  if (saved === "dark" || (!saved && mq && mq.matches)) {
    document.documentElement.setAttribute("data-theme", "dark");
  }
  paintThemeColor();

  // Sans choix explicite enregistré, suivre le système même s'il bascule en
  // cours de lecture (mode nuit automatique, par exemple).
  if (mq && mq.addEventListener) {
    mq.addEventListener("change", function (e) {
      var pref = null;
      try { pref = localStorage.getItem("theme"); } catch (err) {}
      if (pref) return;
      if (e.matches) document.documentElement.setAttribute("data-theme", "dark");
      else document.documentElement.removeAttribute("data-theme");
      paintThemeColor();
    });
  }
})();

// La barre d'adresse du navigateur prend la couleur de fond de la page.
function paintThemeColor() {
  var dark = document.documentElement.getAttribute("data-theme") === "dark";
  var m = document.querySelector('meta[name="theme-color"]');
  if (!m) {
    m = document.createElement("meta");
    m.setAttribute("name", "theme-color");
    document.head.appendChild(m);
  }
  m.setAttribute("content", dark ? "#14161a" : "#ffffff");
}

function toggleTheme() {
  var root = document.documentElement;
  if (root.getAttribute("data-theme") === "dark") {
    root.removeAttribute("data-theme");
    try { localStorage.setItem("theme", "light"); } catch (e) {}
  } else {
    root.setAttribute("data-theme", "dark");
    try { localStorage.setItem("theme", "dark"); } catch (e) {}
  }
  paintThemeColor();
}
