> **DRAFT — Not for distribution.** Human Context Protocol (HCP) v2, Draft Specification, version 2.0-draft-3. Pages: [Introduction](introduction.md) · [Specification](specification.md) · [Guides](guides.md) · [Path to v2 Final](path-to-v2-final.md)

# Path to v2 Final

This page says what remains open before v2 is final ([P1](#p1-roadmap)), what changed from v1 ([P2](#p2-changes-from-v1)), and what each draft changed ([P3](#p3-changelog)). It is informative.

# P1. Roadmap

This section is written for all audiences, not only implementers. Pilot partners, policymakers, and anyone deciding whether HCP fits their use case need to know what remains open without reading the protocol sections. It is plain language, not requirements language. Each item below names where in this specification it will land, so that the roadmap points at a Part rather than a gap.

Draft 4 will take in comments on Draft 3, the findings of the HCP Development and Testing working group, Richard Whitt's (GliaNet) analysis of the fiduciary layer, and Turn.io's conformance suite. None had arrived when Draft 3 was assembled.

## P1.1 Before v2 Is Final

| Item | What remains open | Home |
|--------------------------------|------------------------------------------------------------------|------------|
| Permanent namespace | The placeholder hcp.example is replaced by a permanent namespace. The maintainers hope to secure hcp.me. | 1.7, Appendix A |

This table is not a complete readiness checklist. Open technical questions include [E2E confidentiality and delivery (#22)](https://github.com/loyalagents/hcp-spec/issues/22) and [hard deletion and replay (#23)](https://github.com/loyalagents/hcp-spec/issues/23). Their remedies and implications for a final release remain subject to review.

## P1.2 Done in Draft 2

Every item planned for Draft 2 was done in Draft 2 ([P3](#p3-changelog)).

## P1.3 Done in Draft 3

Draft 3 includes the planned sections and features summarized in P3. Inclusion is not evidence that every design question is resolved or every behavior validated; see the open questions linked in P1.1 and later work in P1.4.

## P1.4 Later

| Item | What remains open | Home | Source |
|--------------------------------|------------------------------------------------------------------|--------------|------------|
| Automated conflict resolution | Resolving a conflict without the Context Subject's act: confidence-weighted resolution, or deprecation of stale inferences. It waits for pilots to report how often conflicts arise, how people resolve them, and how often they accept proposals ([G1.2](guides.md#g12-what-pilots-should-record)). A registered dimension vocabulary waits for the values pilots adopt. | 4.7, 15 | v1 §7.2; workshop |
| Cross-HCP federation | How two HCP instances share context. No new actor is needed: one provider acts as a client toward another. | A Federation Profile | v1 §7.5 |
| On-device and federated execution | Keeping sensitive context on the person's device. Core is unaffected. | G1.3 | v1 §7.4 |
| Named onward recipients | Naming in a grant the parties a client may pass context to, for categories above Low. Draft 3 allows onward sharing of Low-sensitivity context only, by a separate act at approval, optionally limited to named domains ([3.12](specification.md#312-onward-disclosure), [6.1.4](specification.md#614-grant-distinction-temporary-vs-persistent)). | 17, a Federation Profile | D3c |
| Client conformance | Draft 3 adds the first client claim, following directives ([6.4](specification.md#64-directives)). Further client claims, and third-party attestation that a client meets its claims. | 18.1 | DA6 |
| Audit compaction | Whether old `context.read` events may be compacted into summaries for each client. It waits for pilots to report what the read log costs ([G1.2](guides.md#g12-what-pilots-should-record)). Any compaction would have to keep, for each client and period, the categories, purposes, number of entries and retrievals, and the latest use-until: what the disclosure summary needs ([8.6](specification.md#86-disclosure-summary)). | 8 | R3, AU1 |
| Emergency access | Whether a clinician, or another party in an emergency, may reach context the person has not granted, and on what terms. HCP has none today; the costs of that default are set out in 21.11. | 6, 17 | SP11 |
| Assisted authorization | How a person with no device of their own approves a grant through someone else's, such as a health worker's tablet, and how strongly the person is identified when they do. | 6.1.6, G4 | Q33 |
| Deeper delegation chains | Whether a sub-delegate may delegate further. Families and care arrangements may want it, but each level makes it harder for the person to see who holds authority over their context, and for a delegate to stay accountable. Draft 3 allows one level ([17.10](specification.md#1710-sub-delegation)). | 17 | DL1 |
| Permissive onward sharing | Whether onward sharing may go beyond what Draft 3 allows: Medium-sensitivity categories, or a directive set once rather than an election on each grant. Draft 3 allows Low-sensitivity context only, elected on the grant, with each share reported to the person's log ([3.12](specification.md#312-onward-disclosure), [5.2.8](specification.md#528-report-onward-sharing)). Context passed on leaves the reach of revocation and use-until, and the receiving organization has no grant the person approved; in a sensitive category that would be dangerous. It waits on pilot evidence of how implementers use the Low tier. | 3.12, 6.4 | DA5, OS2 |
| Audit integrity format | A common format for hash chains and signed checkpoints, so that a person or auditor can check a log with one tool ([8.7](specification.md#87-integrity)); and whether a receipt the provider gives a client for each read, naming the event it recorded, should count toward a declared level. | 8.7 | C26; implementer feedback (Enkara) |

| Claim selection in grants | Letting a grant name the credential claims a client may receive, so that the person decides at approval rather than the provider at disclosure ([14.9](specification.md#149-selective-disclosure)). | 6.1.5.1, 14.9 | V5 |
| Correction notices | Telling the clients that received an entry when the person corrects or rejects it, so a corrected inference does not live on in their copies. The audit log already records who received what ([8.2](specification.md#82-log-entry-structure)). | 4.2.1, 8.6 | W4 (VTI comparison) |
| Recipient assurance | Whether a grant can require evidence about the receiving system before release, such as remote attestation of its execution environment, a declaration of its protection regime, or listing in a trust registry. | 6.1.5, 13 | W4 (Saturn paper, VTI comparison) |
| Signed export bundle | An export a receiving provider can verify came unaltered from the exporting provider ([5.4.1](specification.md#541-export), [5.4.3](specification.md#543-import)). Which key signs it (the exporting provider's, the person's, or both), and whether it can still be checked after the exporting provider is gone. | 5.4 | W4 (VTI comparison); implementer feedback (Enkara) |
| Unlinkable credential disclosure | Disclosure that two presentations of one credential cannot link, such as the BBS cryptosuite, once it is a W3C Recommendation and verifiers support it ([14.9](specification.md#149-selective-disclosure)). | 14.5, 14.9 | V5 |
| Approval under pre-agreed rules | Whether an agent, or a rule the person agreed in advance, may approve grants for them. Draft 3 requires a person, the Context Subject or a delegate, to approve each grant, and standing rules only deny ([3.2.2](specification.md#322-authorizing-principal), [6.3](specification.md#63-standing-rules), [17.4](specification.md#174-scope-and-grants-under-a-delegation)). A profile would have to say who answers for such approvals, what they may never approve (High-sensitivity categories, persistence, onward sharing), and how the person reviews and revokes them. | 6.1.6, 17, a new profile | ToIP Trust Tasks WG |
| Relationship credentials | Whether a verifiable relationship credential, such as those of the ToIP Decentralized Trust Graph work, can serve as the evidence for a delegation, or name the organizations a client may share onward with ([17.2](specification.md#172-delegations), [3.12](specification.md#312-onward-disclosure)). | 17, a Federation Profile | ToIP Trust Tasks WG |
| Person-signed grant | A grant document the Authorizing Principal signs, bound to the terms shown at approval, so that a party other than the provider can check what was approved; and where its fingerprint appears in the grant and in `grant.issued`. Today a grant is the provider's record, governing every token issued under it ([6.1.5](specification.md#615-grant-representation)). | 6.1.5, 8.1 | Implementer feedback (Enkara) |

Elicitation — how applications draw context out of a person — is out of scope and stays in the Guides.

v1 §7.12, specification architecture and the actor model, is resolved by this draft ([1](specification.md#1-about-this-specification), [3](specification.md#3-actors-and-provenance)).

## P1.5 Notes Carried from v1

**Conflict reconciliation.** Core requires that conflicts be detected and surfaced, and lets the Context Subject resolve them ([4.7](specification.md#47-conflicts)). Automated reconciliation — merging, confidence-weighted resolution, deprecation of stale inferences — has real consequences for trust, and getting it wrong would undermine the principle that the person owns their context. Draft 3 lets a provider or client propose a resolution, which only the person's act carries out ([4.7.4](specification.md#474-proposals)), and sets out what every pair of declaration types changes ([4.7](specification.md#47-conflicts)). Automated resolution will be defined from pilot evidence on how often conflicts arise, how people resolve them, and how often they accept proposals ([P1.4](#p14-later)). Learning Economy Foundation reviewers noted that an inference is judged by what it was drawn from, and that HCP records a confidence value without recording its basis. Draft 3 adds that record, `assertion.basis` ([4.2.5](specification.md#425-basis)), shows it to the person when they resolve a conflict, and requires a proposal to say whether it weighed it ([4.7.3](specification.md#473-resolution), [4.7.4](specification.md#474-proposals)). A dimension may now be a concept from an external code system ([4.2](specification.md#42-entry)). A registered dimension vocabulary is still a candidate; the values pilots adopt are better evidence for it than anything specifiable in advance ([G1.2](guides.md#g12-what-pilots-should-record)).

**Category vocabulary.** The nine categories ([4.5](specification.md#45-category-vocabulary)) are a starting point drawn from the Global Memory Workshop, not a validated registry. Known gaps include civic and public services context; a richer financial context for financial services pilots; cultural and linguistic context, which cuts across other categories; and research and professional credentialing. Learning Economy Foundation reviewers noted that `education_learner_profile` collapses mastery, learning history, and accommodations, which carry different sensitivity, and that family context may warrant its own category rather than sitting in `coordination_context`. Because categories are what grants are scoped to, each of these is a consent question before it is a taxonomy question. Cross-sector SME engagement and pilot evidence are the planned inputs. Richard Ng (Native) asked whether categories should be discovered rather than fixed in advance, and whether an entry could sit in several. His example is a statement that the person does not want to apply to tobacco companies, which belongs to `values_and_ethics` and to `work_context` alike. The client writing it may not know that a job-search agent reads `work_context`, so the choice of category has stakes the writer cannot see. Draft 3 lets an entry sit in several categories, with the consent rules in 4.5: a client assigns only categories it may write, and the person adds others. It also has discovery describe each category, so that clients and consent screens can show what it means ([19](specification.md#19-discovery-document)). Categories that emerge from what people store, rather than being declared in advance, would need pilot evidence first.

**Credential format.** v1 permitted two securing mechanisms as a deliberate deferral ([14.5](specification.md#145-securing-credentials)). The wider identity ecosystem has moved toward selective-disclosure formats — the EU Digital Identity wallet toward SD-JWT VC, ISO mDL toward mdoc — in part because of the complexity of RDF canonicalization. Turn.io proposed profiling v1's Tier 2 on SD-JWT VC outright. That was not adopted, because SD-JWT VC is a distinct credential data model rather than a proof format, and adopting it would break the common envelope and the Open Badges alignment; permitting VC-JOSE-COSE obtains the canonicalization-free path and selective disclosure without either consequence. Draft 2 makes `eddsa-rdfc-2022` mandatory to verify, because it is what Open Badges verifiers already support, and keeps the others as options ([14.5](specification.md#145-securing-credentials)). Pilot evidence on which mechanisms were issued and verified, whether selective disclosure was exercised ([14.9](specification.md#149-selective-disclosure)), and wallet and verifier support will inform whether v2 adds a second mandatory mechanism.

**End-to-end encrypted storage.** Relevance ordering ([7.3](specification.md#73-relevance-ordering)), conflict detection ([15](specification.md#15-memory-manager-profile)), and server-side checks on content ([5.2.3](specification.md#523-create)) assume the provider can read entry content. Draft 3 describes an interface arrangement: under the `storage_encryption` declaration `e2e`, those steps are performed within the Context Subject's trust domain, and the provider stores ciphertext ([4.8](specification.md#48-encrypted-storage)). This arrangement remains under technical review ([P1.1](#p11-before-v2-is-final)). Pilot evidence on how often that domain is unreachable will show whether the design holds ([G1.2](guides.md#g12-what-pilots-should-record)).

**Federation.** Learning Economy Foundation reviewers pointed to wallet-attached storage, which lets a person hold and share artifacts through a storage provider of their choosing. Whether an HCP instance can be one such store, or whether the two compose some other way, is an input to the federation design.

**What HCP does not prevent.** HCP limits what context a model receives and what it may write, and holds clients accountable for downstream use. It does not constrain a model's other capabilities. A general-purpose model with access to tools may take destructive actions whether or not its client conforms to HCP. Section 21 says so ([21.1](specification.md#211-what-hcp-does-not-prevent)).

# P2. Changes from v1

v2 Draft 1 reorganized v1 rather than extending it. Its main changes:

- **Structure.** One linear document becomes six Parts, each with its own conformance identifier, so that a claim names exactly what an implementation supports ([1](specification.md#1-about-this-specification)).
- **Actors.** Roles, provenance layers, and fifteen actor invariants are defined before the data model ([3](specification.md#3-actors-and-provenance)). "User", "agent", and "system" give way to named roles.
- **Planes.** Governance operations — grant management, the audit log, export, hard deletion, confirmation — are reserved to the person's own management client and carried only over HTTP ([1.6](specification.md#16-context-plane-and-governance-plane)).
- **Conformance.** v1's three levels become composable claims and four packages ([18](specification.md#18-conformance-claims-and-packages)).
- **Tiers.** v1's two tiers give way to one entry model: Tier 1's claim shape becomes the General Context Profile ([11](specification.md#11-general-context-profile)), and Tier 2 becomes the VC Evidence Profile ([14](specification.md#14-vc-evidence-profile)).

Some v1 rules are reversed or relaxed:

- Accepting an inference records a confirmation instead of rewriting its declaration type to `person-declared` ([3.8](specification.md#38-confirmation)).
- `userVerified` is removed in favor of confirmation records ([3.5](specification.md#35-provenance-layers)).
- An application can no longer hard-delete an entry over MCP ([5.4.2](specification.md#542-hard-deletion)).
- Conflict detection moves to the Memory Manager Profile, required only of providers that accept inferred entries ([4.7](specification.md#47-conflicts), [15](specification.md#15-memory-manager-profile)).
- An implementation accepting applications operated by others now needs the HTTP Binding, not MCP alone ([18.3](specification.md#183-when-provider-interop-is-required)).
- v1 entries are converted on import, with nothing upgraded ([4.3](specification.md#43-one-form-and-conversion-from-v1)).

Draft 2 specifies what Draft 1 deferred:

- **Entries.** One entry form, with content, assertion, classification, evidence and record kept apart; relationships between entries; a complete status lifecycle; and import ([4](specification.md#4-data-model), [5.4.3](specification.md#543-import)).
- **Authorization.** Purposes the person approves, structured authorization details, the OAuth security baseline, and standing rules ([6](specification.md#6-authorization), [13](specification.md#13-oauth-interop-profile)).
- **Disclosure.** Clients receive disclosures with grant-scoped references and a use-until time; revocation reaches the client, with notice to the person when it cannot; copies kept by law are declared in advance ([7](specification.md#7-disclosure-and-minimization), [6.2](specification.md#62-revocation)).
- **Audit.** Structured events, a declared integrity level, and a disclosure summary for the person ([8](specification.md#8-audit)).
- **Credentials.** One mandatory signature format, credential status, selective disclosure, and Health and Education Context Profiles that meet v1's commitment ([14](specification.md#14-vc-evidence-profile), [16](specification.md#16-health-and-education-context-profiles)).
- **Delegation.** The Delegated Authorization Profile: guardians, caregivers and other delegates, with the person's override and the move to adult autonomy ([17](specification.md#17-delegated-authorization-profile)).

The changelog is in P3. A v1 → v2 section map recording where each v1 section went is available on request.

# P3. Changelog

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

*DRAFT — Not for distribution*

---

The specification text is licensed under CC BY 4.0 ([LICENSE-SPEC.md](../../LICENSE-SPEC.md)). These pages are built from the same source as the Word document by `tools/make_pages.py`; where they differ, please report it as an issue.
