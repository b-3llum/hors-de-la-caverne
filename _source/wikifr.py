#!/usr/bin/env python3
"""Point en.wikipedia links at the French article when one exists.

For each en.wikipedia.org link in a page: ask the MediaWiki langlinks API for the
French equivalent. If there is one, rewrite the URL (keeping the translator's French
link text). If there is not, leave the English URL and mark the text "(en anglais)"
so the reader knows before clicking. Never invents a French title.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = "hors-de-la-caverne-linkcheck/1.0 (static site build)"


def fr_titles(titles):
    """Map en-title -> fr-title (or None) using the langlinks API, 40 at a time."""
    out = {}
    titles = list(titles)
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        q = {"action": "query", "format": "json", "prop": "langlinks",
             "lllang": "fr", "lllimit": "500", "redirects": "1",
             "titles": "|".join(chunk)}
        url = API + "?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.load(r)
        pages = data.get("query", {}).get("pages", {})
        norm = {n["to"]: n["from"] for n in data.get("query", {}).get("normalized", [])}
        redir = {n["to"]: n["from"] for n in data.get("query", {}).get("redirects", [])}
        for p in pages.values():
            t = p.get("title")
            ll = p.get("langlinks")
            fr = ll[0]["*"] if ll else None
            for key in {t, norm.get(t, t), redir.get(t, t)}:
                out[key] = fr
        time.sleep(0.3)          # be polite to the API
    return out


LINK = re.compile(r'<a href="https://en\.wikipedia\.org/wiki/([^"#]+)(#[^"]*)?">(.*?)</a>', re.S)


def process(path, apply=True):
    s = open(path, encoding="utf-8").read()
    raw = {urllib.parse.unquote(m.group(1)).replace("_", " ") for m in LINK.finditer(s)}
    if not raw:
        print("%s: no english wikipedia links" % path)
        return
    mapping = fr_titles(raw)
    switched = flagged = 0

    def repl(m):
        nonlocal switched, flagged
        title = urllib.parse.unquote(m.group(1)).replace("_", " ")
        anchor = m.group(2) or ""
        text = m.group(3)
        fr = mapping.get(title)
        if fr:
            switched += 1
            href = "https://fr.wikipedia.org/wiki/" + urllib.parse.quote(fr.replace(" ", "_"))
            clean = re.sub(r"\s*\(en anglais\)", "", text)
            return '<a href="%s%s">%s</a>' % (href, anchor, clean)
        flagged += 1
        if "(en anglais)" in text:
            return m.group(0)
        return '<a href="https://en.wikipedia.org/wiki/%s%s">%s (en anglais)</a>' % (
            m.group(1), anchor, text)

    out = LINK.sub(repl, s)
    if apply:
        open(path, "w", encoding="utf-8").write(out)
    print("%-30s switched to fr: %3d   kept english (flagged): %3d"
          % (path, switched, flagged))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        process(p)
