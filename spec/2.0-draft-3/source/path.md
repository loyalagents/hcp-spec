# Path to v2 Final

Δ MOVED (v2-draft-3) --- Draft 2's §26 becomes P1, 1.8 becomes P2, and 27.1 becomes P3 (RS1, RS2).

This page says what remains open before v2 is final (P1), what changed from v1 (P2), and what each draft changed (P3). It is informative.

# P1. Roadmap

Δ CHANGED (v2-draft-3) --- What Draft 4 takes in.

This section is written for all audiences, not only implementers. Pilot partners, policymakers, and anyone deciding whether HCP fits their use case need to know what remains open without reading the protocol sections. It is plain language, not requirements language. Each item below names where in this specification it will land, so that the roadmap points at a Part rather than a gap.

Draft 4 will take in comments on Draft 3, the findings of the HCP Development and Testing working group, Richard Whitt's (GliaNet) analysis of the fiduciary layer, and Turn.io's conformance suite. None had arrived when Draft 3 was assembled.

## P1.1 Before v2 Is Final

Δ CHANGED (v2-draft-3) --- Directives for agents are done (6.4) and leave the table (DA1). Delegation chains (one level, 17.10) and delegated attestation (3.7, 14.10) are done and leave the table (DL1, DL6).

| Item | What remains open | Home |
|--------------------------------|------------------------------------------------------------------|------------|
| Permanent namespace | The placeholder hcp.example is replaced by a permanent namespace. The maintainers hope to secure hcp.me. | 1.7, Appendix A |

## P1.2 Done in Draft 2

Δ CHANGED (v2-draft-3) --- Renamed from "Planned for Draft 2".

Every item planned for Draft 2 was done in Draft 2 (P3).

## P1.3 Done in Draft 3

Δ CHANGED (v2-draft-3) --- Provenance on request is done (7.4.1) and leaves the table (K5). Conflict reconciliation is done as far as evidence allows (4.7, 4.7.4); automated resolution and a dimension vocabulary move to P1.4 (M1, M6). End-to-end encrypted storage is done (4.8); audit volume moves to P1.4 (ST1, AU1). The Security and Privacy row adds verification on the person's side (Q24). Security and Privacy Considerations are written (21) and leave the table (SP1). Deployment patterns (G5) and the overview, roles, use cases and comparison (1.9--1.12) are written and leave the table (L11--L14). Renamed from "Planned for Draft 3".

Every item planned for Draft 3 is done in this draft (P3). What remains open is in P1.4.

## P1.4 Later

Δ CHANGED (v2-draft-3) --- Automated conflict resolution, waiting on pilot evidence (M1, M8). Client conformance gains its first claim; permissive onward sharing is recorded, with its consequences (DA5, DA6). Deeper delegation chains are recorded (DL1). Audit compaction, with what it must keep (AU1). Emergency access is added (SP11). Assisted authorization is added (Q33). Onward sharing of Low-sensitivity context is in Draft 3; the two onward-sharing rows say what remains (OS2). Elicitation stays in the Guides (RS1).

| Item | What remains open | Home | Source |
|--------------------------------|------------------------------------------------------------------|--------------|------------|
| Automated conflict resolution | Resolving a conflict without the Context Subject's act: confidence-weighted resolution, or deprecation of stale inferences. It waits for pilots to report how often conflicts arise, how people resolve them, and how often they accept proposals (G1.2). A registered dimension vocabulary waits for the values pilots adopt. | 4.7, 15 | v1 §7.2; workshop |
| Cross-HCP federation | How two HCP instances share context. No new actor is needed: one provider acts as a client toward another. | A Federation Profile | v1 §7.5 |
| On-device and federated execution | Keeping sensitive context on the person's device. Core is unaffected. | G1.3 | v1 §7.4 |
| Named onward recipients | Naming in a grant the parties a client may pass context to, for categories above Low. Draft 3 allows onward sharing of Low-sensitivity context only, by a separate act at approval, optionally limited to named domains (3.12, 6.1.4). | 17, a Federation Profile | D3c |
| Client conformance | Draft 3 adds the first client claim, following directives (6.4). Further client claims, and third-party attestation that a client meets its claims. | 18.1 | DA6 |
| Audit compaction | Whether old `context.read` events may be compacted into summaries for each client. It waits for pilots to report what the read log costs (G1.2). Any compaction would have to keep, for each client and period, the categories, purposes, number of entries and retrievals, and the latest use-until: what the disclosure summary needs (8.6). | 8 | R3, AU1 |
| Emergency access | Whether a clinician, or another party in an emergency, may reach context the person has not granted, and on what terms. HCP has none today; the costs of that default are set out in 21.11. | 6, 17 | SP11 |
| Assisted authorization | How a person with no device of their own approves a grant through someone else's, such as a health worker's tablet, and how strongly the person is identified when they do. | 6.1.6, G4 | Q33 |
| Deeper delegation chains | Whether a sub-delegate may delegate further. Families and care arrangements may want it, but each level makes it harder for the person to see who holds authority over their context, and for a delegate to stay accountable. Draft 3 allows one level (17.10). | 17 | DL1 |
| Permissive onward sharing | Whether onward sharing may go beyond what Draft 3 allows: Medium-sensitivity categories, or a directive set once rather than an election on each grant. Draft 3 allows Low-sensitivity context only, elected on the grant, with each share reported to the person's log (3.12, 5.2.8). Context passed on leaves the reach of revocation and use-until, and the receiving organization has no grant the person approved; in a sensitive category that would be dangerous. It waits on pilot evidence of how implementers use the Low tier. | 3.12, 6.4 | DA5, OS2 |
| Audit integrity format | A common format for hash chains and signed checkpoints, so that a person or auditor can check a log with one tool (8.7). | 8.7 | C26 |
| Claim selection in grants | Letting a grant name the credential claims a client may receive, so that the person decides at approval rather than the provider at disclosure (14.9). | 6.1.5.1, 14.9 | V5 |
| Correction notices | Telling the clients that received an entry when the person corrects or rejects it, so a corrected inference does not live on in their copies. The audit log already records who received what (8.2). | 4.2.1, 8.6 | W4 (VTI comparison) |
| Recipient assurance | Whether a grant can require evidence about the receiving system before release, such as remote attestation of its execution environment, a declaration of its protection regime, or listing in a trust registry. | 6.1.5, 13 | W4 (Saturn paper, VTI comparison) |
| Signed export bundle | An export a receiving provider can verify came unaltered from the exporting provider (5.4.1, 5.4.3). | 5.4 | W4 (VTI comparison) |
| Unlinkable credential disclosure | Disclosure that two presentations of one credential cannot link, such as the BBS cryptosuite, once it is a W3C Recommendation and verifiers support it (14.9). | 14.5, 14.9 | V5 |

Elicitation --- how applications draw context out of a person --- is out of scope and stays in the Guides.

v1 §7.12, specification architecture and the actor model, is resolved by this draft (1, 3).

## P1.5 Notes Carried from v1

Δ CHANGED (v2-draft-3) --- The conflict reconciliation and category vocabulary notes record what Draft 3 has done (K1, K2, K3). The reconciliation note records proposals and external dimension codes (M1, M2, M6). The end-to-end note records the resolution (ST1). The note on what HCP does not prevent points to 21.1 (SP3).

**Conflict reconciliation.** Core requires that conflicts be detected and surfaced, and lets the Context Subject resolve them (4.7). Automated reconciliation --- merging, confidence-weighted resolution, deprecation of stale inferences --- has real consequences for trust, and getting it wrong would undermine the principle that the person owns their context. Draft 3 lets a provider or client propose a resolution, which only the person's act carries out (4.7.4), and sets out what every pair of declaration types changes (4.7). Automated resolution will be defined from pilot evidence on how often conflicts arise, how people resolve them, and how often they accept proposals (P1.4). Learning Economy Foundation reviewers noted that an inference is judged by what it was drawn from, and that HCP records a confidence value without recording its basis. Draft 3 adds that record, `assertion.basis` (4.2.5), shows it to the person when they resolve a conflict, and requires a proposal to say whether it weighed it (4.7.3, 4.7.4). A dimension may now be a concept from an external code system (4.2). A registered dimension vocabulary is still a candidate; the values pilots adopt are better evidence for it than anything specifiable in advance (G1.2).

**Category vocabulary.** The nine categories (4.5) are a starting point drawn from the Global Memory Workshop, not a validated registry. Known gaps include civic and public services context; a richer financial context for financial services pilots; cultural and linguistic context, which cuts across other categories; and research and professional credentialing. Learning Economy Foundation reviewers noted that `education_learner_profile` collapses mastery, learning history, and accommodations, which carry different sensitivity, and that family context may warrant its own category rather than sitting in `coordination_context`. Because categories are what grants are scoped to, each of these is a consent question before it is a taxonomy question. Cross-sector SME engagement and pilot evidence are the planned inputs. Richard Ng (Native) asked whether categories should be discovered rather than fixed in advance, and whether an entry could sit in several. His example is a statement that the person does not want to apply to tobacco companies, which belongs to `values_and_ethics` and to `work_context` alike. The client writing it may not know that a job-search agent reads `work_context`, so the choice of category has stakes the writer cannot see. Draft 3 lets an entry sit in several categories, with the consent rules in 4.5: a client assigns only categories it may write, and the person adds others. It also has discovery describe each category, so that clients and consent screens can show what it means (19). Categories that emerge from what people store, rather than being declared in advance, would need pilot evidence first.

**Credential format.** v1 permitted two securing mechanisms as a deliberate deferral (14.5). The wider identity ecosystem has moved toward selective-disclosure formats --- the EU Digital Identity wallet toward SD-JWT VC, ISO mDL toward mdoc --- in part because of the complexity of RDF canonicalization. Turn.io proposed profiling v1's Tier 2 on SD-JWT VC outright. That was not adopted, because SD-JWT VC is a distinct credential data model rather than a proof format, and adopting it would break the common envelope and the Open Badges alignment; permitting VC-JOSE-COSE obtains the canonicalization-free path and selective disclosure without either consequence. Draft 2 makes `eddsa-rdfc-2022` mandatory to verify, because it is what Open Badges verifiers already support, and keeps the others as options (14.5). Pilot evidence on which mechanisms were issued and verified, whether selective disclosure was exercised (14.9), and wallet and verifier support will inform whether v2 adds a second mandatory mechanism.

**End-to-end encrypted storage.** Relevance ordering (7.3), conflict detection (15), and server-side checks on content (5.2.3) assume the provider can read entry content. Draft 3 resolves this at the interface boundary: under the `storage_encryption` declaration `e2e`, those steps are performed within the Context Subject's trust domain, and the provider stores ciphertext (4.8). Pilot evidence on how often that domain is unreachable will show whether the design holds (G1.2).

**Federation.** Learning Economy Foundation reviewers pointed to wallet-attached storage, which lets a person hold and share artifacts through a storage provider of their choosing. Whether an HCP instance can be one such store, or whether the two compose some other way, is an input to the federation design.

**What HCP does not prevent.** HCP limits what context a model receives and what it may write, and holds clients accountable for downstream use. It does not constrain a model's other capabilities. A general-purpose model with access to tools may take destructive actions whether or not its client conforms to HCP. Section 21 says so (21.1).

# P2. Changes from v1

Δ MOVED (v2-draft-3) --- Draft 2's 1.8 (RS1).

v2 Draft 1 reorganized v1 rather than extending it. Its main changes:

- **Structure.** One linear document becomes six Parts, each with its own conformance identifier, so that a claim names exactly what an implementation supports (1).
- **Actors.** Roles, provenance layers, and fifteen actor invariants are defined before the data model (3). "User", "agent", and "system" give way to named roles.
- **Planes.** Governance operations --- grant management, the audit log, export, hard deletion, confirmation --- are reserved to the person's own management client and carried only over HTTP (1.6).
- **Conformance.** v1's three levels become composable claims and four packages (18).
- **Tiers.** v1's two tiers give way to one entry model: Tier 1's claim shape becomes the General Context Profile (11), and Tier 2 becomes the VC Evidence Profile (14).

Some v1 rules are reversed or relaxed:

- Accepting an inference records a confirmation instead of rewriting its declaration type to `person-declared` (3.8).
- `userVerified` is removed in favor of confirmation records (3.5).
- An application can no longer hard-delete an entry over MCP (5.4.2).
- Conflict detection moves to the Memory Manager Profile, required only of providers that accept inferred entries (4.7, 15).
- An implementation accepting applications operated by others now needs the HTTP Binding, not MCP alone (18.3).
- v1 entries are converted on import, with nothing upgraded (4.3).

Draft 2 specifies what Draft 1 deferred:

- **Entries.** One entry form, with content, assertion, classification, evidence and record kept apart; relationships between entries; a complete status lifecycle; and import (4, 5.4.3).
- **Authorization.** Purposes the person approves, structured authorization details, the OAuth security baseline, and standing rules (6, 13).
- **Disclosure.** Clients receive disclosures with grant-scoped references and a use-until time; revocation reaches the client, with notice to the person when it cannot; copies kept by law are declared in advance (7, 6.2).
- **Audit.** Structured events, a declared integrity level, and a disclosure summary for the person (8).
- **Credentials.** One mandatory signature format, credential status, selective disclosure, and Health and Education Context Profiles that meet v1's commitment (14, 16).
- **Delegation.** The Delegated Authorization Profile: guardians, caregivers and other delegates, with the person's override and the move to adult autonomy (17).

The changelog is in P3. A v1 → v2 section map recording where each v1 section went is available on request.

# P3. Changelog

Δ MOVED (v2-draft-3) --- Draft 2's 27.1. The acknowledgments, 27.2, move to the Introduction (I12) (RS1). The Draft 3 row. Release dates given in full (Q53).

| Version | Date | Summary |
|----------------|----------------------|------------------------------------------------------------------|
| 1.0-draft-1 | July 3, 2026 | First circulated draft |
| 1.0-draft-2 | July 24, 2026 | Entry envelope restructured; a conformance level added; third declaration type; data minimization rewritten |
| 1.0-draft-3 | August 13, 2026 | Second round of pilot and partner feedback |
| 1.0-draft-4 | September 6, 2026 | Grant request; client attribution and authority; minimal response mode; optional metadata field; Common Envelope criterion loosened; issuer-signature note; specification architecture and actor model named as a v2 workstream. v1 froze at this draft. |
| 2.0-draft-1 | October 11, 2026 | Restructured into Parts with Core, bindings, profiles, and implementation guides; the actor and provenance model; per-Part conformance identifiers and packages; the corrections that restructuring touched. The invariant counts in 1.0-draft-4 are corrected: seven adopted, eight deferred. |
| 2.0-draft-2 | October 29, 2026 | One entry model with evidence, relationships and a status lifecycle; purposes and structured authorization; disclosures with use-until and revocation reach; Security Event Token notifications; structured audit and a disclosure summary; import; credential status and one mandatory securing mechanism; Health and Education Context Profiles; the Delegated Authorization Profile; standing rules; inputs from the October 2026 Portable Memory workshop. |
| 2.0-draft-3 | November 6, 2026 | Four pages: Introduction, Specification, Guides, Path to v2 Final; Terms and References. Several categories per entry, described in discovery; the basis and permitted purposes of an assertion; provenance on request. Conflict proposals and issuer-attested conflicts. Directives for agents and the first client claim. One level of sub-delegation, and delegated attestation. End-to-end encrypted storage. Onward sharing of Low-sensitivity context with the person's approval. Security and Privacy Considerations. An overview, worked use cases, a comparison with related protocols, and deployment patterns. Examples labelled by direction; concrete HTTP examples; RFC 3339 times. |

A v1 → v2 section map, recording where each v1 section went and listing every rule tightened in the move, is available on request.

*This document is a working draft developed under the Loyal Agents initiative, a joint venture of Stanford University and Consumer Reports. It has not been formally reviewed or endorsed by Stanford University, Consumer Reports, or any convening partner.*

*DRAFT --- Not for distribution*
