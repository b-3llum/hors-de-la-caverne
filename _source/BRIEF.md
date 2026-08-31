# Out of the Cave — Contributor Brief

You are writing content for **Out of the Cave**, a plain-HTML website of mathematics
problems — an ode to Socrates and the allegory of the cave he narrates in Plato's
*Republic* (Book VII). The site's philosophy: **problems, not answers**. We give the
reader a precisely stated problem, the story of where it came from, and references
(Wikipedia, courses, books, papers) pointing to the knowledge needed to attack it.
We never give solutions. The emphasis is on proof-writing and on understanding how
mathematical ideas came about.

Site root: `/Users/bellum/claude-dir/out-of-the-cave/`
All HTML pages live flat in the root. LaTeX files live in `tex/`.

## Non-negotiable format rules

1. **Copy the page skeleton from `TEMPLATE.html` exactly** — same `<head>` (it now
   loads the locally bundled KaTeX and `site.js`), same `<nav>` block
   character-for-character (it now includes a High School link), same footer.
   Replace only titles, the lede, the tex filename, and the problem content. Do not
   add any other CSS, JS, fonts, or CDN links — KaTeX is served from the local
   `katex/` directory, never a CDN. Do NOT build a filter/search bar: `site.js`
   injects one automatically.
2. **Math notation in HTML**: real LaTeX, rendered client-side by KaTeX.
   Inline math in `\( ... \)`, display math in `\[ ... \]` — never `$` delimiters.
   Use only KaTeX-supported commands (standard amsmath: `\frac`, `\sum`, `\int`,
   `\mathbb{R}`, `\zeta`, `\pmod`, `\binom`, and `aligned`/`cases` environments
   inside display math). Prose stays plain HTML; formulas go in math delimiters.
   Simple standalone symbols in prose (π, ℝ) may stay Unicode. No MathJax.
3. **Problem sections**: each problem is a
   `<section class="problem" id="PREFIX-NN" data-level="LEVEL">` where `LEVEL` is
   exactly one of `High School`, `Undergraduate`, `Graduate`, `Research` (this
   drives the JS level filter and the High School hub page — it must match the
   `[Level]` tag in the title). Follow the template exactly: numbered title with
   level tag, a `<p class="statement">` beginning `<b>Problem.</b>` (statements are
   rendered in a bordered box — self-contained LaTeX, no reliance on surrounding
   text), a `<p class="context">` paragraph on history/provenance (who posed it,
   when, why it matters — this is the soul of the site), and a `<ul class="refs">`
   list.
4. **Levels**, in this order as `<h2>` bands: `High School`, `Undergraduate`,
   `Graduate`, `Research`. Omit a band only if it genuinely cannot exist for the
   field (e.g. functional analysis has no honest high-school band — then start at
   Undergraduate). Every page MUST end with a `Research` band containing real open
   or recently-resolved problems of the field, with status stated honestly.
5. **IDs**: zero-padded, sequential across the whole page (continue numbering across
   level bands): `NT-01, NT-02, …`.

## Reference rules (anti-hallucination — this is why you exist as a separate session)

- Every problem gets 1–4 reference lines. At least one `Background:` link to the
  canonical English Wikipedia article. Use real, canonical URLs
  (`https://en.wikipedia.org/wiki/Exact_Title`). If you are not certain an article
  exists under that title, verify with WebFetch/WebSearch or pick one you are sure of.
- `Reading:` standard, real textbooks only (author, title, chapter if you know it).
- `Course:` real courses — MIT OpenCourseWare numbers you are sure of, or other
  famous free courses (e.g. Harvard, Stanford online). Link to the OCW site.
- `Paper:` only papers you are certain exist. arXiv links only if you are confident
  of the identifier — otherwise give author, title, year, journal with no link.
  Inventing a reference is the one unforgivable sin here. When in doubt, verify on
  the web or leave it out.
- **Status accuracy**: open problems must be labeled open; solved ones solved, with
  solver and year. For anything that may have moved after 2020, do a quick web check
  before asserting status. Knowledge cutoff caution applies.

## Mathematical accuracy

- Statements must be mathematically correct and self-contained (define nonstandard
  terms inline). Prefer classical, well-established problems with real history.
- No solutions, no spoiler hints. "Prove that…" / "Show that…" / "Determine, with
  proof, …" phrasing.
- It is fine (encouraged) for a problem to be famous — the reader is here to think,
  not to be surprised.

## LaTeX files

For each HTML page, write `tex/<same-basename>.tex` containing the SAME problems
(same numbering, same level sections, references as a small itemized list after each
problem — URLs via `\url{}`). It must compile standalone with pdflatex/tectonic.
Use exactly this preamble:

```latex
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\newtheorem{problem}{Problem}
\newenvironment{refs}{\par\small\noindent\emph{References:}\begin{itemize}\setlength\itemsep{0pt}}{\end{itemize}\normalsize}
\title{Out of the Cave \\ \Large FIELD NAME}
\author{}
\date{}
```

Body: `\maketitle`, a one-line italic note "Problems, not answers.", then
`\section*{High School}` etc., each problem as
`\begin{problem}[Short title --- Level] ... \end{problem}` followed by a `refs`
environment. In the .tex, write real LaTeX math (`$\zeta(2)=\pi^2/6$` etc.).
Escape `%`, `&`, `#`, `_` in text. No packages beyond the preamble above.

## Tone

Plain, serious, warm. The lede of each page should orient a newcomer: what the field
studies, one or two sentences of history, what mastering it feels like. Cross-link
related pages in "See also". Deep treatments of the Millennium Prize Problems,
Collatz, Goldbach, etc. live on `open-problems.html` — field pages may include
field-specific open problems in their Research band and should link to
`open-problems.html` where they overlap. The Basel problem and the craft of proof
live on `proofs.html`.

## Round 2: expansion & formatting (current round)

The site exists and works. This round has three goals — apply them to YOUR
assigned pages only. Never touch `tex/`, `highschool.html`, or `manifest.js`
(all regenerated centrally), and never renumber or delete existing problems.

### A. Reformat existing statements for readability

Any statement that contains two or more tasks must be converted from a single
dense paragraph to this exact structure (a `<div>`, replacing the old
`<p class="statement">` — same class, no nested divs):

```html
<div class="statement">
<p><b>Problem.</b> Setup: definitions and given data, in one to three short sentences.</p>
<ol class="parts" type="a">
<li>First task.</li>
<li>Second task.</li>
</ol>
</div>
```

Also: promote any inline formula that is the heart of the problem to display
math `\[ ... \]` on its own line; break sentences longer than ~35 words; keep
single-task statements as a plain `<p class="statement">`. Do not change the
mathematical content, IDs, or level tags while reformatting.

### B. Add SHORT problems at every level

A short problem has a statement of at most two sentences — one clearly defined
task, quickly stated (not necessarily quickly solved). Mark it by adding
`data-kind="short"` to the section tag (attribute order: `id`, `data-level`,
`data-kind`) and a chip after the level span in the title:

```html
<section class="problem" id="XX-27" data-level="Undergraduate" data-kind="short">
<h3>XX-27 · Title <span class="level">[Undergraduate]</span> <span class="kind">short</span></h3>
```

Each level band on each page must gain at least TWO short problems. Short
problems still get a context paragraph (may be brief) and at least one
Background reference. The site's filter bar automatically gains a "Short only"
button — do not build one.

### C. Add full-length problems

Each page also gains at least FOUR new full-length problems that deepen
coverage — topics the page currently skips, placed in the right band. New
problems (short and full) are appended at the END of their level band,
continuing the page's ID numbering from the last existing number. All reference
rules above still apply; verify only what you are genuinely unsure of.

## What to return

When done, your final message must be raw data (not prose for a human): for each
file written — absolute path, problem count per level band, and a list of any
references you could not fully verify (empty list if none).
