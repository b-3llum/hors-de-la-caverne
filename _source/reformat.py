#!/usr/bin/env python3
"""Reformat dense one-paragraph problem statements into a setup + lettered parts list.

<p class="statement"><b>Problem.</b> Setup. (a) task. (b) task.</p>
becomes
<div class="statement">
<p><b>Problem.</b> Setup.</p>
<ol class="parts" type="a"><li>task.</li><li>task.</li></ol>
</div>

Math regions are masked before splitting so a marker inside a formula is never
mistaken for a part label. Single-task statements are left untouched.
"""
import re
import sys

ALPHA = list("abcdefghij")
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"]

MATH = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.S)
STMT = re.compile(r'<p class="statement">(.*?)</p>', re.S)

# A marker must start a new clause: after sentence punctuation, a colon/dash,
# the bold "Problem." lead-in, or the very start of the statement.
LEAD = r"(?:^|(?<=</b>)|(?<=[.:;?!])|(?<=—)|(?<=—))\s*"


def mask_math(text):
    store = []

    def keep(m):
        store.append(m.group(0))
        return "\x00%d\x00" % (len(store) - 1)

    return MATH.sub(keep, text), store


def unmask(text, store):
    return re.sub(r"\x00(\d+)\x00", lambda m: store[int(m.group(1))], text)


def find_parts(masked, seq):
    """Return list of (start, end_of_marker) for a strictly ordered marker run."""
    spans, pos = [], 0
    for label in seq:
        m = re.compile(LEAD + re.escape("(%s)" % label) + r"\s+(?=\S)").search(masked, pos)
        if not m:
            break
        spans.append((m.start(), m.end()))
        pos = m.end()
    return spans


def reformat_statement(inner):
    masked, store = mask_math(inner)
    for seq, typ in ((ALPHA, "a"), (ROMAN, "i")):
        spans = find_parts(masked, seq)
        if len(spans) < 2:
            continue
        head = masked[: spans[0][0]].strip()
        if not head:                      # need a real setup sentence to keep
            head = "<b>Problem.</b>"
            if masked.lstrip().startswith("<b>Problem.</b>"):
                pass
        items = []
        for i, (s, e) in enumerate(spans):
            end = spans[i + 1][0] if i + 1 < len(spans) else len(masked)
            items.append(masked[e:end].strip().rstrip())
        # Drop a dangling empty tail item.
        items = [it for it in items if it]
        if len(items) < 2:
            continue
        head = re.sub(r"\s+$", "", head)
        body = "\n".join("<li>%s</li>" % it for it in items)
        out = ('<div class="statement">\n<p>%s</p>\n'
               '<ol class="parts" type="%s">\n%s\n</ol>\n</div>' % (head, typ, body))
        return unmask(out, store), True
    return inner, False


def process(path):
    src = open(path, encoding="utf-8").read()
    changed = [0]

    def repl(m):
        new, did = reformat_statement(m.group(1))
        if did:
            changed[0] += 1
            return new
        return m.group(0)

    out = STMT.sub(repl, src)
    if changed[0]:
        open(path, "w", encoding="utf-8").write(out)
    return changed[0]


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        n = process(p)
        total += n
        print("%-34s reformatted %3d" % (p, n))
    print("TOTAL reformatted:", total)
