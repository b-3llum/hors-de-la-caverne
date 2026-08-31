// Hors de la Caverne — générateur de feuilles d'exercices.
// Choisit un ensemble de problèmes et l'exporte en page imprimable (Enregistrer en
// PDF) ou en LaTeX compilable. Tout se fait localement : aucun réseau, aucune
// bibliothèque externe.
(function () {
  var chosen = [];      // tableau d'enregistrements PROBLEM_DATA

  function $(id) { return document.getElementById(id); }

  function levels() {
    return Array.prototype.filter
      .call(document.querySelectorAll(".lv"), function (c) { return c.checked; })
      .map(function (c) { return c.value; });
  }
  function areasWanted() {
    return Array.prototype.filter
      .call(document.querySelectorAll(".ar"), function (c) { return c.checked; })
      .map(function (c) { return c.value; });
  }
  function kind() {
    var r = document.querySelector('input[name="kind"]:checked');
    return r ? r.value : "any";
  }

  function pool() {
    var lv = levels(), ar = areasWanted(), kd = kind();
    return PROBLEM_DATA.filter(function (p) {
      if (lv.indexOf(p.level) === -1) return false;
      if (ar.length && ar.indexOf(p.area) === -1) return false;
      if (kd === "short" && p.kind !== "court") return false;
      if (kd === "long" && p.kind === "court") return false;
      return true;
    });
  }

  function showPool() {
    var n = pool().length;
    $("pool").textContent = n + " problème" + (n > 1 ? "s" : "") +
      " correspond" + (n > 1 ? "ent" : "") + " à vos filtres (sur " +
      PROBLEM_DATA.length + " au total).";
  }

  function render() {
    var out = $("out");
    if (!chosen.length) {
      out.innerHTML = '<p class="source-note">Rien de sélectionné pour l\'instant. ' +
        'Tirez un ensemble au hasard ci-dessus, ou cochez des problèmes en parcourant ' +
        'le site et revenez ici.</p>';
      return;
    }
    var head = '<div class="printhead"><h1>Hors de la Caverne — feuille d\'exercices</h1>' +
      "<p>" + chosen.length + " problème" + (chosen.length > 1 ? "s" : "") +
      ". Des problèmes, pas de réponses — les références indiquent où chercher.</p></div>";
    var body = chosen.map(function (p, i) {
      return '<section class="problem" data-level="' + p.level + '">' +
        "<h3>" + (i + 1) + ". " + p.title +
        ' <span class="level">[' + p.level + "]</span>" +
        (p.kind === "court" ? ' <span class="kind">court</span>' : "") + "</h3>" +
        '<div class="statement">' + p.html + "</div>" +
        '<p class="source-note">' + p.id + " — extrait de <a href=\"" + p.page + "#" +
        p.id + '">' + p.area + "</a></p></section>";
    }).join("\n");
    out.innerHTML = head + '<h2 class="screen-only">Votre feuille (' +
      chosen.length + ")</h2>" + body;
    if (window.renderMathInElement) {
      renderMathInElement(out, {
        delimiters: [{ left: "\\[", right: "\\]", display: true },
                     { left: "\\(", right: "\\)", display: false }],
        throwOnError: false
      });
    }
  }

  function draw() {
    var p = pool().slice();
    for (var i = p.length - 1; i > 0; i--) {          // mélange de Fisher–Yates
      var j = Math.floor(Math.random() * (i + 1));
      var t = p[i]; p[i] = p[j]; p[j] = t;
    }
    var n = Math.min(parseInt($("count").value, 10) || 10, p.length);
    chosen = p.slice(0, n).sort(function (a, b) {
      var order = ["Lycée", "Licence", "Master", "Recherche"];
      return order.indexOf(a.level) - order.indexOf(b.level) ||
             a.area.localeCompare(b.area);
    });
    render();
  }

  function loadTicked() {
    var keys;
    try { keys = JSON.parse(localStorage.getItem("hdlc-selection") || "[]"); }
    catch (e) { keys = []; }
    var want = {};
    keys.forEach(function (k) { want[k] = true; });
    chosen = PROBLEM_DATA.filter(function (p) { return want[p.page + "#" + p.id]; });
    if (!chosen.length) {
      alert("Vous n'avez encore coché aucun problème.\n\nEn parcourant une page de " +
            "problèmes, utilisez la case à cocher d'un problème pour l'ajouter ici.");
    }
    render();
  }

  var PREAMBLE = [
    "\\documentclass[11pt]{article}",
    "\\usepackage[margin=1in]{geometry}",
    "\\usepackage[T1]{fontenc}",
    "\\usepackage[french]{babel}",
    "\\usepackage{amsmath,amssymb,amsthm}",
    "\\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}",
    "\\newtheorem{problem}{Problème}",
    "\\title{Hors de la Caverne \\\\ \\Large Feuille d'exercices}",
    "\\author{}",
    "\\date{}",
    "\\begin{document}",
    "\\maketitle",
    "\\noindent\\emph{Des problèmes, pas de réponses.} Aucune solution n'est incluse.",
    "\\medskip",
    ""
  ].join("\n");

  function texEscape(s) {
    return String(s).replace(/([%&#_])/g, "\\$1");
  }

  function downloadTex() {
    if (!chosen.length) { alert("Sélectionnez d'abord des problèmes."); return; }
    var parts = [PREAMBLE];
    chosen.forEach(function (p) {
      parts.push("\\begin{problem}[{" + texEscape(p.title) + " --- " +
                 texEscape(p.level) + "}]\n" + (p.tex || "") + "\n\\end{problem}");
      parts.push("\\noindent\\footnotesize " + texEscape(p.id) +
                 " --- extrait de " + texEscape(p.area) +
                 ", \\emph{Hors de la Caverne}.\\normalsize\n\n\\bigskip\n");
    });
    parts.push("\\vfill\n\\noindent\\emph{Hors de la Caverne} --- des problèmes, " +
               "pas de réponses.\n\\end{document}\n");
    var blob = new Blob([parts.join("\n")], { type: "text/x-tex;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "hors-de-la-caverne-feuille.tex";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof PROBLEM_DATA === "undefined") return;

    var seen = [], html = "";
    PROBLEM_DATA.forEach(function (p) {
      if (seen.indexOf(p.area) === -1) seen.push(p.area);
    });
    seen.forEach(function (a) {
      html += '<label><input type="checkbox" class="ar" value="' +
        a.replace(/"/g, "&quot;") + '"> ' + a + "</label> ";
    });
    $("areas").innerHTML = html;

    document.querySelectorAll(".lv, .ar, input[name=kind]").forEach(function (c) {
      c.addEventListener("change", showPool);
    });
    $("draw").addEventListener("click", draw);
    $("loadticked").addEventListener("click", loadTicked);
    $("clear").addEventListener("click", function () { chosen = []; render(); });
    $("pdf").addEventListener("click", function () {
      if (!chosen.length) { alert("Sélectionnez d'abord des problèmes."); return; }
      window.print();
    });
    $("tex").addEventListener("click", downloadTex);

    showPool();
    if (location.hash === "#export") loadTicked(); else render();
  });
})();
