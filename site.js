// Hors de la Caverne — dynamique des pages : filtre, recherche, sélection.
// Volontairement court et sans dépendance. Deux mises en page l'utilisent :
//   — les pages de domaine, où la barre de filtre (par niveau) est construite ici ;
//   — les deux salles, college.html et highschool.html, où assemble.py a déjà posé
//     une barre par domaine (#areabar) que l'on se contente de câbler.
// Une seule logique de filtrage sert les deux : rien à tenir synchronisé.

// ---- recherche : accents pliés, source LaTeX ignorée ----
function hdlcFold(s) {
  s = String(s);
  s = s.normalize ? s.normalize("NFD").replace(/[̀-ͯ]/g, "") : s;
  // Les noms composés s'écrivent avec un tiret demi-cadratin — Perron–Frobenius,
  // Cauchy–Schwarz — là où le clavier donne un trait d'union. On les confond.
  return s.replace(/[‐-―]/g, "-").toLowerCase();
}

function hdlcSearchText(p) {
  if (p._search === undefined) {
    // KaTeX écrit chaque formule deux fois : une branche MathML — qui porte en
    // plus la source LaTeX dans <annotation> — et une branche HTML visible.
    // Ne lire que la seconde évite de trouver « \frac » dans la page et de
    // compter trois fois le moindre \(n\).
    var c = p.cloneNode(true);
    Array.prototype.forEach.call(c.querySelectorAll(".katex-mathml"),
      function (e) { e.parentNode.removeChild(e); });
    p._search = hdlcFold(c.textContent.replace(/\s+/g, " "));
  }
  return p._search;
}

document.addEventListener("DOMContentLoaded", function () {
  var problems = Array.prototype.slice.call(
    document.querySelectorAll("section.problem[data-level]"));
  if (problems.length < 2) return;

  var LEVELS = ["Collège", "Lycée", "Licence", "Master", "Recherche"];
  var activeLevel = "Tout";
  var activeArea = "all";
  var query = "";
  var shortOnly = false;

  problems.forEach(function (p) {
    var a = p.closest && p.closest("div.area");
    p._area = a ? a.id : null;
  });

  function press(b, on) {
    b.className = on ? "active" : "";
    b.setAttribute("aria-pressed", on ? "true" : "false");
  }

  var roomBar = document.getElementById("areabar");   // salle : barre déjà posée
  var bar, search, count;

  if (roomBar) {
    bar = roomBar;
    var areaButtons = Array.prototype.slice.call(
      bar.querySelectorAll("button[data-area]"));
    areaButtons.forEach(function (b) {
      press(b, b.dataset.area === activeArea);
      b.addEventListener("click", function () {
        activeArea = b.dataset.area;
        areaButtons.forEach(function (x) { press(x, x === b); });
        apply();
      });
    });
    search = document.getElementById("hssearch");
    count = document.getElementById("hscount");
  } else {
    bar = document.createElement("div");
    bar.className = "filterbar";
    var label = document.createElement("span");
    label.textContent = "Afficher : ";
    bar.appendChild(label);

    var makeButton = function (name) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = name;
      press(b, name === "Tout");
      b.addEventListener("click", function () {
        activeLevel = name;
        Array.prototype.forEach.call(bar.querySelectorAll("button[data-level]"),
          function (x) { press(x, x === b); });
        apply();
      });
      b.dataset.level = name;
      return b;
    };
    bar.appendChild(makeButton("Tout"));
    LEVELS.forEach(function (l) {
      if (problems.some(function (p) { return p.dataset.level === l; })) {
        bar.appendChild(makeButton(l));
      }
    });

    search = document.createElement("input");
    search.type = "search";
    search.placeholder = "rechercher un problème…";
    search.setAttribute("aria-label", "Rechercher un problème");

    count = document.createElement("span");
    count.className = "count";
    count.setAttribute("aria-live", "polite");
  }

  // « Courts seulement » : commun aux deux mises en page.
  if (problems.some(function (p) { return p.dataset.kind === "court"; })) {
    var sb = document.createElement("button");
    sb.type = "button";
    sb.textContent = "Courts seulement";
    sb.style.marginLeft = "0.6em";
    press(sb, false);
    sb.addEventListener("click", function () {
      shortOnly = !shortOnly;
      press(sb, shortOnly);
      apply();
    });
    bar.insertBefore(sb, search.parentNode === bar ? search : null);
  }

  if (search.parentNode !== bar) bar.appendChild(search);
  if (count.parentNode !== bar) bar.appendChild(count);
  search.addEventListener("input", function () {
    query = hdlcFold(search.value).trim();
    apply();
  });

  var none = document.createElement("p");
  none.className = "noresult hidden";
  none.textContent = "Aucun problème ne correspond — essayez une autre " +
    "recherche, ou un autre filtre.";

  function apply() {
    var shown = 0;
    problems.forEach(function (p) {
      var ok = (activeLevel === "Tout" || p.dataset.level === activeLevel) &&
               (activeArea === "all" || p._area === activeArea) &&
               (!shortOnly || p.dataset.kind === "court") &&
               (query === "" || hdlcSearchText(p).indexOf(query) !== -1);
      p.classList.toggle("hidden", !ok);
      if (ok) shown++;
    });
    count.textContent = shown + " problème" + (shown > 1 ? "s" : "") +
                        " sur " + problems.length;
    none.classList.toggle("hidden", shown !== 0);
    // Masquer les bandes (salles) et les titres de bande (pages de domaine)
    // dont tous les problèmes sont cachés.
    Array.prototype.forEach.call(document.querySelectorAll("div.area"),
      function (d) {
        d.classList.toggle("hidden", !d.querySelector("section.problem:not(.hidden)"));
      });
    Array.prototype.forEach.call(document.querySelectorAll("h2"), function (h) {
      var el = h.nextElementSibling, any = false, relevant = false;
      while (el && el.tagName !== "H2" && el.tagName !== "HR") {
        if (el.classList && el.classList.contains("problem")) {
          relevant = true;
          if (!el.classList.contains("hidden")) any = true;
        }
        el = el.nextElementSibling;
      }
      if (relevant) h.classList.toggle("hidden", !any);
    });
    // Un problème réaffiché a pu n'être jamais mesuré : une formule trop large
    // pour sa colonne doit être reconnue avant de pousser la page de côté.
    if (window.hdlcRemeasureMath) hdlcRemeasureMath();
  }

  if (!bar.parentNode) {
    var anchor = document.querySelector("p.downloads") ||
                 document.querySelector("p.lede");
    if (anchor) anchor.parentNode.insertBefore(bar, anchor.nextSibling);
  }
  if (!bar.parentNode) return;      // ni chapô ni téléchargements : rien où ancrer
  bar.parentNode.insertBefore(none, bar.nextSibling);

  buildSelector(problems, bar, function () {
    return problems.filter(function (p) { return !p.classList.contains("hidden"); });
  });
  apply();
});

// ---- Choisir des problèmes, puis les imprimer ou les exporter en LaTeX. ----
function ootcSelection() {
  try { return JSON.parse(localStorage.getItem("hdlc-selection") || "[]"); }
  catch (e) { return []; }
}
function ootcSaveSelection(ids) {
  try { localStorage.setItem("hdlc-selection", JSON.stringify(ids)); } catch (e) {}
}

function buildSelector(problems, afterEl, visibleFn) {
  var page = location.pathname.split("/").pop() || "index.html";
  var saved = ootcSelection();

  // Dans une salle, chaque problème porte data-page : la page d'où il vient.
  // C'est cette clé-là que worksheet.html sait retrouver dans PROBLEM_DATA.
  function key(p) { return (p.dataset.page || page) + "#" + p.id; }

  problems.forEach(function (p) {
    var box = document.createElement("label");
    box.className = "pick";
    var cb = document.createElement("input");
    cb.type = "checkbox";
    cb.title = "Ajouter ce problème à votre feuille d'exercices";
    cb.setAttribute("aria-label", "Ajouter " + p.id + " à votre feuille d'exercices");
    cb.checked = saved.indexOf(key(p)) !== -1;
    if (cb.checked) p.classList.add("selected");
    cb.addEventListener("change", function () {
      p.classList.toggle("selected", cb.checked);
      sync();
    });
    box.appendChild(cb);
    var h = p.querySelector("h3");
    if (h) h.parentNode.insertBefore(box, h);
    p._cb = cb;
  });

  var bar = document.createElement("div");
  bar.className = "selbar";
  bar.innerHTML =
    '<span class="n">0</span> sélectionné(s) &nbsp;' +
    '<button type="button" data-a="all">Sélectionner les problèmes affichés</button>' +
    '<button type="button" data-a="none">Effacer</button>' +
    '&nbsp;au hasard <input type="number" min="1" max="50" value="10" ' +
    'aria-label="Nombre de problèmes à tirer au hasard">' +
    '<button type="button" data-a="rand">Tirer</button>' +
    '&nbsp;<button type="button" data-a="pdf"><b>Enregistrer la sélection en PDF</b></button>' +
    '<button type="button" data-a="tex">Télécharger le .tex</button>' +
    '<a href="worksheet.html">feuille d\'exercices &rarr;</a>';
  afterEl.parentNode.insertBefore(bar, afterEl.nextSibling);

  var count = bar.querySelector(".n");
  var num = bar.querySelector("input[type=number]");

  function sync() {
    var chosen = problems.filter(function (p) { return p._cb.checked; });
    count.textContent = chosen.length;
    var mine = {};
    problems.forEach(function (p) { mine[key(p)] = true; });
    var others = ootcSelection().filter(function (k) { return !mine[k]; });
    ootcSaveSelection(others.concat(chosen.map(key)));
  }

  function setAll(list, on) {
    list.forEach(function (p) {
      p._cb.checked = on;
      p.classList.toggle("selected", on);
    });
    sync();
  }

  bar.addEventListener("click", function (e) {
    var a = e.target.closest("button") && e.target.closest("button").dataset.a;
    if (!a) return;
    if (a === "all") setAll(visibleFn(), true);
    if (a === "none") setAll(problems, false);
    if (a === "rand") {
      setAll(problems, false);
      var pool = visibleFn().slice();
      var n = Math.min(parseInt(num.value, 10) || 10, pool.length);
      for (var i = pool.length - 1; i > 0; i--) {      // Fisher–Yates
        var j = Math.floor(Math.random() * (i + 1));
        var t = pool[i]; pool[i] = pool[j]; pool[j] = t;
      }
      setAll(pool.slice(0, n), true);
      if (pool.length) pool[0].scrollIntoView({ block: "center" });
    }
    if (a === "pdf") printSelection(problems);
    if (a === "tex") location.href = "worksheet.html#export";
  });

  sync();
}

// Marquer, avant impression, tout ce qui n'est pas sur le chemin d'un problème
// sélectionné. Passer par le DOM plutôt que par des sélecteurs CSS rend la règle
// indépendante de la structure : <main>, div.area, ou rien du tout.
function hdlcMarkForPrint(chosen) {
  var keep = [];
  chosen.forEach(function (p) {
    for (var el = p; el && el !== document.body; el = el.parentElement) {
      if (keep.indexOf(el) === -1) keep.push(el);
    }
  });
  // Cocher un problème puis changer de filtre le masque sans le décocher : il
  // doit malgré tout s'imprimer. `.hidden` vaut aussi sur papier, et posé sur une
  // div.area il emporterait la bande entière — on le lève le temps de l'impression.
  keep.forEach(function (el) {
    if (el.classList.contains("hidden")) {
      el.classList.remove("hidden");
      el.classList.add("print-unhidden");
    }
  });
  (function walk(root) {
    Array.prototype.forEach.call(root.children, function (el) {
      if (el.classList.contains("printhead")) return;
      if (keep.indexOf(el) !== -1) {
        if (!el.classList.contains("problem")) walk(el);
      } else {
        el.classList.add("print-hide");
      }
    });
  })(document.body);
}
function hdlcUnmarkPrint() {
  Array.prototype.forEach.call(document.querySelectorAll(".print-hide"),
    function (el) { el.classList.remove("print-hide"); });
  Array.prototype.forEach.call(document.querySelectorAll(".print-unhidden"),
    function (el) {
      el.classList.remove("print-unhidden");
      el.classList.add("hidden");
    });
}

function printSelection(problems) {
  var chosen = problems.filter(function (p) { return p._cb.checked; });
  if (!chosen.length) {
    alert("Cochez d'abord les problèmes voulus, ou utilisez « au hasard … Tirer ».");
    return;
  }
  var head = document.querySelector(".printhead");
  if (!head) {
    head = document.createElement("div");
    head.className = "printhead";
    document.body.insertBefore(head, document.body.firstChild);
  }
  // Le bandeau d'impression est réutilisé d'une impression à l'autre et ouvre le
  // corps de page : son propre <h1> serait repris, et le nom du site préfixé une
  // deuxième fois.
  var title = "Problèmes";
  Array.prototype.some.call(document.querySelectorAll("h1"), function (h) {
    if (h.closest(".printhead")) return false;
    title = h.textContent;
    return true;
  });
  head.innerHTML = "<h1>Hors de la Caverne — " + title + "</h1>" +
    "<p>" + chosen.length + " problème" + (chosen.length > 1 ? "s" : "") +
    " sélectionné" + (chosen.length > 1 ? "s" : "") +
    ". Des problèmes, pas de réponses — les références indiquent où chercher.</p>";
  hdlcMarkForPrint(chosen);
  document.body.classList.add("print-selection");
  window.addEventListener("afterprint", function once() {
    document.body.classList.remove("print-selection");
    hdlcUnmarkPrint();
    window.removeEventListener("afterprint", once);
  });
  window.print();
}
