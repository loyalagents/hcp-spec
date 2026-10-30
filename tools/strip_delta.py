"""Remove every Δ note (the 'Δ ...' line and its continuation lines up to the next blank line) from source files, in place.
Usage: python3 -I tools/strip_delta.py FILE.md ...   (rolling redline: each round starts from a clean)"""
import sys, re
for p in sys.argv[1:]:
    src = open(p).read().split('\n'); out = []; i = 0; n = 0
    while i < len(src):
        if src[i].startswith('Δ '):
            n += 1; i += 1
            while i < len(src) and src[i].strip(): i += 1
            while i < len(src) and not src[i].strip() and out and not out[-1].strip(): i += 1  # no doubled blank
            continue
        out.append(src[i]); i += 1
    open(p, 'w').write('\n'.join(out)); print(f'{p}: {n} Δ notes removed')
