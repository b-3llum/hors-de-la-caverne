#!/usr/bin/env python3
"""Merge a round of block files into their pages, with validation.

Usage: merge_round.py <blocks-dir> <prefix>
Only merges a block file whose sections are all well formed and whose IDs do not
already exist on the target page. Prints a per-file report and refuses bad files.
"""
import os
import re
import sys

ROOT = os.environ.get("HDLC_ROOT",
                     os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "_source"))
from insert import insert, parse  # noqa: E402

# block-file stem -> page
PAGES = {
    "calculus": "applied-calculus.html",
    "real-analysis": "pure-real-analysis.html",
    "algebra": "pure-algebra.html",
    "linear-algebra": "pure-linear-algebra.html",
    "number-theory": "pure-number-theory.html",
    "foundations": "pure-foundations.html",
    "combinatorics": "pure-combinatorics.html",
    "discrete-cs": "applied-discrete-cs.html",
    "topology": "pure-topology.html",
    "geometry": "pure-geometry.html",
    "complex-analysis": "pure-complex-analysis.html",
    "functional-analysis": "pure-functional-analysis.html",
    "probability": "applied-probability.html",
    "statistics": "applied-statistics.html",
    "ode": "applied-ode.html",
    "pde": "applied-pde.html",
    "numerical": "applied-numerical.html",
    "optimization": "applied-optimization.html",
    "crypto": "applied-crypto.html",
    "category-theory": "pure-category-theory.html",
    "proofs": "proofs.html",
    "open-problems": "open-problems.html",
    "physics": "applied-physics.html",
    "puzzles-A": "puzzles.html",
    "puzzles-B": "puzzles.html",
}

SEC = re.compile(r'<section class="problem" id="([A-Z]+-\d+)"[^>]*>(.*?)</section>', re.S)


def check(text, page_src):
    """Return list of problems with a block file, empty if it is safe to merge."""
    errs = []
    n_open = len(re.findall(r'<section class="problem"', text))
    n_close = text.count("</section>")
    if n_open != n_close:
        errs.append("section tags %d/%d" % (n_open, n_close))
    if text.count("\\(") != text.count("\\)"):
        errs.append("inline math unbalanced")
    if text.count("\\[") != text.count("\\]"):
        errs.append("display math unbalanced")
    if text.count('data-kind="short"') != text.count('<span class="kind">short</span>'):
        errs.append("short markers vs chips")
    if re.search(r"\\(lt|gt)(?![a-zA-Z])", text):
        errs.append("KaTeX-only \\lt/\\gt")
    ids = [m.group(1) for m in SEC.finditer(text)]
    if len(ids) != len(set(ids)):
        errs.append("duplicate IDs inside block")
    for pid in ids:
        if 'id="%s"' % pid in page_src:
            errs.append("ID already on page: %s" % pid)
    for pid, body in SEC.findall(text):
        if 'class="statement"' not in body:
            errs.append("%s: no statement" % pid)
        if 'class="context"' not in body:
            errs.append("%s: no context" % pid)
        if 'class="refs"' not in body:
            errs.append("%s: no refs" % pid)
    return errs, ids


def main(blocks_dir, prefix):
    merged = skipped = 0
    for stem, page in PAGES.items():
        path = os.path.join(blocks_dir, "%s%s.txt" % (prefix, stem))
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        page_path = os.path.join(ROOT, page)
        src = open(page_path, encoding="utf-8").read()
        errs, ids = check(text, src)
        if errs:
            print("SKIP %-22s -> %-30s %s" % (stem, page, "; ".join(errs[:3])))
            skipped += 1
            continue
        insert(page_path, parse(path))
        # verify fidelity
        after = open(page_path, encoding="utf-8").read()
        norm = lambda t: " ".join(t.split())
        bad = [pid for pid in ids
               if norm(re.search(r'<section class="problem" id="%s".*?</section>' % pid,
                                 text, re.S).group(0))
               != norm(re.search(r'<section class="problem" id="%s".*?</section>' % pid,
                                 after, re.S).group(0))]
        print("OK   %-22s -> %-30s +%d %s"
              % (stem, page, len(ids), "" if not bad else "FIDELITY %s" % bad))
        merged += 1
    print("\nmerged %d file(s), skipped %d" % (merged, skipped))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "r3-")
