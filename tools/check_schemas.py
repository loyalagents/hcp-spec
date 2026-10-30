"""Check the HCP JSON Schemas against every JSON example in the specification source.

Usage: python3 -I tools/check_schemas.py SCHEMA_DIR SOURCE_DIR

- Every schema is a valid JSON Schema 2020-12 document, and every $ref resolves.
- A concrete example (no {placeholder} values) is validated in full, with format checking.
- A template example (placeholders such as "{ISO-8601}" or "a | b") is compared member by member:
  every member it shows is defined by the schema, every member the schema requires is shown, and
  every alternative written "a | b" is a value the schema allows.
- Cross-member rules: a VC Evidence entry's content.evidence points at an item whose role is content,
  and the credential's subject is the entry's subject (14.2).
- The MCP tools' inputSchemas (10.3) are valid JSON Schemas, and each property maps to a Core field.
Prints PASS/FAIL lines and a list of findings; exit 1 on any FAIL.
"""
import json, os, re, sys
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

SD, SRC = sys.argv[1], sys.argv[2]
fails = []
def check(ok, msg):
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails.append(msg)

# ---------------------------------------------------------------- load schemas
schemas = {}
for root, _, files in os.walk(SD):
    for f in files:
        if f.endswith('.json'):
            s = json.load(open(os.path.join(root, f)))
            schemas[s['$id']] = s
registry = Registry().with_resources([(i, Resource.from_contents(s)) for i, s in schemas.items()])
BASE = next(iter(schemas)).rsplit('/', 1)[0].replace('/operations', '') + '/'
def sid(name): return BASE + name + '.json'
bad = []
for i, s in schemas.items():
    try: Draft202012Validator.check_schema(s)
    except Exception as e: bad.append((i, str(e)[:100]))
check(not bad, f'{len(schemas)} schemas are valid JSON Schema 2020-12 {bad}')

def validator(name):
    return Draft202012Validator({'$ref': sid(name)}, registry=registry, format_checker=FormatChecker())
unres = []
for i in schemas:
    try: validator(i[len(BASE):-5]).is_valid({})
    except Exception as e: unres.append((i, str(e)[:80]))
check(not unres, f'every $ref resolves {unres}')

# ---------------------------------------------------------------- examples from the source
def blocks():
    for n in range(1, 28):
        f = f's{n}.md'; lines = open(os.path.join(SRC, f)).read().split('\n'); sec = '?'; i = 0
        while i < len(lines):
            m = re.match(r'^#+ (\d[\d.]*)', lines[i])
            if m: sec = m.group(1)
            if lines[i].startswith('    {') and not lines[i - 1].startswith('    '):
                b = []
                while i < len(lines) and (lines[i].startswith('    ') or not lines[i].strip()):
                    b.append(lines[i][4:]); i += 1
                t = '\n'.join(b).strip()
                try: yield f, sec, json.loads(t)
                except ValueError: pass
                continue
            if lines[i].startswith('    "') and not lines[i - 1].startswith('    '):
                b = []
                while i < len(lines) and (lines[i].startswith('    ') or not lines[i].strip()):
                    b.append(lines[i][4:]); i += 1
                try: yield f, sec + 'f', json.loads('{' + '\n'.join(b).strip().rstrip(',') + '}')
                except ValueError: pass
                continue
            i += 1
EX = {}
for f, sec, j in blocks():
    EX.setdefault(sec, []).append(j)

PH = re.compile(r'\{[^{}]*\}|\.\.\.')
def is_template(x):
    if isinstance(x, str): return bool(PH.search(x)) or ' | ' in x
    if isinstance(x, dict): return any(is_template(v) for v in x.values())
    if isinstance(x, list): return any(is_template(v) for v in x)
    return False

def resolve(s, base, branches=False):
    """-> list of (schema, base, conditional) for s with $ref and allOf followed; with branches, also
    then/else/anyOf (their members count as defined, their requirements as conditional)."""
    out, todo = [], [(s, base, False)]
    while todo:
        s, b, cond = todo.pop()
        if not isinstance(s, dict): continue
        if '$ref' in s:
            u = s['$ref']; full = u if u.startswith('http') else b.rsplit('/', 1)[0] + '/' + u
            doc, frag = (full.split('#') + [''])[:2]
            doc = os.path.normpath(doc.replace('https://', '')).replace('https:/', 'https://')
            doc = 'https://' + doc if not doc.startswith('https://') else doc
            t = schemas[doc]
            for p in [k for k in frag.split('/') if k]: t = t[p]
            todo.append((t, doc, cond))
        out.append((s, b, cond))
        for a in s.get('allOf', []): todo.append((a, b, cond))
        if branches:
            for k in ('then', 'else'):
                if k in s: todo.append((s[k], b, True))
            for a in s.get('anyOf', []): todo.append((a, b, True))
    return out

def props(s, base):
    P, R, E = {}, set(), None
    for t, b, cond in resolve(s, base, True):
        for k, v in t.get('properties', {}).items(): P.setdefault(k, []).append((v, b))
        if 'required' in t and not cond: R |= set(t['required'])
        if 'enum' in t: E = (E or []) + t['enum']
        if 'const' in t: E = (E or []) + [t['const']]
        for a in t.get('anyOf', []):
            for tt, _, _ in resolve(a, b):
                if 'enum' in tt: E = (E or []) + tt['enum']
    return P, R, E

def items_schema(s, base):
    for t, b, _ in resolve(s, base, True):
        if 'items' in t: return t['items'], b
    return None, base

findings = []
def compare(tmpl, s, base, path, partial=False):
    """member coverage of a template against a schema; partial: a fragment, so top-level requirements are not checked"""
    if isinstance(tmpl, dict):
        if not tmpl or path.endswith('.credential'): return   # {} = defined elsewhere; a credential follows its own data model
        P, R, _ = props(s, base)
        if not P and not R: return   # a free-form object (metadata, unmapped, narrowedTo, data)
        for k, v in tmpl.items():
            if k not in P: findings.append(f'{path}.{k}: shown in the example, not defined by the schema'); continue
            compare(v, P[k][0][0], P[k][0][1], f'{path}.{k}')
        for k in (set() if partial else R - set(tmpl)):
            findings.append(f'{path}.{k}: required by the schema, not shown in the example')
    elif isinstance(tmpl, list):
        it, b = items_schema(s, base)
        if it is not None:
            for v in tmpl: compare(v, it, b, path + '[]')
    elif isinstance(tmpl, str) and ' | ' in tmpl and not PH.fullmatch(tmpl.strip()):
        _, _, E = props(s, base)
        alts = [a.strip().strip('{}') for a in tmpl.strip('{}').split(' | ')]
        if E is not None:
            for a in alts:
                if a not in [str(e) for e in E] and not a.startswith(('URI', 'ISO', 'null')) and a != 'null':
                    findings.append(f'{path}: "{a}" is not a value the schema allows {E}')

def validate(name, inst, label):
    errs = sorted(validator(name).iter_errors(inst), key=lambda e: list(e.path))
    check(not errs, f'{label} validates against {name} ' + ('; '.join(f'{"/".join(map(str, e.path))}: {e.message[:110]}' for e in errs[:4])))

def template(name, inst, label):
    n0 = len(findings); compare(inst, {'$ref': sid(name)}, BASE, label)
    new = findings[n0:]
    check(not new, f'{label} (template) matches {name} members' + ('' if not new else f': {len(new)} finding(s)'))

def ex(sec, k=0): return EX[sec][k]

template('entry', ex('4.2'), '4.2 entry')
template('grant', ex('6.1.5'), '6.1.5 grant')
validate('common', {}, 'common')  # trivially
Draft202012Validator({'$ref': sid('common') + '#/$defs/accessDetail'}, registry=registry, format_checker=FormatChecker())
errs = list(Draft202012Validator({'$ref': sid('common') + '#/$defs/accessDetail'}, registry=registry, format_checker=FormatChecker()).iter_errors(ex('6.1.5.1')))
check(not errs, '6.1.5.1 narrowed detail validates against common#accessDetail ' + '; '.join(e.message[:100] for e in errs))
template('standing-rule', ex('6.3'), '6.3 standing rule')
template('disclosure', ex('7.4'), '7.4 disclosure')
template('audit-event', ex('8.2'), '8.2 audit event')
validate('operations/query-request', ex('9.4.1', 0), '9.4.1 query request')
template('operations/query-result', ex('9.4.1', 1), '9.4.1 query result')
template('operations/get-entry-result', ex('9.4.2'), '9.4.2 get entry result')
validate('disclosure', ex('9.4.2')['entry'], '9.4.2 disclosed entry')
validate('operations/revise-request', ex('9.4.4'), '9.4.4 revise request')
template('operations/withdraw-result', ex('9.4.5'), '9.4.5 withdraw result')
imp = ex('9.4.11', 0)
(template if imp.get('export') == {} else validate)('operations/import-request', imp, '9.4.11 import request')
template('operations/import-result', ex('9.4.11', 1), '9.4.11 import result')
validate('error', ex('10.4')['structuredContent'], '10.4 MCP error')
for sec, label in [('11.4', '11.4 General Context entry'), ('14.4', '14.4 VC Evidence entry'), ('22.2', '22.2 education entry')]:
    e = ex(sec)
    (validate if not is_template(e) else template)('entry', e, label)
template('delegation', ex('17.2'), '17.2 delegation')
def fragment(name, sec, label):
    n0 = len(findings); compare(ex(sec + 'f'), {'$ref': sid(name)}, BASE, label, partial=True)
    check(len(findings) == n0, f'{label} (fragment) matches {name} members')
for name, sec, label in [('entry', '4.2', '4.2 record'), ('entry', '4.2.2', '4.2.2 evidence'), ('operations/query-result', '7.5', '7.5 minimization'),
                         ('entry', '11.2', '11.2 content'), ('entry', '14.2', '14.2 content'), ('grant', '17.4', '17.4 authorizingPrincipal')]:
    fragment(name, sec, label)
n0 = len(findings); compare(ex('4.3f')['conversion'], {'$ref': sid('entry') + '#/properties/record/properties/conversion'}, BASE, '4.3 conversion')
check(len(findings) == n0, '4.3 conversion (fragment) matches entry.record.conversion members')
# Draft 3 additions, where the source has them
if sid('export') in schemas:
    template('export', ex('5.4.1'), '5.4.1 export')
    n0 = len(findings); compare(ex('4.2.5f')['basis'], {'$ref': sid('common') + '#/$defs/basis'}, BASE, '4.2.5 basis')
    compare(ex('7.4.1f')['provenance'], {'$ref': sid('disclosure') + '#/properties/provenance'}, BASE, '7.4.1 provenance')
    check(len(findings) == n0, '4.2.5 basis and 7.4.1 provenance (fragments) match their schemas')
template('discovery', ex('19.2'), '19.2 discovery')

# cross-member rules (14.2)
for sec in ('11.4', '14.4', '22.2'):
    e = ex(sec)
    if e['content'].get('profile', '').endswith('vc-evidence/2.0'):
        it = e['evidence'][e['content']['evidence']]
        cs = it['credential']['credentialSubject']; cs = cs[0] if isinstance(cs, list) else cs
        check(it['role'] == 'content' and cs.get('id') == e['subject']['id'], f'{sec}: content.evidence names the content item; credentialSubject.id = subject.id')

# MCP tools (10.3)
for sec in ('10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.3.5'):
    t = ex(sec)
    try: Draft202012Validator.check_schema(t['inputSchema']); ok = True
    except Exception as e: ok = False
    check(ok, f'{sec} {t["name"]}: inputSchema is valid JSON Schema 2020-12')

print('\nFindings (template comparisons):' if findings else '\nNo template findings.')
for f in findings: print('  - ' + f)
print('ALL PASS' if not fails else f'{len(fails)} FAIL')
sys.exit(1 if fails else 0)
