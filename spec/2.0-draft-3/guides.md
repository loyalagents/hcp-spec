> **DRAFT — Not for distribution.** Human Context Protocol (HCP) v2, Draft Specification, version 2.0-draft-3. Pages: [Introduction](introduction.md) · [Specification](specification.md) · [Guides](guides.md) · [Path to v2 Final](path-to-v2-final.md)

# Guides

These guides are non-normative ([1.2](specification.md#12-layers)). Nothing in them is a requirement of this specification. Where a guide relies on a rule, it cites the Part that states it, and that statement governs.

HCP is a protocol, not a user experience pattern. How applications elicit context from people — onboarding interviews, reflective dialogue, passive capture — is outside this specification, and pilot teams should treat elicitation design as an implementation choice. Authorization interaction is different in kind: it is where consent is constituted, and 6.1.4 places requirements on it. The patterns in G4 illustrate those requirements; they do not extend them, and they say nothing about elicitation.

# G1. Pilot Onboarding

## G1.1 Recommended Sequence

**Availability.** This repository does not currently designate a validated Draft 3 reference implementation or publish the behavioral suite named below. See the [artifact status](https://github.com/loyalagents/hcp-spec#drafts-and-available-artifacts) for available examples and implementation projects. Schema/example checks alone do not establish implementation conformance.

1. Stand up an HCP Provider: the reference implementation or a conformant third-party implementation.
2. Choose a package ([18.2](specification.md#182-packages)). If every HCP Client the pilot uses is operated by the Provider Operator, the First-Party package is available. If any client is operated by another organization, Provider Interop is required ([18.3](specification.md#183-when-provider-interop-is-required)).
3. Register each HCP Client, identifying its Client Operator by an identifier and a name the person can recognize ([3.2.8](specification.md#328-client-operator-and-provider-operator)).
4. Define the category scopes the pilot needs ([6.1.1](specification.md#611-scope-naming-convention)).
5. Implement the bindings the package requires: the HTTP Binding, the MCP Binding, or both. MCP over stdio qualifies for First-Party only ([10.1](specification.md#101-scope)).
6. If the pilot will accept `model-inferred` entries, implement the Memory Manager Profile ([4.7](specification.md#47-conflicts), [15](specification.md#15-memory-manager-profile)).
7. Run the conformance test suite ([20](specification.md#20-conformance-testing)).
8. Walk pilot participants through the authorization flow before data collection begins ([G4](#g4-authorization-interaction-patterns)).

## G1.2 What Pilots Should Record

Several decisions in this specification are waiting on pilot evidence ([P1](path-to-v2-final.md#p1-roadmap)). Pilots can supply it by recording the following:

- **Which evidence the pilot tests.** Name the rung: protocol conformance ([20](specification.md#20-conformance-testing)); context quality, such as necessary against excessive disclosure, staleness and correction; task performance against a realistic baseline; outcomes for people; or institutional readiness. Passing conformance tests does not show that disclosed context was appropriate or that it helped anyone, and a pilot that tests one rung should not claim the next.
- **Shared measures for people.** So that pilots can be compared, record where you can: whether people repeat themselves less across AI applications, and how much setup time is saved; whether responses are more relevant; whether people understand what is held, who can see it, and how to correct or revoke it; whether they can find and fix inaccurate or outdated entries; and whether their trust changes. Compare against a simpler alternative, such as copying preferences between assistants by hand. Where possible, keep a replayable test: the same request answered with and without HCP context, to show whether the context changed the answer.
- **Audit volume.** How much storage the audit log used, and how much of it was `context.read` events ([8.1](specification.md#81-required-log-events)). One implementer of Draft 1 found read logging grew to several times the size of everything else held. Evidence of the cost is the input to any change in what read events record ([P1](path-to-v2-final.md#p1-roadmap)).

- **Custom categories.** Where a needed category is missing, define it as a URI under a domain you control ([4.5](specification.md#45-category-vocabulary)), document the category, and submit it for the vocabulary review.
- **Facets or categories.** Whether record or document types were distinguished as facets within an entry or as separate categories, and where people wanted finer control than a category gave them. Both approaches are conformant.
- **Dimension values.** The `classification.dimension` values the pilot used ([4.2](specification.md#42-entry)). No vocabulary is registered, and the values pilots adopt are the best evidence for one.
- **Use-until.** How long clients needed disclosed copies, and whether the floor of 1 hour and the ceilings of 30 days and 24 hours ([7.6](specification.md#76-use-until)) were too short or too long.
- **Conflicts.** How often conflicts arose, between which kinds of entry, and how people resolved them ([4.7.3](specification.md#473-resolution)); how often they accepted a proposal ([4.7.4](specification.md#474-proposals)); and how long conflicts stayed open. This is the input to automated resolution ([P1](path-to-v2-final.md#p1-roadmap)).
- **Residency.** Where context had to be stored and processed in a jurisdiction, and how the pilot met it ([G3.7](#g37-records-erasure-and-residency)).
- **Storage.** Whether the pilot's storage is end-to-end encrypted ([4.8](specification.md#48-encrypted-storage)), and if so how often the trust-domain component could not be reached when a request needed it, and how long requests waited.

## G1.3 On-Device and Operator-Blind Deployments

Core governs behavior at the interface boundary, not internal storage (Part I). A deployment that runs models on the person's device, or splits processing between device and server, is conformant if its behavior across a binding conforms. On-device execution changes nothing in Core. End-to-end encrypted storage is defined in 4.8, and G1.4 describes such deployments.

## G1.4 End-to-End Encrypted Deployments

Under `e2e`, the HCP Provider stores ciphertext, and a component the person controls does the work that needs to read it ([4.8](specification.md#48-encrypted-storage)). That has consequences a deployment should plan for.

- **Reachability.** A query needs the trust-domain component. Where it runs on a phone that is off or out of coverage, the query fails with subject unavailable and the client tries later. Deployments where people are often offline, or share devices, should weigh this before choosing `e2e` ([G3](#g3-health-guide)).
- **Keys.** If the person loses every copy of their keys, their content is lost with them. Recovery that does not hand the keys to the operator needs designing: a recovery key the person keeps, or keys held by several of their own devices.
- **What the operator still sees.** Categories, timing and provenance stay readable ([4.8](specification.md#48-encrypted-storage)). For some people, which categories they hold is itself sensitive; `e2e` does not hide it.
- **Erasure.** Destroying keys is a dependable way to make content unrecoverable, backups included ([5.4.2](specification.md#542-hard-deletion)).
# G2. Education Guide

This guide assembles Core, the General Context Profile ([11](specification.md#11-general-context-profile)), the Education Context Profile ([16.4](specification.md#164-education-context-profile)), and the VC Evidence Profile ([14](specification.md#14-vc-evidence-profile)) for education pilots.

## G2.1 Where Learner Context Goes

v1's education example carried a learner's mastery, goal, pacing, learning preferences, and accessibility needs inside one credential. In v2 they are separated by who asserts them and what evidence supports them.

| Content | Entry | Category | Declaration type | Context Asserter |
|------------------------------------|-------------------------------|------------------------------|--------------------|------------------------------|
| Mastery of a skill, with a score | An Open Badges 3.0 credential as the entry's content ([14.4](specification.md#144-example)) | `education_learner_profile` | `issuer-attested` | The issuing platform |
| Current placement level | A statement, or a credential as the content if the platform issues one | `education_learner_profile` | `issuer-attested` | The assessing platform ([3.7](specification.md#37-statements-attributed-to-the-context-subject)) |
| Goal, such as a placement exam in eight weeks | A statement ([11](specification.md#11-general-context-profile)) | `goals_and_constraints` | `person-declared` | The learner |
| Pacing and learning preferences | A statement ([11](specification.md#11-general-context-profile)) | `education_learner_profile` | `person-declared` | The learner |
| Accessibility needs relevant to learning | A statement ([11](specification.md#11-general-context-profile)) | `education_learner_profile` | `person-declared` | The learner |

Category determines which grants reach an entry ([4.5](specification.md#45-category-vocabulary)). Placing the goal in `goals_and_constraints` means a tutoring client needs that scope as well, and the learner sees it requested as a separate category. A pilot that wants the goal read under the learner-profile grant alone can place it in `education_learner_profile`.

Accommodations and accessibility needs may carry a different sensitivity from mastery data. Whether they warrant a category or facet of their own is part of the vocabulary review ([P1](path-to-v2-final.md#p1-roadmap)); pilots should record what they chose.

## G2.2 Example: Pacing Stated in a Tutoring Application

The learner tells a tutoring application how much time they have to study. The application, a Context Client, writes the statement. Because nothing establishes that the learner made it, the HCP Provider records assurance `unverified` ([3.7](specification.md#37-statements-attributed-to-the-context-subject)). The learner can confirm it later through a Management Client ([3.8](specification.md#38-confirmation)).

**Request body: Context Client → HCP Provider (create, either binding)**

    {
      "@context": ["https://hcp.example/contexts/v2"],
      "schema": "https://hcp.example/spec/entry/2.0",
      "id": "urn:uuid:3e8d2f61-0a4b-4c7e-9d15-6b2a8f0c4e97",
      "type": ["ContextEntry"],
      "subject": { "id": "did:example:subject-b7e2", "relationship": null },
      "content": {
        "profile": "https://hcp.example/spec/profiles/general-context/2.0",
        "value": "On weekdays I can study for 25 to 30 minutes; on weekends, about an hour.",
        "language": "en"
      },
      "assertion": {
        "declarationType": "person-declared",
        "confidence": null,
        "validUntil": null
      },
      "classification": {
        "categories": ["education_learner_profile"],
        "dimension": "study_time"
      },
      "evidence": [],
      "record": {
        "status": "active",
        "version": 1,
        "provenance": {
          "assertedBy": { "id": "did:example:subject-b7e2", "assurance": "unverified" },
          "assertedAt": "2026-02-03T17:20:00Z",
          "source": "conversation-id:tutor-5521",
          "submittedByClient": {
            "id": "https://mathkingdom.example.edu/clients/tutor",
            "name": "Math Kingdom Tutor",
            "operator": { "id": "https://mathkingdom.example.edu", "name": "Math Kingdom" }
          },
          "authorizedUnder": "urn:uuid:8a6c4e21-7f3d-4b90-a2e8-1c5d9b7f3a06",
          "recordedByProvider": "https://provider.example",
          "recordedAt": "2026-02-03T17:20:04Z"
        }
      }
    }

A learning preference ("Worked examples first; graphs help; progressive hints") and an accessibility need ("Large text and high contrast") are written the same way, each as its own entry with its own dimension, so the learner can correct or delete one without touching the others.

## G2.3 Credentials

- Mastery and achievement credentials are Open Badges 3.0 credentials under the VC Evidence Profile ([14.4](specification.md#144-example)). v1 committed that VC Evidence would be required for education pilots at v2. The Education Context Profile meets it: a platform's record of mastery carries a credential, while what a learner says about themselves does not need one ([16.3](specification.md#163-how-v1s-commitment-is-met), [16.4](specification.md#164-education-context-profile)).
- Where credentials are intended to be verified outside the pilot, prefer the embedded Data Integrity mechanism ([14.5](specification.md#145-securing-credentials), [16.4](specification.md#164-education-context-profile)). It has the broadest support among current wallets and verifiers, and 1EdTech notes that less common proof mechanisms may not be accepted everywhere.
- For payloads inside education entries, established objects exist and should be considered before anything bespoke: xAPI statements and IEEE LearnerState objects for learning activity and state, the Comprehensive Learner Record and Open Badges 3.0 for achievement, and 1EdTech's Competencies and Academic Standards Exchange (CASE) for the competency frameworks they refer to. Pilots should record which payload shapes they used ([P1](path-to-v2-final.md#p1-roadmap)).
- A large Comprehensive Learner Record and a set of granular Open Badges can carry the same information with different consent properties. The bundle is a single share-or-not decision; the unbundled set can be released piece by piece. A narrowed grant ([6.1.5.1](specification.md#6151-narrowed-grants)) is one way to release part of a bundle without splitting it. A credential secured with `ecdsa-sd-2023` is another: the provider can disclose only the claims a request needs ([14.9](specification.md#149-selective-disclosure)). Pilots should record which form they encountered and whether learners wanted finer control than it allowed.

## G2.4 Guardian Consent

In Core, the Authorizing Principal is the Context Subject ([3.3](specification.md#33-co-location-and-delegation)). A grant a parent or guardian authorizes for a learner is conformant under the Delegated Authorization Profile ([17](specification.md#17-delegated-authorization-profile)):

- The guardian is a delegate. The Authorization Service establishes the delegation and records its basis, such as an enrollment record or the school's own attestation of the relationship ([17.3](specification.md#173-basis-of-authority)). A school is never the delegate: it acts through its HCP Clients under the grants the guardian authorizes ([17.1](specification.md#171-scope)).
- Scope the delegation to what the deployment needs, typically `education_learner_profile` and `goals_and_constraints`. A learner's `health_context` is in scope only where the basis covers it ([17.4](specification.md#174-scope-and-grants-under-a-delegation)).
- Set `term.atMajority` for a guardian of a minor. At the age of majority every grant the guardian authorized lapses, and the learner sees a summary of the delegated period and re-authorizes what they want ([17.6](specification.md#176-ending-a-delegation)). The guardian keeps read access to the record of the grants they authorized ([17.7](specification.md#177-audit-access)).
- Whether the learner may also authorize grants, and from what age, is a deployment decision under the law that applies ([17.5](specification.md#175-the-context-subjects-override)). The learner can always revoke a grant made for them.
- Pilots holding v1 guardian grants carry them over with an unspecified basis, and establish new delegations under 17.2 before issuing new grants ([17.8](specification.md#178-grants-carried-over-from-v1)).
# G3. Health Guide

This guide assembles Core, the General Context Profile ([11](specification.md#11-general-context-profile)), the Health Context Profile ([16](specification.md#16-health-and-education-context-profiles)), and the VC Evidence Profile ([14](specification.md#14-vc-evidence-profile)) for health pilots.

## G3.1 Sensitivity and Token Lifetimes

The Health Context Profile requires every entry in `health_context` to be treated as high-sensitivity regardless of content, and recommends that access tokens under a grant including `health_context` not exceed one hour ([16.2](specification.md#162-health-context-profile)).

The reason for shorter tokens is exposure. Revocation invalidates authorization evidence at the HCP Provider immediately ([6.2.2](specification.md#622-revocation-propagation)), but a token that has leaked, or that a resource server cannot check against revocation at once, is accepted until it expires. A shorter lifetime narrows that window. How immediate invalidation is achieved for self-contained tokens is open ([P1](path-to-v2-final.md#p1-roadmap)).

## G3.2 Documents That Arrive Before a Grant

Clinical documents often reach a deployment before the person has authorized anything. Core requires that such content produce no entry, no audit event on the Context Subject's log, and no state visible to a Context Client ([4.6](specification.md#46-content-received-before-a-grant)).

The specification does not mandate a holding mechanism, but a safe pattern is a custody area outside the HCP data model — an operator-side inbound queue — that holds the raw document, writes no HCP entry, exposes nothing to any HCP Client, and is drained into the instance only once the Authorizing Principal has authorized the relevant category. An item that is never authorized is never ingested, and is disposed of according to the Provider Operator's retention policy. The property to preserve is that an ungranted document is not yet part of the person's context.

## G3.3 Facets Within the Category

A health pilot may scope grants to `health_context` while distinguishing prescriptions, laboratory results, and clinical notes inside the entry, as facets. Both facets and separate categories are conformant. A narrowed grant ([6.1.5.1](specification.md#6151-narrowed-grants)) can restrict a grant to one facet, for example `"narrowedTo": { "documentType": ["prescription"] }`. Pilots should record which approach they took and whether people wanted finer control than it gave them ([G1.2](#g12-what-pilots-should-record)).

## G3.4 Clinical Assertions and the Person's Own Statements

A model's inference about the person's health is not disclosed to any client until the person confirms it ([16.2](specification.md#162-health-context-profile)). A deployment that infers, for example, that a patient stopped a medication writes the inference as `model-inferred` and asks the person to confirm it, as Turn.io's maternal-health pilot does.

A clinician's or clinical system's assertion is `issuer-attested` ([4.4](specification.md#44-declaration-types)). Where it contradicts an unconfirmed inference, the inference is held back ([4.7](specification.md#47-conflicts)). Where it contradicts something the person has declared, neither is held back and the conflict is never settled by the provider: it is shown to the person, who decides what to do ([4.4](specification.md#44-declaration-types)). Which should prevail is a domain judgment, and this is the case most likely to matter in health pilots. Evidence from them is the intended input to automated resolution ([P1](path-to-v2-final.md#p1-roadmap)).

## G3.5 Credentials

v1 committed that VC Evidence would be required for health pilots at v2. The Health Context Profile meets it: a clinician's or clinical system's assertion carries a credential, as its content or in support, and its status is checked at least hourly ([16.2](specification.md#162-health-context-profile), [14.7](specification.md#147-credential-status)). What the person says about their own health does not need one.

- A provider claiming the profile cannot hold a clinical assertion that carries no credential. Pilots whose clinical systems do not yet issue credentials should plan for issuance early.
- Every VC Evidence implementation verifies `eddsa-rdfc-2022` ([14.5](specification.md#145-securing-credentials)). An issuer that secures credentials with VC-JOSE-COSE, which avoids RDF canonicalization, should check that the providers its pilots use declare it in `vc_securing` ([19](specification.md#19-discovery-document)).

## G3.6 HIPAA

HIPAA compliance requirements sit outside the scope of this specification and must be addressed at the implementation layer.

## G3.7 Records, Erasure and Residency

Three questions recur in health pilots: what a clinic keeps, how data is erased, and where it lives.

- **Clinical records.** A clinic that must keep what it receives in its medical record declares that obligation at registration. The person is told before approving, and again at revocation, that revoking will not remove it ([6.2.5](specification.md#625-copies-kept-under-a-legal-obligation)). Declare it; an undeclared retention is not covered.
- **Erasure.** Hard deletion removes an entry for good ([5.4.2](specification.md#542-hard-deletion)). Destroying the keys under which an entry is encrypted meets it, provided the entry can no longer be recovered from any replica or backup.
- **Residency.** Where the person's context must be stored and processed in their jurisdiction, that is a property of the deployment, and nothing in this specification prevents it. Pilots should record residency requirements they met ([G1.2](#g12-what-pilots-should-record)).

For payloads inside health entries, established code systems such as HL7 FHIR resources and terminology and SNOMED CT should be considered before anything bespoke. Pilots should record which they used; they are inputs to a dimension vocabulary ([P1](path-to-v2-final.md#p1-roadmap)).
# G4. Authorization Interaction Patterns

Nothing in this section is a conformance requirement, and an implementation satisfying 6.1.4 and 6.1.6 by other means is fully conformant. It exists because those sections state requirements as outcomes, and implementers reasonably ask what satisfying them looks like.

In every modality, what the Authorizing Principal is told before they act is set by 6.1.6: the categories requested, the actions permitted, whether access is temporary or persistent, when it expires, the HCP Client and its Client Operator, and the Requesting Party where it differs from the Context Subject. The patterns below say "the disclosure" for this.

**Graphical**

*Satisfying:* a two-step flow in which the person confirms the grant and is then separately offered persistence; or a control defaulting to off, labelled with the consequence rather than the mechanism — "Keep access until I turn it off" rather than "Elect persistent grant."

*Not satisfying:* a pre-checked box; persistence bundled into the primary confirmation control; a label describing the protocol rather than the effect on the person.

**Messaging**

*Satisfying:* the grant is confirmed by an explicit reply, and persistence is offered afterwards as a distinct question requiring its own reply.

*Not satisfying:* a single reply carrying both, such as "reply YES to allow access and remember this next time."

**Voice**

*Satisfying:* the system speaks the disclosure and takes confirmation; persistence is asked separately.

*Not satisfying:* a single affirmative accepted at the end of a long combined disclosure.

*Spoken agreement on a voice call.* The system speaks the disclosure, pauses, and asks the person to say a word or phrase to confirm the grant. Persistence, if offered, is a second spoken question after the grant is confirmed. The spoken confirmation is recorded as the affirmative act, and the modality is recorded in the `grant.issued` event ([6.1.4](specification.md#614-grant-distinction-temporary-vs-persistent)).

*Voice call paired with a messaging channel.* The disclosure is spoken, and confirmation is completed by a reply in an associated messaging channel — a two-tap confirm-and-then-persist in the messaging thread — so the person has a written record of what they agreed to alongside the spoken disclosure. Grant and persistence remain two distinct acts across the two moments.

*Plain-phone keypad.* Where the person has only a basic handset, the disclosure is spoken and confirmation is a keypad entry: one key to confirm the grant, and, only if persistence is offered, a separate subsequent key-press for persistence after a distinct spoken prompt. A single key-press never confirms both, because 6.1.4 does not permit a single act to both authorize access and elect persistence.

**LLM-mediated**

*Satisfying:* the assistant states what is being requested and for what purpose, obtains confirmation, and then in a separate turn asks whether access should persist beyond the current interaction.

*Not satisfying:* inferring persistence from the person's enthusiasm, from a general instruction such as "you can remember things about me," or from prior grants to other clients. A model's reading of the person's intent does not satisfy an authorization requirement ([3.11](specification.md#311-actor-invariants), invariant 6).

**Entries in more than one category.** An entry can be in several categories ([4.5](specification.md#45-category-vocabulary)), and a standing rule reaches it through any of them ([6.3](specification.md#63-standing-rules)). An entry in both `work_context` and `health_context` is therefore withheld from an operator the person has denied health context, even under a grant for work context alone. A person may not expect this, and the screens where it matters can say so:

- *Setting the rule:* "This also hides anything that is partly about your health, even from apps you let see your work context."
- *Approving a grant the rule partly covers:* "Some of your work context is also about your health. Because of your rule, this app will not see those parts."

Saying so does not change what is withheld; it lets the person understand why an application sees less than the grant's categories suggest.

**A test across modalities.** Could a person who wanted temporary access end up with persistent access without having done something specifically to choose it? If so, the pattern does not satisfy 6.1.4, whatever its form.
# G5. Deployment Patterns

This section is informative. Each pattern describes a setting, how the specification applies there, and what remains open.

## G5.1 Health Workers Recording for People

A community health worker visits many households and records what she learns into each person's context, from one tablet.

- **One grant for each person.** Her application is a Context Client holding a separate grant from each person it serves, never one grant for all of them. Where the application is an institutional integration, it requests each token under the grant of the person it is serving ([13.2](specification.md#132-grant-types)).
- **Approval from the person.** The person approves the grant, not the health worker. Where the person has a phone, approval can come by a messaging reply or a short code on their own handset ([G4](#g4-authorization-interaction-patterns)). Where the person has no device, a spoken disclosure and confirmation in the health worker's presence is a pattern this draft does not yet specify ([P1.4](path-to-v2-final.md#p14-later)); the identity questions in 21.3 apply to it with particular force.
- **Whose statement it is.** What the person tells her is recorded as the person's statement, `unverified` until the person confirms it ([3.7](specification.md#37-statements-attributed-to-the-context-subject)). What she observes is recorded with her as the asserter. A result the clinic stands behind is `issuer-attested`, written under an attestation authorization the clinic or the health ministry gave her application ([14.10](specification.md#1410-attestation-authorizations)).
- **Health inferences.** An inference her application makes is held back from other clients until the person confirms it ([16.2](specification.md#162-health-context-profile)).

## G5.2 Shared Devices

Several people may use one phone, and in some households one phone number serves the family.

- **Each person has their own context.** An HCP instance belongs to one person. On a shared device, each person signs in separately, and a Management Client acts only for the person who authenticated ([3.2.3](specification.md#323-hcp-client)).
- **A phone number is not a person.** Sign-in through a messaging application identifies a number, not who is holding the phone ([21.3](specification.md#213-grants)). Before a grant reaches a category of High sensitivity, the Authorization Service asks for more than that sign-in ([6.1.6](specification.md#616-authorization-is-distinct-from-authentication)), such as a PIN the person alone knows.
- **Prefer temporary grants.** A temporary grant ends with the interaction ([6.1.4](specification.md#614-grant-distinction-temporary-vs-persistent)), so a later user of the same phone does not inherit it. A deployment that offers persistent grants on shared phones explains what that means for whoever uses the phone next.
- **Copies on the device.** A client that keeps disclosed context on the phone discards it at its use-until time ([7.6](specification.md#76-use-until)), and before then keeps it where another user of the phone cannot read it.

## G5.3 Low Connectivity

- **Reads need the provider.** A query reaches the provider when it is made. A client working offline relies on what it was disclosed earlier, within its use-until time ([7.6](specification.md#76-use-until)). A deployment that expects long offline periods sets use-until accordingly, within the floor and ceilings that apply ([7.6](specification.md#76-use-until)).
- **Writes can wait.** A client can hold a write and submit it when it reconnects. The provider records when it received the entry ([3.5](specification.md#35-provenance-layers)); the time of the observation belongs in the content.
- **Revocation arrives late.** A client that is offline learns of a revocation when it reconnects, and the person is told when notification does not succeed ([6.2.4](specification.md#624-when-notification-fails)).
- **Encrypted storage.** Where the component that reads the context runs on a phone that is often out of coverage, queries fail until it returns ([G1.4](#g14-end-to-end-encrypted-deployments)).
- **Approval over thin channels.** The Device Authorization Grant ([13.2](specification.md#132-grant-types)), a messaging reply, or a keypad entry on a basic handset ([G4](#g4-authorization-interaction-patterns)) need less bandwidth than a browser redirect.

## G5.4 Mediated Access Where Data Stays Put

Some records cannot leave the institution that holds them, by law or by policy: a national health record, a school system's records.

- **The institution as provider.** The institution can operate an HCP Provider over the records it holds ([3.2.4](specification.md#324-hcp-provider)). The records stay where they are; the person approves each grant, clients receive only what a grant covers, reduced to what the request needs ([7](specification.md#7-disclosure-and-minimization)), and every access is in the person's log ([8](specification.md#8-audit)).
- **Several providers for one person.** A person may then have context with more than one provider: the institution's, and one of their own choosing. HCP does not yet let one provider act as a client of another on the person's behalf; that is the cross-HCP federation item ([P1.4](path-to-v2-final.md#p14-later)).
- **Processing in place.** Where the institution runs a model over the records itself and releases only results, the results are entries the institution asserts, with the records as their source ([3.5](specification.md#35-provenance-layers)).

## G5.5 The Workplace

An organization with many agents and many staff may hold context about its own staff, so that its agents can draw on it.

- **The employee is still the Context Subject.** Each member of staff approves the grants on their context, can read their log, and can withdraw access ([6](specification.md#6-authorization), [8](specification.md#8-audit)). The employer, as Provider Operator, does not approve grants on their behalf.
- **The imbalance of power.** Approval given to an employer is not freely given in the way approval given to an assistant one chose is. A deployment can limit what it asks for to `work_context`, keep a person's own context apart, and say plainly what happens if they decline. Unless storage is end-to-end encrypted, the operator can read what it stores ([4.8](specification.md#48-encrypted-storage)).
- **Between the employer's own agents.** Within one operator, HCP allows a client to pass context to the operator's own components ([3.12](specification.md#312-onward-disclosure)). What a person tells one agent can therefore reach others unless the deployment prevents it. A deployment that wants what is said to one agent to stay there gives each agent its own client and grant, records each statement with the agent that heard it, and lets the person set a directive that forbids passing on ([6.4](specification.md#64-directives)).
- **Leaving.** When a member of staff leaves, they can export their context ([5.4.1](specification.md#541-export)). What the employer itself attested about them, such as a completed training, travels as an attested entry; what the employer may keep is a matter for its legal obligations ([6.2.5](specification.md#625-copies-kept-under-a-legal-obligation)).

## G5.6 Inclusive Access

- **Every modality.** Approval works by voice, by messaging and by keypad, as well as on a screen ([G4](#g4-authorization-interaction-patterns)). A person who cannot use one is offered another.
- **Language and literacy.** What the person is told before approving ([6.1.6](specification.md#616-authorization-is-distinct-from-authentication)) is given in a language they read or hear comfortably, and in plain words. A disclosure that is accurate but not understood does not inform anyone.
- **Help without handing over control.** Someone helping a person, such as a relative or a health worker, can read the screen aloud; the approval remains the person's own act. Where another person is to decide for them, that is a delegation ([17](specification.md#17-delegated-authorization-profile)), recorded as one.
- **Cost.** Data costs money. Approval and queries that need little bandwidth ([G5.3](#g53-low-connectivity)) keep HCP usable where data is expensive.

---

The specification text is licensed under CC BY 4.0 ([LICENSE-SPEC.md](../../LICENSE-SPEC.md)). These pages are built from the same source as the Word document by `tools/make_pages.py`; where they differ, please report it as an issue.
