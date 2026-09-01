#!/usr/bin/env python3
"""Out of the Cave — site assembly.
Validates content pages, generates highschool.html + manifest.js,
and adds compiled-PDF links for any tex/*.pdf that exists.
"""
import html as htmllib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import html2tex  # noqa: E402  — reused for per-problem LaTeX export

ROOT = "/Users/bellum/claude-dir/hors-de-la-caverne"

PAGES = [
    ("pure-foundations.html", "Logique, théorie des ensembles et fondements"),
    ("pure-algebra.html", "Algèbre abstraite"),
    ("pure-linear-algebra.html", "Algèbre linéaire"),
    ("pure-number-theory.html", "Théorie des nombres"),
    ("pure-real-analysis.html", "Analyse réelle et théorie de la mesure"),
    ("pure-complex-analysis.html", "Analyse complexe"),
    ("pure-functional-analysis.html", "Analyse fonctionnelle"),
    ("pure-topology.html", "Topologie"),
    ("pure-geometry.html", "Géométrie"),
    ("pure-combinatorics.html", "Combinatoire et théorie des graphes"),
    ("pure-category-theory.html", "Théorie des catégories"),
    ("applied-calculus.html", "Calcul différentiel et intégral"),
    ("applied-probability.html", "Probabilités"),
    ("applied-statistics.html", "Statistique"),
    ("applied-ode.html", "Équations différentielles et systèmes dynamiques"),
    ("applied-pde.html", "Équations aux dérivées partielles"),
    ("applied-numerical.html", "Analyse numérique"),
    ("applied-optimization.html", "Optimisation et théorie des jeux"),
    ("applied-discrete-cs.html", "Mathématiques discrètes et informatique"),
    ("applied-crypto.html", "Cryptographie et théorie de l'information"),
    ("applied-physics.html", "Physique mathématique"),
    ("puzzles.html", "Casse-tête"),
    ("open-problems.html", "Problèmes ouverts"),
    ("proofs.html", "L'art de la démonstration"),
]

SEC_RE = re.compile(
    r'<section class="problem" id="([A-Za-z]+-\d+)"[^>]*data-level="([^"]+)"[^>]*>(.*?)</section>',
    re.S)
H3_RE = re.compile(r"<h3>.*?·\s*(.*?)\s*<span", re.S)
STMT_RE = re.compile(
    r'<p class="statement">(.*?)</p>|<div class="statement">(.*?)</div>', re.S)

catalogue = []   # one record per problem, for the worksheet builder

problems = []          # manifest entries
school = {"Collège": {}, "Lycée": {}}   # level -> filename -> sections
report = []

for fname, area in PAGES:
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        report.append(f"MISSING PAGE: {fname}")
        continue
    src = open(path, encoding="utf-8").read()
    issues = []
    if 'katex/katex.min.css' not in src: issues.append("no-katex")
    if 'site.js' not in src: issues.append("no-sitejs")
    if 'highschool.html' not in src: issues.append("no-hs-nav")
    if re.search(r'src="https?://', src) or re.search(r'href="https?://[^"]*\.(css)"', src):
        issues.append("external-asset?")
    secs = [(m.group(1), m.group(2), m.group(3), m.group(0)) for m in SEC_RE.finditer(src)]
    plain = len(re.findall(r'<section class="problem"', src))
    if plain != len(secs): issues.append(f"sections-without-data-level:{plain - len(secs)}")
    levels = {}
    for pid, level, body, whole in secs:
        levels[level] = levels.get(level, 0) + 1
        m = H3_RE.search(body)
        title = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip()) if m else pid
        opening = whole[:whole.index(">") + 1]
        entry = {"id": pid, "page": fname, "title": title,
                 "level": level, "area": area}
        short = 'data-kind="court"' in opening
        if short:
            entry["kind"] = "court"
        problems.append(entry)

        # Full record for the worksheet builder: rendered statement + LaTeX.
        sm = STMT_RE.search(body)
        stmt_html = (sm.group(1) or sm.group(2)).strip() if sm else ""
        try:
            tex = html2tex.convert_block(stmt_html)
            tex = re.sub(r"^\s*(\\noindent )?\\textbf\{Problem\.\}\s*", "", tex)
        except Exception:
            tex = ""
        rec = {"id": pid, "page": fname, "area": area, "level": level,
               "title": title, "html": stmt_html, "tex": tex}
        if short:
            rec["kind"] = "court"
        catalogue.append(rec)
        if level in ("Collège", "Lycée"):
            block = re.search(
                r'<section class="problem" id="' + re.escape(pid) + r'".*?</section>',
                src, re.S).group(0)
            note = (f'<p class="source-note">Extrait de '
                    f'<a href="{fname}#{pid}">{area}</a>.</p>')
            block = block.replace("</section>", note + "\n</section>")
            school[level].setdefault(fname, []).append(block)
    report.append(f"OK {fname}: {len(secs)} problems {levels}"
                  + (f"  ISSUES: {issues}" if issues else ""))

# ---- manifest.js ----
with open(os.path.join(ROOT, "manifest.js"), "w", encoding="utf-8") as f:
    f.write("// Generated. One entry per problem on the site.\nvar PROBLEMS = ")
    f.write(json.dumps(problems, ensure_ascii=False))
    f.write(";\n")

# ---- problems-data.js (worksheet builder: statement HTML + LaTeX) ----
with open(os.path.join(ROOT, "problems-data.js"), "w", encoding="utf-8") as f:
    f.write("// Generated. Full problem records for the worksheet builder.\n"
            "var PROBLEM_DATA = ")
    f.write(json.dumps(catalogue, ensure_ascii=False))
    f.write(";\n")

# ---- les deux salles : college.html et highschool.html ----
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# %-formatted so the page's own JavaScript braces need no escaping.
HUB_SHELL = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(h1)s — Hors de la Caverne</title>
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="katex/katex.min.css">
<script src="theme.js"></script>
<script defer src="katex/katex.min.js"></script>
<script defer src="katex/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false});"></script>
</head>
<body>
<nav>
<a href="index.html"><b>Hors de la Caverne</b></a> ·
<a href="college.html">Collège</a> ·
<a href="highschool.html">Lycée</a> ·
<a href="index.html#pure">Pures</a> ·
<a href="index.html#applied">Appliquées</a> ·
<a href="puzzles.html">Casse-tête</a> ·
<a href="open-problems.html">Problèmes ouverts</a> ·
<a href="proofs.html">L'art de la démonstration</a> ·
<a href="worksheet.html">Feuille d'exercices</a> ·
<a href="resources.html">Ressources</a>
<button id="theme-toggle" onclick="toggleTheme()" title="Basculer le thème clair/sombre">☀ / ☾</button>
</nav>
<hr>

<h1>%(h1)s</h1>
<p class="lede">%(lede)s</p>

<div class="filterbar" id="areabar">
<span>Domaines : </span>
<button data-area="all" class="active">Tous les domaines (%(total)d)</button>
%(buttons)s
<input type="search" id="hssearch" placeholder="rechercher parmi ces problèmes…">
<span class="count" id="hscount"></span>
</div>
<hr>

%(sections)s

<hr>
<footer>
<p><i>Hors de la Caverne</i> — des problèmes, pas de réponses.
Les références vous disent où se trouve la lumière ; la sortie, c'est à vous de la
marcher. <a href="index.html">Accueil</a></p>
</footer>
<script>
(function () {
  var pick = "all", query = "";
  var probs = Array.prototype.slice.call(document.querySelectorAll("section.problem"));
  var count = document.getElementById("hscount");
  function apply() {
    var shown = 0;
    document.querySelectorAll("div.area").forEach(function (d) {
      var areaOk = (pick === "all" || d.id === pick), any = false;
      d.querySelectorAll("section.problem").forEach(function (p) {
        var ok = areaOk &&
          (query === "" || p.textContent.toLowerCase().indexOf(query) !== -1);
        p.classList.toggle("hidden", !ok);
        if (ok) { any = true; shown++; }
      });
      d.classList.toggle("hidden", !any);
    });
    count.textContent = shown + " problème(s) sur " + probs.length;
  }
  document.querySelectorAll("#areabar button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#areabar button").forEach(function (x) {
        x.className = x === b ? "active" : "";
      });
      pick = b.dataset.area;
      apply();
    });
  });
  document.getElementById("hssearch").addEventListener("input", function (e) {
    query = e.target.value.toLowerCase();
    apply();
  });
  apply();
})();
</script>
</body>
</html>
"""

ROOMS = [
    ("Collège", "college.html", "La salle des collégiens",
     "Tous les problèmes du site marqués [Collège], rassemblés en un seul endroit — "
     "%(n)d au total. Rien n'y dépasse le programme du collège : fractions, "
     "divisibilité, aires, angles, dénombrement, hasard. En revanche, on y demande "
     "toujours de <b>justifier</b> — expliquer pourquoi c'est vrai, et pas seulement "
     "donner le résultat. C'est exactement ce que font les mathématiciens, en plus "
     "petit. Quand ceux-ci deviendront faciles, la "
     "<a href=\"highschool.html\">salle des lycéens</a> vous attend."),
    ("Lycée", "highschool.html", "La salle des lycéens",
     "Tous les problèmes du site marqués [Lycée], rassemblés en un seul endroit — "
     "%(n)d au total. Aucune connaissance au-delà des mathématiques du lycée n'est "
     "supposée ; en revanche, une démonstration complète est attendue partout. "
     "Choisissez les domaines qui vous appellent, ou parcourez-les tous. Chaque "
     "problème renvoie à sa page d'origine, où les niveaux plus difficiles du même "
     "sujet vous attendent. Vous débutez ? Passez d'abord par la "
     "<a href=\"college.html\">salle des collégiens</a>."),
]

room_totals = {}
for _level, _outfile, _h1, _lede_tpl in ROOMS:
    by_page = school[_level]
    areas = [(f, a) for f, a in PAGES if f in by_page]
    total = sum(len(v) for v in by_page.values())
    room_totals[_level] = total
    if not total:
        continue
    buttons = "\n".join(
        '<button data-area="area-%s">%s (%d)</button>'
        % (slug(a), htmllib.escape(a), len(by_page[f])) for f, a in areas)
    sections = "\n".join(
        '<div class="area" id="area-%s">\n<h2>%s</h2>\n%s\n</div>'
        % (slug(a), htmllib.escape(a), "\n".join(by_page[f])) for f, a in areas)
    hub = HUB_SHELL % dict(h1=_h1, lede=_lede_tpl % dict(n=total), total=total,
                           buttons=buttons, sections=sections)
    with open(os.path.join(ROOT, _outfile), "w", encoding="utf-8") as f:
        f.write(hub)

# ---- PDF links for compiled tex ----
patched = 0
for fname, _ in PAGES:
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path): continue
    base = fname[:-5]
    if not os.path.exists(os.path.join(ROOT, "tex", base + ".pdf")): continue
    src = open(path, encoding="utf-8").read()
    tex_link = f'<a href="tex/{base}.tex" download>LaTeX source</a>'
    pdf_link = f'<a href="tex/{base}.pdf" download>compiled PDF</a>'
    if pdf_link in src: continue
    if tex_link in src:
        src = src.replace(tex_link, tex_link + " · " + pdf_link)
        open(path, "w", encoding="utf-8").write(src)
        patched += 1
    else:
        report.append(f"NO-TEX-LINK: {fname}")

print("\n".join(report))
print("TOTAL problems: %d  College: %d  Lycee: %d  PDF links patched: %d"
      % (len(problems), room_totals.get("Coll\u00e8ge", 0),
         room_totals.get("Lyc\u00e9e", 0), patched))
