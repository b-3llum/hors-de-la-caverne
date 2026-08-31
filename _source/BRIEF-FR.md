# Hors de la Caverne — brief de traduction

You are translating the mathematics problem site **Out of the Cave** into French.
The French edition is called **Hors de la Caverne** (Plato's allegory is
*l'allégorie de la caverne*; "cave" in French means cellar, so "caverne" is correct).

Site root: `/Users/bellum/claude-dir/hors-de-la-caverne/`
The files there are **copies of the English site**. You translate them **in place**.

## The single most important rule

**Translate the text. Do not touch the structure.** After your edit the file must
have exactly the same number of `<section class="problem">` blocks, the same problem
IDs in the same order, the same nesting of tags, and the same LaTeX. If the English
page had 43 problems, the French page has the same 43 problems, translated.

Never drop a problem because it is hard to translate. Never merge or reorder them.

## What to translate

- The `<title>`, the `<h1>`, the `<p class="lede">`, every `<h2>`, every problem
  title in `<h3>`, every `<p class="statement">` / `<div class="statement">`
  (including `<li>` items inside `<ol class="parts">`), every `<p class="context">`,
  every `<li>` in `<ul class="refs">`, the "Où aller plus loin" section, and the
  footer.
- Reference labels: `Background:` → `Contexte :`, `Reading:` → `Lecture :`,
  `Course:` → `Cours :`, `Paper:` → `Article :`, `See also:` → `Voir aussi :`.
  (French typography: a thin space before `:` `;` `?` `!` — a normal space is fine.)
- Use French quotation marks « … » in prose where the English used “ … ”.

## What must NOT change

- **Problem IDs** (`NT-01`, `PUZ-42`, …) — identical, in `id=` and in the `<h3>`.
- **File names and internal links** (`pure-number-theory.html#NT-01`) — the URLs stay
  as they are. Only the link *text* is translated.
- **All LaTeX**, inside `\( … \)` and `\[ … \]` — mathematics is already universal.
  Do not translate variable names or operators. `\text{...}` inside math MAY be
  translated if it contains an English word.
- **External URLs**, except the Wikipedia rule below.
- The `<head>` block, `class` attributes, and the overall HTML skeleton.

## Mandatory substitutions

| English | French |
|---|---|
| `data-level="High School"` | `data-level="Lycée"` |
| `data-level="Undergraduate"` | `data-level="Licence"` |
| `data-level="Graduate"` | `data-level="Master"` |
| `data-level="Research"` | `data-level="Recherche"` |
| `<h2>High School</h2>` | `<h2>Lycée</h2>` (same for the other three) |
| `<span class="level">[High School]</span>` | `<span class="level">[Lycée]</span>` (etc.) |
| `data-kind="short"` | `data-kind="court"` |
| `<span class="kind">short</span>` | `<span class="kind">court</span>` |
| `<b>Problem.</b>` | `<b>Problème.</b>` |
| `<h2>Where to go deeper</h2>` | `<h2>Pour aller plus loin</h2>` |

`open-problems.html` uses thematic `<h2>` headings instead of level bands. Translate
them: "The Millennium Prize Problems" → « Les problèmes du prix du millénaire » ;
"Variations you can actually attack" → « Des variantes réellement abordables » ;
"The Collatz conjecture" → « La conjecture de Collatz » ; "Classic open problems" →
« Problèmes ouverts classiques » ; "Recently fallen" → « Récemment tombés ».

## The exact `<nav>` block (copy verbatim into every page)

```html
<nav>
<a href="index.html"><b>Hors de la Caverne</b></a> ·
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
```

Also set `<html lang="fr">`, and translate the downloads line to:
`<p class="downloads">Télécharger cette feuille de problèmes :
<a href="tex/NAME.tex" download>source LaTeX</a> · <a href="tex/NAME.pdf" download>PDF compilé</a></p>`

And the footer to:
```html
<footer>
<p><i>Hors de la Caverne</i> — des problèmes, pas de réponses.
Les références vous disent où se trouve la lumière ; la sortie, c'est à vous de la
marcher. <a href="index.html">Accueil</a></p>
</footer>
```

## Wikipedia links

Where a **French Wikipedia article exists** for the concept, switch the link to it
(`https://fr.wikipedia.org/wiki/...`) and translate the link text. **Verify the
French article exists** before switching — a quick check against
`https://fr.wikipedia.org/w/api.php?action=query&titles=TITLE&format=json` or a
fetch is enough. If there is no French article, **keep the English URL** and write
the link text in French with " (en anglais)" appended, e.g.
`<a href="https://en.wikipedia.org/wiki/Furstenberg_set">Ensemble de Furstenberg — Wikipédia (en anglais)</a>`.
Never invent a French URL you have not checked.

Books and papers keep their original titles (they are English works); describe them
in French around the title. Where a well-known French translation exists you may note
it, but do not invent one.

## Register and style

Serious, warm, plain — the same voice as the English. Use « vous ». Prefer natural
French mathematical vocabulary: *démonstration* (not "preuve" for a written proof),
*énoncé*, *entier naturel*, *corps*, *anneau*, *groupe*, *espace vectoriel*,
*application* (for a map), *suite*, *série*, *dénombrable*, *borné*, *dérivée*,
*intégrale*, *treillis*, *graphe*, *arête*, *sommet*, *aléatoire*, *espérance*,
*vraisemblance*, *conjecture*, *théorème*, *lemme*, *corollaire*.

Keep the history and provenance intact — names, dates and places are the soul of the
site. Translate the surrounding prose, not the facts.

**Never add a solution.** The site's rule is absolute: problems, no answers. If the
English hedges a status ("open", "not yet refereed", "disputed"), the French must
hedge it identically.

## When you are done

Verify before reporting: same problem count as the English original, same IDs, tags
balanced, `\(`/`\)` and `\[`/`\]` balanced, `data-kind="court"` count equals the
`<span class="kind">court</span>` count, no remaining English in visible text.
