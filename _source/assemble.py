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

ROOT = os.environ.get("HDLC_ROOT",
                     os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def validate(src):
    """Everything every page of the site must carry. Applied to the hand-written
    content pages *and* to the two rooms this script generates, so that a gap in
    the generator is caught the same way a gap in a page would be."""
    issues = []
    if "katex/katex.min.css" not in src: issues.append("no-katex")
    if "site.js" not in src: issues.append("no-sitejs")
    if "mathfit.js" not in src: issues.append("no-mathfit")
    if "highschool.html" not in src: issues.append("no-hs-nav")
    if 'name="description"' not in src: issues.append("no-description")
    if 'rel="icon"' not in src: issues.append("no-favicon")
    if "<main" not in src: issues.append("no-main")
    if 'class="skip"' not in src: issues.append("no-skip-link")
    if re.search(r'src="https?://', src) or re.search(r'href="https?://[^"]*\.(css)"', src):
        issues.append("external-asset?")
    return issues


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
    issues = validate(src)
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
        # Le titre passe lui aussi par html2tex : worksheet.js n'a pas de table
        # Unicode, et bien des titres portent des lettres grecques ou un « $ ».
        try:
            tex_title = html2tex.convert_inline(
                re.sub(r"<span.*?</span>", "", m.group(1), flags=re.S)) if m else pid
        except Exception:
            tex_title = ""
        rec = {"id": pid, "page": fname, "area": area, "level": level,
               "title": title, "tex_title": tex_title,
               "html": stmt_html, "tex": tex}
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
            # La salle doit dire d'où vient chaque problème : c'est cette clé-là
            # (page d'origine, pas la salle) que worksheet.html sait retrouver
            # dans PROBLEM_DATA. L'attribut est posé en fin de balise ouvrante
            # pour que les motifs `id="..." ... data-level="..."` continuent de
            # s'appliquer aux salles comme aux pages.
            block = block.replace(">", f' data-page="{fname}">', 1)
            school[level].setdefault(fname, []).append((pid, fname, block))
    report.append(f"OK {fname}: {len(secs)} problems {levels}"
                  + (f"  ISSUES: {issues}" if issues else ""))

# ---- les titres exportés en LaTeX ne doivent pas être échappés dans les maths ----
MATH_SPAN_RE = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.S)


def tex_escape_title(title):
    """Copie fidèle de texEscape() dans worksheet.js : n'échappe que la prose."""
    def esc(t):
        return re.sub(r"([%&#_$])", r"\\\1", t)
    out, pos = [], 0
    for m in MATH_SPAN_RE.finditer(title):
        out.append(esc(title[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(esc(title[pos:]))
    return "".join(out)


# `\_` (et `\%`, `\&`, `\#`) en mode mathématique ne compile pas : une feuille
# contenant un tel titre casserait tectonic. On le vérifie sur tout le site.
bad_titles = [r["id"] for r in catalogue
              if any(re.search(r"\\[%&#_$]", m.group(0))
                     for m in MATH_SPAN_RE.finditer(
                         r.get("tex_title") or tex_escape_title(r["title"])))]
if bad_titles:
    report.append("TEX-TITLE-ESCAPE (\\_ etc. inside math): " + " ".join(bad_titles))

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


def meta_description(lede_html, limit=155):
    """A <meta name="description"> drawn from the page's own lede."""
    text = htmllib.unescape(re.sub(r"<[^>]+>", "", lede_html))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit - 1].rsplit(" ", 1)[0] + "\u2026"
    return htmllib.escape(text, quote=True)


# %-formatted; the page carries no inline script of its own — site.js does the
# filtering here exactly as it does on a domain page.
HUB_SHELL = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(h1)s — Hors de la Caverne</title>
<meta name="description" content="%(desc)s">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="katex/katex.min.css">
<link rel="stylesheet" href="style.css">
<script src="theme.js"></script>
<script defer src="katex/katex.min.js"></script>
<script defer src="katex/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false});"></script>
<script defer src="mathfit.js"></script>
<script defer src="site.js"></script>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
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
<main id="contenu">

<h1>%(h1)s</h1>
<p class="lede">%(lede)s</p>
<p class="downloads">Télécharger cette feuille de problèmes :
<a href="tex/%(base)s.tex" download>source LaTeX</a></p>

<div class="filterbar" id="areabar">
<span>Domaines : </span>
<button type="button" data-area="all" class="active" aria-pressed="true">Tous les domaines (%(total)d)</button>
%(buttons)s
<input type="search" id="hssearch" aria-label="Rechercher parmi ces problèmes"
  placeholder="rechercher parmi ces problèmes…">
<span class="count" id="hscount" aria-live="polite"></span>
</div>
<hr>

%(sections)s

</main>
<hr>
<footer>
<p><i>Hors de la Caverne</i> — des problèmes, pas de réponses.
Les références vous disent où se trouve la lumière ; la sortie, c'est à vous de la
marcher. <a href="index.html">Accueil</a></p>
</footer>
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

ANCHOR_RE = re.compile(r'href="#([A-Za-z]+-\d+)"')

room_totals = {}
rehomed = 0
for _level, _outfile, _h1, _lede_tpl in ROOMS:
    by_page = school[_level]
    areas = [(f, a) for f, a in PAGES if f in by_page]
    total = sum(len(v) for v in by_page.values())
    # Un problème emporte ses renvois, écrits pour sa page d'origine. Dans la
    # salle la cible est le plus souvent absente et le lien ne mène nulle part :
    # on le fait pointer vers la page d'origine.
    in_room = {pid for v in by_page.values() for pid, _f, _b in v}

    def _rehome(block, home):
        global rehomed

        def one(m):
            global rehomed
            if m.group(1) in in_room:
                return m.group(0)
            rehomed += 1
            return f'href="{home}#{m.group(1)}"'

        return ANCHOR_RE.sub(one, block)

    by_page = {f: [_rehome(b, home) for _pid, home, b in v] for f, v in by_page.items()}
    room_totals[_level] = total
    if not total:
        continue
    buttons = "\n".join(
        '<button type="button" data-area="area-%s" aria-pressed="false">%s (%d)</button>'
        % (slug(a), htmllib.escape(a), len(by_page[f])) for f, a in areas)
    sections = "\n".join(
        '<div class="area" id="area-%s">\n<h2>%s</h2>\n%s\n</div>'
        % (slug(a), htmllib.escape(a), "\n".join(by_page[f])) for f, a in areas)
    lede = _lede_tpl % dict(n=total)
    hub = HUB_SHELL % dict(h1=_h1, lede=lede, desc=meta_description(lede),
                           total=total, buttons=buttons, sections=sections,
                           base=_outfile[:-5])
    # Le lien vers le PDF compilé, s'il a déjà été produit — sinon la boucle de
    # rattrapage plus bas le rajouterait à chaque exécution.
    if os.path.exists(os.path.join(ROOT, "tex", _outfile[:-5] + ".pdf")):
        tex_link = '<a href="tex/%s.tex" download>source LaTeX</a>' % _outfile[:-5]
        hub = hub.replace(
            tex_link,
            tex_link + ' · <a href="tex/%s.pdf" download>PDF compilé</a>' % _outfile[:-5], 1)
    with open(os.path.join(ROOT, _outfile), "w", encoding="utf-8") as f:
        f.write(hub)
    room_issues = validate(hub)
    report.append("OK %s: %d problems"
                  % (_outfile, len(re.findall(r'<section class="problem"', hub)))
                  + (f"  ISSUES: {room_issues}" if room_issues else ""))

# ---- PDF links for compiled tex ----
patched = 0
for fname in [p for p, _ in PAGES] + [r[1] for r in ROOMS]:
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path): continue
    base = fname[:-5]
    if not os.path.exists(os.path.join(ROOT, "tex", base + ".pdf")): continue
    src = open(path, encoding="utf-8").read()
    tex_link = f'<a href="tex/{base}.tex" download>source LaTeX</a>'
    pdf_link = f'<a href="tex/{base}.pdf" download>PDF compilé</a>'
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
