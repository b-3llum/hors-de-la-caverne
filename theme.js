// Light/dark mode. Runs in <head> so the page never flashes the wrong theme.
(function () {
  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  if (saved === "dark" ||
      (!saved && window.matchMedia &&
       window.matchMedia("(prefers-color-scheme: dark)").matches)) {
    document.documentElement.setAttribute("data-theme", "dark");
  }
})();
function toggleTheme() {
  var root = document.documentElement;
  if (root.getAttribute("data-theme") === "dark") {
    root.removeAttribute("data-theme");
    try { localStorage.setItem("theme", "light"); } catch (e) {}
  } else {
    root.setAttribute("data-theme", "dark");
    try { localStorage.setItem("theme", "dark"); } catch (e) {}
  }
}
