Δ REMOVED (v2-draft-3) --- Part VI, Governance, is dissolved: Appendix A, the Path page and the Introduction take its sections (RS1).

# Appendix A. Registries and Published Artifacts

Δ MOVED (v2-draft-3) --- Draft 2's §25. Part VI is dissolved: the roadmap and changelog move to the Path page, and the acknowledgments to the Introduction (RS1, RS2).

This appendix records the registries and published artifacts this specification depends on. Only the registries are normative (1.1).

## A.1 Registries

Δ CHANGED (v2-draft-3) --- Registries for basis kinds and grant actions; 22 audit event types (K3, K4, K5). An export schema registry (J7). Proposal acts and considerations; 23 audit event types (M2). Directive actions and effects, client claims; 25 audit event types (DA3, DA6). Delegation methods and end reasons; attestation authorization kinds (DL4, DL6). Storage postures (ST1). A Core error code, `subject-unavailable` (ST3). 26 audit event types (OS7).

Each registry lists the values defined in this draft. The meaning of each value is defined in the section cited, and that definition governs. Until registries are published separately, this table is the registry.

| Registry | Values | Defined in | Open to new values |
|------------------------------|------------------------------------------------------------------|--------------|------------------------------|
| Conformance identifiers | One per Part, as listed | 1.7 | By later versions of this specification |
| Categories | Version 1: `general_preferences`, `goals_and_constraints`, `health_context`, `education_learner_profile`, `work_context`, `purchase_history_preferences`, `values_and_ethics`, `location_context`, `coordination_context` | 4.5 | By a new version of the category registry, versioned separately (4.5). Custom categories are URIs and are not portable |
| Declaration types | `person-declared`, `model-inferred`, `issuer-attested` | 4.4 | No |
| Entry status | `active`, `deprecated`, `conflicted`, `expired`, `revoked`, `suspended`, `deleted` | 4.2, 4.2.4 | No |
| Entry schemas | `https://hcp.example/spec/entry/2.0` | 4.2, 4.3 | By later versions of this specification |
| Export schemas | `https://hcp.example/spec/export/2.0` | 5.4.1 | By later versions of this specification |
| Content profiles | The General Context Profile (11) and VC Evidence Profile (14) identifiers | 4.2 | Yes, as URIs |
| Evidence roles | `content`, `supports` | 4.2.2 | No |
| Evidence types | `verifiable-credential` | 4.2.2 | Yes |
| Verification results | `verified`, `failed` | 4.2.2 | No |
| Credential status mechanisms | `BitstringStatusListEntry` | 14.7 | By later versions of this specification |
| Relationship types | `derivedFrom`, `supersedes`, `contradicts`, `duplicates` | 4.2.3 | No |
| Directive actions | `share`, `sign`, `transact` | 6.4 | Yes, as URIs |
| Directive effects | `deny`, `ask-first`, `permit` | 6.4 | No |
| Client conformance claims | `https://hcp.example/spec/clients/directives/2.0` | 1.7, 18.1 | By later versions of this specification |
| Proposal acts | `reject`, `accept`, `supersede` | 4.7.4 | No |
| Proposal considerations | `basis`, `declarationType`, `standing`, `permittedPurposes`, `recency`, `confidence` | 4.7.4 | Yes |
| Basis kinds | `conversation`, `document`, `observation`, `assessment`, `entries` | 4.2.5 | Yes |
| Grant actions | `read`, `write`, `provenance` | 6.1.5 | By later versions of this specification |
| Asserter assurance | `unverified`, `authenticated`, `cryptographically-verified` | 3.6 | No |
| Confirmation dispositions | `confirmed`, `rejected` | 3.8 | No |
| Relevance methods | `lexical`, `semantic`, `llm`, `none` | 7.3 | Yes |
| Audit event types | The 26 event types in 8.1 | 8.1 | No |
| Audit integrity levels | `append-only`, `hash-chained`, `signed-checkpoints`, `anchored` | 8.7 | No |
| Security event types | `https://hcp.example/spec/events/grant-revoked` | 9.9 | By later versions of this specification |
| Initiator roles | `management-client`, `context-client`, `authorization-service`, `hcp-provider` | 3.9 | No |
| Core error codes | `malformed-request`, `invalid-token`, `scope-denied`, `idempotency-conflict`, `version-conflict`, `credential-invalid`, `subject-unavailable`, `rate-limited`, `unsupported-version` | 5.5 | No |
| VC securing mechanisms | `eddsa-rdfc-2022`, `ecdsa-sd-2023`, `vc-jose-cose` | 14.5, 19 | By later versions of this specification |
| Conflict detection methods | No values registered; providers declare their own | 15.2, 19 | Yes |
| Authorization detail types | `https://hcp.example/spec/authorization/context-access` | 6.1.5, 13.3 | By later versions of this specification |
| Standing rule effects | `deny` | 6.3 | By later versions of this specification |
| Delegation relationships | `parent-or-guardian`, `legal-guardian`, `attorney-in-fact`, `caregiver` | 17.2 | Yes, as URIs |
| Delegation basis methods | `appointed`, `attested`, `evidence`, `delegated`, `unspecified` | 17.3 | No |
| Storage postures | `server`, `e2e` | 4.8, 19 | No |
| Attestation authorization kinds | `authorization-credential`, `arrangement` | 3.7, 14.10 | No |
| Delegation end reasons | `majority`, `expiry`, `basis-ended`, `relinquished`, `ended-by-subject`, `parent-ended`, `ended-by-delegate` | 17.6 | No |
| Purpose codes | None registered; any absolute URI, including codes defined by other specifications | 6.1.5.2 | Yes |
| Bindings | `http`, `mcp` | 1.5, 19 | By later versions of this specification |
| MCP extension identifier | `example.hcp/hcp` | 10.2 | Changes with the permanent namespace |

No vocabulary is registered for `classification.dimension` (4.2), `record.metadata` (4.2), the keys of a narrowed grant's `narrowedTo` (6.1.5.1), or `subject.relationship` (11.3). Each is a candidate for a later registry (P1).

## A.2 Published Artifacts

Δ CHANGED (v2-draft-3) --- JSON-LD terms for `categories`, `basis` and `permittedPurposes` (K1, K3, K4). Schema identifiers are named; the export, audit event and discovery schemas are listed; terms for the export (J7, J11). A term for `proposal` (M2). A directive schema (DA9). A term for `via` (DL7). A Core schema for reporting onward sharing; a term for `onwardSharing` (OS7). Its example is labelled with what it is and who sends it to whom (RS5).

Identifiers use the placeholder namespace (1.7). Dates are given in each draft's memo, not here.

| Artifact | Identifier | Needed for | Notes |
|----------------------------|-------------------------------------------|----------------------------------------------|---------------------------------------------------|
| Entry JSON Schema | https://hcp.example/schemas/2.0-draft-3/entry.json | Validating entries (4.1.1, 11.1) | The suite's first function depends on it (20) |
| Core schemas | https://hcp.example/schemas/2.0-draft-3/ | The MCP tools' `inputSchema` and `outputSchema` (10.3) | One request and one result schema per operation (5) |
| Audit event and discovery schemas | https://hcp.example/schemas/2.0-draft-3/audit-event.json, .../discovery.json | Testing the audit log (8.2) and the discovery document (19) | Used by the conformance suite (20) |
| Problem-type namespace | https://hcp.example/problems/ | HTTP error responses (9.7) | The type names are normative here and testable without the namespace resolving |
| JSON-LD context | https://hcp.example/contexts/v2 | The `@context` of every entry (4.2) | Not a processing requirement (4.1.1) |
| Conformance identifiers | https://hcp.example/spec/... | Conformance claims (18.1) | Compared as exact strings; need not resolve (1.7) |

**Core schemas.** One schema each for the request and the result of query, get entry, create, revise, withdraw, reading one's own grant, relinquishing it, and reporting onward sharing (5.2), of import, the disclosure summary, and the delegations list (5.4.3, 8.6, 9.4.13), plus the entry (4.2, 11, 14), the export (5.4.1), the disclosure (7.4), the grant (6.1.5), the delegation (17.2), the standing rule (6.3), the directive (6.4), the minimization report (7.5), and the Core error (5.5), with HTTP problem details (9.7). Schemas are written in JSON Schema 2020-12, under a base that names the draft. They are open: they admit members this specification does not define, which an HCP Provider preserves (A.3). Where a schema and the text of this specification differ, the text governs.

**JSON-LD context.** The context is published for semantic interoperability. Conformance requires no JSON-LD processing (4.1.1), and a credential in `evidence` does not reference the HCP context (14.2), so no conformance requirement depends on the context resolving. A draft of the key terms, updated for this draft's entry structure:

**Published artifact: the JSON-LD context**

    {
      "@context": {
        "hcp": "https://hcp.example/vocab/v2#",
        "ContextEntry": "hcp:ContextEntry",
        "schema": "hcp:schema",
        "subject": "hcp:subject",
        "content": "hcp:content",
        "profile": "hcp:profile",
        "value": "hcp:value",
        "assertion": "hcp:assertion",
        "classification": "hcp:classification",
        "evidence": "hcp:evidence",
        "role": "hcp:role",
        "credential": "hcp:credential",
        "verification": "hcp:verification",
        "record": "hcp:record",
        "declarationType": "hcp:declarationType",
        "categories": "hcp:categories",
        "basis": "hcp:basis",
        "permittedPurposes": "hcp:permittedPurposes",
        "dimension": "hcp:dimension",
        "confidence": "hcp:confidence",
        "validUntil": "hcp:validUntil",
        "relationship": "hcp:relationship",
        "provenance": "hcp:provenance",
        "assertedBy": "hcp:assertedBy",
        "assurance": "hcp:assurance",
        "via": "hcp:via",
        "kind": "hcp:kind",
        "assertedAt": "hcp:assertedAt",
        "source": "hcp:source",
        "submittedByClient": "hcp:submittedByClient",
        "authorizedUnder": "hcp:authorizedUnder",
        "recordedByProvider": "hcp:recordedByProvider",
        "recordedAt": "hcp:recordedAt",
        "confirmations": "hcp:confirmations",
        "relationships": "hcp:relationships",
        "proposal": "hcp:proposal",
        "conversion": "hcp:conversion",
        "minimization": "hcp:minimization",
        "retrievalId": "hcp:retrievalId",
        "status": "hcp:status",
        "conflicted": "hcp:conflicted",
        "ContextExport": "hcp:ContextExport",
        "exportedBy": "hcp:exportedBy",
        "exportedAt": "hcp:exportedAt",
        "entries": "hcp:entries",
        "versions": "hcp:versions",
        "rules": "hcp:rules",
        "audit": "hcp:audit"
      }
    }

`capturedBy` and `userVerified` are removed (3.5). `credentialType`, `NLPreference`, `VerifiablePreference`, and `claim` are removed with the tiers (4.2).

## A.3 Extension Points

A custom value at any extension point below MUST be an absolute URI under a domain its definer controls. The `hcp-custom:` prefix of v1 is removed. Each extension point states what an implementation does with a value it does not recognize:

| Extension point | Custom values | An unrecognized value | Defined in |
|------------------------------|------------------------------------|------------------------------------------------------------------|------------|
| Category | URI | Rejected on write with invalid request | 4.5 |
| Content profile | URI | Rejected on write with invalid request; an entry already held is preserved and returned as stored | 4.2 |
| Entry member not defined by this specification | Member name of the definer's choosing | Preserved and not interpreted | 4.2 |
| Evidence type | URI | Preserved and not interpreted; never raises assurance | 4.2.2 |
| Grant restriction (`narrowedTo` key) | URI | Rejected at issuance; a provider that cannot enforce it treats the detail as reaching no entry (fails closed) | 6.1.5.1 |
| Purpose code | URI | Accepted; its description is what the person is shown | 6.1.5.2 |
| Relevance method, conflict detection method | Any string | Declarative only; carries no behavior a client relies on | 7.3, 15.2 |
