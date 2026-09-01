// Hors de la Caverne — dynamique des pages : filtre par niveau et recherche.
// Volontairement court et sans dépendance.
document.addEventListener("DOMContentLoaded", function () {
  var problems = Array.prototype.slice.call(
    document.querySelectorAll("section.problem[data-level]"));
  if (problems.length < 2) return;

  var LEVELS = ["Collège", "Lycée", "Licence", "Master", "Recherche"];
  var activeLevel = "Tout";
  var query = "";
  var shortOnly = false;

  var bar = document.createElement("div");
  bar.className = "filterbar";
  var label = document.createElement("span");
  label.textContent = "Afficher : ";
  bar.appendChild(label);

  function makeButton(name) {
    var b = document.createElement("button");
    b.textContent = name;
    if (name === "Tout") b.className = "active";
    b.addEventListener("click", function () {
      activeLevel = name;
      Array.prototype.forEach.call(bar.querySelectorAll("button"), function (x) {
        x.className = x.textContent === name ? "active" : "";
      });
      apply();
    });
    return b;
  }
  bar.appendChild(makeButton("Tout"));
  LEVELS.forEach(function (l) {
    if (problems.some(function (p) { return p.dataset.level === l; })) {
      bar.appendChild(makeButton(l));
    }
  });

  if (problems.some(function (p) { return p.dataset.kind === "court"; })) {
    var sb = document.createElement("button");
    sb.textContent = "Courts seulement";
    sb.style.marginLeft = "0.6em";
    sb.addEventListener("click", function () {
      shortOnly = !shortOnly;
      sb.className = shortOnly ? "active" : "";
      apply();
    });
    bar.appendChild(sb);
  }

  var search = document.createElement("input");
  search.type = "search";
  search.placeholder = "rechercher un problème…";
  search.addEventListener("input", function () {
    query = search.value.toLowerCase();
    apply();
  });
  bar.appendChild(search);

  var count = document.createElement("span");
  count.className = "count";
  bar.appendChild(count);

  function apply() {
    var shown = 0;
    problems.forEach(function (p) {
      var ok = (activeLevel === "Tout" || p.dataset.level === activeLevel) &&
               (!shortOnly || p.dataset.kind === "court") &&
               (query === "" || p.textContent.toLowerCase().indexOf(query) !== -1);
      p.classList.toggle("hidden", !ok);
      if (ok) shown++;
    });
    count.textContent = shown + " problème" + (shown > 1 ? "s" : "") +
                        " sur " + problems.length;
    // Masquer les titres de bande dont tous les problèmes sont cachés.
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
  }

  var anchor = document.querySelector("p.downloads") ||
               document.querySelector("p.lede");
  if (anchor) anchor.parentNode.insertBefore(bar, anchor.nextSibling);

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

  problems.forEach(function (p) {
    var box = document.createElement("label");
    box.className = "pick";
    var cb = document.createElement("input");
    cb.type = "checkbox";
    cb.title = "Ajouter ce problème à votre feuille d'exercices";
    cb.checked = saved.indexOf(page + "#" + p.id) !== -1;
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
    '<button data-a="all">Sélectionner les problèmes affichés</button>' +
    '<button data-a="none">Effacer</button>' +
    '&nbsp;au hasard <input type="number" min="1" max="50" value="10">' +
    '<button data-a="rand">Tirer</button>' +
    '&nbsp;<button data-a="pdf"><b>Enregistrer la sélection en PDF</b></button>' +
    '<button data-a="tex">Télécharger le .tex</button>' +
    '<a href="worksheet.html">feuille d\'exercices &rarr;</a>';
  afterEl.parentNode.insertBefore(bar, afterEl.nextSibling);

  var count = bar.querySelector(".n");
  var num = bar.querySelector("input[type=number]");

  function sync() {
    var chosen = problems.filter(function (p) { return p._cb.checked; });
    count.textContent = chosen.length;
    var others = ootcSelection().filter(function (k) {
      return k.indexOf(page + "#") !== 0;
    });
    ootcSaveSelection(others.concat(chosen.map(function (p) {
      return page + "#" + p.id;
    })));
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
  var title = (document.querySelector("h1") || {}).textContent || "Problèmes";
  head.innerHTML = "<h1>Hors de la Caverne — " + title + "</h1>" +
    "<p>" + chosen.length + " problème" + (chosen.length > 1 ? "s" : "") +
    " sélectionné" + (chosen.length > 1 ? "s" : "") +
    ". Des problèmes, pas de réponses — les références indiquent où chercher.</p>";
  document.body.classList.add("print-selection");
  window.addEventListener("afterprint", function once() {
    document.body.classList.remove("print-selection");
    window.removeEventListener("afterprint", once);
  });
  window.print();
}
