#!/usr/bin/env python3
"""Insert problem blocks at the end of a named level band.

Usage: insert.py <page.html> <block-file>
The block file contains one or more complete <section class="problem"> blocks,
separated by a line containing only  ---BAND: <Level Name>---
which says where the following sections belong.
"""
import re
import sys


def insert(path, blocks):
    src = open(path, encoding="utf-8").read()
    for band, html in blocks:
        # Locate the <h2> whose text is exactly the band name.
        m = re.search(r"<h2[^>]*>\s*" + re.escape(band) + r"\s*</h2>", src)
        if not m:
            print(f"  !! {path}: no band '{band}'")
            continue
        # End of band = next <h2> or the <hr> that closes the problem area.
        nxt = re.search(r"\n<h2[^>]*>", src[m.end():])
        if nxt:
            cut = m.end() + nxt.start()
        else:
            tail = re.search(r"\n<hr>\s*\n<h2", src[m.end():])
            cut = m.end() + (tail.start() if tail else len(src) - m.end())
        src = src[:cut] + "\n" + html.strip() + "\n" + src[cut:]
    open(path, "w", encoding="utf-8").write(src)


def parse(block_path):
    out, band, buf = [], None, []
    for line in open(block_path, encoding="utf-8"):
        m = re.match(r"---BAND:\s*(.+?)\s*---\s*$", line)
        if m:
            if band and buf:
                out.append((band, "".join(buf)))
            band, buf = m.group(1), []
        else:
            buf.append(line)
    if band and buf:
        out.append((band, "".join(buf)))
    return out


if __name__ == "__main__":
    page, block = sys.argv[1], sys.argv[2]
    b = parse(block)
    insert(page, b)
    n = sum(x[1].count('<section class="problem"') for x in b)
    print(f"{page}: inserted {n} problems into {len(b)} band(s)")
