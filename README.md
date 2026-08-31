# Hors de la Caverne

https://b-3llum.github.io/hors-de-la-caverne/

Un recueil de problèmes de mathématiques en HTML simple — **des problèmes, pas de
réponses**.

Un hommage à Socrate et à l'allégorie de la caverne racontée dans *La République* de
Platon, livre VII : les prisonniers prennent des ombres pour le monde, et la sortie
ne consiste pas à se faire dire ce qui est réel, mais à marcher soi-même vers la
lumière. Chaque problème est accompagné de son histoire — qui l'a posé, quand, et
pourquoi il a compté — et de références indiquant le savoir nécessaire pour
l'attaquer. Aucune solution n'est donnée, nulle part, jamais.

Version française de [Out of the Cave](https://b-3llum.github.io/out-of-the-cave/).

## Ce que contient le site

**1 164 problèmes** dans 24 domaines, du lycée à la recherche ouverte :

| Niveau | Problèmes |
|---|---|
| Lycée | 234 |
| Licence | 383 |
| Master | 312 |
| Recherche | 235 |

Mathématiques pures (fondements, algèbre, algèbre linéaire, théorie des nombres,
analyse réelle et complexe, analyse fonctionnelle, topologie, géométrie,
combinatoire, théorie des catégories) et appliquées (calcul différentiel et
intégral, probabilités, statistique, équations différentielles ordinaires et aux
dérivées partielles, analyse numérique, optimisation, mathématiques discrètes et
informatique, cryptographie et théorie de l'information, physique mathématique),
ainsi que trois collections spéciales :

- **[Casse-tête](puzzles.html)** — 100 énigmes dont la chute est un véritable théorème.
- **[Problèmes ouverts](open-problems.html)** — les problèmes du prix du millénaire
  avec des variantes réellement abordables, une section approfondie sur la conjecture
  de Collatz, les grands problèmes ouverts classiques, et les murs récemment tombés.
- **[L'art de la démonstration](proofs.html)** — le métier lui-même, des exercices de
  technique au problème de Bâle et à l'infinité des nombres premiers.

## Fonctionnalités

- **Niveaux et filtrage.** Chaque problème porte une étiquette Lycée / Licence /
  Master / Recherche. Chaque page dispose d'un filtre par niveau, d'une recherche en
  direct et d'un bouton « Courts seulement » (309 problèmes sont de forme courte).
- **La salle des lycéens.** Les 234 problèmes de niveau lycée rassemblés en un seul
  endroit, sélectionnables par domaine.
- **Composeur de feuilles d'exercices.** Cochez des problèmes en parcourant le site,
  ou tirez un ensemble au hasard par niveau et par domaine, puis enregistrez-les
  seuls en PDF ou téléchargez-les en LaTeX compilable.
- **De vraies mathématiques composées.** KaTeX, embarqué localement — aucun CDN, le
  site fonctionne hors ligne.
- **Téléchargements.** Chaque page propose sa feuille de problèmes en source LaTeX et
  en PDF compilé.
- **Thème clair et sombre**, et une présentation volontairement sobre.

## Comment le site est construit

Uniquement des fichiers statiques. Aucune étape de compilation n'est nécessaire pour
servir le site : ouvrez `index.html` ou pointez n'importe quel serveur web vers ce
répertoire.

Le répertoire `_source/` contient la chaîne de production :

| Script | Rôle |
|---|---|
| `html2tex.py` | Engendre `tex/*.tex` à partir des pages HTML. Le LaTeX est toujours dérivé — jamais écrit à la main. |
| `assemble.py` | Valide chaque page, engendre `highschool.html`, `manifest.js` et `problems-data.js`, et insère les liens de téléchargement des PDF. |
| `insert.py` / `merge_round.py` | Insèrent de nouveaux blocs de problèmes à la fin de la bonne bande de niveau, avec validation. |
| `reformat.py` | Convertit les énoncés d'un seul paragraphe en une mise en place suivie d'une liste de questions. |
| `linkcheck2.sh` | Vérificateur de liens externes en parallèle. |

`BRIEF.md` est le brief de rédaction (style de la maison, structure HTML d'un
problème, règles de référencement) ; `BRIEF-FR.md` est le brief de traduction.

Reconstruire après modification d'une page :

```sh
python3 _source/html2tex.py <page>.html      # régénérer le LaTeX
cd tex && tectonic -X compile --outfmt pdf <page>.tex && cd ..
python3 _source/assemble.py                  # reconstruire la salle, le manifeste, les données
./_source/linkcheck2.sh                      # vérifier tous les liens externes
```

Les PDF se compilent avec [tectonic](https://tectonic-typesetting.github.io/) ;
`pdflatex` et `xelatex` fonctionnent également.

## À propos des références

Chaque problème porte des références, et elles sont vérifiées plutôt que supposées.
Les liens pointent vers Wikipédia en français lorsque l'article existe ; sinon
l'article anglais est conservé et signalé par « (en anglais) ». Aucune URL française
n'a été inventée.

Lorsqu'une affirmation porte sur des travaux récents, son statut réel est indiqué —
démontré, contesté, ou prépublication non expertisée — plutôt qu'aplati en
« résolu ».

## Licence

Les énoncés sont, à de rares exceptions près, des mathématiques classiques dans le
domaine public ; la rédaction, la sélection et l'agencement appartiennent à ce
projet. KaTeX est embarqué sous sa propre licence MIT (voir `katex/`).
