"""Generate the HCP v2 JSON Schemas (JSON Schema 2020-12) listed in 25.2, for one draft.

Usage: python3 -I tools/make_schemas.py OUT_DIR [DRAFT]     (DRAFT default: 2.0-draft-2)

Schemas are open: members this specification does not define are allowed, because an HCP Provider
MUST preserve them (4.2, 25.3). Where the text says a member is withheld or never carried, the schema
forbids it. Cross-member rules a schema cannot state (an evidence index pointing at a `content` item,
a credential subject matching the entry subject) are checked by tools/check_schemas.py and by the
specification's own requirements. Where a schema and the text differ, the text governs (25.2).
"""
import json, os, sys

OUT = sys.argv[1]
DRAFT = sys.argv[2] if len(sys.argv) > 2 else '2.0-draft-2'
D3 = int(DRAFT.rsplit('-', 1)[1]) >= 3   # Draft 3: several categories, basis, permitted purposes, provenance, export
BASE = f'https://hcp.example/schemas/{DRAFT}/'
D2020 = 'https://json-schema.org/draft/2020-12/schema'
GC = 'https://hcp.example/spec/profiles/general-context/2.0'
VC = 'https://hcp.example/spec/profiles/vc-evidence/2.0'

def ref(name, frag=''):
    return {'$ref': name + '.json' + (('#/$defs/' + frag) if frag else '')}
def c(frag):
    return ref('common', frag)
def obj(props, required=(), **kw):
    o = {'type': 'object', 'properties': props}
    if required: o['required'] = list(required)
    o.update(kw); return o
def arr(items, **kw):
    o = {'type': 'array', 'items': items}; o.update(kw); return o
def nullable(s):
    return {'anyOf': [s, {'type': 'null'}]}
S = {'type': 'string'}
DT = {'type': 'string', 'format': 'date-time'}
URI = {'type': 'string', 'format': 'uri', 'pattern': '^[A-Za-z][A-Za-z0-9+.-]*:[^\\s]+$'}

schemas = {}
def schema(name, title, desc, body, sec):
    s = {'$schema': D2020, '$id': BASE + name + '.json', 'title': title,
         'description': f'{desc} Defined in {sec} of the HCP v2 specification ({DRAFT}); where this schema and the text differ, the text governs.'}
    s.update(body); schemas[name] = s

# ------------------------------------------------------------------ common definitions
common_defs = {
    'dateTime': DT,
    'uri': URI,
    'urnUuid': {'type': 'string', 'pattern': '^urn:uuid:[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$',
                'description': 'A urn:uuid: identifier. Any RFC 4122 version (4.2).'},
    'category': {'type': 'string', 'description': 'A registered category slug, or a custom category: an absolute URI (4.5).',
                 'anyOf': [{'pattern': '^[a-z][a-z0-9_]*$'}, {'format': 'uri', 'pattern': '^[A-Za-z][A-Za-z0-9+.-]*:'}]},
    'purposeCode': {'type': 'string', 'format': 'uri', 'pattern': '^[A-Za-z][A-Za-z0-9+.-]*:[^\\s]+$', 'description': 'A purpose code: an absolute URI (6.1.5.2).'},
    'purpose': obj({'code': c('purposeCode'), 'description': {'type': 'string', 'minLength': 1}}, ['code', 'description'],
                   description='A purpose with a description the person can read (6.1.5.2).'),
    'declarationType': {'enum': ['person-declared', 'model-inferred', 'issuer-attested'], 'description': '4.4'},
    'assurance': {'enum': ['unverified', 'authenticated', 'cryptographically-verified'], 'description': '3.6'},
    'entryStatus': {'enum': ['active', 'deprecated', 'conflicted', 'expired', 'revoked', 'suspended', 'deleted'], 'description': '4.2.4'},
    'confidence': {'enum': ['high', 'medium', 'low', None], 'description': '4.2'},
    'relationshipType': {'enum': ['derivedFrom', 'supersedes', 'contradicts', 'duplicates'], 'description': '4.2.3'},
    'role': {'enum': ['management-client', 'context-client', 'authorization-service', 'hcp-provider'], 'description': '3.9'},
    'action': {'enum': ['read', 'write'], 'description': '6.1.5'},
    'named': obj({'id': S, 'name': S}, ['id', 'name']),
    'clientDescription': obj({'id': S, 'name': S, 'operator': c('named')}, ['id', 'name', 'operator'],
                             description='An HCP Client and its Client Operator, as recorded (3.5, 3.2.8).'),
    'legalRetention': obj({'record': S, 'obligation': S, 'period': S}, ['record', 'obligation', 'period'],
                          description='A record the client keeps under a declared legal obligation (6.2.5).'),
    'credential': obj({'@context': {'type': ['array', 'string']}, 'type': {'type': ['array', 'string']},
                       'issuer': {'type': ['string', 'object']}, 'credentialSubject': {'type': ['object', 'array']}},
                      ['@context', 'type', 'issuer', 'credentialSubject'],
                      description='A W3C Verifiable Credential, held whole as its issuer secured it (4.2.2, 14.2). Its own data model governs its contents.'),
    'verification': obj(dict({'result': {'enum': ['verified', 'failed']}, 'at': DT}, **({'by': {'enum': ['provider', 'trust-domain']}} if D3 else {})), ['result', 'at'],
                        description='The HCP Provider\'s record of its most recent verification (4.2.2). Set only by the provider.'),
    'evidenceItem': {
        'type': 'object', 'description': 'An evidence item (4.2.2). An item of a type the provider does not recognize is preserved.',
        'properties': {'role': {'enum': ['content', 'supports']}, 'type': S,
                       'credential': True, 'verification': c('verification')},
        'required': ['role', 'type'],
        'allOf': [{'if': {'properties': {'type': {'const': 'verifiable-credential'}}, 'required': ['type']},
                   'then': {'properties': {'credential': c('credential')}, 'required': ['credential']}}]},
    'evidence': arr(c('evidenceItem'), contains={'properties': {'role': {'const': 'content'}}, 'required': ['role']},
                    minContains=0, maxContains=1, description='At most one item whose role is content (4.2.2).'),
    'content': {
        'type': 'object', 'description': 'What is said about the Context Subject; its shape is named by its profile (4.2, 11, 14).',
        'properties': {'profile': URI}, 'required': ['profile'],
        'allOf': [
            {'if': {'properties': {'profile': {'const': GC}}},
             'then': {'properties': {'value': {'type': ['string', 'object']}, 'language': nullable(S)}, 'required': ['value']}},
            {'if': {'properties': {'profile': {'const': VC}}},
             'then': {'properties': {'evidence': {'type': 'integer', 'minimum': 0}}, 'required': ['evidence'], 'not': {'required': ['value']}}}]},
    'assertion': {
        'type': 'object', 'description': 'What the submitting client states about the assertion (4.2).',
        'properties': dict({'declarationType': c('declarationType'), 'confidence': c('confidence'), 'validUntil': nullable(DT)},
                           **({'basis': c('basis'), 'permittedPurposes': arr(c('purposeCode'), uniqueItems=True)} if D3 else {})),
        'required': ['declarationType'],
        'allOf': [{'if': {'properties': {'declarationType': {'const': 'model-inferred'}}},
                   'then': {'properties': {'confidence': {'enum': ['high', 'medium', 'low']}}, 'required': ['confidence']},
                   'else': {'properties': {'confidence': {'type': 'null'}}}}]},
    'classification': (obj({'categories': arr(c('category'), minItems=1, uniqueItems=True), 'dimension': nullable(S),
                            'permittedPurposes': arr(c('purposeCode'), uniqueItems=True)}, ['categories'],
                           description='HCP\'s classification of the entry (4.2, 4.2.6, 4.5).') if D3 else
                       obj({'category': c('category'), 'dimension': nullable(S)}, ['category'],
                           description='HCP\'s classification of the entry (4.2, 4.5).')),
    'accessDetail': obj({'type': {'const': 'https://hcp.example/spec/authorization/context-access'},
                         'actions': arr(c('grantAction' if D3 else 'action'), minItems=1, uniqueItems=True),
                         'categories': arr(c('category'), minItems=1, uniqueItems=True),
                         'purposes': arr(c('purpose'), minItems=1),
                         'narrowedTo': {'type': 'object', 'description': 'Implementation-defined; only narrows (6.1.5.1).'},
                         **({'onwardSharing': obj({'domains': arr(S, uniqueItems=True), 'notTo': arr(S, uniqueItems=True)},
                                                  description='Elected by the person; only in a detail with read whose categories are all Low (3.12, 6.1.4, 6.1.5).')} if D3 else {})},
                        ['type', 'actions', 'categories', 'purposes'],
                        description='An authorization detail (6.1.5); under the OAuth Interop Profile, an RFC 9396 authorization detail (13.3).'),
    'minimization': obj({'method': S}, ['method'], description='The minimization report (7.5). It MUST NOT carry any measure of what was withheld, which no schema can check by name.'),
}
if D3:
    common_defs['grantAction'] = {'enum': ['read', 'write', 'provenance'], 'description': '6.1.5'}
    common_defs['basis'] = obj({'drawnFrom': arr(S), 'task': S, 'setting': S, 'rationale': S},
                               description='What an assertion was drawn from (4.2.5). It identifies no party but the Context Subject.')
schema('common', 'HCP common definitions', 'Definitions shared by the HCP schemas.', {'$defs': common_defs}, 'the sections cited in each definition')

# ------------------------------------------------------------------ entry (4.2)
provenance = obj({
    'assertedBy': obj(dict({'id': S, 'assurance': c('assurance')},
                           **({'via': obj({'kind': {'enum': ['authorization-credential', 'arrangement']}, 'id': S}, ['kind', 'id'])} if D3 else {})),
                      ['id', 'assurance']),
    'assertedAt': DT, 'source': S,
    'submittedByClient': c('clientDescription'),
    'authorizedUnder': S, 'recordedByProvider': S, 'recordedAt': DT,
    'confirmations': arr(obj({'disposition': {'enum': ['confirmed', 'rejected']}, 'confirmedBy': obj({'id': S}, ['id']), 'confirmedAt': DT},
                             ['disposition', 'confirmedBy', 'confirmedAt']))},
    ['assertedBy', 'assertedAt', 'source', 'submittedByClient', 'authorizedUnder', 'recordedByProvider', 'recordedAt'],
    description='Who asserted, submitted, authorized, recorded and confirmed this version (3.5-3.8).')
proposal = obj({'act': {'enum': ['reject', 'accept', 'supersede']}, 'entry': S, 'rationale': {'type': 'string', 'minLength': 1},
                'weighed': arr(S, minItems=1), 'proposedBy': obj({'role': c('role'), 'id': S}, ['role', 'id']), 'proposedAt': DT},
               ['act', 'entry', 'rationale', 'weighed', 'proposedBy', 'proposedAt'],
               description='A proposal for resolving a conflict; it changes nothing until the Context Subject acts (4.7.4).')
relationship = obj(dict({'type': c('relationshipType'), 'target': S, 'assertedBy': obj({'role': c('role'), 'id': S}, ['role', 'id']), 'recordedAt': DT},
                        **({'proposal': proposal} if D3 else {})),
                   ['type', 'target', 'assertedBy', 'recordedAt'],
                   **({'allOf': [{'if': {'not': {'properties': {'type': {'const': 'contradicts'}}}}, 'then': {'not': {'required': ['proposal']}}}]} if D3 else {}))
record = obj({'status': c('entryStatus'), 'version': {'type': 'integer', 'minimum': 1}, 'provenance': provenance,
              'relationships': arr(relationship),
              'conversion': obj({'from': S, 'convertedAt': DT, 'convertedBy': S, 'unmapped': {'type': 'object'}}, ['from', 'convertedAt', 'convertedBy']),
              'metadata': {'type': 'object'}},
             ['status', 'version', 'provenance'])
schema('entry', 'HCP entry', 'An HCP entry, in the one form a provider emits.', {
    'type': 'object',
    'properties': {
        '@context': {'type': ['array', 'string']},
        'schema': {'const': 'https://hcp.example/spec/entry/2.0'},
        'id': c('urnUuid'),
        'type': arr(S, contains={'const': 'ContextEntry'}),
        'subject': obj({'id': S, 'relationship': {'type': 'null', 'description': 'Reserved (4.2, 11.3).'}}, ['id']),
        'content': c('content'), 'assertion': c('assertion'), 'classification': c('classification'),
        'evidence': c('evidence'), 'record': record},
    'required': ['schema', 'id', 'type', 'subject', 'content', 'assertion', 'classification', 'record']}, '4.2')

# ------------------------------------------------------------------ disclosure (7.4)
disc_evidence_item = {'allOf': [c('evidenceItem')], 'properties': {'revealed': arr({'type': 'string', 'description': 'A JSON Pointer into the stored credential (14.9).'})}}
schema('disclosure', 'HCP disclosure', 'An entry as disclosed to a Context Client: never the stored entry.', {
    'type': 'object',
    'properties': {
        'ref': {'type': 'string', 'minLength': 1, 'description': 'Grant-scoped, opaque, never the entry id.'},
        'version': {'type': 'integer', 'minimum': 1},
        'content': c('content'), 'evidence': arr(disc_evidence_item), 'assertion': c('assertion'),
        'classification': c('classification'),
        'standing': obj({'assurance': c('assurance'), 'confirmed': {'type': 'boolean'}}, ['assurance', 'confirmed']),
        'useUntil': DT,
        'relationships': arr(obj({'type': c('relationshipType'), 'target': S}, ['type', 'target'])),
        **({'onwardSharing': {'const': True, 'description': 'The client may share from this entry under 3.12 (7.4).'}} if D3 else {}),
        **({'provenance': obj({'submittedBy': obj({'name': S, 'operator': S}, ['name', 'operator']),
                               'source': {'enum': ['conversation', 'document', 'person-input', 'integration']},
                               'assertedAt': DT, 'recordedAt': DT}, ['submittedBy', 'source', 'assertedAt', 'recordedAt'],
                              description='Only under a grant with the provenance action; names, never identifiers (7.4.1).',
                              **{'not': {'anyOf': [{'required': [k]} for k in ['id', 'confirmedBy', 'authorizedUnder', 'submittedByClient']]}})} if D3 else {})},
    'required': ['ref', 'version', 'content', 'assertion', 'classification', 'standing', 'useUntil'],
    'not': {'anyOf': [{'required': [k]} for k in ['id', 'subject', 'record', 'schema']]},
    '$comment': 'Withheld members (7.4): id, subject, record (status, provenance, conversion, metadata).'}, '7.4')

# ------------------------------------------------------------------ grant (6.1.5)
schema('grant', 'HCP grant', 'The record of an authorization.', {
    'type': 'object',
    'properties': {
        'grantId': c('urnUuid'),
        'subject': obj({'id': S}, ['id']),
        'authorizingPrincipal': obj({'id': S, 'delegation': S}, ['id']),
        'client': obj(dict({'id': S, 'name': {'type': 'string', 'minLength': 1}, 'operator': c('named'), 'legalRetention': c('legalRetention')},
                           **({'claims': arr(URI, uniqueItems=True)} if D3 else {})), ['id', 'name', 'operator']),
        'requestingParty': obj({'type': {'enum': ['person', 'organization']}, 'id': S, 'name': S}, ['type', 'id']),
        'access': arr(c('accessDetail'), minItems=1),
        'scopes': arr({'type': 'string', 'pattern': '^hcp:[^:]+(:[^:]+)*:(read|write)$'}),
        'grantType': {'enum': ['temporary', 'persistent']},
        'issuedAt': DT, 'expiresAt': nullable(DT),
        'status': {'enum': ['active', 'revoked', 'expired']}},
    'required': ['grantId', 'subject', 'authorizingPrincipal', 'client', 'access', 'grantType', 'issuedAt', 'expiresAt', 'status'],
    'allOf': [{'if': {'properties': {'grantType': {'const': 'temporary'}}}, 'then': {'properties': {'expiresAt': DT}}},
              {'if': {'properties': {'grantType': {'const': 'persistent'}}}, 'then': {'properties': {'expiresAt': {'type': 'null'}}}}]}, '6.1.5')

# ------------------------------------------------------------------ standing rule (6.3)
schema('standing-rule', 'HCP standing rule', 'A deny rule the Context Subject sets across every grant.', {
    'type': 'object',
    'properties': dict({'ruleId': c('urnUuid'), 'effect': {'const': 'deny'},
                        'operators': arr({'type': 'string', 'minLength': 1}, minItems=1),
                        'categories': arr(c('category'), minItems=1), 'setBy': S, 'createdAt': DT},
                       **({'requires': arr(URI, minItems=1)} if D3 else {})),
    'required': ['ruleId', 'effect', 'setBy', 'createdAt'] if D3 else ['ruleId', 'effect', 'operators', 'setBy', 'createdAt'],
    **({'anyOf': [{'required': ['operators']}, {'required': ['requires']}]} if D3 else {})}, '6.3')
if D3:
    schema('directive', 'HCP directive', 'What a client may do with context it received, or on the Context Subject\'s behalf.', {
        'type': 'object',
        'properties': {'directiveId': c('urnUuid'),
                       'action': {'anyOf': [{'enum': ['share', 'sign', 'transact']}, URI]},
                       'effect': {'enum': ['deny', 'ask-first', 'permit']},
                       'text': {'type': 'string', 'minLength': 1},
                       'categories': arr(c('category'), minItems=1), 'operators': arr({'type': 'string', 'minLength': 1}, minItems=1),
                       'setBy': S, 'createdAt': DT},
        'required': ['directiveId', 'action', 'effect', 'text', 'setBy', 'createdAt']}, '6.4')

# ------------------------------------------------------------------ delegation (17.2)
schema('delegation', 'HCP delegation', 'One person\'s authority to act as Authorizing Principal for the Context Subject.', {
    'type': 'object',
    'properties': {
        'delegationId': c('urnUuid'),
        'subject': obj({'id': S}, ['id']),
        'delegate': obj({'id': S, 'name': {'type': 'string', 'minLength': 1}}, ['id', 'name']),
        'relationship': {'anyOf': [{'enum': ['parent-or-guardian', 'legal-guardian', 'attorney-in-fact', 'caregiver']}, URI]},
        'basis': obj(dict({'method': {'enum': ['appointed', 'attested', 'evidence', 'delegated', 'unspecified'] if D3 else ['appointed', 'attested', 'evidence', 'unspecified']},
                           'description': S, 'evidence': arr(c('evidenceItem')), 'covers': arr(c('category')),
                           'establishedBy': S, 'establishedAt': DT}, **({'parent': c('urnUuid')} if D3 else {})),
                     ['method', 'description', 'establishedBy', 'establishedAt'],
                     allOf=[{'if': {'properties': {'method': {'const': 'evidence'}}}, 'then': {'properties': {'evidence': {'minItems': 1}}, 'required': ['evidence']}}]
                           + ([{'if': {'properties': {'method': {'const': 'delegated'}}}, 'then': {'required': ['parent']}, 'else': {'not': {'required': ['parent']}}}] if D3 else [])),
        'scope': obj({'categories': arr(c('category'), minItems=1), 'actions': arr(c('action'), minItems=1, uniqueItems=True)}, ['categories', 'actions']),
        'term': obj({'endsAt': nullable(DT), 'atMajority': {'type': 'boolean'}}, ['endsAt', 'atMajority']),
        'ended': obj({'at': DT, 'reason': {'enum': ['majority', 'expiry', 'basis-ended', 'relinquished', 'ended-by-subject'] + (['parent-ended', 'ended-by-delegate'] if D3 else [])}}, ['at', 'reason']),
        **({'mayDelegate': {'type': 'boolean', 'default': False}} if D3 else {})},
    'required': ['delegationId', 'subject', 'delegate', 'relationship', 'basis', 'scope', 'term']}, '17.2')

# ------------------------------------------------------------------ minimization report, errors
schema('minimization-report', 'HCP minimization report', 'The minimization report carried by query and get-entry results.',
       {'allOf': [c('minimization')]}, '7.5')
CODES = ['malformed-request', 'invalid-token', 'scope-denied', 'idempotency-conflict', 'version-conflict',
         'credential-invalid', 'rate-limited', 'unsupported-version'] + (['subject-unavailable'] if D3 else [])
schema('error', 'HCP Core error', 'A Core error as a binding carries it: the MCP Binding\'s structuredContent of a tool execution error (10.4).', {
    'type': 'object', 'properties': {'type': {'enum': CODES}, 'detail': S}, 'required': ['type', 'detail']}, '5.5, 10.4')
schema('problem', 'HCP problem details', 'A Core error as the HTTP Binding carries it: RFC 9457 problem details (9.7).', {
    'type': 'object',
    'properties': {'type': {'enum': ['https://hcp.example/problems/' + k for k in CODES]}, 'title': S,
                   'status': {'enum': [400, 401, 403, 409, 422, 429] + ([503] if D3 else [])}, 'detail': S},
    'required': ['type', 'title', 'status', 'detail']}, '9.7')

# ------------------------------------------------------------------ operations (5.2, 5.4.3, 8.6, 9.4.13)
def op(name, title, sec, body):
    schema('operations/' + name, title, f'{title}.', body, sec)
def r(name):  # ref from operations/ to a top-level schema
    return {'$ref': '../' + name + '.json'}
def rc(frag):
    return {'$ref': '../common.json#/$defs/' + frag}
entry_or_disclosure = {'anyOf': [r('disclosure'), r('entry')],
                       'description': 'A disclosure where the requester is a Context Client (7.4); otherwise the entry.'}
TS = DT
op('query-request', 'Query request', '5.2.1', {'type': 'object', 'properties': {
    'query': {'type': 'string', 'minLength': 1}, 'categories': arr(rc('category')), 'purpose': rc('purposeCode'),
    'purposeDescription': S, 'maxEntries': {'type': 'integer', 'minimum': 1, 'default': 5}}, 'required': ['query', 'purpose']})
op('query-result', 'Query result', '5.2.1', {'type': 'object', 'properties': {
    'entries': arr(entry_or_disclosure, maxItems=20), 'retrievalId': rc('urnUuid'), 'minimization': rc('minimization'),
    'categoriesSearched': arr(rc('category')), 'timestamp': TS, **({'directives': arr(r('directive'))} if D3 else {})},
    'required': ['entries', 'retrievalId', 'minimization', 'categoriesSearched', 'timestamp']})
named_entry = {'ref': {'type': 'string'}, 'entryId': rc('urnUuid')}
op('get-entry-request', 'Get entry request', '5.2.2', {'type': 'object', 'properties': dict(named_entry, **{
    'purpose': rc('purposeCode'), 'purposeDescription': S, 'version': {'type': 'integer', 'minimum': 1}}),
    'required': ['purpose'], '$comment': 'The HTTP Binding carries ref or entryId in the path (9.4.2); the MCP tool carries ref (10.3.2).'})
op('get-entry-result', 'Get entry result', '5.2.2', {'type': 'object', 'properties': {
    'entry': entry_or_disclosure, 'retrievalId': rc('urnUuid'), 'minimization': rc('minimization'), 'timestamp': TS,
    **({'directives': arr(r('directive'))} if D3 else {})},
    'required': ['entry', 'retrievalId', 'minimization', 'timestamp']})
op('create-request', 'Create request', '5.2.3, 9.4.3', {'type': 'object', 'properties': {
    'schema': {'const': 'https://hcp.example/spec/entry/2.0'},
    'subject': obj({'id': S}, ['id']), 'content': rc('content'), 'evidence': rc('evidence'),
    'classification': rc('classification'), 'assertion': rc('assertion'),
    'record': obj({'provenance': obj({'assertedBy': obj({'id': S}, ['id']), 'assertedAt': DT, 'source': S}, ['source']),
                   'relationships': arr(obj(dict({'type': rc('relationshipType'), 'target': S},
                                                 **({'proposal': obj({'act': {'enum': ['reject', 'accept', 'supersede']}, 'entry': S, 'rationale': S, 'weighed': arr(S, minItems=1)},
                                                                     ['act', 'entry', 'rationale', 'weighed'])} if D3 else {})), ['type', 'target']))}, ['provenance'])},
    'required': ['schema', 'subject', 'content', 'classification', 'assertion', 'record'],
    '$comment': 'An entry in the form of 4.2 carrying the fields of 5.2.3 and omitting those the provider assigns (9.4.3). assertedBy.id is required except for person-declared entries and credential content (5.2.3); that rule depends on content and is checked by the provider.'})
op('create-result', 'Create result', '5.2.3', entry_or_disclosure)
op('revise-request', 'Revise request', '5.2.4, 9.4.4', {'type': 'object', 'properties': dict(named_entry, **{
    'expectedVersion': {'type': 'integer', 'minimum': 1}, 'content': rc('content'), 'evidence': rc('evidence'),
    'reason': {'type': 'string', 'minLength': 1},
    'assertion': obj({'declarationType': rc('declarationType'), 'confidence': rc('confidence'), 'validUntil': nullable(DT)}),
    'record': obj({'provenance': obj({'assertedBy': obj({'id': S}, ['id']), 'assertedAt': DT, 'source': S}),
                   'relationships': arr(obj({'type': rc('relationshipType'), 'target': S}, ['type', 'target']))})}),
    'required': ['expectedVersion', 'content', 'reason'],
    'not': {'anyOf': [{'required': ['subject']}, {'required': ['classification']}]},
    '$comment': 'A revision does not change subject or classification (5.2.4). The HTTP Binding names the entry in the path (9.4.4).'})
op('revise-result', 'Revise result', '5.2.4', entry_or_disclosure)
op('withdraw-request', 'Withdraw request', '5.2.5', {'type': 'object', 'properties': dict(named_entry, reason={'type': 'string', 'minLength': 1}), 'required': ['reason']})
op('withdraw-result', 'Withdraw result', '5.2.5, 9.4.5', {'type': 'object', 'properties': dict(named_entry, **{
    'status': {'const': 'deleted'}, 'hardDeleted': {'type': 'boolean'}, 'timestamp': TS}), 'required': ['status', 'timestamp'],
    ('oneOf' if D3 else 'anyOf'): [{'required': ['ref']}, {'required': ['entryId']}]})
op('read-own-grant-result', 'Read own grant result', '5.2.6', r('grant'))
if D3:
    op('report-sharing-request', 'Report onward sharing request', '5.2.8, 9.4.16', {'type': 'object', 'properties': {
        'recipient': obj({'domain': {'type': 'string', 'minLength': 1}, 'name': {'type': 'string', 'minLength': 1}}, ['domain', 'name']),
        'refs': arr({'type': 'string'}, minItems=1), 'purpose': rc('purposeCode'), 'sharedAt': DT},
        'required': ['recipient', 'refs', 'purpose', 'sharedAt'], '$comment': 'Result: none (204 over HTTP).'})
op('import-request', 'Import request', '5.4.3, 9.4.11', {'type': 'object', 'properties': {
    'export': r('export') if D3 else {'type': 'object'}, 'dryRun': {'type': 'boolean'},
    'categoryMap': {'type': 'object', 'additionalProperties': rc('category')}}, 'required': ['export']})
op('import-result', 'Import result', '5.4.3, 9.4.11', {'type': 'object', 'properties': {
    'outcomes': arr(obj({'id': S, 'outcome': {'enum': ['imported', 'converted', 'skipped', 'rejected']}, 'reason': S}, ['id', 'outcome'],
                        allOf=[{'if': {'properties': {'outcome': {'const': 'rejected'}}}, 'then': {'required': ['reason']}}])),
    'dryRun': {'type': 'boolean'}}, 'required': ['outcomes']})
summary_client = obj({
    'client': rc('clientDescription'),
    'grants': arr(obj({'grantId': rc('urnUuid'), 'status': {'enum': ['active', 'revoked', 'expired']}}, ['grantId', 'status'])),
    'categories': arr(rc('category')), 'purposes': arr(rc('purposeCode')),
    'entries': {'type': 'integer', 'minimum': 0}, 'retrievals': {'type': 'integer', 'minimum': 0},
    'firstAt': DT, 'lastAt': DT, 'usableUntil': nullable(DT),
    'notification': {'enum': ['delivered', 'abandoned', 'none']}, 'legalRetention': rc('legalRetention')},
    ['client', 'grants', 'categories', 'purposes', 'entries', 'retrievals', 'firstAt', 'lastAt', 'usableUntil', 'notification'])
op('disclosure-summary-result', 'Disclosure summary result', '8.6, 9.4.12', {'type': 'object', 'properties': {'clients': arr(summary_client)}, 'required': ['clients'],
   '$comment': 'Member shapes are inferred from the descriptions in 8.6, which fix content but not structure.'})
op('delegations-result', 'Delegations list result', '9.4.13', {'type': 'object', 'properties': {'delegations': arr(r('delegation'))}, 'required': ['delegations']})

if D3:
    schema('export', 'HCP export', 'The Context Subject\'s export, which import takes.', {
        'type': 'object',
        'properties': {'@context': {'type': ['array', 'string']}, 'type': {'const': 'ContextExport'},
                       'schema': {'const': 'https://hcp.example/spec/export/2.0'}, 'subject': obj({'id': S}, ['id']),
                       'exportedBy': S, 'exportedAt': DT,
                       'options': obj({'excludeDeleted': {'type': 'boolean'}, 'includeVersions': {'type': 'boolean'}, 'includeAudit': {'type': 'boolean'}}),
                       'entries': arr({'type': 'object'}, description='Entries in any schema the importing provider accepts (4.3); each validated against that schema.'),
                       'versions': arr({'type': 'object'}), 'rules': arr(ref('standing-rule')), 'directives': arr(ref('directive')), 'delegations': arr(ref('delegation')), 'audit': arr(ref('audit-event'))},
        'required': ['@context', 'type', 'schema', 'subject', 'exportedBy', 'exportedAt', 'entries', 'rules']}, '5.4.1')

# ------------------------------------------------------------------ additional: audit event (8.2), discovery (19)
EVENTS = ['context.created', 'context.read', 'context.revised', 'context.recategorized', 'context.withdrawn', 'context.hardDeleted',
          'context.confirmed', 'context.exported', 'context.imported', 'context.expired', 'context.credentialStatus',
          'grant.issued', 'grant.revoked', 'grant.expired', 'delegation.established', 'delegation.ended', 'rule.set', 'rule.removed',
          'conflict.detected', 'conflict.resolved'] + (['context.restricted', 'conflict.proposed', 'directive.set', 'directive.removed', 'context.shared'] if D3 else [])
schema('audit-event', 'HCP audit event', 'One event in the Context Subject\'s audit log. Not listed in 25.2; offered for the conformance suite.', {
    'type': 'object',
    'properties': {
        'eventId': c('urnUuid'), 'eventType': S, 'timestamp': DT,
        'participants': obj({'initiator': obj({'role': c('role'), 'id': S}, ['role', 'id']), 'clientOperator': obj({'id': S}, ['id']),
                             'requestingParty': obj({'id': S}, ['id']), 'authorizingPrincipal': obj({'id': S}, ['id']),
                             'provider': obj({'id': S}, ['id']), 'retrievalId': c('urnUuid'), 'model': obj({'id': S}, ['id'])},
                            ['initiator', 'provider']),
        'entryId': nullable(c('urnUuid')), 'relatedEntryId': nullable(c('urnUuid')),
        **({'categories': arr(c('category'))} if D3 else {'category': nullable(c('category'))}),
        'purpose': nullable(c('purposeCode')), 'purposeDescription': nullable(S), 'grantId': nullable(c('urnUuid')),
        'disclosed': arr(obj({'entryId': c('urnUuid'), 'version': {'type': 'integer', 'minimum': 1}, 'useUntil': DT, **({'provenance': {'type': 'boolean'}} if D3 else {}),
                              'revealed': arr(obj({'evidence': {'type': 'integer', 'minimum': 0}, 'claims': arr(S)}, ['evidence', 'claims']))},
                             ['entryId', 'version', 'useUntil'])),
        'data': {'type': 'object'}},
    'required': ['eventId', 'eventType', 'timestamp', 'participants'],
    '$comment': 'eventType values: ' + ', '.join(EVENTS) + ' (8.1). Left open here so that the event types of a later draft do not fail validation.'}, '8.2')
schema('discovery', 'HCP discovery document', 'The discovery document every conforming implementation publishes. Not listed in 25.2.', {
    'type': 'object',
    'properties': {
        'hcp_version': S, 'provider': URI, 'provider_operator': c('named'),
        'conformsTo': arr(URI, minItems=1), 'bindings': arr({'enum': ['http', 'mcp']}, minItems=1, uniqueItems=True),
        'protected_resource_metadata': URI, 'jwks_uri': URI,
        'entries_endpoint': URI, 'grants_endpoint': URI, 'audit_endpoint': URI, 'export_endpoint': URI,
        'delegations_endpoint': URI, 'rules_endpoint': URI, 'mcp_endpoint': URI, **({'directives_endpoint': URI, 'shares_endpoint': URI} if D3 else {}),
        'supported_categories': (arr({'type': 'object', 'properties': {'id': c('category'), 'name': S, 'description': S,
                                       'sensitivity': {'enum': ['low', 'medium', 'high']}, 'registry': S, 'definer': URI},
                                      'required': ['id', 'name', 'description', 'sensitivity'],
                                      'oneOf': [{'required': ['registry']},
                                                {'required': ['definer'], 'properties': {'sensitivity': {'enum': ['medium', 'high']}}}]}, minItems=1)
                                 if D3 else arr(c('category'), minItems=1)), 'category_registry': S,
        'accepts_entry_schemas': arr(URI, minItems=1), 'minimization_method': {'type': 'string', 'not': {'const': 'none'}},
        'conflict_detection': S,
        'audit_durability': obj({'default': {'const': 'synchronous'}, 'bounded': obj({'context.read': {'type': 'integer', 'minimum': 0}}, additionalProperties=False)}, ['default']),
        'audit_integrity': {'enum': ['append-only', 'hash-chained', 'signed-checkpoints', 'anchored']},
        'pagination': obj({'audit': {'const': 'cursor'}}), 'problem_type_base': URI, 'rate_limits': obj({'documentation_url': URI}),
        'vc_securing': obj({'issues': arr({'enum': ['eddsa-rdfc-2022', 'ecdsa-sd-2023', 'vc-jose-cose']}),
                            'verifies': arr({'enum': ['eddsa-rdfc-2022', 'ecdsa-sd-2023', 'vc-jose-cose']}, contains={'const': 'eddsa-rdfc-2022'})},
                           ['issues', 'verifies']),
        'credential_status_interval': {'type': 'integer', 'minimum': 1, 'maximum': 86400},
        **({'storage_encryption': {'enum': ['server', 'e2e']}} if D3 else {})},
    'required': ['hcp_version', 'provider', 'provider_operator', 'conformsTo', 'bindings', 'jwks_uri', 'supported_categories',
                 'category_registry', 'accepts_entry_schemas', 'minimization_method', 'audit_durability', 'audit_integrity'] + (['storage_encryption'] if D3 else []),
    'allOf': [{'if': {'properties': {'bindings': {'contains': {'const': 'http'}}}},
               'then': {'required': ['entries_endpoint', 'grants_endpoint', 'audit_endpoint', 'export_endpoint', 'rules_endpoint', 'pagination', 'problem_type_base'] + (['directives_endpoint'] if D3 else [])}},
              {'if': {'properties': {'conformsTo': {'contains': {'const': 'https://hcp.example/spec/profiles/vc-evidence/2.0'}}}},
               'then': {'required': ['vc_securing', 'credential_status_interval']}},
              {'if': {'properties': {'conformsTo': {'contains': {'const': 'https://hcp.example/spec/profiles/memory-manager/2.0'}}}},
               'then': {'required': ['conflict_detection']}},
              {'if': {'properties': {'conformsTo': {'contains': {'const': 'https://hcp.example/spec/profiles/oauth-interop/2.0'}}}},
               'then': {'required': ['protected_resource_metadata']}}]}, '19')

for name, s in schemas.items():
    p = os.path.join(OUT, name + '.json'); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(s, open(p, 'w'), indent=2, ensure_ascii=False); open(p, 'a').write('\n')
print(f'wrote {len(schemas)} schemas to {OUT}')
