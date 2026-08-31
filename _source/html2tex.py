#!/usr/bin/env python3
"""Generate tex/<page>.tex from each Out of the Cave HTML problem page.

The HTML already carries real LaTeX inside \\( ... \\) and \\[ ... \\], so this is a
faithful structural conversion: same problems, same numbering, same references.
"""
import html as htmllib
import unicodedata as _unicodedata
import os
import re
import sys

ROOT = "/Users/bellum/claude-dir/hors-de-la-caverne"
TEX = os.path.join(ROOT, "tex")

# Unicode that may appear in prose -> LaTeX (text mode).
UNI = {
    "—": "---", "–": "--", "’": "'", "‘": "`", "“": "``", "”": "''",
    "·": "$\\cdot$", "…": "\\dots{}", "×": "$\\times$", "±": "$\\pm$",
    "≤": "$\\le$", "≥": "$\\ge$", "≠": "$\\ne$", "≡": "$\\equiv$",
    "→": "$\\to$", "↦": "$\\mapsto$", "⇒": "$\\Rightarrow$", "⟹": "$\\implies$",
    "∈": "$\\in$", "∉": "$\\notin$", "⊂": "$\\subset$", "⊆": "$\\subseteq$",
    "∪": "$\\cup$", "∩": "$\\cap$", "∅": "$\\emptyset$", "∂": "$\\partial$",
    "∇": "$\\nabla$", "⋅": "$\\cdot$", "∞": "$\\infty$", "√": "$\\sqrt{\\ }$",
    "∑": "$\\sum$", "∏": "$\\prod$", "∫": "$\\int$", "≈": "$\\approx$",
    "∼": "$\\sim$", "∀": "$\\forall$", "∃": "$\\exists$", "¬": "$\\neg$",
    "∧": "$\\wedge$", "∨": "$\\vee$", "⟨": "$\\langle$", "⟩": "$\\rangle$",
    "‖": "$\\|$", "°": "$^\\circ$", "′": "$'$", "″": "$''$",
    "α": "$\\alpha$", "β": "$\\beta$", "γ": "$\\gamma$", "δ": "$\\delta$",
    "ε": "$\\varepsilon$", "ζ": "$\\zeta$", "η": "$\\eta$", "θ": "$\\theta$",
    "κ": "$\\kappa$", "λ": "$\\lambda$", "μ": "$\\mu$", "ν": "$\\nu$",
    "ξ": "$\\xi$", "π": "$\\pi$", "ρ": "$\\rho$", "σ": "$\\sigma$",
    "τ": "$\\tau$", "φ": "$\\varphi$", "χ": "$\\chi$", "ψ": "$\\psi$",
    "ω": "$\\omega$", "Γ": "$\\Gamma$", "Δ": "$\\Delta$", "Θ": "$\\Theta$",
    "Λ": "$\\Lambda$", "Σ": "$\\Sigma$", "Φ": "$\\Phi$", "Ψ": "$\\Psi$",
    "Ω": "$\\Omega$", "ℝ": "$\\mathbb{R}$", "ℤ": "$\\mathbb{Z}$",
    "ℚ": "$\\mathbb{Q}$", "ℂ": "$\\mathbb{C}$", "ℕ": "$\\mathbb{N}$",
    "ℵ": "$\\aleph$", "ℓ": "$\\ell$", "√": "$\\surd$", "∎": "",
    "½": "$\\tfrac12$", "¼": "$\\tfrac14$", "¾": "$\\tfrac34$",
    "²": "$^2$", "³": "$^3$", "⁴": "$^4$", "₁": "$_1$", "₂": "$_2$", "₃": "$_3$",
    "ö": '\\"o', "ü": '\\"u', "ä": '\\"a', "é": "\\'e", "è": "\\`e",
    "á": "\\'a", "í": "\\'i", "ó": "\\'o", "ú": "\\'u", "ñ": "\\~n",
    "ç": "\\c{c}", "ø": "\\o{}", "å": "\\aa{}", "Ö": '\\"O', "É": "\\'E",
    "Ł": "\\L{}", "ł": "\\l{}", "š": "\\v{s}", "č": "\\v{c}", "ř": "\\v{r}",
    "ż": "\\.z", "ą": "\\k{a}", "ę": "\\k{e}", "\u00a0": "~", "\u2009": "\\,",
    "\u200b": "", "\ufeff": "",
}

UNI.update({
    "ô": "\\^o", "î": "\\^i", "ā": "\\=a", "ī": "\\={\\i}", "ı": "\\i{}",
    "ő": "\\H{o}", "ű": "\\H{u}", "ń": "\\'n", "ß": "\\ss{}", "Ü": '\\"U',
    "§": "\\S{}", "−": "$-$", "⊣": "$\\dashv$", "⇔": "$\\Leftrightarrow$",
    "⊗": "$\\otimes$", "⊕": "$\\oplus$", "≅": "$\\cong$", "≪": "$\\ll$",
    "≫": "$\\gg$", "⌊": "$\\lfloor$", "⌋": "$\\rfloor$", "⌈": "$\\lceil$",
    "⌉": "$\\rceil$", "†": "$\\dagger$", "∘": "$\\circ$", "∝": "$\\propto$",
    "ç": "\\c{c}", "Å": "\\AA{}", "æ": "\\ae{}", "Ø": "\\O{}",
    "ý": "\\'y", "ă": "\\u{a}", "ň": "\\v{n}", "ş": "\\c{s}", "ů": "\\r{u}",
    "ě": "\\v{e}", "ž": "\\v{z}", "ť": "\\v{t}", "ď": "\\v{d}", "ĺ": "\\'l",
    "ő": "\\H{o}", "â": "\\^a", "û": "\\^u", "ê": "\\^e", "ï": '\\"i',
    "İ": "\\.I", "ğ": "\\u{g}", "Ç": "\\c{C}", "Š": "\\v{S}", "Ž": "\\v{Z}",
    "à": "\\`a", "Č": "\\v{C}", "ś": "\\'s", "ć": "\\'c", "ù": "\\`u",
    "ò": "\\`o", "ì": "\\`i", "É": "\\'E", "Á": "\\'A", "Ó": "\\'O",
    "ã": "\\~a", "õ": "\\~o", "ǎ": "\\v{a}", "ǐ": "\\v{\\i}", "ǒ": "\\v{o}", "ǔ": "\\v{u}", "ū": "\\=u",
})

SPECIAL = {"%": "\\%", "&": "\\&", "#": "\\#", "_": "\\_", "$": "\\$"}


# Édition française : les lettres accentuées restent en UTF-8 (inputenc/XeTeX les
# gèrent). Seuls les symboles mathématiques et typographiques passent en LaTeX.
for _k in [k for k in list(UNI)
           if len(k) == 1 and _unicodedata.category(k).startswith("L")
           and "LATIN" in _unicodedata.name(k, "")
           and not UNI[k].startswith("$")]:
    del UNI[_k]
UNI["\u00ab"] = "\\og{}"
UNI["\u00bb"] = "\\fg{}"
UNI["\u202f"] = "~"

def esc_text(s):
    """Escape a run of plain prose (no math, no markup) for LaTeX."""
    out = []
    for ch in s:
        if ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ch in UNI:
            out.append(UNI[ch])
        elif ch in "{}":
            out.append("\\" + ch)
        elif ch == "^":
            out.append("\\textasciicircum{}")
        elif ch == "~":
            out.append("\\textasciitilde{}")
        elif ch == "\\":
            out.append("\\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


MATH_RE = re.compile(r"(\\\(.*?\\\)|\\\[.*?\\\])", re.S)


def convert_inline(frag):
    """Convert an HTML fragment (prose + markup + LaTeX math) to LaTeX."""
    # Markup -> placeholders that survive escaping.
    frag = re.sub(r"<b>(.*?)</b>", lambda m: "\x01textbf\x02" + m.group(1) + "\x03", frag, flags=re.S)
    frag = re.sub(r"<strong>(.*?)</strong>", lambda m: "\x01textbf\x02" + m.group(1) + "\x03", frag, flags=re.S)
    frag = re.sub(r"<i>(.*?)</i>", lambda m: "\x01textit\x02" + m.group(1) + "\x03", frag, flags=re.S)
    frag = re.sub(r"<em>(.*?)</em>", lambda m: "\x01emph\x02" + m.group(1) + "\x03", frag, flags=re.S)
    frag = re.sub(r"<code>(.*?)</code>", lambda m: "\x01texttt\x02" + m.group(1) + "\x03", frag, flags=re.S)
    # Links: keep text, show URL.
    def link(m):
        url, text = m.group(1), m.group(2)
        text = re.sub(r"<[^>]+>", "", text)
        return "\x01href\x02" + url + "\x04" + text + "\x03"
    frag = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', link, frag, flags=re.S)
    frag = re.sub(r"<br\s*/?>", " ", frag)
    frag = re.sub(r"<[^>]+>", "", frag)          # drop any remaining tags
    frag = htmllib.unescape(frag)

    # Escape prose but leave math intact.
    parts = MATH_RE.split(frag)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            inner = p[2:-2]
            out.append("$" + inner + "$" if p.startswith("\\(") else "\\[" + inner + "\\]")
        else:
            out.append(esc_text(p))
    s = "".join(out)

    # Restore markup placeholders.
    s = re.sub(r"\x01href\x02(.*?)\x04(.*?)\x03",
               lambda m: m.group(2) + " (\\url{" + m.group(1).replace("\\%", "%").replace("\\#", "#").replace("\\_", "_").replace("\\&", "&") + "})",
               s, flags=re.S)
    s = re.sub(r"\x01(\w+)\x02(.*?)\x03", lambda m: "\\" + m.group(1) + "{" + m.group(2) + "}", s, flags=re.S)
    # KaTeX-only spellings that plain LaTeX does not define. Match the control
    # word itself, however it is followed (space, \;, {}, punctuation).
    s = re.sub(r"\\gt(?![a-zA-Z])\s*(?:\{\})?", ">", s)
    s = re.sub(r"\\lt(?![a-zA-Z])\s*(?:\{\})?", "<", s)
    return re.sub(r"[ \t]+", " ", s).strip()


PROB_RE = re.compile(
    r'<section class="problem" id="([^"]+)"[^>]*data-level="([^"]+)"[^>]*>(.*?)</section>', re.S)
KIND_RE = re.compile(r'data-kind="([^"]+)"')
H3_RE = re.compile(r"<h3>(.*?)</h3>", re.S)
STMT_RE = re.compile(
    r'<p class="statement">(.*?)</p>|<div class="statement">(.*?)</div>', re.S)


LIST_RE = re.compile(r"<(ol|ul)[^>]*>(.*?)</\1>", re.S)
LI_ITEM_RE = re.compile(r"<li>(.*?)</li>", re.S)


def convert_block(frag):
    """Convert an HTML fragment that may contain <p> paragraphs and lists."""
    frag = re.sub(r"</p>\s*<p[^>]*>", "\x05", frag)      # paragraph break
    frag = re.sub(r"</?p[^>]*>", "", frag)
    out, pos = [], 0
    for m in LIST_RE.finditer(frag):
        out.append(convert_inline(frag[pos:m.start()]))
        items = LI_ITEM_RE.findall(m.group(2))
        if m.group(1) == "ol":
            body = "\n".join("\\item[(%s)] %s" % (chr(97 + i), convert_inline(it))
                             for i, it in enumerate(items))
            out.append("\n\\begin{enumerate}\n%s\n\\end{enumerate}\n" % body)
        else:
            body = "\n".join("\\item %s" % convert_inline(it) for it in items)
            out.append("\n\\begin{itemize}\n%s\n\\end{itemize}\n" % body)
        pos = m.end()
    out.append(convert_inline(frag[pos:]))
    return "".join(out).replace("\x05", "\n\n\\noindent ")
CTX_RE = re.compile(r'<p class="context">(.*?)</p>', re.S)
REFS_RE = re.compile(r'<ul class="refs">(.*?)</ul>', re.S)
LI_RE = re.compile(r"<li>(.*?)</li>", re.S)

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[french]{babel}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\newtheorem{problem}{Problème}
\newenvironment{refs}{\par\small\noindent\emph{Références :}\begin{itemize}\setlength\itemsep{0pt}}{\end{itemize}\normalsize}
\title{Hors de la Caverne \\ \Large %s}
\author{}
\date{}
\begin{document}
\maketitle
\noindent\emph{Des problèmes, pas de réponses.} Chaque problème ci-dessous est posé
sans solution. Les références indiquent où trouver les connaissances nécessaires.
\medskip
"""


def convert_page(fname):
    src = open(os.path.join(ROOT, fname), encoding="utf-8").read()
    title = re.search(r"<h1>(.*?)</h1>", src, re.S).group(1)
    title = htmllib.unescape(re.sub(r"<[^>]+>", "", title)).strip()
    body = src[src.index("</nav>"):]

    # Walk headings and problems in document order.
    tokens = []
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>|<section class="problem".*?</section>', body, re.S):
        chunk = m.group(0)
        if chunk.startswith("<h2"):
            h = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
            if h.lower().startswith(("where to go", "see also")):
                continue
            tokens.append(("h2", h))
        else:
            pm = PROB_RE.search(chunk)
            if pm:
                tokens.append(("prob", pm))

    out = [PREAMBLE % esc_text(title)]
    count = 0
    for kind, val in tokens:
        if kind == "h2":
            out.append("\n\\section*{%s}\n" % esc_text(val))
            continue
        pid, level, inner = val.group(1), val.group(2), val.group(3)
        h3 = H3_RE.search(inner)
        # Titles may contain math, so convert rather than escape them.
        name_html = re.sub(r"<span.*?</span>", "", h3.group(1), flags=re.S)
        name_html = re.sub(r"^\s*" + re.escape(pid) + r"\s*(&middot;|·|:|-)?\s*", "", name_html)
        name = convert_inline(name_html)
        opening = re.search(r'<section class="problem"[^>]*id="' + re.escape(pid) + r'"[^>]*>',
                            val.group(0))
        if opening and KIND_RE.search(opening.group(0)):
            level = level + ", short"
        stmt = STMT_RE.search(inner)
        ctx = CTX_RE.search(inner)
        refs = REFS_RE.search(inner)
        if not stmt:
            print("  !! %s: no statement" % pid)
            continue
        count += 1
        s = convert_block(stmt.group(1) or stmt.group(2))
        s = re.sub(r"^\s*(\\noindent )?\\textbf\{Probl\\`eme\.\}\s*", "", s)
        out.append("\\begin{problem}[{%s --- %s}]\n\\textbf{%s.} %s\n\\end{problem}"
                   % (name, esc_text(level), esc_text(pid), s))
        if ctx:
            out.append("\n\\noindent " + convert_inline(ctx.group(1)) + "\n")
        if refs:
            items = LI_RE.findall(refs.group(1))
            if items:
                out.append("\\begin{refs}")
                for it in items:
                    out.append("\\item " + convert_inline(it))
                out.append("\\end{refs}")
        out.append("\n\\bigskip\n")

    out.append("\n\\vfill\n\\noindent\\emph{Hors de la Caverne} --- des probl\\`emes, pas de r\\'eponses.\n"
               "\\end{document}\n")
    text = "\n".join(out)

    dest = os.path.join(TEX, fname[:-5] + ".tex")
    open(dest, "w", encoding="utf-8").write(text)
    leftover = sorted({c for c in text if ord(c) > 127})
    return count, leftover


if __name__ == "__main__":
    os.makedirs(TEX, exist_ok=True)
    names = sys.argv[1:] or sorted(
        f for f in os.listdir(ROOT)
        if f.endswith(".html") and f not in
        ("index.html", "resources.html", "TEMPLATE.html", "highschool.html"))
    total = 0
    for f in names:
        n, left = convert_page(f)
        total += n
        print("%-34s %3d problems  %s" % (f, n, ("non-ascii: " + " ".join(left)) if left else ""))
    print("TOTAL:", total)
