# Encryption design review and investigation

- **Status:** open, non-normative investigation. Findings and candidate remedies
  below are review conclusions and proposals, not adopted protocol changes.
- **Goal:** investigate and fully document HCP's encryption design, and develop
  specification, schema, example, and conformance changes where the findings
  warrant them.
- **Reviewed:** 2026-11-08; HCP `2.0-draft-3`, normative source revision
  `2e2939c9bebcefb3bed7bb3522231c0e4d65a315`; repository baseline
  `b764a058eac15a4cd843892e60473089b2e835bb`.
- **Initial evidence:** source and schema inspection, with independent review.
  No deployed E2E implementation, cryptographic implementation, or conformance
  result is assessed. Source links below pin the reviewed revision.

## Problem and intended outcome

Draft 3 moves decryption and content-dependent processing into a component
controlled by the Context Subject. It leaves encrypted storage, grants, lifecycle
state, and audit responsibilities with the HCP Provider. The public HTTP and MCP
bindings still exchange ordinary entry and disclosure objects.

The central unresolved question is **how an authorized client receives plaintext
without a provider-operated endpoint also receiving that plaintext**. Keeping
storage keys away from the provider does not answer this: a wallet could decrypt
a disclosure and return it to a provider process that serializes it to the client.
The provider would see the disclosure without ever possessing a storage key.

The investigation should establish the intended confidentiality guarantee, trace
every content-bearing path, and reconcile the responsibilities on either side of
the trust boundary. An implementation-neutral specification can leave internal
algorithms open while making that boundary observable and testable. The current
architecture freedom means a secure split implementation may be possible; the
review does not establish that E2E is inherently incompatible with HCP.

This document starts the investigation. The initial change adds this record and
its README entry point. It does not amend Draft 3's normative requirements,
generated pages, or schemas. The same work can develop concrete fixes after the
decisions below are recorded and reviewed.

## What Draft 3 currently says

The central sources are [encrypted storage, §4.8][storage], [deployment guidance,
G1.4][deployments], [discovery, §19.3][discovery], and [security considerations,
§21.8–21.9][security]. The guides and security considerations are informative.

| Topic | Current text and its limits |
| --- | --- |
| Selecting E2E | `server` and `e2e` are both allowed. This review found no general requirement or `SHOULD` to choose E2E. Declaring `storage_encryption` is required. |
| Ordinary encryption at rest | `server` means the provider can read content. It does not establish whether disks, databases, or backups are encrypted. No blanket requirement or `SHOULD` for that encryption was found in Draft 3. |
| E2E fields | Under `e2e`, `content`, `evidence`, `assertion.basis`, and `classification.dimension` are encrypted. The rest of `classification` and `assertion`, and `record`, remain readable. |
| Key custody | The provider must not hold content keys. Provider-operated components are excluded from the person's trust domain. Category-wide or grant-wide keys must not be released to an HCP Client. |
| Content processing | The trust-domain component decrypts and constructs disclosures, ranks and limits results, applies content-based narrowing, detects conflicts where required, and performs content/credential checks. |
| Recipient | An authorized Context Client receives selected, decrypted disclosures, as under `server`. It does not receive bulk storage access. |
| Audit and verification | The component reports disclosures to the provider. Trust-domain credential verification is identified with `verification.by: "trust-domain"`. |
| Unavailability | A request needing an unreachable component fails with `subject-unavailable`; required checks cannot be skipped. HTTP maps this to 503. |
| Deletion | Destroying all relevant key copies can implement hard deletion, including backups, provided unencrypted members are also removed and the entry is unrecoverable. |

Encryption at rest, confidentiality in transit, and who may decrypt are distinct
questions. A provider can encrypt its disks and still read their contents. TLS
protects data between its endpoints; a provider terminating a TLS connection can
read the application data on that connection ([RFC 8446, §1][tls]).

### Logical responsibilities and the missing path

This is a reading of responsibilities, not a specified network topology:

```text
PROVIDER SIDE                         PERSON'S TRUST DOMAIN
+-------------------------+           +-------------------------+
| Encrypted entry storage |           | Content keys            |
| Readable metadata       |           | Decrypt and validate    |
| Grants and lifecycle    |           | Filter, rank and limit  |
| Audit log               |<--report--| Construct disclosure    |
+-------------------------+           +------------+------------+
                                                  |
                                      ??? protected delivery ???
                                                  |
                                                  v
                                     +-------------------------+
                                     | Authorized HCP Client   |
                                     | Selected plaintext      |
                                     +-------------------------+
```

An unsafe completion of that missing path is:

```text
Person's component --plaintext--> Provider --HTTPS--> Client
                                      |
                              can read the disclosure
```

Two limits must remain explicit in any revision:

- Categories, timing, provenance, and other specified metadata are deliberately
  visible to the provider. E2E currently does not promise to hide all metadata.
- A person can deliberately grant access to a client operated by the same
  organization as their provider. That client may receive authorized plaintext
  in its recipient capacity. Provider/storage confidentiality must not be
  confused with a promise to hide that authorized disclosure from its recipient.
  Subsequent copy use and onward sharing remain client obligations; encryption
  cannot recall plaintext already received ([§21.1][downstream]).

## Findings

The identifiers below are stable discussion references. All remain open.
"Normative conflict" means the cited requirements prescribe incompatible
outcomes for the scenario. "Design gap" identifies a missing boundary or a
permitted disclosure risk. "Coverage gap" means tooling does not enforce a
requirement that still applies. Candidate remedies need review before adoption.

### ENC-01: No confidential binding path is specified

**Classification:** high-priority design gap.

[§4.8][storage] prohibits provider custody of keys and assigns disclosure
construction to the subject's component. [HTTP get/create/revise][http-entries]
and [MCP tools][mcp-tools] still carry ordinary content. Discovery names provider
endpoints but no interoperable arrangement for the independent component and
the recipient. Merely adding another endpoint would not establish trust in it.

**Scenario:** a hosted HTTP/MCP process authenticates the request, asks the
person's wallet to prepare a disclosure, and serializes the wallet's plaintext
reply. The provider sees the result. Create, revise, import, export, management
views, response caches, diagnostics, and model-assisted processing can expose
plaintext through the same placement mistake.

**Investigation and candidate remedy:** decide whether `e2e` promises encrypted
storage/key separation alone or confidentiality throughout processing and
delivery. For the stronger promise, specify where protected channels terminate,
how recipients and subject components authenticate, and how plaintext bypasses
provider-visible processing. Cover ingress as well as egress. Clarify which
query text, reasons, and other content-derived fields the promise covers; the
current encrypted-field list does not automatically cover them.

### ENC-02: Active-provider and recipient-substitution threats are unresolved

**Classification:** high-priority threat-model decision; conditional security gap.

The [Authorization Service may be deployed within the provider][roles].
[§21.7][identity] explicitly leaves how a wallet proves its identity to the
provider unspecified. The E2E text does not establish an independently trusted
consent-to-recipient binding at the component that releases plaintext.

**Scenario:** if that component accepts provider-supplied grants and recipient
identities without independent checks, a compromised Provider/Authorization
Service can fabricate authority or substitute its own recipient and induce a
disclosure. A protected channel to an attacker-selected recipient would not
solve this. If mutable clear policy metadata is trusted without integrity and
freshness checks, relabeling or rollback is another path to investigate.

**Investigation and candidate remedy:** name the adversaries. Distinguish a
provider that follows the protocol but observes traffic from one that can alter
grants, identities, metadata, or messages. If active compromise is covered,
define independently trustworthy consent and recipient binding, component
enrollment/replacement, freshness, and rejection of replay or substitution.
A signature from the compromised authority alone cannot establish its honesty.
The [MLS architecture's authentication-service analysis][mls-auth] illustrates
this class of threat; it is not a proposal to adopt MLS for HCP.

### ENC-03: Clear conflict explanations can repeat encrypted facts

**Classification:** high-priority confidentiality design gap.

[§4.8][storage] leaves `record` readable. A [conflict proposal][proposals] sits in
`record.relationships[].proposal` and includes a natural-language `rationale`.

**Scenario:** a legitimate proposal says, "Keep the newer entry because the
person moved to Boston." Encrypted entry content is reproduced in a clear
explanation. This needs no malicious client. Free-form metadata, audit reasons,
and extension members need the same content-flow review; their existence does
not itself prove that a particular implementation leaks.

**Candidate remedy:** encrypt content-bearing explanations while retaining
the identifiers and actions necessary for lifecycle enforcement. Define which
operational metadata may remain clear and where content-derived free text must
go. This is distinct from the intentional category/timing/provenance exposure.

### ENC-04: Hard deletion conflicts with mandatory original-response replay

**Classification:** high-priority normative conflict; affects both storage modes.

[§9.6][idempotency] requires retaining a write's key and associated response for
at least 24 hours and returning the original response on an identical retry.
[Create returns the entry or disclosure][create], including content.
[§5.4.2][deletion] requires hard-deleted entries to be unrecoverable and never
returned again.

```text
1. Create entry with Idempotency-Key K; operation commits.
2. The person hard-deletes that entry.
3. With otherwise valid authority, retry the identical request with K
   within 24 hours.

Replay rule:   return original response, including content.
Deletion rule: entry is unrecoverable and never returned again.
```

**Candidate remedy:** explicitly let deletion override response replay, retain
a content-free idempotency tombstone, and define the retry outcome. Include
retained response bodies and all provider-managed copies in erasure semantics.
An E2E implementation's response storage must also respect its selected
confidentiality boundary. Deletion of HCP-managed state must not be presented as
recalling copies previously disclosed to clients.

### ENC-05: Disclosure reporting lacks a failure and recovery contract

**Classification:** implementation-handoff gap, not a demonstrated contradiction.

[§4.8][storage] requires reporting which entries were disclosed. [§8.2][audit]
also needs the exact versions, `useUntil`, provenance disclosure, and any
selectively revealed credential claims. [§8.4][durability] requires synchronous
durability unless a bounded read window is declared, and caps that window at
10,000 milliseconds.

**Scenario:** the person's component releases plaintext and then loses power
before its report reaches the provider. The provider may miss the event or
reconstruct it against a different version. Existing completeness and durability
requirements prohibit the resulting omissions; the split design supplies no
release/report checkpoint or recovery example showing how they are met.

**Candidate remedy:** specify a complete disclosure manifest, retrieval identity,
the observable release checkpoint, acknowledgement/retry reconciliation, and
failure behavior. Do not equate handoff with confirmed remote receipt. Preserve
both synchronous and declared bounded durability, including through component
failure. Coordinate authorization rechecks and release with revocation rather
than silently using stale permission. Related work is already tracked in
[#2, in-flight revocation][issue-2] and [#14, audit recovery guidance][issue-14].

### ENC-06: Operator and component definitions complicate safe endpoint placement

**Classification:** role-definition ambiguity, including a self-hosting edge case.

[§3.1 and §3.2.4][roles] define a component as something HCP does not communicate
with directly and the Provider as the service exposing the HCP interface.
[§4.8][storage] excludes every component operated by the Provider Operator from
the person's trust domain. Moving the HCP endpoint into a person's wallet to
address ENC-01 therefore needs an explicit role description.

The text also allows a person to operate their own provider. Their own wallet
then appears both to qualify as a subject-controlled component and to be excluded
as a provider-operated component. This does not prevent a self-hosted deployment
from using `server`, or prove all E2E deployments impossible; it leaves what
`e2e` classifies in that deployment unclear.

**Candidate remedy:** distinguish the logical Provider, plaintext-processing
component, and storage operator, with an actor-labelled deployment example.
Explain self-hosted and provider-operated-client cases explicitly. Reconcile
grant enforcement responsibilities rather than delegating them implicitly to
an ordinary client bridge.

### ENC-07: Verifier-location attribution is not enforced by schema validation

**Classification:** narrower artifact/coverage gap.

[§4.8][storage] requires marking verification performed by the trust domain;
[§7.4][disclosures] exposes that distinction to recipients. The [schema
generator][schema-generator] defines `verification.by` but requires only `result`
and `at`. The [generated schema][verification-schema] therefore accepts a
verification object without `by`. The [VC example][vc-example] also omits it.

**Scenario:** an E2E implementation emits `cryptographically-verified` assurance
and a verification object without its location. Structural validation cannot
detect the missing distinction. This remains contrary to the E2E text; schema
acceptance is not a permission to omit it. The ordinary server-mode example
alone does not establish an E2E normative violation.

**Candidate remedy:** require location on the relevant outputs, or define clear
defaults plus storage-posture-aware semantic checks. Add a negative E2E fixture.
Continue advising consequential credential consumers to verify the credential
themselves; the person's component can falsely vouch for one ([§21.9][security]).

## Decisions and candidate architectures

No architecture or cryptographic suite has been selected by this review.

| Decision | Question to settle |
| --- | --- |
| D1: Guarantee | Does `e2e` mean encrypted stored fields only, or confidentiality from the storage/provider path during all processing? Which content-derived inputs and outputs are protected? Separately, should ordinary at-rest encryption become a baseline requirement or recommendation? |
| D2: Adversaries | Are passive observation, storage compromise, active Provider/Authorization Service compromise, malicious recipients, and compromised subject devices covered or explicitly excluded? |
| D3: Roles and endpoints | Which component is the HCP endpoint, who operates it, who terminates TLS/other protected channels, and how does the topology fit HTTP, MCP, governance, and self-hosting? |
| D4: Authority and integrity | How are consent, recipient identity/keys, subject/entry/version, mutable policy metadata, revocation, and replay protection bound and checked at release? |
| D5: State transitions | What happens when audit, disclosure, mutation, retry, expiry, deletion, or recovery spans a component outage? Which event is the release boundary? |
| D6: Keys and copies | What are the key scopes, enrollment/rotation/recovery rules, backup and multi-device assumptions, cache/index/log boundaries, and criteria for completed erasure? |
| D7: Evidence | Which claims are schema-checkable, which need behavioral tests, and which need deployment/security evidence? How is posture advertised and downgrade prevented? |

Three directions are worth comparing before editing normative text:

| Candidate | What it would require | Principal tradeoff |
| --- | --- | --- |
| A: Person-controlled binding endpoint | Terminate the confidential client channel inside the person's trusted processor; use a separate ciphertext store. Clarify the logical Provider versus storage operator and preserve independent HCP authorization enforcement. | Can keep ordinary HCP objects at the trusted endpoint; needs discovery, enrollment, reachability, and role changes. Calling the endpoint a Provider does not by itself satisfy today's `e2e` definition. |
| B: Confidential delivery through a blind relay | Protect selected responses to the authorized client before they enter the provider relay, and protect incoming content to the subject component. Specify authenticated recipient binding, framing/negotiation, and audit coordination. | Can use a hosted relay; requires client/binding support or a precisely defined lower-layer channel. It cannot silently substitute ciphertext for the ordinary disclosure expected by today's client. |
| C: Explicitly narrower storage promise | Define precisely what key-separated encrypted storage guarantees, what plaintext the operator may see during operations, and how it is named and disclosed. | Smaller transport change, but does not deliver the stronger operator-blind promise motivating this review. It would need an explicit product/specification decision and accurate terminology. |

For A or B, the intended confidentiality boundary would be:

```text
PERSON'S TRUSTED PROCESSOR                   AUTHORIZED CLIENT
  storage keys                                authenticated peer
  policy checks and minimization              selected plaintext
          |                                           ^
          +==== authenticated protected channel =======+
                              |
                    optional provider relay
                    sees only protected traffic

Provider storage/control path: ciphertext + declared metadata + audit reports
```

This is a candidate security boundary, not an adopted message sequence. Storage
keys need not be shared with the client: it receives only the selected disclosure
through its authenticated channel. An authorized recipient's subsequent misuse
of plaintext remains a separate threat. Enrollment, key substitution, consent,
policy freshness, and downgrade resistance still need resolution under D2–D4.

### Paths that need complete sequences

For each path, record operators, plaintext locations, authenticated peers,
authorization evidence, mutable-state checks, durable effects, retries, and
behavior when the subject component is unavailable. Include transport termination,
model services, caches, logs, backups, and diagnostics rather than only databases.

| Path | Content-bearing work and investigation focus |
| --- | --- |
| Query and get | Query input, narrowed-grant filtering, ranking/limits, decryption, disclosure construction, current permission, audit and protected release. |
| Create and revise | Protect incoming content and evidence; authenticate the asserter/submitting client; validate and detect conflicts; commit version/audit; protect the result and retained idempotency response. |
| Import | Protect the bundle, including inactive/history content and governance records; define verification, dry-run, per-entry outcomes, and failure semantics. |
| Export and management views | Deliver whole entries to authenticated management authority; keep governance access separate from context grants. Define which delegated roles may receive which plaintext. |
| Confirmation and conflict resolution | Bind the person's action to the intended version; protect rationale and other free text; coordinate status/provenance changes. |
| Revocation and expiry | Identify the last authorization check and release boundary; prevent stale authority or content after outages without promising recall of received bytes. |
| Hard deletion and retry | Erase relevant keys/copies/metadata; settle response-cache behavior; handle offline recovery devices and incomplete erasure truthfully. |
| Enrollment, restart and recovery | Authenticate replacement devices/recipients; reconcile audit, policy, key state, and versions before admission; prevent downgrade or resurrection. |

Encrypted credentials and provider-written verification are not inherently
contradictory: an implementation may use internal projections. Likewise, an
effective credential-expiry deadline can be established at ingest without later
decrypting the credential. The handoff, integrity, failure, and recovery rules
for such derived state need examples and tests. Dormant-provider deadlines are
already tracked separately in [#3][issue-3]; this investigation must not silently
resolve that issue by weakening expiry.

## Investigation checkpoints and completion criteria

| Checkpoint | Deliverable and review boundary |
| --- | --- |
| 1. Establish the problem | Review this pinned source assessment, correct disputed findings, and record accepted/refuted/deferred dispositions with reasons. The initial draft PR reaches this checkpoint; all remedies remain proposals. |
| 2. Select the contract | Record D1–D7 decisions and one complete topology with read, write, export, and failure sequences. Independently review the confidentiality and authority boundaries before implementing a protocol change. |
| 3. Develop focused fixes | Edit owning section sources and the schema generator where needed; regenerate pages/schemas. Include examples and tests for each adopted change. Related lifecycle fixes may proceed once their independent contract is settled. |
| 4. Validate the revision | Run the affected repository checks and the behavioral/deployment evidence appropriate to each claim. Review the complete candidate, reconcile related issues, and document remaining limitations before the PR leaves draft. |

The following are proposed acceptance scenarios, not tests already run:

- **T1 — Plaintext trace (ENC-01/D3):** seed unique synthetic content and trace
  query/get/create/revise/import/export across every process and channel. Prove
  protected plaintext and storage keys are absent from provider/storage processes,
  caches, logs, and external model calls, except an explicitly authorized recipient
  capacity. A string scan alone is insufficient evidence of the boundary.
- **T2 — Identity and authority attacks (ENC-02/D4):** exercise substituted
  component/recipient keys, forged consent/grants, modified metadata, stale policy,
  replayed requests, and downgrade. Define expected rejection or documented
  non-coverage from the selected threat model before running the cases.
- **T3 — Free-text leakage (ENC-03):** generate a normal conflict rationale that
  repeats a synthetic protected fact; exercise audit reasons and extension fields.
  Verify each follows the adopted encrypted/clear placement rules.
- **T4 — Erasure and replay (ENC-04):** create/revise with a key, hard-delete, and
  retry within the retention period. Verify the adopted content-free retry outcome
  and absence of recoverable copies, including the response cache and backups in
  scope. Distinguish provider-managed state from earlier recipient copies.
- **T5 — Audit interruption (ENC-05):** interrupt before and after durable audit,
  before release, and after release but before acknowledgement. Reconcile exact
  versions, recipients and deadlines without invented receipt or duplicate events;
  preserve the declared durability guarantee through failure.
- **T6 — Revocation race (ENC-05/D5):** pause a prepared disclosure, revoke or
  narrow authority, then resume. Coordinate the expected release outcome with
  #2 and recheck deadlines after stalls; do not renew them to complete a request.
- **T7 — Unavailable component and recovery (D5/D6):** interrupt processing,
  credential checks, or recovery; verify fail-closed behavior without weaker
  responses, unbounded audit delay, expired access, or resurrected deleted state.
- **T8 — Attribution (ENC-07):** omit or falsify verifier location in an E2E
  fixture; ensure semantic/conformance checks distinguish provider from subject
  verification. Verify schema acceptance is not treated as proof of conformance.
- **T9 — Role/topology cases (ENC-06):** demonstrate the selected contract with
  an independent provider, a self-hosted deployment, and an explicitly authorized
  provider-operated client. Confirm the advertised guarantee matches each case.
- **T10 — Binding parity (ENC-01/D7):** test HTTP and MCP, including management
  operations through their allowed paths, discovery, unsupported-client behavior,
  and exact error semantics. No silent confidentiality downgrade.

The investigation is complete when the guarantee and threat model are explicit,
the selected topology has complete success/failure paths, every finding has a
reviewed disposition, and adopted fixes update their normative sources, examples,
schemas and relevant conformance evidence together. A finding may be refuted or
deferred with an explicit limitation and revisit condition; recording it does not
mean it has been fixed. Structural JSON checks alone cannot prove key custody or
absence of plaintext in an operator's infrastructure.

For the initial documentation-only change, check source references, local links
and anchors, Markdown structure, whitespace, and affected documentation readers.
The repository's page/schema generators consume the specification sources, not
this design note. A later normative/schema change should use `make pages` and
`make check` as applicable under the README's prerequisites, plus the new behavior
checks. No application migration, live personal data, or release is involved.

## Related work and source references

- [#2: In-flight revocation ordering][issue-2] overlaps the E2E release checkpoint.
- [#3: Dormant-provider expiry deadlines][issue-3] owns the separate availability
  conflict; E2E adds another component whose availability must be accounted for.
- [#14: Audit initialization/recovery guidance][issue-14] supplies related
  persistence lessons, without selecting an E2E protocol or storage engine.

These links record related work, not resolutions or dependencies on a particular
application. Protocol decisions and reusable adoption guidance belong here;
implementation-specific rollout and qualification evidence remain with the
implementations.

[storage]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s4.md#48-encrypted-storage
[deployments]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/g1.md#g14-end-to-end-encrypted-deployments
[discovery]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s19.md#193-members
[security]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s21.md#218-keys
[downstream]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s21.md#211-what-hcp-does-not-prevent
[http-entries]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s9.md#942-get-entry
[mcp-tools]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s10.md#103-tools
[roles]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s3.md#31-roles-entities-and-components
[identity]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s21.md#217-discovery-and-identity
[proposals]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s4.md#474-proposals
[idempotency]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s9.md#96-idempotency
[create]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s5.md#523-create
[deletion]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s5.md#542-hard-deletion
[audit]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s8.md#82-log-entry-structure
[durability]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s8.md#84-durability
[disclosures]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s7.md#74-disclosures-to-context-clients
[schema-generator]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/tools/make_schemas.py#L70-L71
[verification-schema]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/schemas/2.0-draft-3/common.json#L210-L234
[vc-example]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s14.md#L132-L135
[issue-2]: https://github.com/loyalagents/hcp-spec/issues/2
[issue-3]: https://github.com/loyalagents/hcp-spec/issues/3
[issue-14]: https://github.com/loyalagents/hcp-spec/issues/14
[tls]: https://www.rfc-editor.org/rfc/rfc8446.html#section-1
[mls-auth]: https://www.rfc-editor.org/rfc/rfc9750.html#section-8.4.3
