# Testing: counts the raw SGML entities (&lt;, &amp;) in the corpus and shows the context of any remaining 'lt' and 'amp' tokens, 
#to verify the entity cleanup in reuters_parser.py.

import os
import re
from reuters_parser import parse_all_files, tokenize, DATA_DIR

# 1. How often do the entities appear in the raw files?
raw_lt = raw_amp = raw_lt_no_semicolon = 0
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".sgm"):
        with open(os.path.join(DATA_DIR, filename), "r", encoding="latin-1") as f:
            content = f.read()
        raw_lt += content.count("&lt;")
        raw_amp += content.count("&amp;")
        raw_lt_no_semicolon += len(re.findall(r"&lt(?![;\w])", content))
print(f"Raw files: '&lt;' x {raw_lt}, '&amp;' x {raw_amp}, '&lt' without semicolon x {raw_lt_no_semicolon}")

# 2. In which documents do the tokens 'lt' and 'amp' still appear, and in what context?
docs = parse_all_files()
for junk in ["lt", "amp"]:
    hits = []
    for newid, title, body in docs:
        text = title + " " + body
        if junk in tokenize(text):
            hits.append((newid, text))
    print(f"\n'{junk}': {len(hits)} documents")
    for newid, text in hits[:5]:
        m = re.search(r"\b" + junk + r"\b", text, re.IGNORECASE)
        start = max(0, m.start() - 40)
        print(f"  NEWID {newid}: {text[start:m.end() + 40]!r}")