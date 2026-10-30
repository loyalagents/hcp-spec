"""Build a clean HCP spec .docx in the v1 Draft 4 house style from a restricted Markdown source.

Usage: python3 -I build.py TEMPLATE.docx SOURCE.md OUT.docx "Header text"
Δ lines (change notes) in the source are dropped. Rendering lives in hcpdoc.py, shared with redline.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hcpdoc

if __name__ == '__main__':
    TPL, SRC, OUT, HEADER = sys.argv[1:5]
    n = hcpdoc.build(TPL, open(SRC, encoding='utf-8').read(), OUT, HEADER, mode='clean')
    print('wrote', OUT, 'paragraph-level blocks:', n)
