> **DRAFT — Not for distribution.** Human Context Protocol (HCP) v2, Draft Specification, version 2.0-draft-3. Pages: [Introduction](introduction.md) · [Specification](specification.md) · [Guides](guides.md) · [Path to v2 Final](path-to-v2-final.md)

# Specification

This page is the normative specification. Section 1 says how it is organized and Section 2 maps its terms. Parts I to IV state its requirements, Part V explains what it protects against, Appendix A holds its registries, and the References list the standards it cites.

# 1. About This Specification

This section describes how the specification is organized and sets the rules that bindings, profiles, and Implementation Guides must follow. Its rules govern how this specification and its extensions are written. Requirements on implementations that it summarizes are stated, and claimed, in the Parts it cites.

## 1.1 Parts

HCP is published in four pages: the Introduction, the Specification, the Guides, and the Path to v2 Final. The Specification is divided into Parts. Each Part can later become a separate document without changing its content or its conformance identifier ([1.7](#17-conformance-identifiers)).

| Part | Contents | Normative | Claimable |
|------------------|------------------------------------------------------------------|-----------|-----------|
| Introduction page | Purpose, HCP in brief, roles, worked use cases, scope, related work, acknowledgments (I1–I12) | No | No |
| Specification §1 | This section | Yes, for authors of bindings, profiles, and guides | No |
| Specification §2 | Terms, by building block, and HCP's terms beside OAuth's ([2](#2-terms)) | No | No |
| I — Core | Actors and provenance, data model, operations and errors, authorization, disclosure and minimization, audit (3–8) | Yes | Yes |
| II — Bindings | HTTP Binding ([9](#9-http-binding)), MCP Binding ([10](#10-mcp-binding)) | Yes | Each binding |
| III — Profiles | General Context, First-Party Authorization, OAuth Interop, VC Evidence, Memory Manager, Health Context, Education Context, Delegated Authorization (11–17) | Yes | Each profile |
| IV — Conformance | Conformance claims and packages, discovery document, conformance testing (18–20) | Yes | No |
| V — Security and Privacy Considerations | What HCP protects against and what it leaves to others ([21](#21-security-and-privacy-considerations)) | No | No |
| Appendix A | Registries and published artifacts (A.1–A.3) | Registries only | No |
| References | The standards this specification cites, normative and informative | No | No |
| Guides page | Pilot onboarding, education, health, authorization interaction patterns, deployment patterns (G1–G5) | No | No |
| Path to v2 Final page | Roadmap, changes from v1, changelog (P1–P3) | No | No |

## 1.2 Layers

**Core** defines what is true regardless of how HCP is carried: the actors, the data model, the operations and their results, lifecycle, authorization semantics, disclosure and minimization, audit semantics, and the error taxonomy. Every implementation claiming any HCP conformance conforms to Core (Part I).

**A Binding** carries Core operations and representations over a specific protocol. It defines framing, operation names, protocol metadata, how authorization evidence is carried, response representation, and the mapping of Core errors. A binding MUST preserve the semantics Core defines and MUST NOT redefine the meaning of a Core operation or field.

**A Profile** adds stricter rules for a domain, a security posture, an evidence type, or a deployment pattern. A profile MAY make optional Core behavior mandatory, MAY narrow the choices Core permits, and MAY define additional fields through the extension mechanism. A profile MUST NOT weaken or contradict a Core requirement, and MUST NOT redefine the meaning of a Core operation or field. Core MAY require a profile of any implementation that does a stated thing; the Memory Manager Profile ([15](#15-memory-manager-profile)) and the Health and Education Context Profiles ([16](#16-health-and-education-context-profiles)) are required in this way.

**An Implementation Guide** assembles Core, bindings, and profiles for a use case and adds examples, recommended packages, deployment practice, and interaction patterns. Implementation Guides are non-normative. A guide that needs a rule MUST cite a profile that states it; a rule stated only in a guide is not a requirement of this specification.

There is one canonical meaning for every HCP operation and object, however many bindings carry it and however many profiles constrain it.

## 1.3 Sorting Requirements

Every requirement in this specification, and every requirement proposed for it, is placed by the following questions, asked in order. The first answer of yes places it.

1. Does the requirement define meaning that must be identical everywhere? → **Core**.
2. Does it name HTTP, MCP, framing, headers, methods, tool names, or protocol-specific errors? → **Binding**.
3. Is it a stricter rule for one domain, security posture, evidence type, or deployment pattern? → **Profile**.
4. Does it describe algorithms, storage, user experience, examples, deployment choices, or recommended practice? → **Implementation Guide**.

Applied to requirements carried over from HCP v1:

| Requirement | Placement |
|------------------------------------------------------------------|------------------------------------------------|
| Content that arrives before a grant authorizing its handling produces no entry, no audit event, and no state visible to a Context Client | Core ([4](#4-data-model)) |
| A conflicted entry is not returned to a Context Client | Core ([4](#4-data-model)) |
| Entries in `health_context` are treated as high-sensitivity | Health Context Profile ([16](#16-health-and-education-context-profiles)) |
| Recording the party who authorized a grant on a minor's behalf | Delegated Authorization Profile ([17](#17-delegated-authorization-profile)) |
| The matching rule and normalization used to detect a conflict | Memory Manager Profile ([15](#15-memory-manager-profile)) |
| Temporary access is the default outcome of authorization | Core ([6](#6-authorization)) |
| Authorization Code with PKCE | OAuth Interop Profile ([13](#13-oauth-interop-profile)) |
| Return status 403 for an unauthorized request | HTTP Binding ([9](#9-http-binding)) |
| Return the Core error not authorized | Core ([5](#5-operations-and-errors)) |
| Education credentials use Open Badges 3.0 | Education Context Profile ([16.4](#164-education-context-profile)) |
| Confirming a grant by voice in two prompts | Implementation Guide ([G4](guides.md#g4-authorization-interaction-patterns)) |

## 1.4 The Interface Boundary

HCP governs behavior at the interface boundary, not internal storage. Core states this as a requirement at the start of Part I. Every requirement in Core, the bindings, and the profiles is therefore written as behavior observable across a binding or in an export. Where a requirement names a field, it names the field as exchanged, not as stored.

## 1.5 Bindings and Transports

A binding carries HCP over another protocol. This specification defines two: the HTTP Binding ([9](#9-http-binding)) and the MCP Binding ([10](#10-mcp-binding)). "Transport" is used only in its MCP sense, for MCP's own stdio and Streamable HTTP transports, which sit beneath the MCP Binding.

Core defines one request schema and one result schema for each operation, and one error taxonomy ([5](#5-operations-and-errors)). Each binding maps them:

- A binding MAY expose a subset of an operation's fields. It MUST NOT give any field a different meaning.
- A restriction on what a caller may do is a Core rule, not a property of a binding's shape. That a Context Client cannot create an `issuer-attested` entry or an entry whose content is a credential follows from Core ([3.7](#37-statements-attributed-to-the-context-subject)), not from the fields an MCP tool happens to accept.
- The HTTP Binding maps Core errors to HTTP status codes and problem types. The MCP Binding maps them to tool execution errors. The mappings are in 9 and 10.

The discovery document declares the bindings an implementation exposes as `"bindings": ["http", "mcp"]` ([19](#19-discovery-document)). This replaces v1's `supported_transports`.

## 1.6 Context Plane and Governance Plane

HCP operations fall on one of two planes.

| Plane | Operations | Who may call | Bindings |
|-------------------|------------------------------------------------------------|---------------------------------|---------------------|
| Context | Query, get an entry, create, revise, withdraw (soft delete only); an HCP Client reading or relinquishing its own grant, or reporting onward sharing ([3.12](#312-onward-disclosure)) | Any HCP Client holding a grant that covers the operation ([6](#6-authorization)) | HTTP and MCP |
| Governance | List grants; revoke a grant; read the audit log; read the disclosure summary; export and import; hard delete; confirm or reject an entry ([3.8](#38-confirmation)); change an entry's categories ([4.5](#45-category-vocabulary)); restrict its purposes ([4.2.6](#426-permitted-purposes)); set or remove a standing rule ([6.3](#63-standing-rules)); set or remove a directive ([6.4](#64-directives)) | A Management Client acting for the Authorizing Principal ([3.2.3](#323-hcp-client)) | HTTP only |

Core restricts governance operations to a Management Client acting for the Authorizing Principal ([6](#6-authorization)), and the MCP Binding carries none of them ([10](#10-mcp-binding)). A Management Client can also perform context operations.

The planes divide operations, not events. Operations on both planes produce audit events ([8](#8-audit)); reading the audit log is a governance operation.

A binding is not a modality. The person-facing capabilities required by 18 can be offered through any modality the implementation supports, including natural language in an LLM-mediated interface. Where that interface is an HCP Client, it reaches governance operations as a Management Client over the HTTP Binding. A provider whose only binding is MCP, permitted under the First-Party package ([18](#18-conformance-claims-and-packages)), offers those capabilities through its own person-facing interface rather than through an HCP binding.

## 1.7 Conformance Identifiers

Core, each binding, and each profile has its own versioned conformance identifier. An implementation states what it conforms to as a `conformsTo` list of these identifiers in its discovery document ([19](#19-discovery-document)). This replaces v1's single `conformance_level`. Because claims name Parts rather than the release package, they remain valid if the Parts are later published separately.

Identifiers in this draft use the placeholder domain hcp.example. The permanent namespace will be fixed before v2 is final; the maintainers hope to secure hcp.me for it. Conformance identifiers are compared as exact strings and need not resolve ([19](#19-discovery-document)), so a later move of the specification's location does not invalidate a claim.

| Specification | Conformance identifier |
|-------------------------------------|--------------------------------------------------------------|
| Core | https://hcp.example/spec/core/2.0 |
| HTTP Binding | https://hcp.example/spec/bindings/http/2.0 |
| MCP Binding | https://hcp.example/spec/bindings/mcp/2.0 |
| General Context Profile | https://hcp.example/spec/profiles/general-context/2.0 |
| First-Party Authorization Profile | https://hcp.example/spec/profiles/first-party-authorization/2.0 |
| OAuth Interop Profile | https://hcp.example/spec/profiles/oauth-interop/2.0 |
| VC Evidence Profile | https://hcp.example/spec/profiles/vc-evidence/2.0 |
| Memory Manager Profile | https://hcp.example/spec/profiles/memory-manager/2.0 |
| Health Context Profile | https://hcp.example/spec/profiles/health-context/2.0 |
| Education Context Profile | https://hcp.example/spec/profiles/education-context/2.0 |
| Delegated Authorization Profile | https://hcp.example/spec/profiles/delegated-authorization/2.0 |
| Directives (client claim) | https://hcp.example/spec/clients/directives/2.0 |

Packages name the combinations most implementations claim. They are defined in 18:

| Package | Comprises | v1 equivalent |
|---------------------|----------------------------------------------------------------------------------|---------------|
| First-Party | Core + General Context + any one binding + First-Party Authorization | Core |
| Provider Interop | Core + General Context + HTTP Binding + OAuth Interop | Interop |
| Agent Interop | Provider Interop + MCP Binding | None |
| VC Evidence | Adds to any package | VC-Extended |

An implementation that accepts HCP Clients operated by anyone other than its own Provider Operator is required to claim Provider Interop ([18](#18-conformance-claims-and-packages)).

Until v2 is final, a draft may break compatibility with the draft before it. Each draft's changes to the wire are listed in its changelog entry ([P3](path-to-v2-final.md#p3-changelog)).

## 1.8 Requirements Language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, and OPTIONAL are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals. Sections and passages marked informative contain no requirements.

## 1.9 Building Blocks

HCP is built from six building blocks. They name what the Specification defines; they do not reorder it.

| Building block | What it defines | Where |
|----------------|------------------------------------------------------------------------|--------|
| Entries | The record of one piece of context: content, assertion, classification, evidence, and record, with provenance and lifecycle | 3, 4 |
| Grants | The Authorizing Principal's permission for one HCP Client: categories, actions, purposes, duration, and revocation | 6.1, 6.2, 12, 13, 17 |
| Disclosure | What a Context Client receives: minimized, with grant-scoped references and a use-until time | 5.2, 7 |
| Rules | Standing rules the provider enforces across every grant, and directives that clients follow | 6.3, 6.4 |
| Audit | The Context Subject's log of every grant, access and change, and its integrity | 8 |
| Discovery | The document in which an implementation describes what it supports | 19 |

## 1.10 Data Formats

Every time in this specification is a date-time as defined by RFC 3339 (section 5.6): a profile of ISO 8601 that always carries a time zone offset, such as `2026-11-05T20:23:00Z`. Templates write it as `{date-time}`. JSON Schema's `date-time` format, which the published schemas use ([A.2](#a2-published-artifacts)), is the same profile.
# 2. Terms

This section is informative. It is a reader's map: each term is defined in the section it cites, and that section governs. The parties come first, then one table for each building block ([1.9](#19-building-blocks)), then the terms HCP shares with OAuth.

## 2.1 Parties

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Context Subject | The natural person the context is about ([3.2.1](#321-context-subject)) |
| Authorizing Principal | Whoever governs a Context Subject's context and approves grants: the person, or a delegate ([3.2.2](#322-authorizing-principal), [17](#17-delegated-authorization-profile)) |
| Delegate | A person who acts for a Context Subject under a delegation the HCP Provider records ([17.1](#171-scope), [17.2](#172-delegations)) |
| HCP Client | Software that makes HCP requests and holds the grant it acts under; it is the security principal, not any model within it ([3.2.3](#323-hcp-client)) |
| Management Client | An HCP Client acting for the Authorizing Principal; only it may perform governance operations ([3.2.3](#323-hcp-client)) |
| Context Client | An HCP Client acting under a grant for a task; it performs context operations only ([3.2.3](#323-hcp-client)) |
| HCP Provider | The service that holds context, enforces grants and rules, and keeps the audit log ([3.2.4](#324-hcp-provider)) |
| HCP instance | What a provider holds for one Context Subject: entries, grants and audit log ([3.1](#31-roles-entities-and-components)) |
| Authorization Service | Authenticates the Authorizing Principal, presents what is asked, and issues grants ([3.2.5](#325-authorization-service)) |
| Context Asserter | Whoever made the statement an entry records: the person, a model, or an issuer ([3.2.6](#326-context-asserter)) |
| Requesting Party | Whoever the HCP Client is working for in a task ([3.2.7](#327-requesting-party)) |
| Client Operator, Provider Operator | The organizations accountable for an HCP Client and for an HCP Provider ([3.2.8](#328-client-operator-and-provider-operator)) |
| Trust domain | Components the Context Subject controls, which read content when storage is end-to-end encrypted ([4.8](#48-encrypted-storage)) |

## 2.2 Entries

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Entry | One piece of context about a Context Subject: `content`, `assertion`, `classification`, `evidence` and `record` ([4.2](#42-entry)) |
| Declaration type | Whether the Context Subject stated the content, a model inferred it, or an issuer attested to it ([4.4](#44-declaration-types)) |
| Basis | What an assertion was drawn from: a conversation, a document, an observation, an assessment, or other entries ([4.2.5](#425-basis)) |
| Confidence | A model's estimate for an inference, required only for `model-inferred` entries ([4.4](#44-declaration-types)) |
| Category | A kind of context, registered or custom, that grants and rules name; an entry may be in several ([4.5](#45-category-vocabulary)) |
| Sensitivity | Low, Medium or High, the default each category carries ([4.5](#45-category-vocabulary)) |
| Permitted purposes | Purposes an entry may be disclosed for, set by its asserter or the Authorizing Principal ([4.2.6](#426-permitted-purposes)) |
| Evidence | Items that make up or support an entry, such as a verifiable credential ([4.2.2](#422-evidence), [14](#14-vc-evidence-profile)) |
| Provenance | Who asserted, submitted and confirmed each version of an entry ([3.5](#35-provenance-layers), [4.2](#42-entry)) |
| Assurance | How strongly the HCP Provider established who the Context Asserter was ([3.6](#36-asserter-assurance)) |
| Confirmation | The Context Subject's confirming or rejecting what was attributed to them or inferred about them ([3.8](#38-confirmation)) |
| Status | Where an entry stands in its lifecycle: `active`, `deprecated`, `conflicted`, `expired`, `revoked`, `suspended` or `deleted` ([4.2.4](#424-status)) |
| Conflict | Two entries about the same thing that cannot both hold; standing decides which prevails ([4.7](#47-conflicts)) |
| Proposal | A client's suggested resolution of a conflict, which only the Authorizing Principal can act on ([4.7.4](#474-proposals)) |
| Storage posture | `server`, or `e2e` where the provider cannot read entry content ([4.8](#48-encrypted-storage), [A.1](#a1-registries)) |

## 2.3 Grants

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Grant | The Authorizing Principal's permission for one HCP Client: what it may do, with which categories, for which purposes, until when ([6.1](#61-grant-model), [6.1.5](#615-grant-representation)) |
| Authorization detail | One element of a grant's `access`: categories, actions, purposes, and any narrowing or onward sharing ([6.1.5](#615-grant-representation)) |
| Action | `read`, `write` or `provenance` ([6.1.5](#615-grant-representation)) |
| Purpose | A code naming what context may be used for; a grant names its purposes ([6.1.5.2](#6152-purposes)) |
| Temporary grant, persistent grant | A grant that ends with the interaction, and one the Authorizing Principal elected to keep ([6.1.4](#614-grant-distinction-temporary-vs-persistent)) |
| Narrowed grant | A grant whose `narrowedTo` limits it further than its categories ([6.1.5.1](#6151-narrowed-grants)) |
| Onward sharing | The Authorizing Principal's election that a client may tell organizations it deals with what a task needs from Low-sensitivity context ([3.12](#312-onward-disclosure), [6.1.4](#614-grant-distinction-temporary-vs-persistent)) |
| Context operation, governance operation | Operations on context under a grant, and operations that govern the instance, reserved to a Management Client ([1.6](#16-context-plane-and-governance-plane)) |
| Revocation | Ending a grant, and with it everything issued under it ([6.2](#62-revocation)) |
| Legal retention | A copy a client declared it must keep by law, which revocation does not reach ([6.2.5](#625-copies-kept-under-a-legal-obligation)) |
| Delegation | The record that a delegate may act for a Context Subject, on what basis, with what scope, and until when ([17](#17-delegated-authorization-profile)) |

## 2.4 Disclosure

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Disclosure | What a Context Client receives for one entry: only what the grant covers, minimized ([7.4](#74-disclosures-to-context-clients)) |
| `ref` | A reference to a disclosed entry, valid only under the grant it was disclosed under ([7.4](#74-disclosures-to-context-clients)) |
| Use-until | The time after which a client stops using what was disclosed ([7.6](#76-use-until)) |
| Minimization | Limiting a response to the categories, purposes, quantity and relevance a request needs ([7](#7-disclosure-and-minimization)) |
| Relevance method | How the provider orders entries for a query: `lexical`, `semantic`, `llm` or `none` ([7.3](#73-relevance-ordering), [A.1](#a1-registries)) |
| Onward disclosure | Passing disclosed context on; allowed within the client's own operator, and to other organizations only as 3.12 permits ([3.12](#312-onward-disclosure)) |
| Provenance on request | The `provenance` action, under which a client receives an entry's provenance ([7.4.1](#741-provenance-on-request)) |

## 2.5 Rules

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Standing rule | A rule the Authorizing Principal sets once and the HCP Provider enforces across every grant, such as denying a category to an operator ([6.3](#63-standing-rules)) |
| Directive | An instruction about what an agent may do with context, such as signing or passing it on, which clients that claim to follow directives obey ([6.4](#64-directives)) |
| Directive effect | `deny`, `ask-first` or `permit` ([6.4](#64-directives), [A.1](#a1-registries)) |
| Client conformance claim | A claim an HCP Client makes, such as following directives, recorded with its grants ([6.4](#64-directives), [A.1](#a1-registries)) |

## 2.6 Audit

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Audit log | The record of every grant, access and change in an HCP instance, readable by the Authorizing Principal ([8](#8-audit)) |
| Event type | The kind of event a log entry records, from the list in 8.1 ([8.1](#81-required-log-events), [8.2](#82-log-entry-structure)) |
| Disclosure summary | A readable account of who received what, under which grant, and how long they may use it ([8.6](#86-disclosure-summary)) |
| Integrity level | How tamper-evident the log is, from `append-only` to `anchored` ([8.7](#87-integrity), [A.1](#a1-registries)) |
| Controller-side logging | The Provider Operator's own records, kept apart from the Context Subject's log, for obligations that log cannot meet ([8.5](#85-controller-side-logging)) |
| Security event | A signed notification, such as a revocation, pushed to clients ([9.9](#99-revocation-notification-delivery)) |

## 2.7 Discovery

| Term | Meaning |
|------------------------|------------------------------------------------------------------------|
| Discovery document | The document in which an implementation says what it supports and where ([19](#19-discovery-document)) |
| Conformance identifier | The versioned URI of a Part, binding or profile ([1.7](#17-conformance-identifiers)) |
| Conformance claim | The list of identifiers an implementation conforms to, in `conformsTo` ([18](#18-conformance-claims-and-packages), [19](#19-discovery-document)) |
| Package | A combination of claims, such as First-Party, Provider Interop or Agent Interop ([18](#18-conformance-claims-and-packages)) |
| Binding | How operations are carried: the HTTP Binding ([9](#9-http-binding)) or the MCP Binding ([10](#10-mcp-binding)) |
| Profile | A Part III specification that an implementation may claim (11–17) |

## 2.8 HCP Terms and OAuth

3.2.10 maps the roles to OAuth, MCP and the Verifiable Credentials Data Model. This table gives the reason behind each name.

| HCP term | OAuth term | Why the HCP name |
|------------------------|------------------------|------------------------------------------------------------------------|
| HCP Client | Client | HCP also has clients authorized without OAuth, under the First-Party Authorization Profile ([12](#12-first-party-authorization-profile)), and the name keeps the client apart from any model inside it ([3.2.3](#323-hcp-client)) |
| HCP Provider | Resource server | It does more than serve protected resources: it records provenance, enforces standing rules, and keeps the person's audit log ([3.2.4](#324-hcp-provider)) |
| Authorization Service | Authorization server | It is a role, which may be part of the provider; under the OAuth Interop Profile it is the authorization server ([3.2.5](#325-authorization-service), [13](#13-oauth-interop-profile)) |
| Authorizing Principal | Resource owner | A delegate can authorize for another person, so the one who approves and the one the context is about are named separately ([3.2.2](#322-authorizing-principal), [17](#17-delegated-authorization-profile)) |
| Context Subject | Resource owner, usually | The person the context is about stays the subject whoever authorizes ([3.2.1](#321-context-subject)) |
| Grant | Authorization grant, with the consent behind it | An OAuth grant is a credential for obtaining tokens; an HCP grant is the lasting record of what was approved, which governs every token issued under it ([6.1.5](#615-grant-representation)) |
| Authorization detail | Authorization details (RFC 9396) | The same structure; HCP adds purposes, narrowing and onward sharing ([6.1.5](#615-grant-representation)) |
| Category | Scope | Scopes are derived from categories ([6.1.1](#611-scope-naming-convention)); a category also carries a sensitivity and consent rules that a scope string does not ([4.5](#45-category-vocabulary)) |
| Revocation | Token revocation | Revoking a grant ends every token issued under it, and clients are told ([6.2](#62-revocation)) |
| Requesting Party | — | OAuth does not model who a client acts for in a task; the term follows UMA's ([3.2.7](#327-requesting-party)) |
# Part I — Core

Core defines what is true regardless of how HCP is carried. Every implementation claiming any HCP conformance MUST conform to Core.

**The interface boundary.** HCP governs behavior at the interface boundary, not internal storage. An implementation MAY use any storage, indexing, ranking, or processing architecture, provided its behavior as observed across an HCP binding or in an export conforms to this specification. Where entry content is stored end-to-end encrypted, the requirements that need to read it are met within the Context Subject's trust domain ([4.8](#48-encrypted-storage)).

# 3. Actors and Provenance

This section defines who takes part in HCP, what each party is accountable for, and how an entry records where it came from. It precedes the data model because the meaning of an entry's subject, its declaration type, its provenance, the parties named in a grant, and the parties named in an audit event all depend on it.

## 3.1 Roles, Entities, and Components

A **role** is a responsibility this specification standardizes. A role is defined only where at least one of the following holds: it sends or receives HCP messages; it makes, or is subject to, an authorization decision; its identity is needed for provenance or audit; or this specification assigns it obligations.

An **entity** is the person, organization, or deployed software that occupies one or more roles.

A **component** is part of an entity that HCP does not communicate with directly: a language model, a vector store, a database, a policy engine, a consent screen, an MCP tool implementation. A component is never an actor, however important it is to an implementation.

A model is a component. It MAY be the Context Asserter of an entry ([3.2.6](#326-context-asserter)). It is never the HCP Client, the Authorizing Principal, the Requesting Party, or the Client Operator.

An **HCP instance** is a resource, not an actor: the entries, lifecycle records, grants, and audit log held for one Context Subject and exposed through an HCP Provider. A provider may host many instances. A requirement stated of an instance is a requirement on the HCP Provider for that instance.

| Not an actor | What it is |
|-------------------------|----------------------------------------------------------------|
| HCP instance | A resource held for one Context Subject |
| Context store | A storage component behind the HCP Provider ([1.4](#14-the-interface-boundary)) |
| Model | A processing component; sometimes the Context Asserter |
| MCP host | A common implementation of an HCP Client ([10](#10-mcp-binding)) |
| Grant | An authorization record ([6](#6-authorization)) |
| Access token | A credential representing a grant |
| Audit log | A resource governed on the Context Subject's behalf ([8](#8-audit)) |
| Notification endpoint | An endpoint operated for an HCP Client ([6](#6-authorization)) |
| "System" | Not an identity; each event names the responsible role ([3.9](#39-audit-participants)) |

**Terminology.** Normative sentences in this specification name roles. Explanatory text uses "the person" for the Context Subject where the meaning is plain. "User", "agent", "application", and "system" are not used normatively. Enumerated values follow the same rule: v1's `user-declared` and `user-input` are `person-declared` and `person-input`.

## 3.2 Roles

| Role | Status | Responsibility |
|------------------------|--------------------------|----------------------------------------------------------|
| Context Subject | Required | The person the context describes |
| Authorizing Principal | Required | Grants, narrows, and revokes access |
| HCP Client | Required | Makes HCP requests and holds and presents the grant |
| HCP Provider | Required | Exposes the HCP interface and enforces it for each instance |
| Authorization Service | Required | Obtains the Authorizing Principal's decision and creates the grant |
| Context Asserter | Required for each entry | Originated the assertion an entry contains |
| Requesting Party | Required when it differs from the Context Subject | The person or organization for whose benefit the client acts |
| Client Operator | Required metadata | The organization accountable for an HCP Client |
| Provider Operator | Required metadata | The organization accountable for an HCP Provider |

### 3.2.1 Context Subject

The Context Subject is the natural person an HCP entry describes. An HCP instance has exactly one primary Context Subject, and every entry in it makes assertions about that person ([3.11](#311-actor-invariants), invariant 2). An entry may mention other people — "my manager is unavailable on Fridays" — without making any of them a Context Subject. The entry remains context about its subject.

The Context Subject is not necessarily the person using a client, the author of an assertion, the party requesting access, the party empowered to authorize it, or the holder of a credential. These usually coincide; this specification does not assume they do.

### 3.2.2 Authorizing Principal

The Authorizing Principal is the party with authority to grant, narrow, and revoke access to an HCP instance. It approves or declines grants, chooses temporary or persistent access, revokes grants, reviews grants and the audit log, confirms or rejects entries, and requests correction, export, and hard deletion.

Authentication establishes who is interacting with the Authorization Service. It does not establish that the party has authority to approve access ([6](#6-authorization)). In Core, the Authorizing Principal MUST be the Context Subject ([3.3](#33-co-location-and-delegation)).

### 3.2.3 HCP Client

The HCP Client is the authenticated software that makes HCP requests to an HCP Provider and holds and presents the grant under which it acts. Examples: an assistant application's backend, an agent runtime, an MCP host or its integration, an institutional integration, a command-line tool, and the person's own management application.

An HCP Client acts in one of two capacities:

- **Management Client.** An HCP Client acting for the Authorizing Principal, under credentials the Authorizing Principal obtained by authenticating for that purpose. Governance operations are reserved to a Management Client ([1.6](#16-context-plane-and-governance-plane), [6](#6-authorization)). This replaces v1's references to "the person's own authenticated session".
- **Context Client.** An HCP Client acting under a grant for a task. A Context Client performs context operations only.

The same software MAY act in both capacities under different credentials. The capacity is a property of the credentials presented, not of the software.

The HCP Client, not any model operating within it, is the security principal. The component that presents credentials holds the grant ([10](#10-mcp-binding)).

### 3.2.4 HCP Provider

The HCP Provider is the service that exposes the HCP interface for one or more HCP instances and enforces this specification for each. It authenticates HCP Clients, enforces grants and their restrictions, records and retrieves context, applies minimization, maintains lifecycle state, records provenance, produces audit events, and supports governance operations. It enforces a grant independently of any decision made by an intermediary ([3.11](#311-actor-invariants), invariant 10).

Any organization, institution or individual may operate an HCP Provider, including a person running one for themselves. This specification assumes nothing about how a person chooses a provider. A person moves to another provider by export and import ([5.4.1](#541-export), [5.4.3](#543-import)), which carry their entries, with provenance, and their standing rules ([6.3](#63-standing-rules)).

### 3.2.5 Authorization Service

The Authorization Service authenticates the Authorizing Principal, presents what is being requested, records the decision, creates the grant, issues the authorization evidence the HCP Client presents, and expires and revokes grants. It decides what has been authorized; the HCP Provider decides whether a given request falls within it.

The Authorization Service MAY be deployed within the HCP Provider. Under the OAuth Interop Profile ([13](#13-oauth-interop-profile)) it is the OAuth authorization server. Under the First-Party Authorization Profile ([12](#12-first-party-authorization-profile)) it is functionality within the provider or its person-facing application, and its obligations are unchanged.

### 3.2.6 Context Asserter

The Context Asserter is the person, model, or organization that originated the assertion an entry contains. It is recorded separately from the HCP Client that submitted the entry ([3.11](#311-actor-invariants), invariant 7).

| Entry | Context Asserter |
|----------------------------------------------------------|--------------------------------------------|
| "I prefer concise answers." | The Context Subject |
| The person appears to prefer morning flights. | The model that made the inference |
| The student completed Calculus I. | The university |
| The patient is allergic to penicillin. | The clinician or clinical system |

The term issuer is reserved for the issuer of a credential under the VC Evidence Profile ([14](#14-vc-evidence-profile)). The VC roles of issuer, holder, and verifier are defined there and are not Core roles.

### 3.2.7 Requesting Party

The Requesting Party is the person or organization for whose benefit, or at whose direction, the HCP Client seeks access. It is not necessarily the Client Operator.

| Situation | Requesting Party | HCP Client | Client Operator |
|----------------------------------|------------------|------------------------|--------------------------|
| A person plans their own trip | The person | Travel assistant | The travel company |
| A clinician uses an EHR assistant | The clinician or clinic | EHR assistant | The EHR vendor or clinic |
| A teacher uses a tutoring platform | The teacher or school | Tutoring platform | The education company |

The Requesting Party is fixed in the grant when the Authorizing Principal approves it ([3.4](#34-the-grant-binds-the-actors)).

### 3.2.8 Client Operator and Provider Operator

The Client Operator is the organization accountable for an HCP Client. The Provider Operator is the organization accountable for an HCP Provider. Neither is a protocol peer; both are identified so that the person can tell which organization is accountable.

- Client registration MUST identify the Client Operator by an identifier and a name the person can recognize. A product name alone does not satisfy this. The Client Operator's name MUST be shown to the Authorizing Principal when a grant is requested and wherever grants are listed.
- The discovery document MUST identify the Provider Operator ([19](#19-discovery-document)).

### 3.2.9 How Each Role Is Identified

| Role | Basis of identity or authority |
|-------------------------|--------------------------------------------------------------|
| Context Subject | Bound to the HCP instance; presented to each HCP Client as a per-client pseudonym ([3.4](#34-the-grant-binds-the-actors)) |
| Authorizing Principal | Authenticated by the Authorization Service when granting, and by the provider when acting through a Management Client |
| HCP Client | Client registration and the authorization evidence it presents |
| HCP Provider | Its endpoint and discovery document |
| Authorization Service | The authorization evidence the HCP Provider accepts from it |
| Context Asserter | Recorded with an assurance level ([3.6](#36-asserter-assurance)) |
| Requesting Party | Bound into the grant at approval ([3.4](#34-the-grant-binds-the-actors)) |
| Client Operator | Client registration |
| Provider Operator | The discovery document |

### 3.2.10 Relationship to Other Standards (Informative)

| HCP role | OAuth 2.0 | MCP | VC Data Model and UMA |
|------------------------|-------------------------------|----------------------------------------|---------------------------------|
| Context Subject | Usually the resource owner | No direct equivalent | Credential subject |
| Authorizing Principal | Resource owner | The person taking part in authorization | Not necessarily the holder |
| HCP Client | Client | The host-side application and its client connection | Sometimes a verifier |
| HCP Provider | Resource server | Server | May act as repository or verifier |
| Authorization Service | Authorization server | Authorization server protecting the server | No equivalent |
| Context Asserter | No equivalent | No equivalent | Issuer, where credentialed |
| Requesting Party | Not modeled | No equivalent | UMA requesting party |

The mappings are deliberately not one-to-one. The Context Subject is not the resource owner where a delegate authorizes ([17](#17-delegated-authorization-profile)). The HCP Client is not the MCP client connection alone, because the application's identity, its authorization state, and its control over the model may belong to the wider host.

## 3.3 Co-location and Delegation

Roles MAY be co-located. Co-location does not remove the obligations of any role ([3.11](#311-actor-invariants), invariant 1). In a typical first-party deployment the person is Context Subject, Authorizing Principal, and Requesting Party; the assistant application is the HCP Client; and one service is both HCP Provider and Authorization Service.

In Core, the Authorizing Principal MUST be the Context Subject. A grant authorized by any other party is conformant only under the Delegated Authorization Profile ([17](#17-delegated-authorization-profile)). That profile defines what gives a delegate authority, the scope of that authority, how it ends, the Context Subject's override, and what happens when a minor reaches the age of majority. Under it the Context Subject remains the person the entries describe, and can always revoke a grant made for them ([17.5](#175-the-context-subjects-override)).

The `authorizingPrincipal` member of the grant ([3.4](#34-the-grant-binds-the-actors)) replaces v1's `grantor`, which was recorded but never interpreted.

Because v1 required `grantor` to be recorded, the party who authorized each v1 guardian grant is known. Such grants carry over as delegated grants with an unspecified basis ([17.8](#178-grants-carried-over-from-v1)).

## 3.4 The Grant Binds the Actors

Every grant identifies the Context Subject, the Authorizing Principal, the HCP Client, and the Client Operator, and identifies the Requesting Party when it differs from the Context Subject ([3.11](#311-actor-invariants), invariants 3 and 4). The grant object is defined whole in 6. Its actor members follow these rules:


| Member | Rule |
|-----------------------|----------------------------------------------------------------------|
| `subject` | Identifies the Context Subject by a pseudonym specific to the HCP Client. The provider MUST NOT present the same identifier for one Context Subject to two different HCP Clients, so that clients cannot link the person across services. |
| `authorizingPrincipal` | Identifies the Authorizing Principal. In Core it identifies the Context Subject and carries the same pseudonym as `subject`. Under the Delegated Authorization Profile it identifies the delegate and names the delegation ([17.4](#174-scope-and-grants-under-a-delegation)). Replaces `grantor`. |
| `client.operator` | The Client Operator, taken from client registration ([3.2.8](#328-client-operator-and-provider-operator)). |
| `requestingParty` | Fixed when the grant is approved and shown to the Authorizing Principal before the approving act ([6](#6-authorization)). A request MUST NOT supply or change it. Omitted means the Context Subject. |

## 3.5 Provenance Layers

An entry's provenance records five separate facts, all in `record.provenance`, which is defined whole in 4. Provenance belongs to a version: each version of an entry carries its own.

| Layer | Question | Field | Set by |
|------------------|----------------------------------------|------------------------------------|--------------------------|
| Assertion | Who originated the assertion, and when? | `assertedBy.id`, `assertedAt` | The submitting HCP Client |
| | How was the asserter's identity established? | `assertedBy.assurance`, `assertedBy.via` | The HCP Provider ([3.6](#36-asserter-assurance), [3.7](#37-statements-attributed-to-the-context-subject)) |
| Submission | Which HCP Client sent it? | `submittedByClient` | The HCP Provider |
| Authorization | Which grant permitted the write? | `authorizedUnder` | The HCP Provider |
| Record | Which provider recorded it, and when? | `recordedByProvider`, `recordedAt` | The HCP Provider |
| Confirmation | Did the Context Subject later confirm or reject it? | `confirmations` | The HCP Provider ([3.8](#38-confirmation)) |

Evidence is held in the entry's `evidence` ([4.2](#42-entry)), not in provenance. A credential there is either the entry's content or support for it ([4.2.2](#422-evidence)). Evidence never raises `assertedBy.assurance` by itself ([3.11](#311-actor-invariants), invariant 15); a credential that is the entry's content is recorded as `cryptographically-verified` only when its proof is validated ([14.6](#146-ingest)).

`record.provenance.source` is retained. It is the submitting client's statement of where the assertion came from — a conversation, a document, direct input, an integration — and the provider records it as supplied without verifying it.

Requirements:

- The HCP Provider MUST set `assertedBy.assurance`, `submittedByClient`, `authorizedUnder`, `recordedByProvider`, `recordedAt`, and `confirmations` itself. It MUST NOT take any of them from a request.
- `submittedByClient` has the same shape as the grant's `client` ([3.4](#34-the-grant-binds-the-actors)): the client's identifier and name, and its operator's identifier and name, as they stood when the version was recorded. A later rename or change of operator does not alter them.
- `assertion.declarationType` records what kind of party asserted the entry; `assertedBy.id` records which one.
- Where `assertion.declarationType` is `model-inferred`, `assertedBy.id` SHOULD identify the model that produced the inference at a granularity that distinguishes model versions, rather than naming only the application that wrote the entry.
- `assertedBy` alone records who asserted the entry.
- Where the entry's content is a credential ([14](#14-vc-evidence-profile)), `assertedBy` identifies the credential's issuer, and the credential is not altered.

**Replaces.** `record.provenance.capturedBy` is replaced by `assertedBy` and `submittedByClient`. `capturedAt` is replaced by `assertedAt` and `recordedAt`. `userVerified` is removed; confirmation is recorded in `confirmations` ([3.8](#38-confirmation)). v1's `claim.issuer` and `claim.issuanceDate` are removed: the first repeated `assertedBy.id`, the second `recordedAt`. How a v1 entry's provenance is carried into v2 is set out in 4.3.

**Visibility to Context Clients.** Which provenance fields are returned to a Context Client is shown in 3.10. The redaction rule is in 7; the Context Subject's own access is not redacted.

## 3.6 Asserter Assurance

`assertedBy.assurance` records how the HCP Provider established who the Context Asserter is.

| Value | Meaning |
|----------------------------|------------------------------------------------------------------|
| `unverified` | The submitting HCP Client named the asserter, and nothing else establishes it |
| `authenticated` | The asserter submitted under its own credentials, or through an HCP Client the asserter itself authorized to submit on its behalf, by an authorization the HCP Provider verified ([3.7](#37-statements-attributed-to-the-context-subject), [14.10](#1410-attestation-authorizations)) |
| `cryptographically-verified` | The assertion is signed, and the provider verified the proof |

The value records how strongly the asserter's identity was established. It does not require a strong identity, and it is not a judgment of whether the asserter is trustworthy. That judgment belongs to each consumer of the entry, and HCP does not store it. A provider MUST NOT record a higher value than it established ([3.11](#311-actor-invariants), invariant 15).

A client making a consequential decision on a credential — eligibility, an age threshold, a clinical record — SHOULD verify the credential itself rather than rely on `assurance` or `verification`. A credential can be verified by anyone who receives it ([14](#14-vc-evidence-profile)), and under end-to-end encrypted storage the check behind those values was made on the Context Subject's side ([4.8](#48-encrypted-storage)).

Confirmation by the Context Subject does not change assurance. It is recorded separately ([3.8](#38-confirmation)).

## 3.7 Statements Attributed to the Context Subject

A declaration type supplied by a caller does not by itself establish that the Context Subject made or confirmed an assertion ([3.11](#311-actor-invariants), invariant 8). An entry whose `declarationType` is `person-declared` is recorded with assurance `authenticated` only on one of these bases:

- the entry was written by a Management Client;
- the Authorization Service obtained the Context Subject's confirmation of that statement when it was written.

Without either, the provider accepts the entry and records assurance `unverified`. The Context Subject MAY later confirm it ([3.8](#38-confirmation)).

Only a `person-declared` entry recorded as `authenticated` or `cryptographically-verified`, or an entry the Context Subject has confirmed, has the standing in a conflict that this specification gives the Context Subject's own statements ([4](#4-data-model)). Where an `unverified` `person-declared` entry conflicts with another entry, neither prevails; the conflict is presented to the Context Subject to resolve.

An `issuer-attested` entry is accepted only from an HCP Client authenticated as that issuer, or authorized by that issuer to attest on its behalf. The authorization MUST come from the issuer; a client's own claim to act for an issuer, including one made at registration, is not authorization. The provider rejects any other attempt with the Core error not authorized ([5](#5-operations-and-errors)). A Context Client therefore cannot create `issuer-attested` entries, or entries whose content is a credential, on its own account.

An issuer authorizes a client in one of two ways, and the provider records which in `assertedBy.via` ([4.2](#42-entry)):

- **An attestation authorization.** A Verifiable Credential the issuer issues to the client, naming the client, what it may attest, and until when ([14.10](#1410-attestation-authorizations)). The provider verifies it, and its status, under the VC Evidence Profile. An entry written under one is recorded as `authenticated`.
- **A recorded arrangement.** An agreement between the issuer and the Provider Operator, outside HCP, which the provider records. The provider has only its own word for it, so an entry written under one is recorded as `unverified` ([3.11](#311-actor-invariants), invariant 15).

When an issuer revokes an authorization, or it expires, the provider refuses further `issuer-attested` writes under it. Entries already written keep the assurance recorded with them: provenance belongs to a version and records how the asserter was established when it was written ([3.5](#35-provenance-layers)).

## 3.8 Confirmation

Confirming or rejecting an entry is a governance operation ([1.6](#16-context-plane-and-governance-plane)), performed by the Context Subject through a Management Client. The provider appends a confirmation record: the `disposition` (`confirmed` or `rejected`), `confirmedBy`, and `confirmedAt`.

- A confirmation does not change the entry's `declarationType` or its `assertedBy` ([3.11](#311-actor-invariants), invariant 12), and does not create a new version.
- A confirmation applies to the version it was made on. A new version starts with no confirmations, so a revision never inherits the Context Subject's endorsement of earlier wording.
- A Context Client MUST NOT revise an entry whose current version the Context Subject has rejected.
- Where the Context Subject edits the entry while confirming it, the edit creates a new version. That version is the Context Subject's own statement: `declarationType` `person-declared`, `assertedBy.id` identifying the Context Subject, and assurance `authenticated`.
- Status transitions on confirmation and rejection are those in 4.

An entry is authoritative in a conflict if it is a `person-declared` entry recorded as `authenticated` or `cryptographically-verified`, or if the most recent confirmation record on its current version is `confirmed`, whoever asserted it. Consumers MUST determine standing from assurance and confirmation records, not from `declarationType` alone.

This reverses v1, under which accepting an inference rewrote its `declarationType` to `user-declared` (now `person-declared`).

## 3.9 Audit Participants

Each audit event identifies its participants in a `participants` block, which replaces v1's `actorId` and `actorType`. The audit event, including the block, is defined whole in 8.

`initiator.role` is one of `management-client`, `context-client`, `authorization-service`, or `hcp-provider`.

- `initiator` and `provider` are always present. Where the initiator is an HCP Client, `clientOperator` is present.
- `requestingParty`, `authorizingPrincipal`, and `retrievalId` are present wherever the event concerns a grant or a disclosure.
- `model` is present where the initiating client identifies the model that constructed the request. It never replaces the client.
- An event with no initiating client, such as a grant expiring or a conflict being detected, names the Authorization Service or the HCP Provider as initiator. No event names "system".

## 3.10 Actor-Identifying Fields

Every field that identifies a party, or records how a party was identified, is listed below. Each is defined in the object named, and that definition governs. The table is a cross-reference for checking that the grant, the entry, and the audit event identify parties consistently.

| Field | Object | Set by | Returned to a Context Client | Defined in |
|--------------------------------|------------|------------------------|----------------------|------------|
| `subject` | Grant | Authorization Service | Yes, in its own grant | 6 |
| `authorizingPrincipal` | Grant | Authorization Service | Yes, in its own grant | 6 |
| `authorizingPrincipal.delegation` | Grant | Authorization Service, under the Delegated Authorization Profile | No | 6, 17 |
| `delegate`, `basis.establishedBy` | Delegation | Authorization Service | No | 17 |
| `client.id`, `client.name` | Grant | Client registration | Yes, in its own grant | 6 |
| `client.operator` | Grant | Client registration | Yes, in its own grant | 6 |
| `client.claims` | Grant | Client registration | Yes, in its own grant | 6, 18 |
| `requestingParty` | Grant | Authorization Service, at approval | Yes, in its own grant | 6 |
| `assertedBy.id` | Entry | Submitting HCP Client | No | 4 |
| `assertedBy.assurance` | Entry | HCP Provider | Yes | 4 |
| `assertedBy.via` | Entry | HCP Provider | No | 3.7, 4 |
| `basis.parent` | Delegation | Authorization Service | No | 17.10 |
| `assertedAt` | Entry | Submitting HCP Client | Yes | 4 |
| `source` | Entry | Submitting HCP Client | No | 4 |
| `submittedByClient` | Entry | HCP Provider | No | 4 |
| `authorizedUnder` | Entry | HCP Provider | No | 4 |
| `recordedByProvider` | Entry | HCP Provider | Yes | 4 |
| `recordedAt` | Entry | HCP Provider | Yes | 4 |
| `confirmations[].disposition`, `confirmedAt` | Entry | HCP Provider | Yes | 4 |
| `confirmations[].confirmedBy` | Entry | HCP Provider | No | 4 |
| `relationships[].assertedBy` | Entry | HCP Provider, from the asserting HCP Client or Memory Manager | No | 4 |
| `conversion.convertedBy` | Entry | HCP Provider | No | 4 |
| `participants` (all members) | Audit event | HCP Provider | No; reading the audit log is a governance operation | 8 |

## 3.11 Actor Invariants

A grant authorizes an HCP Client — the authenticated party holding and presenting it — not any component that happens to construct a request on that client's behalf. The following invariants hold in every binding and profile.

| # | Invariant | Applied in |
|------|----------------------------------------------------------------------|------------|
| 1 | Roles MAY be co-located. Co-location does not remove the obligations of any role. | 3.3 |
| 2 | An HCP instance has exactly one primary Context Subject, and every entry in it makes assertions about that Context Subject. | 3.2.1, 4 |
| 3 | Every grant MUST identify the Context Subject, the Authorizing Principal, the HCP Client, and the Client Operator. | 3.4, 6 |
| 4 | Every grant MUST identify the Requesting Party when it differs from the Context Subject. | 3.4, 6 |
| 5 | Every protected operation MUST be attributable to an authenticated HCP Client. An operation with no attributable client is not authorized, regardless of its content. | 6 |
| 6 | An HCP Client MUST NOT derive additional authority from model-generated intent or request arguments. That a model produced a plausible request for a scope, or that its output implies the Context Subject's intent, does not itself satisfy an authorization requirement of this specification. | 6 |
| 7 | The Context Asserter MUST be recorded separately from the HCP Client that submitted the assertion. | 3.5, 4 |
| 8 | A declaration type supplied by a caller MUST NOT by itself establish that the Context Subject made or confirmed the assertion. | 3.7, 4 |
| 9 | A model MUST NOT be treated as the authenticated HCP Client merely because it generated the request's arguments. Authentication attaches to the client presenting the grant, not to whatever component assembled the call. | 6, 10 |
| 10 | The HCP Provider enforces a grant's scope and restrictions independently of any permission decision made by an MCP host, agent runtime, or other intermediary. A host permitting a tool call does not substitute for, or relax, HCP's own enforcement. | 6, 10 |
| 11 | An issuer's signature secures the integrity of a credential; it does not itself authorize its disclosure. Whether the HCP Provider may release an entry carrying that credential to a given HCP Client is governed entirely by the grant ([6](#6-authorization)). | 6, 14 |
| 12 | Confirmation of an assertion by the Context Subject MUST NOT change its recorded Context Asserter. | 3.8, 4 |
| 13 | Audit events MUST identify every security-relevant participant, not a generic user, agent, or system actor. | 3.9, 8 |
| 14 | The HCP Client is responsible for downstream processing performed by models and other components operating under it. Delegating a request's construction to a model does not delegate the client's obligations under this specification. | 3.12, 6 |
| 15 | An actor identity that cannot be verified MUST NOT be silently upgraded to a trusted identity. An unauthenticated or unverifiable caller MUST be recorded and treated as such, not promoted to trusted status by default or by omission. | 3.6, 6 |

Invariants 5, 6, 9, 10, 14, and 15 were adopted in v1 at 4.1.8, and invariant 11 at 2.4.1. Invariants 1–4, 7, 8, 12, and 13 are new in v2.

## 3.12 Onward Disclosure

An HCP Client MUST NOT pass context disclosed to it under a grant to a party operated by a different organization — that is, by anyone other than its own Client Operator. That party obtains its own grant from the Authorizing Principal. An HCP Client MAY pass disclosed context to components and services operated by its own Client Operator, and remains responsible for that processing under invariant 14. The copy's use-until time travels with it ([7.6](#76-use-until)).

The rule is deliberately strict. A handoff between two organizations' agents requires a fresh authorization by the person, because that is the point at which a new organization gains access. A directive can restrict passing context further, including within one operator; none can relax this section ([6.4](#64-directives)).

**Onward sharing the person allowed.** One exception rests on the grant itself. Where an authorization detail carries `onwardSharing` ([6.1.5](#615-grant-representation)), which the Authorizing Principal elects by a separate act ([6.1.4](#614-grant-distinction-temporary-vs-persistent)), the HCP Client MAY tell an organization it deals with in carrying out a task for the Context Subject what that task needs from an entry disclosed to it with `onwardSharing` set ([7.4](#74-disclosures-to-context-clients)), for one of the detail's purposes:

- It MUST state only what the task needs, in its own words. It MUST NOT pass on entries, `ref`s, provenance, evidence or credentials, or a copy of a disclosure.
- It MUST NOT share with an organization outside `onwardSharing.domains`, where that is present, or named in `onwardSharing.notTo`.
- A directive whose `action` is `share` applies: under `deny` the client MUST NOT share, and under `ask-first` it MUST ask the Context Subject each time ([6.4](#64-directives)).
- It MUST report each share to the HCP Provider ([5.2.8](#528-report-onward-sharing)).

The receiving organization is outside HCP. What it does with what it was told is beyond the protocol's reach ([21.1](#211-what-hcp-does-not-prevent), [21.4](#214-disclosure)).

Context a Management Client exports at the Authorizing Principal's direction is not disclosed under a grant and is not subject to this section.

## 3.13 How the Roles Interact (Informative)

**Read.**

1. The Requesting Party gives the HCP Client a task.
2. The HCP Client requests a grant. The Authorization Service authenticates the Authorizing Principal and shows the client, its operator, the Requesting Party, the categories and actions, the purposes, the duration, and any restrictions.
3. The Authorizing Principal approves. The Authorization Service creates the grant and issues authorization evidence to the HCP Client.
4. The HCP Client sends a query to the HCP Provider with the evidence, the categories, the query, and a declared purpose.
5. The HCP Provider identifies the client, finds the grant, applies scope and restrictions, selects and minimizes entries, and records the disclosure and declared purpose in the audit log.
6. The HCP Client decides what reaches any model. Credentials never enter the model's context ([10](#10-mcp-binding)).

**Model-inferred write.**

1. A model produces an inference. The HCP Client decides whether to submit it.
2. The HCP Client submits the assertion, naming the model as Context Asserter.
3. The HCP Provider records the model as asserter with assurance `unverified`, the client as submitter, the grant, and the time it recorded the entry.
4. The Context Subject may later confirm or reject it. A confirmation adds a record and leaves the asserter unchanged.

**Revocation.**

1. The Authorizing Principal revokes the grant through a Management Client or the Authorization Service.
2. The Authorization Service marks the grant revoked and invalidates the evidence issued under it. The HCP Provider rejects later requests under it and records the revocation.
3. The HCP Client is notified ([6](#6-authorization)) and remains responsible for what it already holds.
# 4. Data Model

## 4.1 Overview

An HCP entry describes the Context Subject through independent properties:

| Property | What it holds | Set by | Defined in |
|-----------------------|------------------------------------------------|------------------------------------------------------------|----------------------|
| `subject` | Who the entry is about | HCP Client; MUST identify the Context Subject | 4.2 |
| `content` | What is said, in the shape a content profile defines | HCP Client | 4.2; General Context Profile ([11](#11-general-context-profile)) |
| `assertion` | What kind of party said it, how confident it is, and until when it holds | HCP Client | 4.2, 4.4 |
| `classification` | Which category it belongs to, and the dimension it addresses | HCP Client on create; afterwards only by governance ([4.2.1](#421-mutability)) | 4.2, 4.5 |
| `evidence` | Credentials that are the content, or that support it | HCP Client | 4.2.2; VC Evidence Profile ([14](#14-vc-evidence-profile)) |
| `record` | Lifecycle, version, provenance, and relationships | HCP Provider | 4.2, 3.5, 4.2.3 |

The properties vary independently. A statement the Context Subject made about a health condition is high-sensitivity without carrying any credential; an Open Badges credential carries a proof without being sensitive; and either may be inferred, declared, or attested. This section defines the entry, declaration types, the category vocabulary, and what Core requires when entries conflict.

## 4.1.1 Processing Requirements

Conformance requires no JSON-LD processing.

- The `@context` array is a fixed constant. Implementations MUST emit it exactly as specified in 4.2 and MAY compare it literally on ingest.
- Implementations are not required to perform JSON-LD expansion, compaction, flattening, framing, or RDF canonicalization, and are not required to embed a JSON-LD processor.
- Validation of an entry is JSON Schema validation against the schema published alongside this specification ([Appendix A](#appendix-a-registries-and-published-artifacts)).
- An implementation that treats entries as plain JSON documents carrying a constant `@context` is fully conformant to Core.

A credential in `evidence` may be secured with a mechanism that requires canonicalization ([14](#14-vc-evidence-profile)). That requirement is confined to the credential.

## 4.2 Entry

Every HCP entry is a JSON document conforming to the following structure. It has one form ([4.3](#43-one-form-and-conversion-from-v1)).

**Template: the entry, as the HCP Provider holds it**

    {
      "@context": ["https://hcp.example/contexts/v2"],
      "schema": "https://hcp.example/spec/entry/2.0",
      "id": "urn:uuid:{entry-uuid}",
      "type": ["ContextEntry"],
      "subject": { "id": "{subject-identifier}", "relationship": null },
      "content": { },
      "assertion": {
        "declarationType": "person-declared | model-inferred | issuer-attested",
        "confidence": "{high | medium | low | null}",
        "validUntil": "{date-time | null}",
        "basis": { },
        "permittedPurposes": ["{purpose URI}"]
      },
      "classification": {
        "categories": ["{category}"],
        "dimension": "{dimension-string | null}",
        "permittedPurposes": ["{purpose URI}"]
      },
      "evidence": [ ],
      "record": { }
    }

`subject.id` MUST identify the Context Subject of the HCP instance that holds the entry ([3.11](#311-actor-invariants), invariant 2). The subject identifier MAY be any URI, including a pseudonym the HCP Provider issues. HCP defines no DID method. `subject.relationship` is reserved ([11.3](#113-relationship)).

`content` is what is said about the Context Subject. Its shape is named by `content.profile`, a URI. This specification defines two content profiles: the General Context Profile, for statements in natural language or as structured objects ([11](#11-general-context-profile)), and the VC Evidence Profile, for an entry whose content is a credential ([14](#14-vc-evidence-profile)). Where the content is a credential, `content` names the evidence item that holds it instead of restating it ([4.2.2](#422-evidence)).

`assertion` is what the submitting HCP Client states about the assertion: what kind of party made it ([4.4](#44-declaration-types)), how confident an inferring model is ([4.4](#44-declaration-types)), and `validUntil`, the time after which the content no longer holds. `validUntil` describes the content. It is not the time after which a client may no longer use a disclosed copy ([7](#7-disclosure-and-minimization)). The assertion may also state what it was drawn from, in `basis` ([4.2.5](#425-basis)), and the purposes for which the entry may be used, in `permittedPurposes` ([4.2.6](#426-permitted-purposes)).

`classification` is HCP's classification of the entry: its categories ([4.5](#45-category-vocabulary)), its dimension, and any narrowing of its purposes by the Authorizing Principal ([4.2.6](#426-permitted-purposes)). It sits apart from `content` and `evidence` because HCP determines it: an issuer of a Verifiable Credential has no reason to know HCP's category vocabulary, and category governs authorization scope, which is not an issuer's decision to make.

`schema` identifies the version of this entry structure. It is required on every entry, including entries in an export, and its value in this draft is `https://hcp.example/spec/entry/2.0`, compared as an exact string ([1.7](#17-conformance-identifiers)). An HCP Provider MUST reject with invalid request ([5.5](#55-errors)) a write naming a schema it does not accept ([4.3](#43-one-form-and-conversion-from-v1)).

### record

**Template: the entry's `record` member**

    "record": {
      "status": "active | deprecated | conflicted | expired | revoked | suspended | deleted",
      "version": 1,
      "provenance": {
        "assertedBy": {
          "id": "{identifier}",
          "assurance": "unverified | authenticated | cryptographically-verified",
          "via": { "kind": "authorization-credential | arrangement", "id": "{identifier}" }
        },
        "assertedAt": "{date-time}",
        "source": "{conversation-id | document-id | person-input | integration}",
        "submittedByClient": {
          "id": "{client-identifier}",
          "name": "{client name}",
          "operator": { "id": "{operator-identifier}", "name": "{organization name}" }
        },
        "authorizedUnder": "{grant-id}",
        "recordedByProvider": "{provider-identifier}",
        "recordedAt": "{date-time}",
        "confirmations": [
          {
            "disposition": "confirmed | rejected",
            "confirmedBy": { "id": "{identifier}" },
            "confirmedAt": "{date-time}"
          }
        ]
      },
      "relationships": [
        {
          "type": "derivedFrom | supersedes | contradicts | duplicates",
          "target": "{entry-id}",
          "assertedBy": { "role": "{role}", "id": "{identifier}" },
          "recordedAt": "{date-time}",
          "proposal": { }
        }
      ]
    }

`record.provenance` records who asserted, submitted, authorized, recorded, and confirmed each version of the entry. Its rules are in 3.5–3.8. `record.relationships` is defined in 4.2.3, and `record.conversion`, present only on an entry converted from v1, in 4.3.

### Required Fields

| Field | Type | Description |
|-------------------------------------------|------------|------------------------------------------------------------------|
| `schema` | URI | The entry structure version |
| `id` | URN (UUID) | Globally unique entry identifier. Stable across all versions of the entry; never reassigned on revision. |
| `type` | Array | Must include "ContextEntry" |
| `subject.id` | URI | The Context Subject |
| `content.profile` | URI | The content profile defining the shape of `content` |
| `assertion.declarationType` | Enum | `person-declared`, `model-inferred`, or `issuer-attested`; never omitted. See 4.4. |
| `classification.categories` | Array | One or more categories, each a slug from the registered category vocabulary or a custom category URI, without duplicates ([4.5](#45-category-vocabulary)) |
| `record.provenance.assertedBy.id` | String | The Context Asserter ([3.5](#35-provenance-layers)) |
| `record.provenance.assertedBy.assurance` | Enum | How the asserter's identity was established ([3.6](#36-asserter-assurance)) |
| `record.provenance.assertedAt` | Date-time | When the assertion was made, as the submitting client states it |
| `record.provenance.source` | String | Origin of the entry, as the submitting client states it |
| `record.provenance.submittedByClient` | Object | The HCP Client that submitted this version, and its operator ([3.5](#35-provenance-layers)) |
| `record.provenance.authorizedUnder` | String | The grant under which this version was written |
| `record.provenance.recordedByProvider` | String | The HCP Provider that recorded this version |
| `record.provenance.recordedAt` | Date-time | When the provider recorded this version |
| `record.version` | Integer | Monotonically increasing revision number, starting at 1 |
| `record.status` | Enum | Lifecycle state of the entry |

The `record.version` field is a positive integer beginning at 1. Each successful revision MUST increment `record.version` by exactly 1. Implementations MUST NOT skip or reuse version numbers within an entry's revision history. Revision history is linear: the version preceding version *n* is *n* − 1, and a revision names the version it revises ([5.2.4](#524-revise)). `record.provenance.recordedAt` of the current version is the time the entry was last revised.

No UUID version is mandated for `id`: any RFC 9562 version MAY be used, and implementations MUST NOT assume or require a particular one.

The fields required in `content` are defined by its content profile ([11](#11-general-context-profile), [14](#14-vc-evidence-profile)).

### Optional Fields

| Field | Notes |
|--------------------------------------|------------------------------------------------------------------|
| `assertion.confidence` | MUST be present and non-null when `assertion.declarationType` is `model-inferred`. MUST be null or omitted for any other declaration type. |
| `assertion.validUntil` | If absent or null, the content does not expire. |
| `assertion.basis` | What the assertion was drawn from ([4.2.5](#425-basis)) |
| `assertion.permittedPurposes` | The purposes the asserter permits the entry to be used for ([4.2.6](#426-permitted-purposes)). Absent means no limit. |
| `classification.permittedPurposes` | The Authorizing Principal's narrowing of those purposes ([4.2.6](#426-permitted-purposes)). Absent means no limit. |
| `classification.dimension` | Free-form identifier for the dimension addressed by the entry, scoped within its categories. A hint for conflict detection ([15](#15-memory-manager-profile)). No vocabulary is registered. It MAY be a URI naming a concept in an external code system, such as SNOMED CT or LOINC, and is then compared as an exact string. |
| `evidence` | Evidence items ([4.2.2](#422-evidence)). Absent or empty when the entry carries none. |
| `record.provenance.confirmations` | Confirmation records for this version ([3.8](#38-confirmation)). Absent or empty when the version has none. |
| `record.provenance.assertedBy.via` | Present only where an HCP Client attested for an issuer under the issuer's authorization: its kind, and the identifier of the attestation authorization or the recorded arrangement ([3.7](#37-statements-attributed-to-the-context-subject)) |
| `record.relationships` | Relationships to other entries ([4.2.3](#423-relationships)). Absent or empty when there are none. |
| `record.conversion` | Present only on an entry converted from v1 ([4.3](#43-one-form-and-conversion-from-v1)). |
| `record.metadata` | Optional. Object. Free-form key-value data an implementation attaches to the entry for its own purposes — internal identifiers, application tags, integration bookkeeping. Not part of the assertion and not interpreted by HCP. |

`classification.dimension` is scoped within the entry's categories: the same string on two entries that share no category denotes two different dimensions and MUST NOT be treated as a match.

`record.metadata` carries no HCP-defined meaning and MUST NOT be used to store data that affects category, scope, or authorization. Conflict handling ([4.7](#47-conflicts)), minimization ([7](#7-disclosure-and-minimization)), and grant restrictions ([6.1.5.1](#6151-narrowed-grants)) operate over the fields those sections name, not over `metadata`. No vocabulary is registered, and `metadata` contents are not guaranteed portable across implementations.

An HCP Provider MUST preserve members of an entry that this specification does not define and MUST NOT interpret them ([A.3](#a3-extension-points)).

## 4.2.1 Mutability

These rules are stated as behavior observable across a binding or in an export ([1.4](#14-the-interface-boundary)).

- Once a version of an entry has been exposed, its `content`, `assertion`, and `evidence` MUST NOT change. A change to any member of them produces a new version, and `record.version` increments. The one exception is `verification` on an evidence item, which the HCP Provider updates when a credential's status changes ([4.2.2](#422-evidence), [14.7](#147-credential-status)).
- A change to a credential in `evidence` requires a new credential from its issuer. The HCP Provider MUST NOT alter a credential.
- `subject` MUST NOT change.
- The fields in `classification` and `record` MAY change without a new version, with one exception: `record.provenance` belongs to a version and is fixed when that version is recorded, apart from confirmation records appended to it ([3.8](#38-confirmation)). No credential's proof covers `classification` or `record`.
- `classification.categories` determines which grants reach the entry. Adding, removing, or replacing a category moves the entry between authorization scopes, and is therefore a governance operation ([5.4](#54-governance-operations)): it MUST be performed only by a Management Client acting for the Authorizing Principal, and MUST be recorded as a `context.recategorized` event naming the prior and new categories in detail.
- `classification.permittedPurposes` likewise changes only by a governance operation, recorded as a `context.restricted` event ([4.2.6](#426-permitted-purposes)).
- `record.provenance` sits in `record` because it describes how this HCP Provider received each version, not what an issuer attested. Two providers holding the same credential will hold different provenance for it, and both are correct.

## 4.2.2 Evidence

Each item in `evidence` carries a credential and states its role:

**Template: an evidence item**

    "evidence": [
      {
        "role": "content | supports",
        "type": "verifiable-credential",
        "credential": { },
        "verification": { "result": "verified | failed", "at": "{date-time}", "by": "provider | trust-domain" }
      }
    ]

| Member | Rule |
|-------------|------------------------------------------------------------------|
| `role` | `content`: the credential is the entry's content. `supports`: the credential backs the statement in `content.value`. |
| `type` | The kind of evidence. This draft defines `verifiable-credential`, a complete W3C Verifiable Credential ([14](#14-vc-evidence-profile)). |
| `credential` | The credential, whole, exactly as its issuer secured it |
| `verification` | The HCP Provider's record of its most recent verification of the credential: `result`, `verified` or `failed`, and `at`, when it was established. Set only under the VC Evidence Profile ([14.6](#146-ingest), [14.8](#148-supporting-credentials)). `by` says where it was made: `provider`, or `trust-domain` where the provider's storage is end-to-end encrypted and a component in the Context Subject's trust domain verified the credential for it ([4.8](#48-encrypted-storage)). |

Requirements:

- An entry carries at most one item whose `role` is `content`. Where it carries one, `content` names it ([14.2](#142-credential-and-signature-boundary)) and carries no `value`.
- The signature boundary: a credential's proof covers that credential and nothing else in the entry. `subject`, `content`, `assertion`, `classification`, `record`, and `verification` are never covered by any proof, and lifecycle changes to them do not invalidate one.
- The HCP Provider MUST NOT alter a credential, or any member of an evidence item other than `verification`.
- The HCP Provider sets `verification` itself. It MUST NOT take it from a request, and MUST NOT emit it for a credential it has not verified.
- An evidence item never raises `assertedBy.assurance` by itself, whatever its `verification` ([3.11](#311-actor-invariants), invariant 15). An entry is recorded as `cryptographically-verified` only under the VC Evidence Profile, when the credential that is its content passes validation ([14.6](#146-ingest)).
- An HCP Provider that does not conform to the VC Evidence Profile ([14](#14-vc-evidence-profile)) MUST reject a write carrying an evidence item whose `role` is `content`. It MAY accept `supports` items, which it preserves and does not interpret.
- An evidence item of a `type` the HCP Provider does not recognize is preserved and not interpreted ([A.3](#a3-extension-points)).

Under the VC Evidence Profile, a `supports` credential is verified on ingest and its status kept; a failure is recorded, not rejected ([14.8](#148-supporting-credentials)). An HCP Provider that does not conform to that profile records no `verification`.

## 4.2.3 Relationships

`record.relationships` records how an entry relates to other entries held by the same HCP instance.

| Type | Meaning | Effect in this draft |
|----------------|------------------------------------------------------------------|----------------------|
| `derivedFrom` | This entry was inferred or composed from the target | None; informational |
| `supersedes` | This entry replaces the target | The target becomes `deprecated` where a Management Client asserted the relationship, or the target's own Context Asserter did ([4.2.4](#424-status)); otherwise none |
| `contradicts` | This entry and the target cannot both be true | The conflict rules in 4.7 |
| `duplicates` | This entry states the same thing as the target | None; informational |

Requirements:

- A relationship is asserted by an HCP Client with a create or revise ([5.2.3](#523-create), [5.2.4](#524-revise)), by a Management Client, or by the HCP Provider under the Memory Manager Profile ([15](#15-memory-manager-profile)). The provider records `assertedBy` (the role, as in 3.9, and identifier of the asserting party) and `recordedAt`. It MUST NOT take either from a request.
- An HCP Client MAY assert a relationship only to an entry in a category its grant authorizes it to read. Any other target fails with not authorized ([5.5](#55-errors)), without disclosing whether the target exists.
- A `contradicts` relationship is symmetric: the provider records it on both entries. It MAY carry a proposal for resolving the conflict, which changes nothing until the Context Subject accepts it ([4.7.4](#474-proposals)).
- When either entry in a `contradicts` relationship is revised, a relationship asserted by an HCP Client is removed unless the revision asserts it again, and a relationship asserted under the Memory Manager Profile is kept only if the provider's method still finds the conflict ([15.3](#153-re-evaluation)).
- A Context Client receives a relationship only where its target is disclosed in the same response, with the target named by its `ref` ([7.4](#74-disclosures-to-context-clients)). When it asserts a relationship, it names the target by its `ref`.

## 4.2.4 Status

`record.status` is the entry's lifecycle state. A change of status never creates a version ([4.2.1](#421-mutability)).

| Status | Meaning | Entered when | Left when | Context Client |
|------------------------------|-----------------------------------|------------------------------------------------|----------------------------------------|----------------|
| `active` | Current and usable | Created; or returned to by the transitions in 4.7.3 and below | Any other transition | Reads it |
| `deprecated` | Replaced or set aside | A `supersedes` relationship that deprecates it ([4.2.3](#423-relationships)); acceptance of a conflicting entry ([4.7.3](#473-resolution)) | A revision | Cannot read it |
| `conflicted` | Held until the person resolves a conflict | 4.7.2 | 4.7.3 | Cannot read it |
| `expired` | Its content no longer holds | Its `assertion.validUntil`, or its credential's `validUntil` ([14.2](#142-credential-and-signature-boundary)), has passed | A revision whose validity has not passed | Cannot read it |
| `revoked` | Its content credential's issuer has revoked it | The status of its content credential shows it revoked ([14.7](#147-credential-status)) | A revision carrying a new credential | Cannot read it |
| `suspended` | Its content credential's issuer has suspended it | The status of its content credential shows it suspended ([14.7](#147-credential-status)) | The issuer lifts the suspension, returning it to the state it held; or a revision carrying a new credential | Cannot read it |
| `deleted` | Withdrawn, and still held | Withdraw ([5.2.5](#525-withdraw)); rejection in a conflict ([4.7.3](#473-resolution)) | Hard deletion ([5.4.2](#542-hard-deletion)), which removes the entry | Cannot read it |

- A Context Client reads only `active` entries. A query never returns an entry in another state, and a get entry by `ref` for one MUST fail with not authorized ([5.5](#55-errors)), exactly as for an entry that does not exist.
- The Context Subject sees entries in every state, through a Management Client and in export ([5.4.1](#541-export)).
- `expired` is set lazily, as a grant's expiry is ([8.1](#81-required-log-events)). The HCP Provider MUST NOT disclose an entry whose validity has passed, whether or not it has set the status yet. It MUST set `expired`, and append a `context.expired` event, no later than the first access to the entry after its validity passes, or within 24 hours of that time, whichever is first.
- `expired` takes precedence over `active`, `deprecated`, `conflicted` and `suspended`; `revoked` over every state but `deleted`; `suspended` over `active`, `deprecated` and `conflicted`; `deleted` over all. A deleted entry is held in full until it is hard-deleted.
- `revoked` and `suspended` are set without delay once the provider establishes the status ([14.7](#147-credential-status)), and each change is recorded as a `context.credentialStatus` event ([8.1](#81-required-log-events)).

## 4.2.5 Basis

An assertion is judged by what it was drawn from. `assertion.basis` records that, so that the Context Subject, and a client that receives the entry, can judge it. It is part of the assertion: it belongs to a version, and it is disclosed with the entry ([7.4](#74-disclosures-to-context-clients)).

**Template: the `assertion.basis` member**

    "basis": {
      "drawnFrom": ["conversation | document | observation | assessment | entries"],
      "task": "{the task during which the assertion was made}",
      "setting": "{where it was made, such as a classroom or a clinic visit}",
      "rationale": "{why, in words the Context Subject can read}"
    }

| Member | Rule |
|--------------|------------------------------------------------------------------|
| `drawnFrom` | The kinds of material the assertion was drawn from. The set is open; the values above are defined. `entries` means other entries, which the asserting client SHOULD also name by `derivedFrom` relationships ([4.2.3](#423-relationships)). |
| `task`, `setting`, `rationale` | Natural language. Each is optional. |

- A `model-inferred` entry SHOULD carry `assertion.basis`. An entry of any other declaration type MAY.
- `assertion.basis` MUST NOT identify any party other than the Context Subject, and MUST NOT carry an identifier of a client, a grant, a conversation, or a document. Who made the assertion, and where, is recorded in `record.provenance` ([3.5](#35-provenance-layers)), which is withheld from Context Clients ([7.4](#74-disclosures-to-context-clients)). The HCP Provider cannot check free text against this rule; the submitting HCP Client is responsible for it.

## 4.2.6 Permitted Purposes

A grant approves purposes for categories ([6.1.5.2](#6152-purposes)). An entry may be limited further, to some purposes only, so that the uses its asserter permitted travel with it. Where it is, a request naming any other purpose does not receive it, whatever the grant approved ([7.1](#71-category-and-purpose-bound)).

- `assertion.permittedPurposes` is set by the asserter, as part of the assertion: by the issuer for an `issuer-attested` entry, and by the writing client for any other. It belongs to a version, and only a revision changes it. Only an issuer revises an `issuer-attested` entry ([3.7](#37-statements-attributed-to-the-context-subject)), so only the issuer can widen its list.
- `classification.permittedPurposes` is set by the Authorizing Principal through a Management Client, as a governance operation ([5.4](#54-governance-operations)), recorded as a `context.restricted` event naming the prior and new lists. It can only narrow: a purpose it lists that `assertion.permittedPurposes` does not list has no effect.
- An entry MAY be disclosed for a purpose only where each list present includes it. A list that is absent sets no limit.
- Each value is a purpose code ([6.1.5.2](#6152-purposes)). Neither list widens a grant: a request naming a purpose the grant did not approve for the entry's categories fails as before.

## 4.3 One Form, and Conversion from v1

The structure in 4.2 is the only form in which an HCP Provider emits an entry.

- An HCP Provider MUST emit entries only in the form specified in 4.2, with `schema` set as specified there.
- An HCP Provider MAY accept entries written under v1, in v1's grouped form or its flat form, through import only. It MUST declare every entry schema it accepts in its discovery document as `accepts_entry_schemas` ([19](#19-discovery-document)).
- A context operation ([5.2](#52-context-operations)) carrying an entry in any form other than 4.2 MUST be rejected with invalid request ([5.5](#55-errors)).
- An HCP Provider MUST remain able to read entries in any form it has previously written.

**Conversion from v1.** An HCP Provider that accepts a v1 entry converts it to the form in 4.2:

- Conversion is not a revision. It does not increment `record.version`, does not create a version, and does not append a `context.revised` event.
- Conversion leaves the provenance v1 recorded unaltered, under the mapping below. It adds no confirmation record.
- Every v1 asserter is recorded with assurance `unverified`, because v1 did not record how the asserter was identified. The one exception is an entry whose content is a credential that the provider validates at conversion under the VC Evidence Profile ([14.6](#146-ingest)), which is recorded as `cryptographically-verified`.
- v1's `userVerified` creates no confirmation record and gives the entry no standing in a conflict ([4.7.1](#471-standing)). A v1 entry that was `user-declared` therefore has no standing until the Context Subject confirms it ([3.8](#38-confirmation)).
- The provider records the conversion in `record.conversion`. The Context Subject's own access shows it, and it is withheld from Context Clients ([7.4](#74-disclosures-to-context-clients)).
- The HCP Provider SHOULD offer the Context Subject, through a Management Client, a way to confirm converted entries whose `record.conversion.unmapped` carries `userVerified: true`. A confirmation so made is an ordinary confirmation record ([3.8](#38-confirmation)).

**Template: `record.conversion`, on an entry converted from v1**

    "conversion": {
      "from": "{v1 entry schema}",
      "convertedAt": "{date-time}",
      "convertedBy": "{provider-identifier}",
      "unmapped": { "userVerified": true }
    }

`unmapped` holds, verbatim, every v1 member that has no place in the form in 4.2.

| v1 field | v2 field |
|-----------------------------------------|------------------------------------------------------------------|
| `credentialType` | Removed. `NLPreference` becomes `content.profile` set to the General Context Profile ([11](#11-general-context-profile)); `VerifiablePreference` becomes an evidence item whose `role` is `content` ([14](#14-vc-evidence-profile)). |
| `claim.subject.id`, `claim.credentialSubject.id` | `subject.id` |
| `claim.subject.preference` | `content.value` |
| `claim.subject.relationship` | `subject.relationship` |
| `claim.issuer`, `claim.issuanceDate` | Removed |
| `claim.expirationDate` | `assertion.validUntil` |
| `record.category`, `record.dimension` | `classification.categories`, holding the one category; `classification.dimension` |
| `record.declarationType` | `assertion.declarationType`; `user-declared` becomes `person-declared` |
| `record.confidence` | `assertion.confidence` |
| `record.status`, `record.version` | Unchanged |
| `record.previousVersion` | Removed |
| `record.provenance.capturedBy` | `record.provenance.assertedBy.id`, with assurance as above |
| `record.provenance.capturedAt` | `record.provenance.assertedAt` |
| `record.provenance.source` | Unchanged; `user-input` becomes `person-input` |
| `record.provenance.userVerified` | `record.conversion.unmapped` |

v1 recorded neither the submitting client nor the grant. Where the HCP Provider cannot establish them, it records `submittedByClient` and `authorizedUnder` as the import that carried the entry ([5.4.1](#541-export)), and `recordedByProvider` and `recordedAt` as itself and the time of conversion.

## 4.4 Declaration Types

`assertion.declarationType` records what kind of party asserted the content of an entry; `record.provenance.assertedBy.id` records which one ([3.5](#35-provenance-layers)). It is never omitted and never null.

| Value | Meaning |
|---------------------|------------------------------------------------------------------|
| `person-declared` | The Context Subject stated it |
| `model-inferred` | A model derived it from the Context Subject's activity, without the Context Subject having stated it |
| `issuer-attested` | A party other than the Context Subject and other than an inferring model asserted it — a credential issuer, an institutional integration, or an assessing platform |

- `assertion.confidence` is required and non-null only for `model-inferred` entries. For `issuer-attested` entries the assurance is the proof of a credential that is the entry's content ([14](#14-vc-evidence-profile)), or otherwise the recorded provenance, not a confidence estimate.
- Where `assertion.declarationType` is `model-inferred`, the model is identified as set out in 3.5. A confidence value is not interpretable without knowing what produced it, and a Context Subject deciding whether to accept a quarantined inference ([4.7.3](#473-resolution)) is entitled to know what made it. A `derivedFrom` relationship ([4.2.3](#423-relationships)) can name the entries an inference was drawn from, and `assertion.basis` what else it was drawn from, the task and the setting ([4.2.5](#425-basis)).
- Confidence is its asserter's own estimate. Values from different asserters are not comparable: `high` from one model and `high` from another say nothing about each other. An HCP Provider MUST NOT use confidence values from different asserters as an input to relevance ordering ([7.3](#73-relevance-ordering)) or to standing ([4.7.1](#471-standing)).
- `issuer-attested` is the expected value for an entry whose content is a credential, but it is not restricted to them. An entry captured from an institutional integration without a credential is `issuer-attested` even though nothing signs it; in that case `record.provenance.source` and `record.provenance.assertedBy` are the only evidence of the assertion, and implementations SHOULD NOT treat it as carrying the assurance a validated credential would.
- A declaration type supplied by a caller does not by itself establish that the Context Subject made the assertion ([3.7](#37-statements-attributed-to-the-context-subject)). Confirmation is recorded separately from declaration type ([3.8](#38-confirmation)): a Context Subject can confirm an `issuer-attested` entry is about them without having asserted its content.

**Conflicts involving issuer-attested entries.** An `issuer-attested` entry is never quarantined ([4.7](#47-conflicts)). Against an unconfirmed `model-inferred` entry it stands, and the inference is quarantined: an institution's record outranks a model's guess. Against the Context Subject's own declaration it is a real and consequential case — a measured result against what someone says about themselves — and which should prevail is not obvious. It depends on the domain, on what the claim is being used for, and on how much the Context Subject contests it. Neither entry is quarantined, and the conflict is never settled by the provider: it is surfaced to the Context Subject, who may withdraw their own entry or take the matter up with the issuer ([4.7](#47-conflicts)). A personal correction therefore never silently rewrites an attestation, and an attestation never silently overrides the person.

## 4.5 Category Vocabulary

Categories are the primary unit of access control. Every HCP entry belongs to one or more categories, listed in `classification.categories`. Grants are scoped to categories ([6](#6-authorization)). A grant reaches an entry when it covers any one of the entry's categories, so a second category widens which clients may receive the entry. For that reason:

- An HCP Client MAY assign on create only categories its grant authorizes it to write ([5.2.3](#523-create)). It MUST NOT add a category to an existing entry.
- Adding or removing a category on an existing entry is a governance operation of the Authorizing Principal ([4.2.1](#421-mutability), [5.4](#54-governance-operations)).
- Where a standing rule denies a Client Operator any of an entry's categories, the entry MUST NOT be disclosed to that operator's clients, whichever category a request names ([6.3](#63-standing-rules)).
- An entry's default sensitivity is the highest default sensitivity among its categories ([7.6](#76-use-until)).
- A disclosure lists only those of the entry's categories that the requesting grant covers ([7.4](#74-disclosures-to-context-clients)).

An entry is in each of its categories. A requirement that applies to entries in a category applies to every entry that lists it, whatever its other categories ([16](#16-health-and-education-context-profiles)).

The following categories are registered, as version 1 of the category registry ([A.1](#a1-registries)). The registry is versioned separately from this specification, and an implementation declares the registry version it uses in its discovery document as `category_registry` ([19](#19-discovery-document)). This vocabulary is provisional; it is drawn from the use cases and domains represented at the Global Memory Workshop and has not yet been pressure-tested across sectors. Cross-sector SME engagement is the intended mechanism for expanding and validating it ([P1](path-to-v2-final.md#p1-roadmap)).

Implementers may define custom categories. A custom category MUST be an absolute URI under a domain its definer controls, so that two definers cannot collide. Custom categories are not portable across HCP implementations without bilateral agreement.

An HCP Provider MUST reject with invalid request ([5.5](#55-errors)) a write any of whose `classification.categories` is neither a registered category it holds nor a custom category it supports. It declares both in `supported_categories` ([19](#19-discovery-document)), describing each one: its name, a description, its default sensitivity, and the registry it comes from, or its definer for a custom category. A client choosing categories, and an Authorization Service showing a grant request, can then show what each category means. The Authorization Service MUST describe each requested category to the Authorizing Principal as the HCP Provider describes it, not as the client does ([6.1.6](#616-authorization-is-distinct-from-authentication)).

A custom category MUST declare a default sensitivity of Medium or High. Low is reserved for registered categories, whose sensitivity the registry sets.

`classification.categories` determines which grants reach an entry ([4.2.1](#421-mutability)); a custom category's description and sensitivity are declared by each provider that supports it, so two implementations agree on what access it implies only where they declare it alike.

| Category Slug | Description | Default Sensitivity |
|------------------------------|----------------------------------------------------------|-------------------|
| `general_preferences` | Communication style, formatting, language preferences | Low |
| `goals_and_constraints` | Long-term goals, time constraints, stated priorities | Low |
| `health_context` | Medical conditions, accessibility needs, medications | High |
| `education_learner_profile` | Mastery state, learning preferences, pacing | Medium |
| `work_context` | Role, tools, professional preferences | Medium |
| `purchase_history_preferences` | Shopping preferences, brand affinities | Low |
| `values_and_ethics` | Stated ethical commitments, content boundaries | Medium |
| `location_context` | Geographic preferences and constraints | Medium |
| `coordination_context` | Scheduling rules, availability, relationship constraints | Medium |

Sensitivity levels inform default sharing behavior but do not override the grants the Authorizing Principal has made.

## 4.6 Content Received Before a Grant

Content destined for an HCP instance that arrives before a grant authorizing its handling exists MUST NOT produce an entry, an audit event on the Context Subject's log, or any state visible to a Context Client. It is not yet part of the Context Subject's context. How such content is held, if at all, is outside this specification; the health guide describes one safe pattern ([G3](guides.md#g3-health-guide)).

## 4.7 Conflicts

Core defines what happens when two entries conflict. Two entries conflict when a `contradicts` relationship links them ([4.2.3](#423-relationships)), whether an HCP Client, a Management Client, or the HCP Provider asserted it. How a provider finds conflicts itself is defined by the Memory Manager Profile ([15](#15-memory-manager-profile)). An HCP Provider that accepts `model-inferred` entries MUST conform to the Memory Manager Profile.

What a conflict changes depends on the declaration types of the two entries:

| Entries in conflict | Consequence |
|----------------------------------------|------------------------------------------------------------------|
| `person-declared` and `model-inferred` | 4.7.2 |
| `issuer-attested` and `model-inferred` | 4.7.2, with the `issuer-attested` entry treated as authoritative |
| Two `model-inferred` entries, same asserter | Where neither is authoritative, the entry recorded earlier is set to `deprecated`: the asserter has corrected itself. Otherwise 4.7.2 |
| Two `model-inferred` entries, different asserters | 4.7.2 |
| Any other pair: `person-declared` and `issuer-attested`, two `person-declared`, two `issuer-attested` | No status changes. The conflict is surfaced to the Context Subject ([4.7.2](#472-consequences)) |

"Same asserter" means the same `record.provenance.assertedBy.id` on the current versions. The HCP Provider MUST NOT set `record.status` to `conflicted` on an `issuer-attested` entry ([4.4](#44-declaration-types)), and MUST NOT compare confidence values across asserters to decide a conflict ([4.4](#44-declaration-types)).

Whatever the pair, the HCP Provider appends `conflict.detected` and surfaces the conflict ([4.7.2](#472-consequences)). A conflict that changed no status stays recorded while the `contradicts` relationship stands, and is resolved, with a `conflict.resolved` event whose transition is `ended`, when either entry is withdrawn, rejected, or revised so that the conflict no longer holds, or when the Context Subject keeps both ([4.7.3](#473-resolution)). Where an asserter's later inference deprecates its earlier one, the provider appends `conflict.detected` and then `conflict.resolved` with the transition `asserter-superseded`.

A provider never resolves a conflict on the Context Subject's behalf, except where an asserter corrects itself. It may propose a resolution ([4.7.4](#474-proposals)).

### 4.7.1 Standing

Which entry prevails in a conflict is decided by standing, not by declaration type alone. An entry is authoritative if it is a `person-declared` entry recorded as `authenticated` or `cryptographically-verified`, or if the most recent confirmation record on its current version is `confirmed` ([3.8](#38-confirmation)).

### 4.7.2 Consequences

However a conflict is asserted, the following are required without variation:

- Where one entry is authoritative and the other is not, the HCP Provider MUST set the entry that is not authoritative to `conflicted`, and the authoritative entry MUST remain active.
- Where neither entry is authoritative — for instance, an `unverified` `person-declared` entry and a `model-inferred` entry — the HCP Provider MUST set both to `conflicted`, so that the Context Subject resolves the conflict ([3.7](#37-statements-attributed-to-the-context-subject)).
- The HCP Provider MUST NOT set an authoritative entry to `conflicted`.
- Where both entries are authoritative, no status changes. Conflicts between two of the Context Subject's own statements, confirmed or declared, are surfaced to them, never settled ([4.7](#47-conflicts)).
- The HCP Provider MUST append a `conflict.detected` event to the audit log, identifying both entries. This holds for every pair in 4.7, including those whose status does not change.
- A conflicted entry MUST NOT be returned to a Context Client in response to a query or a single-entry request. It remains visible to the Context Subject.
- The HCP Provider MUST surface the conflict to the Context Subject through the audit log, and MAY additionally surface it by notification.

### 4.7.3 Resolution

Resolution is an act of the Context Subject, performed through a Management Client. Automated resolution is not defined ([P1](path-to-v2-final.md#p1-roadmap)); a provider or client may propose one ([4.7.4](#474-proposals)).

Before the Context Subject resolves a conflict, the Management Client SHOULD show them, for each entry, its basis ([4.2.5](#425-basis)), declaration type ([4.4](#44-declaration-types)), standing ([4.7.1](#471-standing)), and permitted purposes ([4.2.6](#426-permitted-purposes)), and any proposal with its rationale ([4.7.4](#474-proposals)). These are what a person needs to judge an inference, and what a proposal is required to say it weighed.

The acts are:

- **Rejecting an entry.** A rejection of the conflicted entry ([5.4](#54-governance-operations)). The provider appends a `rejected` confirmation record and sets the entry's `record.status` to `deleted`. Where the other entry is `conflicted` and has no other unresolved conflict, the provider MUST return it to `active`. It appends no confirmation record to it, because the person rejected one entry rather than accepting the other. An authoritative entry is unaffected.
- **Accepting an entry.** A confirmation of the conflicted entry ([5.4](#54-governance-operations)). The provider appends a `confirmed` confirmation record and sets its `record.status` to `active`. Where another entry in the conflict was authoritative, the provider MUST set that entry's `record.status` to `deprecated`, unless it is `issuer-attested`: an attestation is never deprecated by the person's acceptance of another entry, and both stay active, with the conflict surfaced as one that changed no status ([4.4](#44-declaration-types), [4.7](#47-conflicts)). The entry's `declarationType` and `assertedBy` are unchanged ([3.8](#38-confirmation)). The prior state remains available through version history.
- **Superseding both.** A revision of the entry the Context Subject wants to keep. The HCP Provider MUST re-evaluate the conflict against the revised entry ([4.2.3](#423-relationships)); where the revision no longer conflicts, any entry quarantined by it MUST return to `active`.
- **Keeping both.** Where the conflict changed no status ([4.7](#47-conflicts)), the Context Subject may close it and keep both entries as they are. The provider records the transition `dismissed` and keeps the `contradicts` relationship as history. The conflict is not surfaced again unless either entry is revised, when it is evaluated anew ([15.3](#153-re-evaluation)).

The HCP Provider MUST append a `conflict.resolved` event on any of these transitions.

Where an authoritative entry is deleted while a conflict is outstanding, the conflicted entry MUST remain conflicted. It does not become authoritative by the removal of what it contradicted.

### 4.7.4 Proposals

A proposal says how its author would resolve a conflict, and why. It is carried on the `contradicts` relationship ([4.2.3](#423-relationships)):

**Template: a proposal, on the relationship that records a conflict**

    "proposal": {
      "act": "reject | accept | supersede",
      "entry": "{entry-id}",
      "rationale": "{why, in words the Context Subject can read}",
      "weighed": ["basis | declarationType | standing | permittedPurposes | recency | confidence"],
      "proposedBy": { "role": "{role}", "id": "{identifier}" },
      "proposedAt": "{date-time}"
    }

| Member | Rule |
|--------------|------------------------------------------------------------------|
| `act`, `entry` | One of the acts in 4.7.3, and the entry it applies to: reject it, accept it, or supersede it by a revision the Context Subject makes |
| `rationale` | Why, in natural language |
| `weighed` | What the proposal considered. The set is open; the values above are defined. `confidence` may be weighed only between entries of the same asserter ([4.4](#44-declaration-types)). |
| `proposedBy`, `proposedAt` | Set by the HCP Provider, never taken from a request |

- The HCP Provider, under the Memory Manager Profile ([15](#15-memory-manager-profile)), MAY propose a resolution of a conflict it detected. An HCP Client MAY propose a resolution of a conflict it asserts, with the create or revise that asserts it ([5.2.3](#523-create), [5.2.4](#524-revise)). A relationship carries at most one proposal; a later one replaces it.
- A proposal changes no status. The HCP Provider MUST NOT apply it. It MUST append a `conflict.proposed` event ([8.1](#81-required-log-events)) and surface the proposal with the conflict ([4.7.2](#472-consequences)).
- The Context Subject accepts a proposal by performing the act it names, through a Management Client ([4.7.3](#473-resolution)). The act is theirs, and its `conflict.resolved` event records that it followed a proposal. A proposal the Context Subject declines is removed, and the conflict stays open.

A proposal is never disclosed to a Context Client ([7.4](#74-disclosures-to-context-clients)).

## 4.8 Encrypted Storage

An HCP Provider declares how it stores entry content, as `storage_encryption` in its discovery document ([19](#19-discovery-document)):

- `server`: the provider can read entry content. Every requirement applies as written.
- `e2e`: the provider stores entry content encrypted under keys it does not hold. The steps that need to read content are performed within the Context Subject's trust domain, as set out below.

**The trust domain.** The Context Subject's trust domain is the set of components that act only for the Context Subject and hold the keys to their content: their own device, a wallet, or an agent they run. The Provider Operator, and every component it operates, is outside it.

**What is encrypted.** Under `e2e`, `content`, `evidence`, `assertion.basis`, and `classification.dimension` are encrypted. The rest of `classification` and `assertion`, and `record`, are not, because they are what the provider enforces: the category bound, standing rules, directives, the status lifecycle, and the audit log. An operator under `e2e` can therefore still see which categories an entry is in, when entries are written and revised, and who wrote them. A Management Client SHOULD tell the Context Subject so.

**Steps performed within the trust domain.** Under `e2e`, a component within the Context Subject's trust domain performs these steps. The HCP Provider conforms to them where its behavior across a binding conforms (Part I).

| Step | Requirement |
|--------------------------------------------|----------------------------------|
| Decrypting entries, and building disclosures from them | 7.4 |
| Relevance ordering, and the quantity bound applied to it | 7.2, 7.3 |
| Narrowing by anything other than categories or entry identifiers | 6.1.5.1, Rule 4 |
| Conflict detection | 15 |
| Checks on content at write: its profile's shape, a credential's validation and status, and the asserter taken from a credential's issuer | 5.2.3, 14.6, 14.7 |

- The HCP Provider MUST NOT hold the keys, and a component it operates is never part of the trust domain.
- Keys MUST NOT be released to an HCP Client for a category or a grant. A Context Client receives only the entries disclosed to it, decrypted, exactly as under `server`; a client holding keys to a whole category would defeat the quantity bound ([7.2](#72-quantity-bound)).
- The trust-domain component reports to the HCP Provider which entries it disclosed, and the provider records them, so that the audit log is as complete as under `server` ([8.2](#82-log-entry-structure)). Where the component verifies a credential, the provider records the result with `verification.by` `trust-domain`, so that anyone relying on it can see who checked ([4.2.2](#422-evidence)). An entry whose content credential the component validated is still recorded as `cryptographically-verified`, because its proof was verified ([14.6](#146-ingest)).
- Where a request needs the trust-domain component and it cannot be reached, the request MUST fail with subject unavailable ([5.5](#55-errors)). It MUST NOT be answered with ciphertext, with fewer checks, or with entries chosen without the relevance ordering.

G1.4 describes what this means for a deployment.
# 5. Operations and Errors

## 5.1 Operations

HCP supports five operations on entries for HCP Clients acting under a grant, and a set of governance operations for the Authorizing Principal. Any conformant system — an AI assistant, a healthcare portal, an education platform — interacts with an HCP instance through exactly these operations, and only under the access the Authorizing Principal has explicitly granted.

| Operation | Plane ([1.6](#16-context-plane-and-governance-plane)) | In plain language | Section |
|--------------------------|------------|-----------------------------------------------------------------|---------|
| Query | Context | Retrieve entries relevant to a query. Only entries in authorized categories are returned, filtered to the minimum necessary for the stated purpose. | 5.2.1 |
| Get entry | Context | Retrieve one named entry, for a stated purpose. | 5.2.2 |
| Create | Context | Create a new entry. Its provenance is recorded automatically ([3.5](#35-provenance-layers)). | 5.2.3 |
| Revise | Context | Create a new version of an entry. The prior version is never deleted; it is versioned. | 5.2.4 |
| Withdraw | Context | Mark an entry as deleted (soft delete). | 5.2.5 |
| Read own grant | Context | An HCP Client reads the grant under which it acts. | 5.2.6 |
| Relinquish own grant | Context | An HCP Client gives up the grant under which it acts. | 5.2.7 |
| Report onward sharing | Context | An HCP Client tells the HCP Provider what it shared with another organization, where the person allowed it. | 5.2.8 |
| Governance operations | Governance | List and revoke grants, read the audit log and the disclosure summary, export and import, hard delete, confirm or reject an entry, change an entry's categories, restrict its purposes, set and remove standing rules and directives. | 5.4 |

Core defines one request and one result for each operation below. A binding MAY expose a subset of an operation's fields; it MUST NOT give any field a different meaning ([1.5](#15-bindings-and-transports)).

No operations on stored entries other than the context operations are available to a Context Client. Context Client access is always query-scoped and minimized; bulk retrieval of a Context Subject's entries by a Context Client is not supported. The Context Subject's own export of their data ([5.4](#54-governance-operations)) is a governance operation and is not restricted by this section.

## 5.2 Context Operations

### 5.2.1 Query

| Request field | Required | Description |
|------------------|-------------|------------------------------------------------------------------|
| `query` | Yes | Natural language query describing the context or task |
| `categories` | No | Categories to query. An entry matches where any of its categories is among them. Omitted means every category the grant can read for the purpose named. |
| `purpose` | Yes | A purpose code: one the grant approved for the categories queried ([6.1.5.2](#6152-purposes)) |
| `purposeDescription` | No | Plain language statement of the task. Recorded in the audit log. |
| `maxEntries` | No | Maximum entries to return. Default 5; subject to the ceiling in 7.2. |

| Result field | Description |
|----------------------|------------------------------------------------------------------|
| `entries` | The entries returned, in relevance order ([7.3](#73-relevance-ordering)): disclosures where the requester is a Context Client ([7.4](#74-disclosures-to-context-clients)) |
| `retrievalId` | `urn:uuid:` identifier of this retrieval, recorded in the audit event |
| `minimization` | The minimization report ([7.5](#75-reporting)) |
| `categoriesSearched` | The categories searched: those named in the request, or, where it named none, every category the grant can read for the purpose named |
| `directives` | The directives that apply, where the requester is a Context Client ([6.4](#64-directives)) |
| `timestamp` | Date-time of the response |

A query naming any category outside the grant's scopes, or a purpose the grant did not approve for those categories, MUST fail with not authorized ([5.5](#55-errors)). Query results are not paginated ([7.2](#72-quantity-bound)). Both bindings return `categoriesSearched`.

### 5.2.2 Get Entry

Retrieves a single entry. A Context Client names it by the `ref` it was disclosed with ([7.4](#74-disclosures-to-context-clients)); a Management Client by its `id`.

| Request field | Required | Description |
|------------------|-------------|------------------------------------------------------------------|
| `ref` or `entryId` | Yes, one of them | The entry's `ref` (a Context Client) or its `id` (a Management Client) |
| `purpose` | Yes | A purpose code: one the grant approved for a category of the entry ([6.1.5.2](#6152-purposes)) |
| `purposeDescription` | No | Plain language statement of the task. Recorded in the audit log. |
| `version` | No | Integer. Returns the specified version rather than the current one. |

| Result field | Description |
|----------------------|------------------------------------------------------------------|
| `entry` | The entry: a disclosure where the requester is a Context Client ([7.4](#74-disclosures-to-context-clients)) |
| `retrievalId` | `urn:uuid:` identifier of this retrieval |
| `minimization` | The minimization report ([7.5](#75-reporting)) |
| `directives` | The directives that apply, where the requester is a Context Client ([6.4](#64-directives)) |
| `timestamp` | Date-time of the response |

Requirements:

- At least one of the entry's categories MUST be within the caller's authorized scopes with `purpose` among those the grant approved for it ([6.1.5.2](#6152-purposes)). The entry is subject to the bounds in 7.1: no standing rule may deny the caller's Client Operator any of its categories ([6.3](#63-standing-rules)), and its permitted purposes, where present, MUST include `purpose` ([4.2.6](#426-permitted-purposes)).
- The HCP Provider MUST append a `context.read` event identical in structure to the event appended for a query, including the stated purpose.
- A Context Client receives a disclosure ([7.4](#74-disclosures-to-context-clients)), with its use-until time ([7.6](#76-use-until)), as for a query.
- Entry-selection minimization under 7 is inapplicable by construction, since the caller has named a single entry. Conformance testing MUST NOT treat the absence of entry-selection filtering on this operation as non-conformance.
- A Context Client can name only entries disclosed to it under the same grant, since it knows no other `ref`.
- A request for an entry that does not exist, that is outside the caller's authorized scopes, whose `ref` belongs to another grant, or that is not `active` ([4.2.4](#424-status)), MUST fail with not authorized ([5.5](#55-errors)), so that entry existence is not disclosed to unauthorized callers.

The entry is returned inside a result rather than bare, so that the minimization report required by 7.5 has somewhere to sit.

### 5.2.3 Create

| Request field | Required | Description |
|------------------------------|-------------|------------------------------------------------------------------|
| `schema` | Yes | The entry structure version ([4.2](#42-entry)) |
| `subject.id` | Yes | The Context Subject ([4.2](#42-entry)) |
| `content` | Yes | The content, in the shape its profile defines ([11](#11-general-context-profile), [14](#14-vc-evidence-profile)) |
| `evidence` | No | Evidence items ([4.2.2](#422-evidence)) |
| `classification.categories` | Yes | One or more category slugs or custom category URIs, each one the grant authorizes the caller to write ([4.5](#45-category-vocabulary)) |
| `assertion.basis` | No | What the assertion was drawn from ([4.2.5](#425-basis)) |
| `assertion.permittedPurposes` | No | Purpose codes the entry may be used for ([4.2.6](#426-permitted-purposes)) |
| `assertion.declarationType` | Yes | `person-declared`, `model-inferred`, or `issuer-attested` ([4.4](#44-declaration-types)) |
| `classification.dimension` | No | Dimension within the entry's categories ([4.2](#42-entry)) |
| `assertion.confidence` | Conditional | Required and non-null when `declarationType` is `model-inferred`; null or omitted otherwise |
| `assertion.validUntil` | No | When the content stops holding ([4.2](#42-entry)) |
| `record.provenance.assertedBy.id` | Conditional | The Context Asserter. Required unless `declarationType` is `person-declared`, in which case the provider records the Context Subject, or the entry's content is a credential, in which case the provider takes it from the credential's issuer ([14.6](#146-ingest)). |
| `record.provenance.assertedAt` | No | When the assertion was made. Omitted means the provider records `recordedAt`. |
| `record.provenance.source` | Yes | Origin of the entry |
| `record.relationships` | No | Relationships to assert, each a `type` and a `target`: the target's `ref` for a Context Client, its `id` for a Management Client ([4.2.3](#423-relationships)). A `contradicts` relationship MAY carry a `proposal` ([4.7.4](#474-proposals)), naming its entry the same way. |

The HCP Provider assigns everything else:

| Field | Assigned by |
|-------------------------------------------|---------------------------------------------------------|
| `id` | HCP Provider |
| `record.status` | HCP Provider |
| `record.version` | HCP Provider |
| `record.provenance.assertedBy.assurance`, `submittedByClient`, `authorizedUnder`, `recordedByProvider`, `recordedAt`, `confirmations` | HCP Provider ([3.5](#35-provenance-layers)) |
| `record.relationships[].assertedBy`, `recordedAt` | HCP Provider ([4.2.3](#423-relationships)) |

Requirements:

- A write that omits or nulls `confidence` while declaring `model-inferred` MUST be rejected with invalid request ([5.5](#55-errors)). A write that supplies a non-null `confidence` while declaring anything other than `model-inferred` MUST be rejected the same way.
- A write naming a `schema` the HCP Provider does not accept, or any category it does not hold, MUST be rejected with invalid request ([4.2](#42-entry), [4.5](#45-category-vocabulary)). A write naming a category the caller's grant does not authorize it to write MUST fail with not authorized ([5.5](#55-errors)).
- An `issuer-attested` write is accepted only from an HCP Client authenticated as the issuer, or authorized by it; any other is rejected with not authorized ([3.7](#37-statements-attributed-to-the-context-subject)). A write whose content is a credential is `issuer-attested`.
- Where the content is a credential, the client supplies it whole, including its proof, in an evidence item, and the HCP Provider MUST NOT modify it ([4.2.2](#422-evidence)).
- Under end-to-end encrypted storage, the checks on content are made within the Context Subject's trust domain ([4.8](#48-encrypted-storage)).

Result: the created entry with provider-assigned fields populated, as a disclosure carrying its new `ref` where the requester is a Context Client ([7.4](#74-disclosures-to-context-clients)).

### 5.2.4 Revise

| Request field | Required | Description |
|--------------------------|-------------|------------------------------------------------------------------|
| `ref` or `entryId` | Yes, one of them | The entry to revise, named as for get entry ([5.2.2](#522-get-entry)) |
| `expectedVersion` | Yes | The `record.version` of the current version, which this revision replaces |
| `content` | Yes | The revised content, whole. Where the content is a credential, the new credential, whole, in `evidence`. |
| `evidence` | No | The revision's evidence items, whole ([4.2.2](#422-evidence)). Omitted means none. |
| `reason` | Yes | Reason for the revision. Recorded in the audit log. |
| `assertion.declarationType` | No | The declaration type of the revised assertion. Omitted means unchanged. |
| `assertion.confidence`, `assertion.validUntil`, `assertion.basis`, `assertion.permittedPurposes` | Conditional | As for create |
| `record.provenance.assertedBy.id`, `assertedAt`, `source` | Conditional | As for create, for the revised assertion |
| `record.relationships` | No | As for create ([4.2.3](#423-relationships)) |

A revision creates a new version. It replaces `content`, `assertion`, and `evidence` whole; `subject` and `classification` are not changed by a revision ([4.2.1](#421-mutability)). Its provenance belongs to the new version and is recorded as for create ([3.5](#35-provenance-layers)): the revised assertion is attributed to its own Context Asserter, and the new version starts with no confirmations ([3.8](#38-confirmation)).

Where `expectedVersion` is not the entry's current `record.version`, the revision MUST fail with version conflict ([5.5](#55-errors)) and change nothing. Revisions are therefore never lost to a concurrent one: a client that read version 4 cannot overwrite a version 5 it has not seen.

Result: the revised entry, with `record.version` incremented by 1, as a disclosure where the requester is a Context Client ([7.4](#74-disclosures-to-context-clients)). The entry's `id`, and its `ref` under the grant, are unchanged by a revision.

A Context Client MUST NOT revise an entry whose current version the Context Subject has rejected ([3.8](#38-confirmation)).

### 5.2.5 Withdraw

| Request field | Required | Description |
|------------------|-------------|------------------------------------------------------------------|
| `ref` or `entryId` | Yes, one of them | The entry to withdraw, named as for get entry ([5.2.2](#522-get-entry)) |
| `reason` | Yes | Reason for withdrawal. Recorded in the audit log. |

Withdraw sets the entry's `record.status` to `deleted`. A deleted entry is hidden from Context Clients immediately. It remains held, and remains visible to the Context Subject, until hard-deleted ([5.4](#54-governance-operations)).

Result: the `ref` or `entryId` named, `status` (`deleted`), and `timestamp`.

### 5.2.6 Read Own Grant

An HCP Client MAY read the grant under which it acts ([6.1.5](#615-grant-representation)). It receives that grant only, with the directives that apply to it ([6.4](#64-directives)). Where the grant is narrowed to particular entries ([6.1.5.1](#6151-narrowed-grants)), a Context Client receives their `ref`s, never their `id`s. Reading it discloses nothing the client was not already told at authorization time, and no audit event is required.

### 5.2.7 Relinquish Own Grant

An HCP Client MAY relinquish the grant under which it acts. Relinquishing is a revocation of that grant: it takes effect as 6.2.2 requires and is recorded as a `grant.revoked` event naming the client as initiator ([3.9](#39-audit-participants)). No revocation notification is sent to the client that relinquished the grant.

A client can relinquish only the grant it presents. A request naming any other grant MUST fail with not authorized ([5.5](#55-errors)). Revoking any other grant remains a governance operation ([5.4](#54-governance-operations), [6.2.1](#621-revocation-by-the-authorizing-principal)).

Result: none. The HTTP Binding carries this operation and responds 204, with no body ([9.4.6](#946-grants)). The MCP Binding does not carry it in this draft.

### 5.2.8 Report Onward Sharing

An HCP Client that shares context with another organization under 3.12 MUST report each share to the HCP Provider, when it next reaches the provider.

| Field | Required | Description |
|---------------|----------|------------------------------------------------------------------|
| `recipient` | Yes | The organization told: its DNS `domain`, and a `name` the person can recognize |
| `refs` | Yes | The `ref` of each entry the client drew on ([7.4](#74-disclosures-to-context-clients)) |
| `purpose` | Yes | The purpose code, one of the detail's purposes ([6.1.5.2](#6152-purposes)) |
| `sharedAt` | Yes | When the client shared |

The HCP Provider appends a `context.shared` event for every report ([8.1](#81-required-log-events)), naming the entries by their `id`. Where the share was not one the grant allowed — the detail carries no `onwardSharing`, an entry was not eligible ([7.4](#74-disclosures-to-context-clients)), or the recipient is outside `domains` or in `notTo` — the event records `permitted: false`, and the operation fails with not authorized ([5.5](#55-errors)). The event is recorded either way, because the share has already happened and the Context Subject is entitled to see it.

Result: none. The HTTP Binding responds 204, with no body ([9.4.16](#9416-onward-sharing)). The MCP Binding carries it as `hcp_reportSharing` ([10.3.6](#1036-hcp_reportsharing)).

## 5.3 Minimal Response Mode (Removed)

Draft 1 let a query ask for a `minimal` response, which reduced each General Context entry to its identifier, category, dimension, and value. A Context Client now always receives disclosures ([7.4](#74-disclosures-to-context-clients)), which carry no provenance or lifecycle fields beyond what judging standing requires. The section number is kept so that citations of it resolve.

## 5.4 Governance Operations

Governance operations are performed only by a Management Client acting for the Authorizing Principal ([6.1.9](#619-governance-operations)), and are carried only by the HTTP Binding ([1.6](#16-context-plane-and-governance-plane), [9](#9-http-binding)). The audit events they produce are listed in 8.1.

| Operation | Effect | Section |
|-------------------------|------------------------------------------------------------------|---------|
| List grants | Enumerates all grants for the instance, filtered by status if asked | 6.1.5 |
| Revoke grant | Revokes a grant | 6.2 |
| Read audit log | Returns the audit log, filtered as asked | 8.3 |
| Export | Returns the Context Subject's entries | 5.4.1 |
| Import | Loads entries from an export, at the Context Subject's direction | 5.4.3 |
| Disclosure summary | Summarizes what each client has received | 8.6 |
| Hard delete | Permanently removes an entry | 5.4.2 |
| Confirm or reject | Appends a confirmation record to an entry's current version | 3.8, 4.7.3 |
| Change categories | Sets an entry's categories | 4.2.1, 4.5 |
| Restrict purposes | Sets `classification.permittedPurposes` on an entry | 4.2.6 |
| Set or remove a standing rule | Denies context to named Client Operators, or to clients without a claim, across all categories or within some | 6.3 |
| Set or remove a directive | States what clients may do with context they receive, or on the person's behalf | 6.4 |

Confirm or reject, change categories, and restrict purposes MUST carry `expectedVersion`, the `record.version` the Management Client showed the Context Subject. Where it is not the entry's current version, the operation MUST fail with version conflict ([5.5](#55-errors)) and change nothing, so that a person never confirms, rejects, or recategorizes a version they have not seen.

### 5.4.1 Export

**Document.** An export is a JSON-LD document:

**Response body: HCP Provider → Management Client (export, HTTP)**

    {
      "@context": ["https://hcp.example/contexts/v2"],
      "type": "ContextExport",
      "schema": "https://hcp.example/spec/export/2.0",
      "subject": { "id": "{subject identifier}" },
      "exportedBy": "{provider-identifier}",
      "exportedAt": "{date-time}",
      "options": { "excludeDeleted": false, "includeVersions": false, "includeAudit": false },
      "entries": [ ],
      "versions": [ ],
      "rules": [ ],
      "directives": [ ],
      "delegations": [ ],
      "audit": [ ]
    }

| Member | Rule |
|--------------|------------------------------------------------------------------|
| `schema` | The export structure version, compared as an exact string ([1.7](#17-conformance-identifiers)) |
| `subject`, `exportedBy`, `exportedAt` | The Context Subject, the exporting HCP Provider, and when the export was made |
| `options` | The options requested, below |
| `entries` | The current version of each entry exported, in the form of 4.2 |
| `versions` | Superseded versions, each in the form of 4.2. Present only where requested. |
| `rules` | The Context Subject's standing rules ([6.3](#63-standing-rules)) |
| `directives` | The Context Subject's directives ([6.4](#64-directives)) |
| `delegations` | The delegations made for the Context Subject, ended ones included, as a record ([17.2](#172-delegations)). An import does not establish them: a delegation is established by an Authorization Service. |
| `audit` | The audit log, as events in the structure of 8.2. Present only where requested. |

**Default content.** The current version of every entry across all categories that has not been hard-deleted. This includes entries whose `record.status` is `active`, `deprecated`, `conflicted`, `expired`, `revoked`, `suspended`, or `deleted`. Every entry carries its status. The export also carries the Context Subject's standing rules ([6.3](#63-standing-rules)).

The default follows one principle: **the export contains anything whose existence the Context Subject could not otherwise infer from it.** A soft-deleted entry is still held and still processed, and a person reading a filtered export has no way to discover that it exists — they cannot ask for what they do not know is there. A superseded version, by contrast, is announced by the current entry's `record.version`, and the audit log is separately available ([8.3](#83-access-to-the-audit-log)). Both are therefore opt-in.

An export request MAY ask for:

- **Excluding deleted entries.** Omits entries whose `record.status` is `deleted`. Intended for a Context Subject preparing to move their context to another provider, where entries they have deleted should not travel with it.
- **Including versions.** Additionally returns superseded versions of each entry returned, rather than the current version alone.
- **Including the audit log.** Additionally returns the Context Subject's audit log in the structure specified in 8.2. This is equivalent to the export already required by 8.3 and is offered as a convenience, not as an additional capability.

Entries removed by hard deletion are by definition unrecoverable and MUST NOT be returned under any option.

The HCP Provider MUST append a `context.exported` event for every export, recording the options used in detail.

### 5.4.2 Hard Deletion

Implementations MUST support hard deletion at the Context Subject's request, to support applicable erasure and deletion obligations. Hard deletion is a governance operation: a Context Client cannot perform it, and an attempt by any caller other than a Management Client acting for the Authorizing Principal MUST fail with not authorized ([5.5](#55-errors)). A Context Client can only withdraw ([5.2.5](#525-withdraw)), which hides the entry from Context Clients immediately.

Hard deletion MAY be carried out by destroying every copy of the keys that decrypt the entry, in backups as well, provided the entry's unencrypted members are also removed. The outcome is the same: the entry is unrecoverable, and is never returned again ([5.4.1](#541-export)).

### 5.4.3 Import

Import loads the entries of an HCP export ([5.4.1](#541-export)) into the Context Subject's instance, at their direction, through a Management Client. It is not federation: one person moves their own context ([P1](path-to-v2-final.md#p1-roadmap)).

| Request field | Required | Description |
|------------------|-------------|------------------------------------------------------------------|
| `export` | Yes | An HCP export ([5.4.1](#541-export)), with entries in any schema the provider accepts ([4.3](#43-one-form-and-conversion-from-v1)) |
| `dryRun` | No | If true, report the outcome for each entry and change nothing |
| `categoryMap` | No | For categories the provider does not hold: the category each is to be replaced by |

Result: one outcome for each entry in the export: `imported`, `converted` (a v1 entry, converted under 4.3), `skipped` (a deleted entry the request chose not to carry, or an exact duplicate of one held), or `rejected`, with the reason.

Requirements:

- An implementation that imports v1 entries converts them as 4.3 requires.
- An entry whose `id` is already held, with different content, MUST be rejected. It is never overwritten.
- The HCP Provider MUST NOT reinstate as active any entry carrying `record.status: deleted`. It either preserves the status or omits the entry. The safeguard against deleted context resurfacing at another provider belongs on the reading side, not in what a person is permitted to see of their own data.
- The HCP Provider MUST preserve each entry's `assertion.declarationType` and `record.provenance`, including its confirmation records, as exported. Assurance values remain the exporting provider's record, which `recordedByProvider` shows. Nothing is upgraded ([3.11](#311-actor-invariants), invariant 15).
- An entry whose content is a credential is verified again under the VC Evidence Profile, with its status ([14.6](#146-ingest), [14.7](#147-credential-status)). One that fails is rejected as credential invalid ([5.5](#55-errors)). A supporting credential is verified again and its `verification` recorded anew ([14.8](#148-supporting-credentials)).
- The HCP Provider MUST NOT silently re-categorize an imported entry: because `classification.categories` governs which grants reach the entry ([4.2.1](#421-mutability)), assigning a different category on import changes what the Authorizing Principal's existing and future grants mean. An entry with a category the provider does not hold is rejected, unless `categoryMap` replaces each such category. Each replacement is recorded as a `context.recategorized` event naming the prior and new categories, exactly as for any other change of categories ([4.2.1](#421-mutability)).
- Standing rules in the export are applied as the Context Subject's own ([6.3](#63-standing-rules)). Delegations in the export are not established; the Management Client shows them to the Context Subject as a record ([17.2](#172-delegations)).
- The HCP Provider MUST append one `context.imported` event for each import other than a dry run, listing the entries and their outcomes ([8.1](#81-required-log-events)).

## 5.5 Errors

Core defines the following errors. Each has a code, which bindings carry: the HTTP Binding as a problem type ([9.7](#97-errors)), the MCP Binding in a tool execution error ([10.4](#104-errors)). The codes are v1's problem-type names, with `version-conflict` and `credential-invalid` added in Draft 2 and `subject-unavailable` in Draft 3. A Core error is an object with two members: `type`, its code, and `detail`, a human-readable explanation that discloses nothing the condition forbids. The MCP Binding carries the object itself ([10.4](#104-errors)); the HTTP Binding carries it as problem details, with `type` as a problem type ([9.7](#97-errors)).

| Error | Code | Condition |
|-----------------------|------------------------|------------------------------------------------------------------|
| invalid request | `malformed-request` | The request fails schema validation or a Core rule on its content |
| unauthenticated | `invalid-token` | Missing, malformed, or expired authorization evidence |
| not authorized | `scope-denied` | The request falls outside the caller's grant — its categories, actions, or purposes — or the entry does not exist. The response MUST NOT disclose which. |
| conflict | `idempotency-conflict` | A retried request does not match the original ([9.6](#96-idempotency)) |
| version conflict | `version-conflict` | The request names a version that is not the entry's current version ([5.2.4](#524-revise), [5.4](#54-governance-operations)) |
| credential invalid | `credential-invalid` | A credential that is an entry's content fails verification: its proof, its securing mechanism, its verification method, or its status ([14.6](#146-ingest)). The detail names which, and does not reveal status-list internals. |
| subject unavailable | `subject-unavailable` | Under end-to-end encrypted storage, the request needs the Context Subject's trust domain, which cannot be reached ([4.8](#48-encrypted-storage)). The HCP Client MAY retry later. |
| rate limited | `rate-limited` | The caller has exceeded a rate limit. Revocation is never rate limited ([6.2.1](#621-revocation-by-the-authorizing-principal)). |
| unsupported version | `unsupported-version` | The requested protocol version is not supported. The HCP Provider MUST NOT silently serve a different version. |
# 6. Authorization

## 6.1 Grant Model

HCP specifies authorization as category-scoped, revocable grants, represented per 6.1.5. Every HCP Client MUST hold such a grant before any operation on entries is permitted. This applies without distinction to HCP Clients operated by the Provider Operator and to HCP Clients operated by others.

How a grant is obtained is defined by the authorization profile an implementation claims: the OAuth Interop Profile ([13](#13-oauth-interop-profile)) or the First-Party Authorization Profile ([12](#12-first-party-authorization-profile)). The choice of profile does not relax any grant semantics specified in this section. Where grants are obtained through a channel other than OAuth 2.0, the requirements of 6.1.6 apply in full.

### 6.1.1 Scope Naming Convention

Scopes map directly to HCP categories and permitted actions, in the form `hcp:{category}:{action}`.

Examples:

- `hcp:health_context:read` — read-only access to health context entries
- `hcp:general_preferences:read hcp:general_preferences:write` — read and write access to general preferences
- `hcp:education_learner_profile:read` — read-only access to learner profile

Wildcards are not permitted. Each scope MUST be explicitly named.

Scope strings are a compact view of a grant's `access` ([6.1.5](#615-grant-representation)): each names a registered category and an action that a detail in `access` covers. A custom category ([4.5](#45-category-vocabulary)) is a URI, and its colons would make a scope string ambiguous, so custom categories appear only in `access`, never in a scope string.

### 6.1.2 How Grants Are Obtained

The grant types available, and the authorization requests that start them, are defined by the authorization profiles: OAuth grant types and their requests in the OAuth Interop Profile ([13](#13-oauth-interop-profile)); a non-OAuth authenticated channel, for first-party access only, in the First-Party Authorization Profile ([12](#12-first-party-authorization-profile)). Token lifetimes are defined by the OAuth Interop Profile ([13](#13-oauth-interop-profile)).

The term "session" is not used normatively in this specification. Temporary grants are bounded by an absolute expiry timestamp, not by an implementation-defined session lifetime.

### 6.1.3 Grant Duration

| Bound | Default | Maximum |
|------------------------------------|------------|------------|
| Temporary grant absolute expiry | 4 hours | 24 hours |

Persistent grants have no fixed expiry and remain active until revoked ([6.1.4](#614-grant-distinction-temporary-vs-persistent)).

### 6.1.4 Grant Distinction: Temporary vs. Persistent

Every grant is classified as either temporary or persistent. Temporary is the default. Persistent access requires explicit, affirmative action by the Authorizing Principal at authorization time.

**Temporary grants (default):**

- Carry an absolute expiry timestamp fixed at authorization time. The expiry MUST NOT exceed 24 hours from issuance.
- The expiry MUST be recorded in the `grant.issued` audit event, and MUST be presented to the Authorizing Principal at authorization time as a concrete time or duration.
- Refresh tokens MAY be issued within the grant's absolute expiry window. A refresh token MUST NOT be honored after the grant's absolute expiry, regardless of the refresh token's own stated lifetime.
- Expire automatically; no action by the Authorizing Principal is required to terminate. The HCP Provider MUST append a `grant.expired` event per 8.1. This does not require a background process running at the moment of expiry: per 8.1, the event may be appended on the first access presenting the expired grant, or within 24 hours of the expiry timestamp, whichever comes first. An implementation whose store is dormant between interactions may therefore write the event when it next handles a request, and is not required to run a scheduled sweep.

**Persistent grants:**

- Remain active across interactions until explicitly revoked by the Authorizing Principal
- Issue refresh tokens per the lifetimes in the OAuth Interop Profile ([13](#13-oauth-interop-profile))
- MUST require a distinct, affirmative action by the Authorizing Principal to elect, separate from the standard authorization confirmation

**Conformance requirement:**

Temporary access MUST be the default outcome of any authorization interaction. Electing persistent access MUST require a separate affirmative act by the Authorizing Principal, subject to the following:

- The act MUST be distinct from the act by which the Authorizing Principal confirms the grant itself. A single act MUST NOT both authorize access and elect persistence.
- Persistence MUST NOT be pre-selected by any means, including a pre-set control, a pre-filled value, or a default the person must act to decline.
- Before the act, the Authorizing Principal MUST be told what persistent access means: that it survives the current interaction and remains in effect until they revoke it.
- The elected grant type, and the modality through which it was elected, MUST be recorded in the `grant.issued` audit event.

**Onward sharing:**

Where a grant request asks for onward sharing ([3.12](#312-onward-disclosure), [6.1.5](#615-grant-representation)), the grant is issued without it unless the Authorizing Principal elects it:

- Electing it MUST be a separate affirmative act, after the grant is confirmed, and distinct from the act that elects persistence.
- It MUST NOT be pre-selected by any means.
- Before the act, the Authorizing Principal MUST be told which categories it covers, that the client may tell organizations it deals with for them what a task needs from that context, and that HCP cannot control what those organizations then do with it. They MAY limit it to named organizations (`domains`).
- The election is recorded in the `grant.issued` event, in `access`.

These requirements are stated in terms of what the Authorizing Principal does and what is recorded, not in terms of interface elements. They apply identically to graphical, voice, messaging, and LLM-mediated authorization. The authorization interaction patterns ([G4](guides.md#g4-authorization-interaction-patterns)) illustrate patterns that satisfy them in each modality and are non-normative.

### 6.1.5 Grant Representation

6.1.1 through 6.1.4 specify how authorization is bounded. This section specifies the record of an authorization: the artifact the Authorizing Principal inspects, and the object a conformance suite examines.

HCP defers to OAuth 2.0 for the authorization mechanism ([I9](introduction.md#i9-relationship-to-existing-standards), [13](#13-oauth-interop-profile)). OAuth does not define a person-facing enumeration of granted authorizations, so the requirement that the Authorizing Principal can view and revoke all active grants ([18](#18-conformance-claims-and-packages)) is not satisfied by that dependency. The representation below is the minimum sufficient to satisfy it. Where later OAuth grant-management work provides an equivalent representation, HCP is expected to map onto it rather than maintain a parallel model; field names here are chosen with that in mind.

**Grant object**

**Template: the grant, as the Authorization Service records it**

    {
      "grantId": "urn:uuid:{grant-uuid}",
      "subject": { "id": "{per-client pseudonym}" },
      "authorizingPrincipal": { "id": "{per-client pseudonym}", "delegation": "{delegation id | omitted}" },
      "client": {
        "id": "{client-identifier}",
        "name": "{name the person can recognize}",
        "operator": { "id": "{operator-identifier}", "name": "{organization name}" },
        "legalRetention": { "record": "{the record kept}", "obligation": "{the law or rule}", "period": "{how long}" },
        "claims": ["{client conformance identifier}"]
      },
      "requestingParty": { "type": "person | organization", "id": "{identifier}", "name": "{name}" },
      "access": [
        {
          "type": "https://hcp.example/spec/authorization/context-access",
          "actions": ["read | write | provenance"],
          "categories": ["{category}"],
          "purposes": [ { "code": "{purpose URI}", "description": "{shown to the person}" } ],
          "narrowedTo": { },
          "onwardSharing": { "domains": ["{DNS domain}"], "notTo": ["{DNS domain | operator identifier}"] }
        }
      ],
      "scopes": ["hcp:{category}:{action}"],
      "grantType": "temporary | persistent",
      "issuedAt": "{date-time}",
      "expiresAt": "{date-time | null}",
      "status": "active | revoked | expired"
    }

| Field | Notes |
|------------------------|------------------------------------------------------------------|
| `grantId` | Stable for the life of the grant. Matches the `grantId` recorded in audit events ([8.2](#82-log-entry-structure)). |
| `subject`, `authorizingPrincipal`, `client.operator`, `requestingParty` | The actors the grant binds. Their rules are in 3.4. |
| `client.name` | MUST be a name the person can recognize. A grant list presenting only opaque client identifiers does not satisfy 18. |
| `client.legalRetention` | Present only where the client declared at registration that the law requires it to keep what it receives in a record ([6.2.5](#625-copies-kept-under-a-legal-obligation)) |
| `client.claims` | The client conformance claims the client declared at registration ([18.1](#181-claims)). Absent where it declared none. |
| `access` | What the grant authorizes: one or more authorization details, each naming `actions`, `categories`, and the `purposes` the person approved for them ([6.1.5.2](#6152-purposes)), and optionally `narrowedTo` ([6.1.5.1](#6151-narrowed-grants)). `provenance` is an action only alongside `read`: it adds provenance to what the client reads ([7.4.1](#741-provenance-on-request)). The type identifies the HCP authorization detail; under the OAuth Interop Profile it is an RFC 9396 authorization detail ([13.3](#133-grant-request)). |
| `access[].onwardSharing` | Present only where the Authorizing Principal elected onward sharing for the detail ([6.1.4](#614-grant-distinction-temporary-vs-persistent)); it lets the client share under 3.12. A client asks for it by including the member in the detail it requests. It MAY be present only in a detail that includes `read` and all of whose categories have a default sensitivity of Low ([4.5](#45-category-vocabulary)); an Authorization Service MUST reject any other request for it with invalid request ([5.5](#55-errors)). `domains`, where present, limits it to organizations at those DNS domains, as the Authorizing Principal chose. `notTo` is set by the HCP Provider: each operator that a standing rule denies any of the detail's categories ([6.3](#63-standing-rules)), kept current as rules change. Any person-facing presentation of the grant ([18](#18-conformance-claims-and-packages)) MUST show it. |
| `scopes` | Derived from `access`, in the form specified in 6.1.1, for display and for clients that use scope strings. It MUST NOT grant anything `access` does not. |
| `grantType` | Per 6.1.4. |
| `expiresAt` | For temporary grants, the absolute expiry required by 6.1.4; MUST NOT be null. For persistent grants, null. |
| `status` | `expired` is set on lapse of `expiresAt`; `revoked` on revocation by the Authorizing Principal ([6.2.1](#621-revocation-by-the-authorizing-principal)). |

`authorizingPrincipal` replaces v1's `grantor`. In Core the Authorizing Principal is the Context Subject ([3.3](#33-co-location-and-delegation)). `delegation` is present only for a grant a delegate authorized under the Delegated Authorization Profile ([17.4](#174-scope-and-grants-under-a-delegation)).

**Grant access**

An HCP Provider MUST NOT disclose a grant issued to one HCP Client to any other HCP Client. This holds on every binding.

Grants are enumerated in two ways:

- **By a Management Client** acting for the Authorizing Principal, as a governance operation ([5.4](#54-governance-operations)): all grants for the instance, filtered by status where asked; the default is active.
- **By an HCP Client reading its own grant** ([5.2.6](#526-read-own-grant)): only the grant under which that client acts.

Where no binding the implementation exposes carries these operations, the HCP Provider MUST still maintain grant objects conforming to this section, and the Authorizing Principal MUST still be able to enumerate and revoke grants through a supported modality ([18](#18-conformance-claims-and-packages)). No audit event is required for reading a grant list: a person reading their own grant list is not an access to entry content, and a client reading its own grant discloses nothing it was not already told at authorization time.

**Fields deliberately excluded**

- *Last access time.* The audit log already answers when a client read what. Duplicating it into the grant object creates two records that can disagree.
- *Delegation chains.* Not permitted in this draft ([17.1](#171-scope), [P1.1](path-to-v2-final.md#p11-before-v2-is-final)).

### 6.1.5.1 Narrowed Grants

A detail in a grant's `access` MAY narrow its categories below category grain with the optional `narrowedTo` member.

**Template: a narrowed authorization detail**

    {
      "type": "https://hcp.example/spec/authorization/context-access",
      "actions": ["read"],
      "categories": ["health_context"],
      "purposes": [ { "code": "https://purposes.example/medication-reminders", "description": "Medication reminders" } ],
      "narrowedTo": { "entryIds": ["urn:uuid:...", "urn:uuid:..."] }
    }

The contents of `narrowedTo` are implementation-defined. This specification fixes what a restriction means and guarantees, not a closed vocabulary of narrowing keys: pilots will discover which dimensions matter (entry identifiers, document facets, and others), and a premature vocabulary would be wrong in the same way a premature dimension vocabulary would be ([4.2](#42-entry)). A common set is registry work ([P1](path-to-v2-final.md#p1-roadmap)). A custom narrowing key is a URI ([A.3](#a3-extension-points)). An implementation narrowing by facet might write `"narrowedTo": { "documentType": ["prescription"] }`; both forms are conformant and both are legible to the person as less than the whole category.

**Four rules govern the field. They are normative and independent of storage architecture.**

- **Rule 1 — restrictions only narrow.** A restriction MUST NOT grant access beyond the categories and actions of the detail that carries it. The effective authority of a detail is the intersection of its categories, actions, and `narrowedTo`, never the union. A `narrowedTo` naming an entry outside the detail's categories has no widening effect and MUST be ignored for authorization.
- **Rule 2 — unknown narrowing fails closed.** A narrowing key the Authorization Service does not support MUST be rejected at issuance with invalid request ([5.5](#55-errors)). An HCP Provider holding a detail whose `narrowedTo` it cannot enforce MUST treat that detail as reaching no entry. A restriction is never ignored because it is not understood.
- **Rule 3 — the object never overstates.** Where a grant is narrowed, the detail MUST carry its `narrowedTo`, and any person-facing presentation of the grant ([18](#18-conformance-claims-and-packages)) MUST reflect the narrowing rather than the bare scope. An implementation MUST NOT present `hcp:health_context:read` as the grant when the authorization was restricted to two entries. A detail with no `narrowedTo` member is unrestricted at category grain; the member is additive, and its absence means full category.
- **Rule 4 — enforcement.** Where the HCP Provider performs query-time filtering, a response MUST exclude any entry that the grant's restrictions place outside effective authority, on every read path: query and get entry, whatever the entry's content. Restrictions compose with minimization ([7](#7-disclosure-and-minimization)) as a prior filter: restrictions bound what the grant reaches, and minimization bounds what a query returns within that reach. An entry excluded by restriction is never a candidate for minimization.

The `grant.issued` audit event ([8.1](#81-required-log-events)) MUST record the narrowing alongside the categories and actions, so the Context Subject's own log shows how narrow a grant was, not merely that it was issued. No new event type is required; the existing `grant.issued` detail carries it.

Under end-to-end encrypted storage, filtering by anything other than categories or entry identifiers is performed within the Context Subject's trust domain ([4.8](#48-encrypted-storage)). Rules 1 through 3 govern the grant object and are unaffected.

### 6.1.5.2 Purposes

A purpose is a code, an absolute URI, with a description the person can read. This specification registers no purpose codes. Codes defined elsewhere, such as those of the Personal Data Portability Protocol ([I10](introduction.md#i10-related-work)), MAY be used.

- Every detail in a grant's `access` MUST carry at least one purpose. A grant is never issued without one.
- Before the approving act, the Authorizing Principal MUST be shown the description of each purpose ([6.1.6](#616-authorization-is-distinct-from-authentication)).
- Where a grant request names no purpose, the Authorization Service MUST ask the Authorizing Principal to choose one or more before approving. The HCP Client learns the purposes approved by reading its own grant ([5.2.6](#526-read-own-grant)).
- Every query and get entry names a purpose code ([5.2.1](#521-query), [5.2.2](#522-get-entry)). Where that code is not among the purposes of a detail in the grant covering the categories requested, the request MUST fail with not authorized ([5.5](#55-errors)).
- The purposes of an existing grant MUST NOT be widened without a further affirmative act ([6.1.6](#616-authorization-is-distinct-from-authentication)).

What a purpose binds is the client's declaration. The HCP Provider cannot observe what a client does with what it receives. A purpose fixes what the client may say it is doing, and what the Authorizing Principal approved, and the audit log records both ([8](#8-audit)). Use outside the declared purpose remains the client's responsibility ([3.11](#311-actor-invariants), invariant 14).

### 6.1.6 Authorization Is Distinct From Authentication

Authorization MUST NOT be inferred from authentication. The existence of an authenticated session, continued use of an application, account creation, or acceptance of terms of service MUST NOT be treated as the granting of access to entries.

Where a redirect-based OAuth flow is used, this separation is structural: the Authorizing Principal leaves the client, authorizes, and returns. Where grants are obtained through another authenticated channel — an in-application session, a messaging interface, an LLM-mediated dialogue — the separation MUST be preserved explicitly:

- The Authorizing Principal MUST perform an affirmative act to create a grant, distinct from any act by which they authenticated.
- Before that act, the Authorizing Principal MUST be told which categories are requested, each as the HCP Provider describes it ([4.5](#45-category-vocabulary)), which actions are permitted on them, the purposes for which they are requested ([6.1.5.2](#6152-purposes)), the longest time a disclosed copy may be used ([7.6](#76-use-until)), whether the grant is temporary or persistent, when it expires, the HCP Client and its Client Operator ([3.2.8](#328-client-operator-and-provider-operator)), the Requesting Party where it differs from the Context Subject ([3.4](#34-the-grant-binds-the-actors)), and, where the client declared one, the record the law requires it to keep and that revoking will not remove what it has kept there ([6.2.5](#625-copies-kept-under-a-legal-obligation)). Where a standing rule excludes a requested category, they MUST be told so ([6.3](#63-standing-rules)). Where a detail includes `provenance`, they MUST be told, as a separate item, that the client will see which apps and organizations contributed each entry ([7.4.1](#741-provenance-on-request)). They MUST be told whether the client has claimed to follow their directives ([6.4](#64-directives)). Where the request asks for onward sharing, they MUST be told so, and it is elected as 6.1.4 requires.
- The act MUST be recorded as a `grant.issued` event, carrying in detail the modality through which it was obtained and the strength of the authentication behind it, as `acr` (OpenID Connect Core 1.0).
- Before a grant reaches a High-sensitivity category ([4.5](#45-category-vocabulary)), the Authorization Service SHOULD require more than a sign-on through a messaging application alone ([21.3](#213-grants)).
- The categories, actions, or purposes of an existing grant MUST NOT be widened without a further affirmative act meeting the same requirements. A client requiring additional categories obtains a new grant or replaces the existing one.

These requirements are the substance of what a redirect-based flow accomplishes structurally. An implementation that satisfies them through a different channel satisfies this section; an implementation that does not is non-conformant regardless of binding.

### 6.1.7 Grant Request

The request that starts a grant is defined by the authorization profile ([12](#12-first-party-authorization-profile), [13](#13-oauth-interop-profile)). Whatever the profile, the outcome required by 6.1.6 holds: before the Authorizing Principal acts, they MUST be told what 6.1.6 lists, and the act MUST be recorded as a `grant.issued` event.

An HCP Client requesting scopes beyond what its task requires does not violate this section — HCP does not evaluate the necessity of a request, only what happens to it. Overbroad requests are visible to the Authorizing Principal at authorization time and to the Provider Operator in the resulting grant ([6.1.5](#615-grant-representation)); minimization ([7](#7-disclosure-and-minimization)) governs what a granted client subsequently retrieves, not what it may ask to be granted.

If the Authorizing Principal declines the request, no grant is created. Declining is not itself a security-relevant event: this specification does not require it to be logged, and an implementation MAY choose to record it for its own purposes.

### 6.1.8 Client Attribution and Authority

A grant authorizes an HCP Client, not any component that constructs a request on its behalf. The rules that follow from this are actor invariants 5, 6, 9, 10, 14, and 15 ([3.11](#311-actor-invariants)), and apply to every operation in this section.

### 6.1.9 Governance Operations

Governance operations ([5.4](#54-governance-operations)) MUST be performed only by a Management Client acting for the Authorizing Principal ([3.2.3](#323-hcp-client)). Any other caller MUST receive not authorized ([5.5](#55-errors)). A grant held by a Context Client never authorizes a governance operation, whatever its scopes. Under the Delegated Authorization Profile, a Management Client may act for the Context Subject or for a delegate, within what 17 allows each.

## 6.2 Revocation

Revocation is a first-class operation.

### 6.2.1 Revocation by the Authorizing Principal

The Authorizing Principal MUST be able to revoke any grant at any time, through a Management Client ([5.4](#54-governance-operations)) or the person-facing capabilities required by 18. Under the Delegated Authorization Profile, the Context Subject can also revoke every grant made for them, whoever authorized it ([17.5](#175-the-context-subjects-override)).

An HCP Client MAY also give up the grant under which it acts, as a context operation ([5.2.7](#527-relinquish-own-grant)). It cannot revoke any other grant.

Revocation MUST NOT be rate limited. The Authorizing Principal's ability to revoke access is not subject to throttling under any circumstance.

### 6.2.2 Revocation Propagation

Upon revocation:

- All authorization evidence issued under the grant, including access and refresh tokens, MUST be invalidated immediately: once revocation completes, no request presenting evidence issued under the grant succeeds. To meet this, the HCP Provider MUST determine the grant's current status on every request, by its own record of the grant or by token introspection (RFC 7662). It MUST NOT rely on a token's own validity alone, because a self-contained token stays valid after its grant is revoked.
- The revocation event MUST be appended to the audit log within 60 seconds.
- If the HCP Client holds disclosed entries, the HCP Provider MUST notify it, per 6.2.3, where the client has registered a notification endpoint.

Revocation ends the use of every copy disclosed under the grant, whatever its use-until time ([7.6](#76-use-until)):

- When an HCP Client is notified that its grant is revoked ([6.2.3](#623-revocation-notification)), it MUST stop using every copy disclosed under that grant, and MUST NOT pass any of them on. The one exception is a copy kept under a declared legal obligation ([6.2.5](#625-copies-kept-under-a-legal-obligation)).
- A request that fails because its grant has been revoked is itself a notice. The client MUST treat it exactly as a notification.

What the client does with its copies remains the client's responsibility ([3.11](#311-actor-invariants), invariant 14). The HCP Provider cannot enforce deletion; it bounds the harm with use-until, makes revocation reach the client, and records what happened ([6.2.3](#623-revocation-notification), [6.2.4](#624-when-notification-fails)).

### 6.2.3 Revocation Notification

Where an HCP Client has registered a notification endpoint, the notification required by 6.2.2 is delivered to it as a Security Event Token (RFC 8417). How it is delivered — push delivery, signing, identifiers, and retry — is defined by the HTTP Binding ([9.9](#99-revocation-notification-delivery)).

A client with no notification endpoint still receives every disclosure, but its use-until times are capped at 1 hour ([7.6](#76-use-until)).

**Auditing.** A `revocation.notified` event MUST be appended on first successful delivery, and on abandonment after retries are exhausted, with the outcome recorded in detail.

**Independence.** Revocation takes effect at the HCP Provider immediately per 6.2.2, whether or not notification succeeds. Failure or delay in delivery MUST NOT postpone or reverse the invalidation of authorization evidence.

**Abuse controls.** An HCP Provider MAY rate-limit notification delivery, and the registration of notification endpoints, to protect itself and the endpoints. It MUST NOT rate-limit, delay, or condition revocation itself ([6.2.1](#621-revocation-by-the-authorizing-principal)).

### 6.2.4 When Notification Fails

Where delivery of a revocation notification is abandoned ([9.9](#99-revocation-notification-delivery)), the HCP Provider MUST tell the Authorizing Principal, through the person-facing capabilities required by 18, that the client was not notified, and the time at which the last copy disclosed under the grant stops being usable. That time is the latest `useUntil` among those copies, which the audit log records ([8.2](#82-log-entry-structure)). The disclosure summary shows it as well ([8.6](#86-disclosure-summary)).

### 6.2.5 Copies Kept Under a Legal Obligation

Some clients are bound by law to keep what they receive. A clinic that records a patient's history in its medical record is bound by law to keep that record for years. Revocation cannot recall it, and this section makes that known in advance rather than leaving the promise of 6.2.2 unmet.

- An HCP Client that is required by law to keep context it receives in a record MUST declare it at registration: the record, the obligation, and the period. The HCP Provider records the declaration in each grant to that client as `client.legalRetention` ([6.1.5](#615-grant-representation)).
- Before the Authorizing Principal approves such a grant, they MUST be told that the client keeps what it receives in that record, under that obligation, and that revoking the grant will not remove it ([6.1.6](#616-authorization-is-distinct-from-authentication)).
- A copy the client places in that record is exempt from use-until ([7.6](#76-use-until)) and from the end of use on revocation ([6.2.2](#622-revocation-propagation)) only so far as the obligation requires. Once its use-until time passes or the grant is revoked, the client keeps it to meet that obligation, does not otherwise use it under this grant, and MUST NOT pass it on under HCP.
- When the grant is revoked, the HCP Provider MUST tell the Authorizing Principal, through the person-facing capabilities required by 18, which client keeps copies under a declared obligation, in which record, and for how long. The disclosure summary shows it ([8.6](#86-disclosure-summary)).
- A copy kept under an obligation the client did not declare is not covered by this section. Keeping it after revocation does not conform.

What the law requires of the record itself, such as giving the patient access to it, is outside this specification.

## 6.3 Standing Rules

A grant governs one client. A standing rule governs every grant: "never give my context to anyone in this namespace", for everything or only for health. The Context Subject sets it once, and the HCP Provider enforces it on every grant, present and future.

**Template: a standing rule**

    {
      "ruleId": "urn:uuid:{rule-uuid}",
      "effect": "deny",
      "operators": ["{DNS domain | operator identifier}"],
      "requires": ["{client conformance identifier}"],
      "categories": ["{category}"],
      "setBy": "{context-subject | delegation id}",
      "createdAt": "{date-time}"
    }

| Member | Rule |
|--------------|------------------------------------------------------------------|
| `ruleId` | Stable for the life of the rule |
| `effect` | `deny`, the only effect in this draft. A standing rule never widens access. |
| `operators` | The Client Operators ([3.2.8](#328-client-operator-and-provider-operator)) the rule applies to. Absent means every operator, and is allowed only with `requires`. A DNS domain matches every operator whose identifier's host is that domain or a subdomain of it; any other value matches one operator identifier exactly. |
| `requires` | Client conformance claims ([18.1](#181-claims)). Where present, the rule denies only clients of the named operators that do not make every claim listed: "only apps that follow my directives may read my health context." |
| `categories` | The categories the rule applies to. Absent means every category, held now or later: the rule applies across all of the person's context. |
| `setBy` | Set by the HCP Provider: `context-subject`, or the `delegationId` of the delegate who set it ([17.2](#172-delegations)) |
| `createdAt` | Set by the HCP Provider |

Requirements:

- The Context Subject sets and removes standing rules through a Management Client, as a governance operation ([5.4](#54-governance-operations)). The HCP Provider appends `rule.set` or `rule.removed` ([8.1](#81-required-log-events)).
- The HCP Provider MUST NOT issue a grant whose `access` reaches a category a standing rule denies to that grant's Client Operator. Before the approving act, the Authorizing Principal is told which requested categories a rule excludes ([6.1.6](#616-authorization-is-distinct-from-authentication)). The rule can be overridden only by removing it, which is a separate act.
- An operator that a standing rule denies any category of a detail carrying `onwardSharing` is listed in that detail's `notTo`, on every grant, from the moment the rule is set ([6.1.5](#615-grant-representation)). A client cannot share with it under 3.12.
- A standing rule reaches an entry through any of its categories. Where a rule denies a Client Operator any category of an entry, the entry is withheld from that operator's clients, whichever category a request names ([4.5](#45-category-vocabulary), [7.1](#71-category-and-purpose-bound)).
- A standing rule applies to existing grants from the moment it is set, through the status check made on every request ([6.2.2](#622-revocation-propagation)). A request it covers fails with not authorized ([5.5](#55-errors)). Where it covers every category a grant reaches, the HCP Provider revokes the grant, and 6.2.2–6.2.4 apply.
- A delegate cannot authorize a grant a standing rule denies ([17.4](#174-scope-and-grants-under-a-delegation)). Under the Delegated Authorization Profile, a delegate MAY also set standing rules, within the categories of the delegation's scope, through a Management Client acting for them. The Context Subject can remove any standing rule; a delegate can remove only the rules they set. Each rule records who set it, in `setBy`.
- Standing rules are part of the Context Subject's export ([5.4.1](#541-export)). An import ([5.4.3](#543-import)) brings them with it, because they only restrict access.

A standing rule controls which clients receive context. What a client may do with context it has received, or on the person's behalf, is a directive ([6.4](#64-directives)).

## 6.4 Directives

A directive tells a client what it may do with context it has received, or on the Context Subject's behalf: "never pass my health context to another agent", "ask me before you sign anything", "you may book appointments for me". The Context Subject sets it once, and the HCP Provider delivers it with every disclosure it applies to.

**Template: a directive**

    {
      "directiveId": "urn:uuid:{directive-uuid}",
      "action": "share | sign | transact | {URI}",
      "effect": "deny | ask-first | permit",
      "text": "{the directive, in the person's words}",
      "categories": ["{category}"],
      "operators": ["{DNS domain | operator identifier}"],
      "setBy": "{context-subject | delegation id}",
      "createdAt": "{date-time}"
    }

| Member | Rule |
|--------------|------------------------------------------------------------------|
| `directiveId` | Stable for the life of the directive |
| `action` | What the directive governs. `share`: passing context the client received to another agent, including a component of its own Client Operator ([3.12](#312-onward-disclosure)). `sign`: signing, agreeing to, or committing to anything on the Context Subject's behalf. `transact`: spending, buying, or entering a contract on the Context Subject's behalf. Any other action is an absolute URI ([A.3](#a3-extension-points)). |
| `effect` | `deny`: the client MUST NOT take the action. `ask-first`: the client MUST obtain the Context Subject's confirmation each time before taking it. `permit`: the client may take it without asking. |
| `text` | Required. The directive in the Context Subject's words, shown to them when it is set. A client that does not recognize `action` reads the directive from `text`. |
| `categories` | The categories whose context the directive governs. Absent means every category, held now or later. |
| `operators` | The Client Operators the directive applies to, matched as for standing rules ([6.3](#63-standing-rules)). Absent means every operator. |
| `setBy`, `createdAt` | Set by the HCP Provider, as for standing rules |

Requirements:

- The Context Subject sets and removes directives through a Management Client, as a governance operation ([5.4](#54-governance-operations)). The HCP Provider appends `directive.set` or `directive.removed` ([8.1](#81-required-log-events)). Under the Delegated Authorization Profile, a delegate MAY set directives within the categories of the delegation's scope, and removes them as for standing rules ([6.3](#63-standing-rules)).
- **Directives only narrow.** A directive never widens access to context: it does not authorize a disclosure the grant does not, or onward disclosure beyond 3.12. `permit` applies only to actions this specification does not otherwise govern, such as signing. A `share` directive whose effect is `permit` relaxes nothing in 3.12: onward sharing to another organization is allowed only by the grant ([6.1.4](#614-grant-distinction-temporary-vs-persistent)), and a `share` directive whose effect is `deny` or `ask-first` applies to it. Where two directives that apply disagree, `deny` prevails over `ask-first`, and `ask-first` over `permit`.
- **Delivery.** Every query and get-entry result to a Context Client carries `directives`: each directive whose `operators` match the client's Client Operator, and whose `categories` include a category of an entry disclosed or are absent ([5.2.1](#521-query), [5.2.2](#522-get-entry)). A client reading its own grant receives the directives that apply to it ([5.2.6](#526-read-own-grant)). Directives are delivered whether or not the client claims to follow them. A directive set after a disclosure reaches the client with its next result. Because every client a directive applies to receives its `text`, a Management Client SHOULD tell the Context Subject, when they write one, that those clients will see it, and SHOULD scope a directive about sensitive context to its categories.
- **Clients that claim to follow directives.** An HCP Client that claims `https://hcp.example/spec/clients/directives/2.0` ([1.7](#17-conformance-identifiers), [18.1](#181-claims)) MUST follow every directive delivered to it, the most recent it has received, for as long as it holds context disclosed under the grant. A directive whose `action` it does not recognize it MUST NOT treat as a permission. Under the MCP Binding the claim binds the host, which holds the grant ([10.5](#105-who-holds-the-grant)): it MUST apply directives itself. Passing a directive to a model is not following it.
- **The claim.** A client declares the claim at registration, and the grant records it in `client.claims` ([6.1.5](#615-grant-representation)). Before approving a grant, the Authorizing Principal is told whether the client has made it ([6.1.6](#616-authorization-is-distinct-from-authentication)). A standing rule can deny every client that has not ([6.3](#63-standing-rules)).
- **What the provider can and cannot see.** The HCP Provider cannot observe what a client does with a directive. A claim is a declaration, as a purpose is ([6.1.5.2](#6152-purposes)), and the audit log records which directives each result carried ([8.2](#82-log-entry-structure)). Third-party attestation of client claims is later work ([P1.4](path-to-v2-final.md#p14-later)).
- Directives are part of the Context Subject's export ([5.4.1](#541-export)). An import ([5.4.3](#543-import)) brings them with it.
# 7. Disclosure and Minimization

Data minimization is enforced at query time, not at grant time. An authorized category is the outer bound of what may be returned, not a description of what should be.

This section states minimization as four requirements rather than as an outcome. Requirements 7.1, 7.2, and 7.4 are mechanically verifiable; 7.3 is verified by declaration. 7.5 specifies how a response reports them, and 7.6 how long a disclosed copy may be used.

## 7.1 Category and Purpose Bound

A response MUST contain only entries that the grant under which the request was made reaches: at least one of the entry's categories is within the grant's scopes, with the purpose the request names approved for it ([6.1.5.2](#6152-purposes)). Within that, a response MUST NOT contain:

- an entry any of whose categories a standing rule denies to the client's Client Operator ([6.3](#63-standing-rules)); or
- an entry whose permitted purposes, where present, exclude the purpose the request names ([4.2.6](#426-permitted-purposes)).

This holds regardless of the relevance of the entry to the stated query.

## 7.2 Quantity Bound

A response MUST NOT contain more entries than the lesser of the requested `maxEntries` and a ceiling of 20. The ceiling applies to every binding.

An implementation MUST NOT return additional entries in order to reach `maxEntries`. Where fewer entries meet the implementation's relevance criteria than were requested, fewer are returned. `maxEntries` is a ceiling, not a target.

Query results are not paginated. `maxEntries` is a minimization control rather than a page size, and a cursor over a minimized result set would permit an authorized client to enumerate an entire category one page at a time — precisely what this section exists to prevent. Where a pilot finds the ceiling of 20 insufficient, the appropriate response is evidence toward raising it.

The quantity bound is defeated if a Context Client issues a sequence of semantically rephrased queries to sweep a category a few entries at a time, assembling in aggregate what a single request may not return. A client that does so is acting adversarially toward the minimization contract, and an HCP Provider MAY treat a pattern of rephrased queries against one category and grant as a signal to rate-limit or to decline.

## 7.3 Relevance Ordering

An implementation MUST apply a relevance ordering to candidate entries and MUST return entries in that order. Returning entries in storage order, insertion order, or arbitrary order is non-conformant.

An implementation MUST declare the method determining the final ordering in its discovery document ([19](#19-discovery-document)). The set of method values is open; the following are registered:

| Value | Meaning |
|------------|------------------------------------------------------------------|
| `lexical` | Ordering derived from term or token overlap between query and entry |
| `semantic` | Ordering derived from embedding or vector similarity |
| `llm` | Ordering derived from a language model's judgment of relevance to the stated query and purpose |
| `none` | No ordering applied, because the request named a single entry ([5.2.2](#522-get-entry)) |

Where an implementation combines methods, it declares the one determining the final ordering. Under end-to-end encrypted storage, the ordering is applied within the Context Subject's trust domain ([4.8](#48-encrypted-storage)).

## 7.4 Disclosures to Context Clients

Where the requester is a Context Client, a response MUST carry each entry as a **disclosure**, never as the stored entry:

**Template: a disclosure, HCP Provider → Context Client (either binding)**

    {
      "ref": "{grant-scoped reference}",
      "version": 2,
      "content": { },
      "evidence": [ ],
      "assertion": { "declarationType": "...", "confidence": null, "validUntil": null },
      "classification": { "categories": ["{category}"], "dimension": "{dimension | null}", "permittedPurposes": ["{purpose URI}"] },
      "standing": { "assurance": "unverified | authenticated | cryptographically-verified", "confirmed": true },
      "useUntil": "{date-time}",
      "onwardSharing": true,
      "relationships": [ { "type": "{type}", "target": "{ref}" } ]
    }

| Member | Rule |
|------------------|------------------------------------------------------------------|
| `ref` | A reference to the entry, opaque to the client, stable for one grant and one entry, and different under every other grant. It MUST NOT reveal or be derivable into the entry's `id`. The client names the entry by its `ref` in get entry, revise, and withdraw ([5.2](#52-context-operations)). A `ref` presented under any other grant fails with not authorized ([5.5](#55-errors)). |
| `version`, `content`, `assertion` | As stored, for the version disclosed ([4.2](#42-entry)), including `basis` and `permittedPurposes` ([4.2.5](#425-basis), [4.2.6](#426-permitted-purposes)) |
| `evidence` | As stored, including each item's `verification` ([4.2.2](#422-evidence)), except that a credential may be disclosed in derived form. An item carrying a derived credential adds `revealed`, the JSON Pointers into the stored credential of the claims it reveals ([14.9](#149-selective-disclosure)). |
| `classification` | The categories the requesting grant covers, the dimension, and `permittedPurposes` where present. The entry's other categories are withheld: they would tell the client what else the entry concerns. |
| `standing` | `assurance` is `record.provenance.assertedBy.assurance`; `confirmed` is true where the most recent confirmation record on the version disclosed is `confirmed` ([3.8](#38-confirmation)) Where it rests on a credential the Context Subject's trust domain verified, the evidence item's `verification.by` says so ([4.8](#48-encrypted-storage)). |
| `useUntil` | The time after which the client may no longer use the copy ([7.6](#76-use-until)) |
| `onwardSharing` | True where the detail of the requesting grant that reaches the entry carries `onwardSharing` ([6.1.5](#615-grant-representation)), and every category of the entry, including those withheld, has a default sensitivity of Low ([4.5](#45-category-vocabulary)). Omitted otherwise. It is how the client knows what it may share under 3.12; it reveals of the withheld categories only that none is above Low. |
| `relationships` | Only relationships whose target is disclosed in the same response, with the target named by its `ref` ([4.2.3](#423-relationships)) |

Everything else in the entry is withheld: its `id` and `subject`, its status, and the rest of `record`, including the provenance fields that identify parties (`source`, `submittedByClient`, `authorizedUnder`, `assertedBy.id`, `confirmedBy`), `record.conversion`, and `record.metadata`. These fields describe the Context Subject's activity with other systems rather than the entry itself. Disclosing them tells one client which other clients a person uses and which of their conversations produced what, which no grant authorizes. A stable `id` would also let two clients that compare notes recognize the same entry, which a grant-scoped `ref` does not. What a client needs to judge an entry's standing, it receives in `standing` ([3.8](#38-confirmation)).

A credential in `evidence` cannot be altered without breaking its proof ([4.2.2](#422-evidence)). Where it is secured with a mechanism that supports selective disclosure, the HCP Provider SHOULD disclose a derived credential revealing only the claims the request's purpose requires and those its issuer made mandatory ([14.9](#149-selective-disclosure)). Otherwise it is disclosed whole, and may carry identifiers of its own, such as the credential subject's identifier.

A client SHOULD present disclosed content, and the text of directives ([6.4](#64-directives)), to a model as data and never as instructions. An entry may carry text written to steer a model that reads it ([21.10](#2110-models)).

Disclosure is a property of the response, not of storage. Entries MUST continue to carry complete provenance as stored, and the Context Subject's own access — through export, the audit log, or a Management Client — receives whole entries with their stable identifiers.

### 7.4.1 Provenance on Request

A Context Client whose grant includes the `provenance` action for an entry's category ([6.1.5](#615-grant-representation)) receives, in addition, `provenance` on each disclosure of that entry:

**Template: the `provenance` member of a disclosure, HCP Provider → Context Client**

    "provenance": {
      "submittedBy": { "name": "{client name}", "operator": "{organization name}" },
      "source": "conversation | document | person-input | integration",
      "assertedAt": "{date-time}",
      "recordedAt": "{date-time}"
    }

It answers a question such as "why do you think I prefer graphs?" without exposing more than that answer needs.

- An HCP Provider MUST NOT issue a grant including `provenance` unless its Requesting Party is the Context Subject ([3.4](#34-the-grant-binds-the-actors)).
- `submittedBy` carries the names of the client that submitted the version disclosed and of its Client Operator, as recorded in `submittedByClient` ([3.5](#35-provenance-layers)). `source` is the kind of origin `record.provenance.source` records, not its value.
- `provenance` MUST NOT carry an identifier of a client, a Client Operator, a grant, a conversation, or a document, nor `confirmedBy`. Whether the Context Subject confirmed the version is already in `standing`.
- The audit log marks each disclosure that carried provenance ([8.2](#82-log-entry-structure)).

## 7.5 Reporting

Query and get-entry responses MUST carry a minimization report:

**Template: the minimization report in a result, HCP Provider → Context Client**

    "minimization": {
      "method": "{declared method, or none}"
    }

A get-entry response reports `method` as `none` ([7.3](#73-relevance-ordering)). The report MUST NOT include the number of entries considered, the number available within scope, or any other measure of what was withheld; such counts disclose the size of a Context Subject's holdings to a client that was not granted them.

## 7.6 Use-Until

Every disclosure carries `useUntil`. After that time, the HCP Client MUST NOT use the copy, or pass it on, without fetching it again ([3.12](#312-onward-disclosure)), except as a declared legal obligation requires ([6.2.5](#625-copies-kept-under-a-legal-obligation)). The HCP Provider sets it at disclosure:

1. **An explicit time applies first.** Where the entry has an `assertion.validUntil`, or its credential a `validUntil` ([14.2](#142-credential-and-signature-boundary)), or the provider sets a time of its own, `useUntil` is the earliest of these. An explicit time earlier than the floor below still applies: content that no longer holds is not usable for an hour.
2. **Otherwise, a heuristic.** `useUntil` is the disclosure time plus 10% of the time since the entry was last revised, the `recordedAt` of its current version ([4.2](#42-entry)). The heuristic follows HTTP heuristic freshness (RFC 9111 §4.2.2).
3. **A floor and ceilings.** A heuristic time is never less than 1 hour after disclosure. No time is more than 30 days after disclosure, or 24 hours for an entry whose default sensitivity is High: the highest among its categories ([4.5](#45-category-vocabulary)). A custom category has the sensitivity its provider declares for it, which is never Low ([4.5](#45-category-vocabulary)).
4. **No notification channel, short copies.** Where the HCP Client has no registered notification endpoint ([6.2.3](#623-revocation-notification)), `useUntil` is never more than 1 hour after disclosure. The cap comes from the missing channel, not from the grant.

The grant does not cap `useUntil`: a temporary grant limits access, not use of a copy already disclosed. Revocation does end it. When a client is notified that a grant is revoked, every copy disclosed under that grant becomes unusable at once, whatever its `useUntil` ([6.2.3](#623-revocation-notification)).

Before the Authorizing Principal approves a grant, they MUST be told the longest time a disclosed copy may be used under it: the ceiling that applies to the categories requested, or 1 hour where the client has no notification endpoint ([6.1.6](#616-authorization-is-distinct-from-authentication)).

The floor and ceilings are starting values, to be tuned with pilot evidence ([G1.2](guides.md#g12-what-pilots-should-record)). `useUntil` is not signed in this draft.
# 8. Audit

The audit log is append-only, inspectable by the Context Subject, and required for every implementation conforming to Core. Its level of tamper-evidence is declared ([8.7](#87-integrity)).

## 8.1 Required Log Events

| Event Type | Trigger |
|---------------------------|------------------------------------------------------------------|
| `context.created` | Any create ([5.2.3](#523-create)) |
| `context.read` | Any query ([5.2.1](#521-query)) or get entry ([5.2.2](#522-get-entry)) |
| `context.revised` | Any revise ([5.2.4](#524-revise)) |
| `context.recategorized` | Any change of an entry's categories ([4.2.1](#421-mutability)) |
| `context.restricted` | Any change of the Authorizing Principal's permitted purposes for an entry ([4.2.6](#426-permitted-purposes)) |
| `context.withdrawn` | Any withdraw ([5.2.5](#525-withdraw)) |
| `context.hardDeleted` | Any hard deletion ([5.4.2](#542-hard-deletion)) |
| `context.confirmed` | Any confirmation or rejection of an entry ([3.8](#38-confirmation)), with the disposition in detail |
| `context.exported` | Any export ([5.4.1](#541-export)) |
| `context.imported` | Any import other than a dry run ([5.4.3](#543-import)) |
| `context.shared` | A client reports sharing context with another organization ([5.2.8](#528-report-onward-sharing)) |
| `context.expired` | An entry's validity has passed, and its status is set to `expired` ([4.2.4](#424-status)) |
| `context.credentialStatus` | An entry becomes or ceases to be `revoked` or `suspended`, or a supporting credential's `verification` changes with its status ([14.7](#147-credential-status), [14.8](#148-supporting-credentials)) |
| `grant.issued` | Any new grant |
| `grant.revoked` | Any revocation |
| `grant.expired` | Automatic expiry of a grant, without revocation by the Authorizing Principal, including at the end of a delegation ([17.6](#176-ending-a-delegation)) |
| `delegation.established` | A delegation is established ([17.2](#172-delegations)) |
| `delegation.ended` | A delegation ends ([17.6](#176-ending-a-delegation)) |
| `rule.set` | A standing rule is set ([6.3](#63-standing-rules)) |
| `rule.removed` | A standing rule is removed ([6.3](#63-standing-rules)) |
| `directive.set` | A directive is set ([6.4](#64-directives)) |
| `directive.removed` | A directive is removed ([6.4](#64-directives)) |
| `conflict.detected` | A conflict between two entries ([4.7](#47-conflicts)) |
| `conflict.proposed` | A proposal is made for resolving a conflict ([4.7.4](#474-proposals)) |
| `conflict.resolved` | A conflict is resolved: a conflicted entry leaves conflicted status through any transition in 4.7.3, an asserter's later inference deprecates its earlier one, or a conflict that changed no status ends ([4.7](#47-conflicts)) |
| `revocation.notified` | Revocation notification sent to an HCP Client's notification endpoint ([6.2.3](#623-revocation-notification)) |

A `grant.expired` event MUST be appended no later than the earlier of (a) the first access attempt presenting the expired grant, or (b) 24 hours after the grant's expiry timestamp. Implementations are not required to append the event at the instant of expiry.

## 8.2 Log Entry Structure

**Template: an audit event, as the HCP Provider records it**

    {
      "eventId": "urn:uuid:{uuid}",
      "eventType": "{event-type}",
      "timestamp": "{date-time}",
      "participants": {
        "initiator": { "role": "{role}", "id": "{identifier}" },
        "clientOperator": { "id": "{operator-identifier}" },
        "requestingParty": { "id": "{identifier}" },
        "authorizingPrincipal": { "id": "{identifier}" },
        "provider": { "id": "{provider-identifier}" },
        "retrievalId": "urn:uuid:{retrieval-uuid}",
        "model": { "id": "{model-identifier}" }
      },
      "entryId": "{urn:uuid or null}",
      "relatedEntryId": "{urn:uuid or null}",
      "categories": ["{category}"],
      "purpose": "{purpose code or null}",
      "purposeDescription": "{stated task or null}",
      "grantId": "{urn:uuid or null}",
      "disclosed": [
        {
          "entryId": "{urn:uuid}",
          "version": 2,
          "useUntil": "{date-time}",
          "provenance": true,
          "revealed": [ { "evidence": 0, "claims": ["{JSON Pointer}"] } ]
        }
      ],
      "data": { }
    }

`participants` replaces v1's `actorId` and `actorType`. `initiator.role` is one of `management-client`, `context-client`, `authorization-service`, or `hcp-provider`. Which members are present is set out in 3.9; no event names "system".

For `conflict.detected`, `conflict.proposed`, and `conflict.resolved`, `entryId` identifies the conflicted entry and `relatedEntryId` identifies the authoritative entry ([4.7.1](#471-standing)). Where neither or both are authoritative, they identify the two entries. `relatedEntryId` is null for all other event types.

`disclosed` is present on `context.read` and lists every entry disclosed by the retrieval: its stable `id`, the version disclosed, and the `useUntil` it was given ([7.6](#76-use-until)). `provenance` is true where the disclosure carried provenance ([7.4.1](#741-provenance-on-request)), and omitted otherwise. Where a credential was disclosed in derived form, `revealed` names the evidence item by its index and lists the claims revealed ([14.9](#149-selective-disclosure)); it is omitted otherwise. The log names entries by their `id`, not by the `ref` the client received, because the log is the Context Subject's ([8.3](#83-access-to-the-audit-log)). The query text is not recorded: it can be as sensitive as the content it asks for.

`data` replaces v1's free-text `detail`. Its members are fixed by event type, so that the log can be filtered, tested, and presented in any language. Where this specification says that an event records something in detail, it is recorded in `data`.

| Event type | `data` members |
|---------------------------|------------------------------------------------------------------|
| `context.created`, `context.revised` | `version`; `reason` (revise) |
| `context.read` | `maxEntries` (query); `categoriesSearched` (query); `directives`, the `directiveId` of each directive the result carried ([6.4](#64-directives)) |
| `context.recategorized` | `from`, `to` (each a list of categories) |
| `context.restricted` | `from`, `to` (each a list of purpose codes, or null) |
| `context.withdrawn` | `reason` |
| `context.confirmed` | `disposition`, `version` |
| `context.exported` | `options` ([5.4.1](#541-export)) |
| `context.imported` | `outcomes`: each entry's `id` and outcome ([5.4.3](#543-import)) |
| `context.shared` | `recipient` (`domain`, `name`), `entries` (each `id`), `purpose`, `sharedAt`, `permitted` ([5.2.8](#528-report-onward-sharing)) |
| `context.expired` | `version` |
| `context.credentialStatus` | `evidence` (the item's index), `role`, `status` (`revoked`, `suspended`, or `valid`), and `entryStatus`, the entry's status after the change |
| `grant.issued` | `access`, `grantType`, `expiresAt`, `modality`, `acr` ([6.1.4](#614-grant-distinction-temporary-vs-persistent), [6.1.6](#616-authorization-is-distinct-from-authentication)); `delegation`, where a delegate authorized it ([17.4](#174-scope-and-grants-under-a-delegation)) |
| `grant.revoked` | none |
| `grant.expired` | `reason`: `expiresAt` or `delegation-ended` ([17.6](#176-ending-a-delegation)) |
| `delegation.established` | `delegationId`, `relationship`, `basis.method`, `basis.parent` (a sub-delegation), `scope` ([17.2](#172-delegations), [17.10](#1710-sub-delegation)) |
| `delegation.ended` | `delegationId`, `reason` ([17.6](#176-ending-a-delegation)) |
| `rule.set`, `rule.removed` | `ruleId`, `operators`, `requires`, `categories`, `setBy` ([6.3](#63-standing-rules)) |
| `directive.set`, `directive.removed` | `directiveId`, `action`, `effect`, `categories`, `operators`, `setBy` ([6.4](#64-directives)) |
| `conflict.detected`, `conflict.resolved` | `transition` (resolved: `rejected`, `accepted`, or `superseded`, [4.7.3](#473-resolution); `dismissed`, [4.7.3](#473-resolution); `asserter-superseded` or `ended`, [4.7](#47-conflicts)); `proposal` (resolved: true where the act followed a proposal, [4.7.4](#474-proposals)) |
| `conflict.proposed` | `act`, `entry`, `weighed`, `proposedBy` ([4.7.4](#474-proposals)) |
| `revocation.notified` | `outcome` (`delivered` or `abandoned`), `attempts`, `lastUseUntil` ([6.2.4](#624-when-notification-fails)) |

Implementations MAY add members to `data`. They are preserved and not interpreted ([A.3](#a3-extension-points)).

## 8.3 Access to the Audit Log

Reading the audit log is a governance operation ([5.4](#54-governance-operations)). The Authorizing Principal MUST be able to, through a Management Client or the person-facing capabilities required by 18:

- View the full audit log
- Filter by HCP Client, category, event type, and date range
- Export the audit log in JSON-LD format

Context Clients MUST NOT have read access to the audit log. Under the Delegated Authorization Profile, the Context Subject reads the whole log, and a delegate or former delegate reads the part 17.7 sets out.

## 8.4 Durability

The append-only requirement in 8 constrains ordering and immutability. It does not by itself specify when an acknowledged append becomes durable against process or host failure. Implementations differ here, and this specification requires the difference to be declared rather than assumed.

- Every event type other than `context.read` MUST be durable before the operation it records is acknowledged to the caller.
- `context.read` MAY be acknowledged before durability, provided the implementation declares a bounded durability window in its discovery document ([19](#19-discovery-document)).
- A declared window MUST NOT exceed 10,000 milliseconds.
- An implementation that declares a window MUST disclose it wherever it presents the audit log to the person, expressed as what the person may be missing rather than as storage behavior. This requirement is modality-neutral: it applies equally to graphical interfaces, to spoken and voice presentation, and to natural language access ([18](#18-conformance-claims-and-packages)). Where the audit log is presented by voice, the disclosure is spoken; the obligation is to convey what may be missing, in whatever modality the log is offered, not to render a particular visual element.
- An implementation that declares no window is asserting synchronous durability for all event types, and conformance testing MAY hold it to that.

This provision governs durability only. It does not relax the ordering, immutability, or completeness requirements in 8.1 through 8.3.

## 8.5 Controller-Side Logging

The log specified in 8.1 through 8.4 is the Context Subject's log. It is theirs to inspect and export, and Context Clients cannot read it ([8.3](#83-access-to-the-audit-log)).

Provider Operators are separately subject to obligations that a per-person log cannot discharge: organization-level access questions spanning many Context Subjects, and records that must survive hard deletion of a person's data in order to evidence that the deletion took place. Accordingly:

- Provider Operators are expected to maintain a controller-side access log. It sits outside the HCP instance and is not part of the HCP data model.
- The controller-side log MUST NOT contain entry content, in whole, in part, or in derived form.
- It MAY contain a pseudonymous subject identifier, participant identifiers, an event type, a category slug, a grant identifier, and a timestamp.
- It MAY retain these after the corresponding Context Subject's data has been hard-deleted, and MAY anchor the integrity of the Context Subject's log.
- The prohibition in 8.3 applies to the Context Subject's log. It does not prohibit the controller-side log.
- The controller-side log SHOULD be designed so that it cannot be cross-matched against the Context Subject's own log to reconstruct entry content or infer it from access patterns. A pseudonymous subject identifier that is stable across the Provider Operator's whole population, for instance, lets the two logs be joined; a per-person or rotating pseudonym resists that. Preserving this un-linkability is discussed in 21.6; for now it is a design expectation, stated so that implementations do not build a scheme that has to be undone.
- Conformance testing does not evaluate the controller-side log.

## 8.6 Disclosure Summary

The HCP Provider MUST make available to the Authorizing Principal a summary of what each HCP Client has received. It is a governance operation ([5.4](#54-governance-operations)), carried by the HTTP Binding ([9.4.12](#9412-disclosure-summary)), and a person-facing capability ([18.4](#184-person-facing-capabilities)). For each client it gives:

| Member | Content |
|------------------------|------------------------------------------------------------------|
| `client` | Object: the client's `id` and `name`, and its `operator`, with `id` and `name` ([3.2.8](#328-client-operator-and-provider-operator)) |
| `grants` | Array: the grants under which it received context, each with `grantId` and `status` |
| `categories` | Array: the categories disclosed to it |
| `purposes` | Array: the purpose codes declared for those disclosures ([6.1.5.2](#6152-purposes)) |
| `entries` | Integer: how many distinct entries were disclosed |
| `retrievals` | Integer: how many retrievals there were |
| `firstAt`, `lastAt` | Date-time: the period over which they took place |
| `usableUntil` | Date-time: the latest `useUntil` among the copies disclosed ([7.6](#76-use-until)), or, where a revocation notice was delivered, the time of delivery |
| `notification` | `delivered`, `abandoned`, or `none`, for the most recent revocation ([6.2.4](#624-when-notification-fails)) |
| `legalRetention` | Object: `record`, `obligation` and `period`, as in the grant, where the client declared one ([6.1.5](#615-grant-representation), [6.2.5](#625-copies-kept-under-a-legal-obligation)) |

The summary is computed from the audit log ([8.2](#82-log-entry-structure)) and MAY be filtered by client, category, and date range. It discloses nothing the log does not hold. It does not show what happens to context after it reaches a client, which the provider cannot see ([6.2.2](#622-revocation-propagation)).

## 8.7 Integrity

Append-only means the log cannot be altered through any HCP operation. It does not, by itself, let anyone detect an alteration made outside them. An HCP Provider MUST declare the integrity of the Context Subject's log in its discovery document as `audit_integrity` ([19](#19-discovery-document)). One that holds entries in a High-sensitivity category ([4.5](#45-category-vocabulary)) SHOULD declare at least `hash-chained` ([21.6](#216-audit)):

| Value | Meaning |
|------------------------|------------------------------------------------------------------|
| `append-only` | Events cannot be changed or removed through any HCP operation. The minimum for conformance. |
| `hash-chained` | Each event carries a hash of the one before it, so a change to any event is detectable |
| `signed-checkpoints` | As `hash-chained`, with the chain's head signed by the provider at intervals |
| `anchored` | As `signed-checkpoints`, with checkpoints recorded outside the provider's control, for example in the controller-side log of another party ([8.5](#85-controller-side-logging)) |

How hashes are computed and checkpoints published is not specified in this draft. The declaration makes the level explicit and testable; pilots that need more than `append-only` will inform a common format ([P1](path-to-v2-final.md#p1-roadmap)).
# Part II — Bindings

# 9. HTTP Binding

## 9.1 Scope

This section maps the Core operations ([5](#5-operations-and-errors)) and errors ([5.5](#55-errors)) onto HTTP. It is identified as https://hcp.example/spec/bindings/http/2.0 ([1.7](#17-conformance-identifiers)).

The HTTP Binding exists for traditional, auditable server-to-server integration — institutional systems, batch jobs, and clients that are not LLM-mediated — where a conventional HTTP client is the natural fit; the MCP Binding ([10](#10-mcp-binding)) exists for agent-native access, where an LLM discovers and invokes tools directly. The HTTP Binding is also the only binding that carries governance operations ([1.6](#16-context-plane-and-governance-plane)), and it is required for the Provider Interop package ([18](#18-conformance-claims-and-packages)).

The base URL is implementation-defined. An implementation exposing the HTTP Binding MUST publish a discovery document at `/.well-known/hcp-configuration` ([19](#19-discovery-document)).

## 9.2 Endpoints

| Core operation | Plane | Method | Path |
|-----------------------------------|------------|--------|------------------------------------------------|
| Query ([5.2.1](#521-query)) | Context | POST | `/v2/entries/query` |
| Get entry ([5.2.2](#522-get-entry)) | Context | GET | `/v2/entries/{entryId}` |
| Create ([5.2.3](#523-create)) | Context | POST | `/v2/entries` |
| Revise ([5.2.4](#524-revise)) | Context | POST | `/v2/entries/{entryId}/revisions` |
| Withdraw ([5.2.5](#525-withdraw)) | Context | DELETE | `/v2/entries/{entryId}` |
| Read own grant ([5.2.6](#526-read-own-grant)) | Context | GET | `/v2/grants`, with a Context Client's token |
| List grants ([5.4](#54-governance-operations)) | Governance | GET | `/v2/grants`, with a Management Client's token |
| Relinquish own grant ([5.2.7](#527-relinquish-own-grant)) | Context | DELETE | `/v2/grants/{grantId}`, with a Context Client's token for that grant |
| Report onward sharing ([5.2.8](#528-report-onward-sharing)) | Context | POST | `/v2/shares` |
| Revoke grant ([6.2](#62-revocation)) | Governance | DELETE | `/v2/grants/{grantId}`, with a Management Client's token |
| Read audit log ([8.3](#83-access-to-the-audit-log)) | Governance | GET | `/v2/audit` |
| Export ([5.4.1](#541-export)) | Governance | GET | `/v2/export` |
| Hard delete ([5.4.2](#542-hard-deletion)) | Governance | DELETE | `/v2/entries/{entryId}?hardDelete=true` |
| Confirm or reject ([3.8](#38-confirmation)) | Governance | POST | `/v2/entries/{entryId}/confirmation` |
| Change categories ([4.2.1](#421-mutability)) | Governance | PUT | `/v2/entries/{entryId}/categories` |
| Restrict purposes ([4.2.6](#426-permitted-purposes)) | Governance | PUT | `/v2/entries/{entryId}/purposes` |
| Import ([5.4.3](#543-import)) | Governance | POST | `/v2/import` |
| Disclosure summary ([8.6](#86-disclosure-summary)) | Governance | GET | `/v2/disclosures` |
| List delegations ([17.2](#172-delegations)) | Governance | GET | `/v2/delegations` |
| List or set standing rules ([6.3](#63-standing-rules)) | Governance | GET, POST | `/v2/rules` |
| Remove standing rule ([6.3](#63-standing-rules)) | Governance | DELETE | `/v2/rules/{ruleId}` |
| List or set directives ([6.4](#64-directives)) | Governance | GET, POST | `/v2/directives` |
| Remove directive ([6.4](#64-directives)) | Governance | DELETE | `/v2/directives/{directiveId}` |
| Relinquish or end delegation ([17.6](#176-ending-a-delegation)) | Governance | DELETE | `/v2/delegations/{delegationId}`, with a delegate's Management Client token, or the Context Subject's for an appointed delegation |

Where the caller is a Context Client, `{entryId}` in a path is the entry's `ref` ([7.4](#74-disclosures-to-context-clients)).

A request to a governance endpoint from anything other than a Management Client acting for the Authorizing Principal, or under the Delegated Authorization Profile for the Context Subject or a delegate ([17](#17-delegated-authorization-profile)), MUST fail with not authorized ([6.1.9](#619-governance-operations)).

## 9.3 General Requirements

All requests MUST include a Bearer token in the Authorization header. Successful responses are `application/ld+json`. Error responses are `application/problem+json` ([9.7](#97-errors)).

**Protocol version.** Every response, including error responses and responses with no body, MUST carry an `HCP-Version` header whose value matches the `hcp_version` published in the implementation's discovery document. Responses do not carry an `hcp_version` member in the body.

Clients MAY send an `HCP-Version` request header naming the protocol version they expect. An implementation that does not support the requested version MUST respond with unsupported version ([9.7](#97-errors)), and MUST NOT silently serve a different version.

## 9.4 Operations

### 9.4.1 Query

`POST /v2/entries/query`. The request body carries the fields in 5.2.1:

**Request: Context Client → HCP Provider (HTTP)**

    POST /v2/entries/query HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    {
      "query": "footwear constraints for hiking",
      "categories": ["health_context"],
      "purpose": "https://purposes.example/product-recommendation",
      "purposeDescription": "Choosing hiking boots",
      "maxEntries": 5
    }

`maxEntries` defaults to 5 and is subject to the ceiling in 7.2.

Response (200):

**Response: HCP Provider → Context Client (HTTP)**

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "entries": [ ],
      "retrievalId": "urn:uuid:3f2c8a1e-6b0d-4e7a-9c55-1d2e3f4a5b6c",
      "minimization": { "method": "lexical" },
      "categoriesSearched": ["health_context"],
      "directives": [ ],
      "timestamp": "2026-10-27T13:02:12Z"
    }

Each item in `entries` is a disclosure where the caller is a Context Client ([7.4](#74-disclosures-to-context-clients)); 9.4.2 shows one.

### 9.4.2 Get Entry

`GET /v2/entries/{entryId}`, with the query parameters `purpose` (required, a purpose code), `purposeDescription` (optional), and `version` (optional), as defined in 5.2.2. Where the caller is a Context Client, the path segment is the entry's `ref` ([7.4](#74-disclosures-to-context-clients)); for a Management Client it is the entry's `id`. The same holds for every path below that names an entry.

A Context Client asks for the entry by its `ref`:

**Request: Context Client → HCP Provider (HTTP)**

    GET /v2/entries/r_8Jq2vNw4TzL0?purpose=https%3A%2F%2Fpurposes.example%2Fproduct-recommendation HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…

Response (200), shown for a General Context entry disclosed to a Context Client ([7.4](#74-disclosures-to-context-clients)):

**Response: HCP Provider → Context Client (HTTP)**

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "entry": {
        "ref": "r_8Jq2vNw4TzL0",
        "version": 2,
        "content": {
          "profile": "https://hcp.example/spec/profiles/general-context/2.0",
          "value": "I need wide-toe-box shoes with arch support."
        },
        "evidence": [],
        "assertion": { "declarationType": "person-declared", "confidence": null, "validUntil": null },
        "classification": { "categories": ["health_context"], "dimension": "footwear_support" },
        "standing": { "assurance": "authenticated", "confirmed": false },
        "useUntil": "2026-10-27T14:02:12Z"
      },
      "retrievalId": "urn:uuid:9a4b6c8d-2e1f-4b3a-8c7d-6e5f4a3b2c1d",
      "minimization": { "method": "none" },
      "timestamp": "2026-10-27T13:02:12Z"
    }

`health_context` has a default sensitivity of High, so this copy is usable for at most 24 hours ([7.6](#76-use-until)).

### 9.4.3 Create

`POST /v2/entries`. The request body is an entry in the form specified in 4.2, carrying the request fields in 5.2.3 and omitting the fields the HCP Provider assigns. Response (201): the created entry with provider-assigned fields populated.

### 9.4.4 Revise

`POST /v2/entries/{entryId}/revisions`. A revision is a new version, created as a subordinate resource of the entry. Request body:

**Request: Context Client → HCP Provider (HTTP)**

    POST /v2/entries/r_8Jq2vNw4TzL0/revisions HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    {
      "expectedVersion": 2,
      "content": {
        "profile": "https://hcp.example/spec/profiles/general-context/2.0",
        "value": "I require high arch support and wide toe box in footwear.",
        "language": "en"
      },
      "reason": "Correction by the Context Subject during conversation"
    }

The body MAY also carry the optional fields in 5.2.4. Response (201): the revised entry, with `record.version` incremented by 1. The entry's `id` is unchanged by a revision. Where `expectedVersion` is not the current version, the response is version conflict ([9.7](#97-errors)).

### 9.4.5 Withdraw and Hard Delete

`DELETE /v2/entries/{entryId}` withdraws an entry ([5.2.5](#525-withdraw)). With the query parameter `hardDelete=true` it hard-deletes the entry instead ([5.4.2](#542-hard-deletion)), which only a Management Client may do ([6.1.9](#619-governance-operations)).

The result names the entry as the caller named it ([5.2.5](#525-withdraw)): a Context Client names it by its `ref` and receives the `ref` back, never the `id`. A Management Client withdraws an entry by its `id`:

**Request: Management Client → HCP Provider (HTTP)**

    DELETE /v2/entries/urn:uuid:7d1e4b2a-0c9f-4a61-8e3d-5b6a7c8d9e0f HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…

Response (200):

**Response: HCP Provider → Management Client (HTTP)**

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "entryId": "urn:uuid:7d1e4b2a-0c9f-4a61-8e3d-5b6a7c8d9e0f",
      "status": "deleted",
      "hardDeleted": false,
      "timestamp": "2026-10-27T15:40:00Z"
    }

### 9.4.6 Grants

`GET /v2/grants` returns grant objects ([6.1.5](#615-grant-representation)). Access is scoped by caller:

- Called by a Management Client acting for the Authorizing Principal, it returns all grants. An optional `status` query parameter filters by status; the default is `active`.
- Called with a Context Client's bearer token, it returns only the grant under which that token was issued.

Responses MAY be paginated per 9.5.

`DELETE /v2/grants/{grantId}` revokes a grant ([6.2](#62-revocation)). Called by a Management Client, it revokes any grant for the instance. Called with a Context Client's bearer token, it relinquishes the grant under which that token was issued ([5.2.7](#527-relinquish-own-grant)); naming any other grant fails with not authorized. Response (204), with no body, in either case.

### 9.4.7 Audit Log

`GET /v2/audit` returns the audit log ([8.3](#83-access-to-the-audit-log)). It MUST support cursor-based pagination ([9.5](#95-pagination)).

### 9.4.8 Export

`GET /v2/export` returns an export ([5.4.1](#541-export)). The export options map to query parameters:

| Parameter | Required | Values | Export option ([5.4.1](#541-export)) |
|-----------|----------|----------------------------------|----------------------------------|
| `include` | Optional | Comma-separated: `audit`, `versions` | Including the audit log; including versions |
| `exclude` | Optional | Comma-separated: `deleted` | Excluding deleted entries |

The `context.exported` event records the parameters used in detail.

### 9.4.9 Confirm or Reject

`POST /v2/entries/{entryId}/confirmation`, where `disposition` is `confirmed` or `rejected`:

**Request: Management Client → HCP Provider (HTTP)**

    POST /v2/entries/urn:uuid:7d1e4b2a-0c9f-4a61-8e3d-5b6a7c8d9e0f/confirmation HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    { "disposition": "confirmed", "expectedVersion": 2 }

The HCP Provider appends the confirmation record to the entry's current version ([3.8](#38-confirmation)) and applies the status transitions in 4.7.3. Response (200): the entry.

### 9.4.10 Change Categories and Restrict Purposes

`PUT /v2/entries/{entryId}/categories`:

**Request: Management Client → HCP Provider (HTTP)**

    PUT /v2/entries/urn:uuid:7d1e4b2a-0c9f-4a61-8e3d-5b6a7c8d9e0f/categories HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    { "categories": ["work_context", "health_context"], "expectedVersion": 2 }

Response (200): the entry, with its new categories. The change is recorded as in 4.2.1.

`PUT /v2/entries/{entryId}/purposes`:

**Request: Management Client → HCP Provider (HTTP)**

    PUT /v2/entries/urn:uuid:7d1e4b2a-0c9f-4a61-8e3d-5b6a7c8d9e0f/purposes HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    { "permittedPurposes": ["https://purposes.example/care-coordination"], "expectedVersion": 3 }

A `permittedPurposes` of null removes the Authorizing Principal's narrowing. Response (200): the entry. The change is recorded as in 4.2.6.

### 9.4.11 Import

`POST /v2/import`. The request body carries the fields in 5.4.3:

**Request: Management Client → HCP Provider (HTTP)**

    POST /v2/import HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    {
      "export": { },
      "dryRun": true,
      "categoryMap": { "https://categories.example/fitness": "general_preferences" }
    }

Response (200): one outcome per entry.

**Response: HCP Provider → Management Client (HTTP)**

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "outcomes": [
        { "id": "urn:uuid:0b6f3a2e-9d4c-4e18-a7b5-c2d1e0f9a8b7", "outcome": "converted" },
        { "id": "urn:uuid:5c8e1d7a-4f2b-4c90-b3a6-e9d8c7b6a5f4", "outcome": "rejected", "reason": "id held with different content" }
      ],
      "dryRun": true
    }

### 9.4.12 Disclosure Summary

`GET /v2/disclosures`, with the optional query parameters `client`, `category`, `from`, and `to`. Response (200): a `clients` array, one member per HCP Client, each carrying the members in 8.6. It MAY be paginated per 9.5.

### 9.4.13 Delegations

An implementation conforming to the Delegated Authorization Profile ([17](#17-delegated-authorization-profile)) exposes:

- `GET /v2/delegations`. Response (200): a `delegations` array of delegation objects ([17.2](#172-delegations)), with ended ones where `status=ended` is asked. A Management Client acting for the Context Subject receives every delegation for them; one acting for a delegate receives only the delegations naming that delegate.
- `DELETE /v2/delegations/{delegationId}`, by a Management Client acting for the delegate it names: relinquishes the delegation ([17.6](#176-ending-a-delegation)). Where the delegation's basis is `appointed`, a Management Client acting for the Context Subject may also call it, which ends the delegation with reason `ended-by-subject`. Response (204). Any other caller receives not authorized.

A delegation is established by the Authorization Service, not through this binding ([17.2](#172-delegations)).

### 9.4.14 Standing Rules

- `GET /v2/rules`. Response (200): a `rules` array of standing rules ([6.3](#63-standing-rules)).
- `POST /v2/rules`, with `operators`, `requires`, or both, and optionally `categories`. Response (201): the rule, with its `ruleId` and `createdAt`. The HCP Provider sets `effect` to `deny`.
- `DELETE /v2/rules/{ruleId}`. Response (204).

Each is called by a Management Client acting for the Context Subject, or, under the Delegated Authorization Profile, for a delegate within the delegation's scope ([6.3](#63-standing-rules)). A delegate's `DELETE` succeeds only for a rule they set. Any other caller receives not authorized.

### 9.4.15 Directives

Directives are set and removed as standing rules are, at their own endpoint:

- `GET /v2/directives`. Response (200): a `directives` array ([6.4](#64-directives)).
- `POST /v2/directives`, with `action`, `effect`, `text`, and optionally `categories` and `operators`. Response (201): the directive, with its `directiveId` and `createdAt`.
- `DELETE /v2/directives/{directiveId}`. Response (204).

The callers allowed are those for standing rules ([9.4.14](#9414-standing-rules)).

### 9.4.16 Onward Sharing

`POST /v2/shares`, with a Context Client's token for the grant under which it shared, reports one share ([5.2.8](#528-report-onward-sharing)). Here the client told an outfitter the person's shoe size, from a `general_preferences` entry:

**Request: Context Client → HCP Provider (HTTP)**

    POST /v2/shares HTTP/1.1
    Host: provider.example
    Authorization: Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ…
    Content-Type: application/json

    {
      "recipient": { "domain": "outfitters.example", "name": "Example Outfitters" },
      "refs": ["r_Q4mx7Lp2Wd9s"],
      "purpose": "https://purposes.example/product-recommendation",
      "sharedAt": "2026-10-27T13:10:00Z"
    }

Response (204), with no body:

**Response: HCP Provider → Context Client (HTTP)**

    HTTP/1.1 204 No Content

A share the grant did not allow responds 403 with the not-authorized problem type ([9.7](#97-errors)); it is recorded all the same.

## 9.5 Pagination

`GET /v2/audit` MUST support cursor-based pagination:

| Parameter | Location | Description |
|-----------|-----------------|------------------------------------------------|
| `cursor` | Query, optional | Opaque continuation token from a prior response |
| `limit` | Query, optional | Maximum events in this page |

Responses carry a `nextCursor` member holding an opaque token, or null when the result set is exhausted. Cursors MUST be opaque to clients, MUST NOT encode credentials or entry content, and MUST remain valid for at least 300 seconds.

A bare sequence number or offset does not satisfy the opacity requirement. A pilot implementer asked whether a plain incrementing integer may serve as a cursor (Turn.io); it may not, because a monotonic cursor discloses the total number of audit events to any client that receives one, which is itself information about the volume of a person's activity. An opaque cursor may be an encrypted or signed offset, or a server-side handle; what it MUST NOT be is a value from which a client can read the size or position of the underlying set.

`POST /v2/entries/query` is not paginated ([7.2](#72-quantity-bound)).

## 9.6 Idempotency

`POST /v2/entries` and `POST /v2/entries/{entryId}/revisions` MUST accept an `Idempotency-Key` request header, and clients SHOULD send one.

- Implementations MUST retain a key and its associated response for at least 24 hours.
- A repeated request bearing a previously seen key and an identical body MUST return the original response — including the original entry `id` and `record.version` — without performing the operation a second time.
- A repeated key accompanied by a differing body MUST be rejected with conflict ([9.7](#97-errors)).
- A replayed request MUST NOT append a second audit event.

`DELETE /v2/entries/{entryId}` SHOULD accept the header. Repeated deletion is harmless to entry state but appends a duplicate audit event without it.

A revision needs a key as much as a create. Without one, a retried revision whose first attempt succeeded fails with version conflict ([5.2.4](#524-revise)), and the client cannot tell its own success from someone else's revision.

## 9.7 Errors

All error responses MUST use `application/problem+json` per RFC 9457, carrying at minimum `type`, `title`, `status`, and `detail`. Implementations MAY add extension members.

Each Core error ([5.5](#55-errors)) maps to one status. Its problem type is its code, relative to https://hcp.example/problems/:

| Core error ([5.5](#55-errors)) | Status | Problem type |
|-----------------------|--------|------------------------|
| invalid request | 422 | `malformed-request` |
| unauthenticated | 401 | `invalid-token` |
| not authorized | 403 | `scope-denied` |
| conflict | 409 | `idempotency-conflict` |
| version conflict | 409 | `version-conflict` |
| credential invalid | 422 | `credential-invalid` |
| subject unavailable | 503 | `subject-unavailable` |
| rate limited | 429 | `rate-limited` |
| unsupported version | 400 | `unsupported-version` |

A `scope-denied` response MUST NOT disclose whether the requested entry exists ([5.2.2](#522-get-entry)).

## 9.8 Rate Limiting

A 429 response MUST include a `Retry-After` header. Implementations SHOULD publish their rate limit policy in the discovery document ([19](#19-discovery-document)).

Rate limiting MUST NOT be applied to `DELETE /v2/grants/{grantId}` ([6.2.1](#621-revocation-by-the-authorizing-principal)).

## 9.9 Revocation Notification Delivery

Where an HCP Client has registered a notification endpoint, the notification required by 6.2.2 is a Security Event Token (SET, RFC 8417), delivered to that endpoint by push delivery (RFC 8935).

**The token.** The provider delivers the SET to the client's notification endpoint:

**Notification: HCP Provider → HCP Client (HTTP push, RFC 8935)**

    POST /hcp/events HTTP/1.1
    Host: client.example
    Content-Type: application/secevent+jwt

    eyJhbGciOiJFUzI1NiIsImtpZCI6InByb3ZpZGVyLTIwMjYifQ.eyJpc3MiOi…

Its payload, decoded:

**Notification payload, decoded: HCP Provider → HCP Client**

    {
      "iss": "https://provider.example",
      "aud": "https://client.example",
      "jti": "urn:uuid:c4d5e6f7-a8b9-4c0d-9e1f-2a3b4c5d6e7f",
      "iat": 1793106300,
      "events": {
        "https://hcp.example/spec/events/grant-revoked": {
          "grantId": "urn:uuid:1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
          "revokedAt": "2026-10-27T13:05:00Z"
        }
      }
    }

- `iss` is the HCP Provider, `aud` the HCP Client being notified, and `iat` the time the token was issued.
- `jti` identifies the notification. It is identical on every delivery attempt, and receiving clients use it to deduplicate.
- The event type is `https://hcp.example/spec/events/grant-revoked`. It names the grant revoked and when.

**Signing.** The SET MUST be signed with JWS using an asymmetric algorithm, with a key published in the JSON Web Key Set at the discovery document's `jwks_uri` ([19](#19-discovery-document)). Receiving clients MUST verify the signature, and SHOULD reject a token whose `iat` differs from local time by more than 300 seconds.

**Delivery.** Delivery is an HTTP POST of the SET, with media type `application/secevent+jwt`, as RFC 8935 specifies. The client acknowledges receipt with 202 Accepted, or rejects the token with 400 and an RFC 8935 error code.

**Retry.** Delivery MUST be retried on connection failure and on any response other than 202 or 400, with exponential backoff, for at least 5 attempts over at least 1 hour before delivery is abandoned. Every attempt MUST carry the same token. A 400 response ends delivery and is recorded as abandoned, with the client's error code.

Auditing, abuse controls, and independence from revocation are Core requirements ([6.2.3](#623-revocation-notification), [6.2.4](#624-when-notification-fails)).
# 10. MCP Binding

## 10.1 Scope

This section maps the Core context operations ([5.2](#52-context-operations)) and errors ([5.5](#55-errors)) onto the Model Context Protocol. It is identified as https://hcp.example/spec/bindings/mcp/2.0 ([1.7](#17-conformance-identifiers)). It targets MCP version 2026-07-28 and relies on no session state: every request carries its own authorization, as that version of MCP requires.

The MCP Binding carries context operations only. It carries no governance operation ([1.6](#16-context-plane-and-governance-plane), [6.1.9](#619-governance-operations)): grant management, the audit log, export, hard deletion, confirmation, and category changes are reached through the HTTP Binding ([9](#9-http-binding)) or the person-facing capabilities required by 18.

The MCP Binding runs over either of MCP's transports:

- **stdio.** Qualifies for the First-Party package only ([18](#18-conformance-claims-and-packages)). Credentials are obtained from the environment, as MCP specifies for stdio.
- **Streamable HTTP.** Required for the Agent Interop package ([18](#18-conformance-claims-and-packages)). MCP's authorization, in which the server is an OAuth resource server, is mapped onto the OAuth Interop Profile ([13](#13-oauth-interop-profile)).

## 10.2 Identifying an HCP Server

An HCP Provider exposing the MCP Binding identifies itself in its `server/discover` response, through MCP's `capabilities.extensions` field, under the extension identifier `example.hcp/hcp`. The settings object points to the HCP discovery document and repeats its conformance claims:

**Response fragment: HCP Provider → MCP host (server/discover)**

    "capabilities": {
      "tools": {},
      "extensions": {
        "example.hcp/hcp": {
          "discovery": "https://provider.example/.well-known/hcp-configuration",
          "conformsTo": [
            "https://hcp.example/spec/core/2.0",
            "https://hcp.example/spec/bindings/mcp/2.0"
          ]
        }
      }
    }

The extension identifier uses the placeholder namespace ([1.7](#17-conformance-identifiers)) and will change with it. A client determines the HCP protocol version from the discovery document ([19](#19-discovery-document)). Tool results do not carry it.

This replaces v1's MCP server manifest (v1 Appendix B) and the discovery document's `mcp_manifest_endpoint`, which duplicated what `server/discover` and `tools/list` already provide.

## 10.3 Tools

| Tool | Core operation |
|---------------------------|----------------------|
| `hcp_queryContext` | Query ([5.2.1](#521-query)) |
| `hcp_getEntry` | Get entry ([5.2.2](#522-get-entry)) |
| `hcp_createEntry` | Create ([5.2.3](#523-create)) |
| `hcp_reviseEntry` | Revise ([5.2.4](#524-revise)) |
| `hcp_withdrawEntry` | Withdraw ([5.2.5](#525-withdraw)) |
| `hcp_reportSharing` | Report onward sharing ([5.2.8](#528-report-onward-sharing)) |

Requirements for every tool:

- Each tool's `inputSchema` and `outputSchema` reference the Core schemas for its operation ([Appendix A](#appendix-a-registries-and-published-artifacts)). A tool MAY expose a subset of the operation's fields ([1.5](#15-bindings-and-transports)).
- Results are returned in `structuredContent`, conforming to the tool's `outputSchema`. For compatibility, the serialized JSON is also returned in a text content block.
- An HCP Provider MAY limit the tools returned by `tools/list` to those the presented grant permits. MCP allows the list to vary by the authorization on the request.
- A tool call is authorized by the grant presented with it, and the HCP Provider enforces that grant independently of any decision by the MCP host ([3.11](#311-actor-invariants), invariant 10).

The schemas below are the HCP-specific part of each tool definition.

### 10.3.1 hcp_queryContext

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_queryContext",
      "description": "Retrieve minimal, relevant entries from the person's HCP instance for a stated purpose.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string",
            "description": "Natural language query describing the context or task." },
          "categories": { "type": "array", "items": { "type": "string" },
            "description": "Optional. Categories to search. Omitted means every category the grant can read for the purpose." },
          "purpose": { "type": "string", "format": "uri",
            "description": "Purpose code: one of the purposes the person approved in the grant." },
          "purposeDescription": { "type": "string",
            "description": "Optional. Plain language statement of the task. Logged to audit trail." },
          "maxEntries": { "type": "integer", "default": 5,
            "description": "Maximum entries to return. Default: 5. Maximum: 20." }
        },
        "required": ["query", "purpose"]
      }
    }

The result carries the fields in 5.2.1, including `categoriesSearched` and `directives` ([6.4](#64-directives)). Each entry is a disclosure ([7.4](#74-disclosures-to-context-clients)), named by its `ref`; the model receives no stable entry identifier.

### 10.3.2 hcp_getEntry

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_getEntry",
      "description": "Retrieve one entry from the person's HCP instance by identifier, for a stated purpose.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "ref": { "type": "string", "description": "The entry's ref, as disclosed under this grant." },
          "purpose": { "type": "string", "format": "uri",
            "description": "Purpose code: one of the purposes the person approved in the grant." },
          "purposeDescription": { "type": "string",
            "description": "Optional. Plain language statement of the task. Logged to audit trail." },
          "version": { "type": "integer",
            "description": "Optional. Returns the specified version rather than the current one." }
        },
        "required": ["ref", "purpose"]
      }
    }

This tool is new in v2. v1 offered single-entry retrieval over HTTP only.

### 10.3.3 hcp_createEntry

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_createEntry",
      "description": "Add a new entry to the person's HCP instance.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "categories": { "type": "array", "items": { "type": "string" }, "minItems": 1, "uniqueItems": true,
            "description": "One or more category slugs or custom category URIs, each one the grant lets this client write." },
          "dimension": { "type": ["string", "null"],
            "description": "Optional. Dimension addressed by this entry, scoped within its categories." },
          "content": { "type": "string", "description": "Natural language statement." },
          "declarationType": { "type": "string", "enum": ["person-declared", "model-inferred"] },
          "confidence": { "type": ["string", "null"], "enum": ["high", "medium", "low", null],
            "description": "Required and non-null when declarationType is model-inferred; null or omitted otherwise." },
          "assertedBy": { "type": "string",
            "description": "The Context Asserter. Required when declarationType is model-inferred: identify the model, at a granularity that distinguishes versions." },
          "sourceContext": { "type": "string",
            "description": "Conversation or document ID from which this entry was derived." },
          "basis": { "type": "object",
            "properties": {
              "drawnFrom": { "type": "array", "items": { "type": "string" } },
              "task": { "type": "string" }, "setting": { "type": "string" }, "rationale": { "type": "string" } },
            "description": "Optional; recommended when declarationType is model-inferred. What this entry was drawn from. Must not identify anyone but the person, or carry any client, conversation or document identifier." },
          "permittedPurposes": { "type": "array", "items": { "type": "string", "format": "uri" },
            "description": "Optional. Purpose codes this entry may be used for." },
          "relationships": { "type": "array",
            "items": { "type": "object",
              "properties": {
                "type": { "type": "string", "enum": ["derivedFrom", "supersedes", "contradicts", "duplicates"] },
                "target": { "type": "string", "description": "The related entry's ref." } },
              "required": ["type", "target"] },
            "description": "Optional. Relationships this entry has to other entries." }
        },
        "required": ["categories", "content", "declarationType", "sourceContext"],
        "allOf": [
          {
            "if": { "properties": { "declarationType": { "const": "model-inferred" } },
                    "required": ["declarationType"] },
            "then": { "required": ["confidence", "assertedBy"],
                      "properties": { "confidence": { "type": "string", "enum": ["high", "medium", "low"] } } },
            "else": { "properties": { "confidence": { "type": "null" } } }
          }
        ]
      }
    }

| Tool field | Core field ([5.2.3](#523-create)) |
|-----------------|---------------------------------------------|
| `categories` | `classification.categories` |
| `dimension` | `classification.dimension` |
| `content` | `content.value`, with `content.profile` set to the General Context Profile ([11](#11-general-context-profile)) |
| `declarationType` | `assertion.declarationType` |
| `confidence` | `assertion.confidence` |
| `assertedBy` | `record.provenance.assertedBy.id` |
| `sourceContext` | `record.provenance.source` |
| `basis` | `assertion.basis` ([4.2.5](#425-basis)) |
| `permittedPurposes` | `assertion.permittedPurposes` ([4.2.6](#426-permitted-purposes)) |
| `relationships` | `record.relationships` ([4.2.3](#423-relationships)) |

This tool creates General Context entries only: `content` carries a natural language statement, and the tool provides no means of supplying evidence, so entries it creates carry none. Its `declarationType` enum omits `issuer-attested` as a subset of the Core operation ([1.5](#15-bindings-and-transports)). That a Context Client cannot attest on an issuer's behalf is a Core rule ([3.7](#37-statements-attributed-to-the-context-subject)), not a consequence of this tool's shape. Entries carrying a credential, and other `issuer-attested` entries, are created through the HTTP Binding ([9.4.3](#943-create)).

A write that violates the `confidence` rule in 5.2.3 is rejected with invalid request ([10.4](#104-errors)).

### 10.3.4 hcp_reviseEntry

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_reviseEntry",
      "description": "Revise an existing entry, creating a new version and preserving version history.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "ref": { "type": "string", "description": "The ref of the entry to revise." },
          "expectedVersion": { "type": "integer",
            "description": "The version this revision replaces. If the entry has since been revised, the call fails with version-conflict." },
          "content": { "type": "string", "description": "The revised statement, whole." },
          "reason": { "type": "string", "description": "Reason for the revision. Logged to audit trail." },
          "declarationType": { "type": "string", "enum": ["person-declared", "model-inferred"],
            "description": "Optional. Declaration type of the revised statement. Omitted means unchanged." },
          "confidence": { "type": ["string", "null"], "enum": ["high", "medium", "low", null] },
          "assertedBy": { "type": "string", "description": "Optional. The Context Asserter of the revised statement." },
          "sourceContext": { "type": "string" }
        },
        "required": ["ref", "expectedVersion", "content", "reason"]
      }
    }

### 10.3.5 hcp_withdrawEntry

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_withdrawEntry",
      "description": "Withdraw an entry. Withdrawn entries are hidden from agents immediately.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "ref": { "type": "string", "description": "The ref of the entry to withdraw." },
          "reason": { "type": "string", "description": "Reason for withdrawal. Logged to audit trail." }
        },
        "required": ["ref", "reason"]
      }
    }

v1's `hardDelete` parameter is removed. Hard deletion is a governance operation and is not available over MCP ([5.4.2](#542-hard-deletion)).

### 10.3.6 hcp_reportSharing

**Tool definition: HCP Provider → MCP host (`tools/list`)**

    {
      "name": "hcp_reportSharing",
      "description": "Report that you told another organization something from the person's context, as their grant allows. Every share must be reported.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "recipient": { "type": "object", "properties": { "domain": { "type": "string" }, "name": { "type": "string" } }, "required": ["domain", "name"] },
          "refs": { "type": "array", "items": { "type": "string" }, "minItems": 1, "description": "The ref of each entry you drew on." },
          "purpose": { "type": "string", "description": "The purpose code under which you shared." },
          "sharedAt": { "type": "string", "format": "date-time" }
        },
        "required": ["recipient", "refs", "purpose", "sharedAt"]
      }
    }

Under the MCP Binding the host holds the grant, so the host reports what it shared, whichever model drafted the words ([10.5](#105-who-holds-the-grant)).

## 10.4 Errors

MCP distinguishes protocol errors from tool execution errors. The MCP Binding uses them as follows:

- A request that MCP itself cannot accept — an unknown tool, or a request that fails MCP's own `tools/call` schema — is a protocol error, returned as a JSON-RPC error.
- Every Core error ([5.5](#55-errors)), including invalid request, is returned as a tool execution error, except as the two items on HTTP below state: a result with `isError: true` whose `structuredContent` carries the error's code ([5.5](#55-errors)) as `type` and a human-readable `detail`, with the same text in a text content block. Each tool's `outputSchema` admits this error object as an alternative to the operation's result.
- Over Streamable HTTP, a request with missing, invalid, or expired authorization is rejected at the HTTP layer with status 401, as MCP's authorization requires. This is how the binding reports unauthenticated.
- Over Streamable HTTP, a not authorized denial that follows from the request alone — a category, action, or purpose the grant does not cover — is rejected at the HTTP layer with status 403 and a `WWW-Authenticate` challenge with error `insufficient_scope`, as MCP's authorization recommends. The challenge's `scope` names the scopes the request needs. A challenge cannot name a purpose, so where the denial is for purpose alone, its `error_description` names the purpose code the request used. The MCP host, which holds the grant ([10.5](#105-who-holds-the-grant)), can then ask the Authorizing Principal for a new or wider grant ([6.1.6](#616-authorization-is-distinct-from-authentication)), requesting the purpose with authorization details ([13.3](#133-grant-request)).
- A not authorized denial that depends on what is stored — an entry outside the grant, or one that does not exist — is returned as a tool execution error carrying `scope-denied`. It never produces a challenge, because a challenge would show that the entry exists ([5.2.2](#522-get-entry)).

A tool execution error carrying a Core error:

**Tool result: HCP Provider → MCP host (`tools/call`)**

    {
      "isError": true,
      "structuredContent": { "type": "scope-denied", "detail": "Entry not available under this grant." },
      "content": [ { "type": "text", "text": "scope-denied: Entry not available under this grant." } ]
    }

A not authorized result MUST NOT disclose whether a requested entry exists ([5.2.2](#522-get-entry)).

Over stdio there is no HTTP layer, and every not authorized denial is a tool execution error.

The split follows who can act on the denial. A 403 reaches the host, which holds the grant and can ask the person for more; a tool execution error reaches the model, which can only work within what it has.

## 10.5 Who Holds the Grant

A grant authorizes an HCP Client ([6.1.8](#618-client-attribution-and-authority)). Under the MCP Binding:

- The grant is held by the component that presents credentials: the MCP host or its HCP integration. It is never held by the model ([3.11](#311-actor-invariants), invariants 6 and 9).
- The access token MUST NOT enter the model's context, and MUST NOT be returned as tool content ([3.11](#311-actor-invariants), invariant 14).
- A host's permission to call a tool does not substitute for the grant, and a grant does not oblige a host to call a tool ([3.11](#311-actor-invariants), invariant 10).
- Where the client claims to follow directives, the host applies them ([6.4](#64-directives)). Placing a directive in the model's context is not following it.
- A local stdio bridge to a remote HCP Provider is an HCP Client in its own right. It holds the token, calls the provider over the HTTP Binding, has its own Client Operator ([3.2.8](#328-client-operator-and-provider-operator)), and is bound by every rule for HCP Clients, including onward disclosure ([3.12](#312-onward-disclosure)).
# Part III — Profiles

A profile adds stricter rules to Core for a domain, a security posture, an evidence type, or a deployment pattern ([1.2](#12-layers)). Each profile in this Part has its own conformance identifier ([1.7](#17-conformance-identifiers)), and an implementation conforms to a profile only by listing that identifier in `conformsTo` ([19](#19-discovery-document)). Claiming a profile requires conforming to Core. Which profiles each package requires is set out in 18.

| Profile | Required by |
|-------------------------------------|----------------------------------------------------------|
| General Context ([11](#11-general-context-profile)) | Every package |
| First-Party Authorization ([12](#12-first-party-authorization-profile)) | The First-Party package |
| OAuth Interop ([13](#13-oauth-interop-profile)) | The Provider Interop and Agent Interop packages |
| VC Evidence ([14](#14-vc-evidence-profile)) | No package; adds to any package |
| Memory Manager ([15](#15-memory-manager-profile)) | Any HCP Provider that accepts `model-inferred` entries ([4.7](#47-conflicts)) |
| Health Context ([16.2](#162-health-context-profile)) | Any HCP Provider that accepts `issuer-attested` entries in `health_context` ([16.1](#161-scope)) |
| Education Context ([16.4](#164-education-context-profile)) | Any HCP Provider that accepts `issuer-attested` entries in `education_learner_profile` ([16.1](#161-scope)) |
| Delegated Authorization ([17](#17-delegated-authorization-profile)) | Any implementation that issues a grant authorized by a party other than the Context Subject ([17.1](#171-scope)) |

# 11. General Context Profile

## 11.1 Scope

This profile defines the content profile for statements: structured natural language, or a structured object, in the entry defined in 4.2. It is identified as https://hcp.example/spec/profiles/general-context/2.0 ([1.7](#17-conformance-identifiers)), and it is required in every package ([18](#18-conformance-claims-and-packages)). The same identifier is the value of `content.profile` for an entry whose content has the shape defined here.

An implementation conforming to this profile MUST accept and emit entries whose `content` has the shape defined in this section. Validation is JSON Schema validation against the published schema ([4.1.1](#411-processing-requirements), [Appendix A](#appendix-a-registries-and-published-artifacts)).

## 11.2 Content

**Template: the content member, General Context Profile**

    "content": {
      "profile": "https://hcp.example/spec/profiles/general-context/2.0",
      "value": "{natural language statement or structured object}",
      "language": "{BCP 47 language tag | null}"
    }

| Field | Required | Set by | Description |
|------------------------------|-------------|--------------------------|----------------------------------------------------|
| `content.profile` | Yes | HCP Client | This profile's identifier |
| `content.value` | Yes | HCP Client | String or Object. The statement. |
| `content.language` | No | HCP Client | The language of a string `value` |

Requirements:

- An entry whose `assertion.validUntil` has passed is `expired` ([4.2.4](#424-status)). It is not disclosed to a Context Client, and it remains visible to the Context Subject.
- An entry with this content profile MAY carry evidence items whose `role` is `supports` ([4.2.2](#422-evidence)). It carries none whose `role` is `content`.

## 11.3 Relationship

`subject.relationship` is reserved. It describes the relationship between the Context Subject identified in `subject.id` and the party who declared or administers the entry, where these differ. This specification assigns no behavior to this field.

The field is reserved for forward compatibility. Implementations MUST NOT interpret its presence, absence, or value as conferring, extending, or limiting authorization. Delegated authority is recorded on a delegation under the Delegated Authorization Profile ([17.2](#172-delegations)), not in this field. The field exists so that deployments that record who declared or administers an entry do so in one shape rather than inventing one per deployment. No vocabulary is registered for it.

## 11.4 Example

An entry with this content profile as the Context Subject sees it, through export or a Management Client. A Context Client receives the same entry with the fields in 7.4 omitted; 9.4.2 shows that form.

**Response body: HCP Provider → Management Client (an entry, as export or a Management Client reads it)**

    {
      "@context": ["https://hcp.example/contexts/v2"],
      "schema": "https://hcp.example/spec/entry/2.0",
      "id": "urn:uuid:7f3a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "type": ["ContextEntry"],
      "subject": { "id": "did:example:subject-a3f9", "relationship": null },
      "content": {
        "profile": "https://hcp.example/spec/profiles/general-context/2.0",
        "value": "I require high arch support in footwear due to a diagnosed condition.",
        "language": "en"
      },
      "assertion": {
        "declarationType": "person-declared",
        "confidence": null,
        "validUntil": null
      },
      "classification": {
        "categories": ["health_context"],
        "dimension": "footwear_support"
      },
      "evidence": [],
      "record": {
        "status": "active",
        "version": 1,
        "provenance": {
          "assertedBy": { "id": "did:example:subject-a3f9", "assurance": "unverified" },
          "assertedAt": "2026-06-15T10:30:00Z",
          "source": "conversation-id:abc123",
          "submittedByClient": {
            "id": "https://assistant.example/clients/hcp",
            "name": "Example Assistant",
            "operator": { "id": "https://assistant.example", "name": "Example Assistant Co." }
          },
          "authorizedUnder": "urn:uuid:5b1d9e3a-2c47-4f80-9a61-0e8c7d2b4f13",
          "recordedByProvider": "https://provider.example",
          "recordedAt": "2026-06-15T10:30:02Z",
          "confirmations": [
            {
              "disposition": "confirmed",
              "confirmedBy": { "id": "did:example:subject-a3f9" },
              "confirmedAt": "2026-06-16T08:12:40Z"
            }
          ]
        },
        "relationships": []
      }
    }

The assistant submitted the statement as `person-declared`, so the provider recorded assurance `unverified` ([3.7](#37-statements-attributed-to-the-context-subject)). The Context Subject later confirmed it through a Management Client, which gives the entry standing in a conflict ([3.8](#38-confirmation)). In v1 this entry carried `userVerified: true`; that field is removed ([3.5](#35-provenance-layers)), and a v1 entry carrying it is converted as 4.3 sets out.
# 12. First-Party Authorization Profile

## 12.1 Scope

This profile permits grants to be obtained through an authenticated channel other than OAuth 2.0, for HCP Clients operated by the Provider Operator. It is identified as https://hcp.example/spec/profiles/first-party-authorization/2.0 ([1.7](#17-conformance-identifiers)), and it is the authorization profile of the First-Party package ([18](#18-conformance-claims-and-packages)). It replaces v1's `"authorization_profile": "first-party"`.

An implementation claiming this profile accepts only first-party clients: HCP Clients whose Client Operator is the Provider Operator. An implementation that accepts, or holds itself out as accepting, authorization requests from any HCP Client it does not itself operate MUST claim the OAuth Interop Profile instead ([13](#13-oauth-interop-profile), [18](#18-conformance-claims-and-packages)).

## 12.2 Requirements

An implementation claiming this profile:

- MUST satisfy 6.1.6 in full;
- MUST list this profile's identifier in `conformsTo`, and MUST NOT list the OAuth Interop Profile's ([19](#19-discovery-document));
- is not eligible for the Provider Interop or Agent Interop packages ([18](#18-conformance-claims-and-packages)).

The authenticated channel may be an in-application session, a messaging interface, or an LLM-mediated dialogue ([6.1.6](#616-authorization-is-distinct-from-authentication)). This specification does not mandate a wire-level request format for it; the channel supplies its own mechanism for a client to name the categories and actions it needs. What is mandated is the outcome specified in 6.1.6 and 6.1.7: before the Authorizing Principal acts, they MUST be told what 6.1.6 lists, and the act MUST be recorded as a `grant.issued` event. The grant is recorded as 6.1.5 specifies, with its `access` and the purposes approved; where the client names no purpose, the Authorizing Principal chooses one in the channel ([6.1.5.2](#6152-purposes)).

Where an implementation claiming this profile issues access or refresh tokens, their lifetimes MUST NOT exceed the maxima in 13.4.

The `conformsTo` declaration is authoritative. A client finding this profile's identifier in a discovery document can determine that it cannot obtain authorization from that implementation, whatever is claimed for the implementation elsewhere. This specification places requirements on what an implementation publishes, not on how it is described.

A conformance suite still needs a means to obtain a credential and trigger grant creation from an implementation claiming this profile. The test hook for this purpose is described in 20.

## 12.3 On the Deviation (Informative)

First-party-only conformance forgoes cross-implementation portability, which is the principal purpose of this specification. It is a defensible posture for a pilot validating other aspects of the protocol under real constraints. It is not a durable end state, and an implementation adopting it should expect to implement the OAuth Interop Profile before its context is expected to move to another provider.
# 13. OAuth Interop Profile

## 13.1 Scope

This profile obtains and represents grants using OAuth 2.0 (RFC 6749). It is identified as https://hcp.example/spec/profiles/oauth-interop/2.0 ([1.7](#17-conformance-identifiers)), and it is required for the Provider Interop and Agent Interop packages ([18](#18-conformance-claims-and-packages)). It replaces v1's `"authorization_profile": "oauth2"`.

Under this profile the Authorization Service is an OAuth 2.0 authorization server and the HCP Provider is an OAuth 2.0 resource server ([3.2.5](#325-authorization-service)). Each grant ([6.1.5](#615-grant-representation)) corresponds to an OAuth authorization, and an access token is a credential representing it ([3.1](#31-roles-entities-and-components)). The grant semantics in 6 are unchanged by this profile; OAuth is the mechanism by which they are obtained. The profile follows the OAuth 2.0 Security Best Current Practice (RFC 9700), as 13.6 sets out.

## 13.2 Grant Types

| Grant Type | Use Case |
|---------------------------------------|----------------------------------------------------------------------|
| Authorization Code + PKCE | User-facing applications and assistants |
| Device Authorization Grant (RFC 8628) | Clients on input-constrained devices, where a redirect is impractical |
| Client Credentials | Trusted institutional integrations (e.g., school SIS); each token is bound to one grant the Authorizing Principal pre-authorized |

Client Credentials ordinarily represents a client acting for itself, and an HCP instance belongs to one person. The grant type is therefore bound to a person's grant:

- The Authorizing Principal pre-authorizes the integration through an interaction meeting 6.1.6. That creates an ordinary grant ([6.1.5](#615-grant-representation)), visible and revocable like any other, which fixes the Context Subject, the Authorizing Principal, and the other actors in 3.4.
- Each token request names that grant in an `authorization_details` element of the HCP type, by its `grantId`. The token issued is valid for that grant only, and so for one Context Subject.
- A Client Credentials token not bound to a grant MUST be rejected by the HCP Provider with unauthenticated ([5.5](#55-errors)).
- An integration serving many people holds one grant for each of them, and requests each token under the grant of the person it serves.

## 13.3 Grant Request

The request is the standard OAuth 2.0 authorization request for the chosen grant type (RFC 6749 §4.1.1 for Authorization Code, RFC 8628 §3.1 for Device Authorization). It names what is asked for in either of two ways:

- **Authorization details** (RFC 9396). An `authorization_details` parameter carrying one or more details of type `https://hcp.example/spec/authorization/context-access`, each with the members of a detail in 6.1.5: `actions`, `categories`, `purposes`, and optionally `narrowedTo`. The Authorization Service MUST accept this form.
- **Scope strings.** A `scope` parameter carrying scopes named per 6.1.1. The Authorization Service MUST read each scope as a detail for that category and action, with no narrowing, and MUST ask the Authorizing Principal to choose the purposes before approving ([6.1.5.2](#6152-purposes)).

The request MUST carry a `resource` parameter (RFC 8707) naming the HCP Provider, and tokens are issued for that resource only. The token response carries the authorization details granted, as RFC 9396 specifies, so the client learns the purposes approved. The outcome required by 6.1.7 applies.

## 13.4 Token Lifetime

| Token Type | Default Lifetime | Maximum Lifetime |
|----------------------------------|-----------------------------------------|----------------------|
| Access token | 1 hour | 24 hours |
| Refresh token (persistent grant) | 30 days | 1 year |
| Refresh token (temporary grant) | Bounded by the grant's absolute expiry | 24 hours |

Tokens issued under this profile MUST NOT exceed the maximum lifetimes above. The absolute expiry of a temporary grant is a Core bound ([6.1.3](#613-grant-duration)), and a refresh token MUST NOT be honored after it, whatever the refresh token's own lifetime ([6.1.4](#614-grant-distinction-temporary-vs-persistent)).

## 13.5 MCP Authorization

Where the MCP Binding runs over Streamable HTTP ([10.1](#101-scope)), MCP's authorization is mapped onto this profile:

- The HCP Provider, as MCP server, is the OAuth resource server, and the Authorization Service is the authorization server MCP's authorization names.
- The scopes requested are those named per 6.1.1, and a grant obtained this way is a grant in every respect of 6.
- The access token is held by the component that presents it ([10.5](#105-who-holds-the-grant)).

- The HCP Provider publishes OAuth 2.0 Protected Resource Metadata (RFC 9728), naming its Authorization Service, as MCP's authorization relies on. The same document serves clients of the HTTP Binding, and the discovery document points to it ([19](#19-discovery-document)).

## 13.6 Security Baseline

An implementation claiming this profile MUST follow the OAuth 2.0 Security Best Current Practice (RFC 9700). In particular:

- Every Authorization Code flow uses PKCE (RFC 7636), for confidential clients as well as public ones.
- The implicit grant and the resource owner password credentials grant are not supported.
- Redirect URIs are compared by exact string match.
- Refresh tokens issued to public clients are sender-constrained or rotated on every use.
- A client that writes `issuer-attested` entries, or claims to follow directives ([6.4](#64-directives)), SHOULD authenticate to the Authorization Service with an asymmetric key, by `private_key_jwt` (RFC 7523) or mutual TLS (RFC 8705), rather than with a shared secret ([21.7](#217-discovery-and-identity)).
- Access tokens are audience-restricted to the HCP Provider ([13.3](#133-grant-request)), and the provider checks the grant's current status on every request ([6.2.2](#622-revocation-propagation)).
# 14. VC Evidence Profile

## 14.1 Scope

This profile defines entries whose content is a complete W3C Verifiable Credential signed by its issuer, held as an evidence item ([4.2.2](#422-evidence)). It is identified as https://hcp.example/spec/profiles/vc-evidence/2.0 ([1.7](#17-conformance-identifiers)), and the same identifier is the value of `content.profile` for such an entry. It adds to any package ([18](#18-conformance-claims-and-packages)) and replaces v1's VC-Extended conformance level.

An implementation conforming to this profile MUST support such entries as specified in this section, with the signature boundary observed ([4.2.2](#422-evidence)).

## 14.2 Credential and Signature Boundary

The credential is held whole in the evidence item whose `role` is `content`: its own `@context`, `type`, `issuer`, `credentialSubject`, and either an embedded Data Integrity proof or the EnvelopedVerifiableCredential form, per 14.5. The credential is a self-contained artifact, verifiable by a generic Verifiable Credentials verifier without reference to the entry around it and without knowledge of HCP vocabulary.

**Template: the content member, VC Evidence Profile**

    "content": {
      "profile": "https://hcp.example/spec/profiles/vc-evidence/2.0",
      "evidence": 0
    }

- `content.evidence` is the index in `evidence` of the item holding the credential. `content` carries no `value`: the credential is not restated.
- The credential's proof covers the credential and nothing else ([4.2.2](#422-evidence)). Lifecycle transitions — a status change under 4.7, a category change under 4.2.1 — do not invalidate the issuer's proof.
- The credential carries no HCP vocabulary. It does not reference the HCP JSON-LD context, and it carries neither category nor declaration type. The issuer asserts; the HCP Provider classifies that assertion in `classification` and `assertion` when it ingests it ([4.2](#42-entry)). An issuer needs no knowledge of this specification in order to produce a credential an HCP instance can hold.
- The credential's `credentialSubject.id` MUST identify the same Context Subject as the entry's `subject.id`.
- The credential's dates are its own, set by its issuer: `validFrom` and `validUntil` under the Verifiable Credentials Data Model 2.0. The entry's `assertion.validUntil` MUST NOT be later than the credential's `validUntil` where the credential has one.
- A credential keeps the `@context` its issuer signed it with. The HCP Provider MUST NOT substitute another version of a context, including a newer version of the same context, because doing so invalidates the proof.

## 14.3 Roles

The Verifiable Credentials roles are defined here and are not Core roles ([3.2.6](#326-context-asserter)).

| VC role | In HCP |
|-------------------|------------------------------------------------------------------|
| Issuer | The Context Asserter of an entry whose content is a credential. `record.provenance.assertedBy.id` identifies it ([3.5](#35-provenance-layers)). |
| Credential subject | The Context Subject. The credential's `credentialSubject` identifies them, as the entry's `subject` does ([14.2](#142-credential-and-signature-boundary)). |
| Holder | The Context Subject, whose HCP instance holds the credential. The HCP Provider stores and returns it on their behalf. |
| Verifier | The HCP Provider, at ingest ([14.6](#146-ingest)) and before each disclosure ([14.7](#147-credential-status)). A Context Client that receives an entry carrying a credential MAY verify it independently. |

## 14.4 Example

An Open Badges 3.0 credential recording a learner's mastery of one topic, with the score as the achievement's result:

**Example: the entry, as the HCP Provider holds it**

    {
      "@context": ["https://hcp.example/contexts/v2"],
      "schema": "https://hcp.example/spec/entry/2.0",
      "id": "urn:uuid:2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d",
      "type": ["ContextEntry"],
      "subject": { "id": "did:example:subject-b7e2", "relationship": null },
      "content": {
        "profile": "https://hcp.example/spec/profiles/vc-evidence/2.0",
        "evidence": 0
      },
      "assertion": {
        "declarationType": "issuer-attested",
        "confidence": null,
        "validUntil": null
      },
      "classification": {
        "categories": ["education_learner_profile"],
        "dimension": null
      },
      "evidence": [
        {
          "role": "content",
          "type": "verifiable-credential",
          "credential": {
            "@context": [
              "https://www.w3.org/ns/credentials/v2",
              "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"
            ],
            "id": "urn:uuid:9c8b7a6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
            "type": ["VerifiableCredential", "OpenBadgeCredential"],
            "name": "Linear Equations: Mastery",
            "issuer": {
              "id": "did:web:mathkingdom.example.edu",
              "type": ["Profile"],
              "name": "Math Kingdom"
            },
            "validFrom": "2026-02-02T00:00:00Z",
            "validUntil": "2027-02-02T00:00:00Z",
            "credentialSubject": {
              "id": "did:example:subject-b7e2",
              "type": ["AchievementSubject"],
              "achievement": {
                "id": "https://mathkingdom.example.edu/achievements/linear-equations",
                "type": ["Achievement"],
                "name": "Linear Equations",
                "description": "Solves linear equations in one and two variables.",
                "criteria": {
                  "narrative": "80 percent or higher on the linear equations assessment."
                },
                "resultDescription": [
                  {
                    "id": "https://mathkingdom.example.edu/results/linear-equations",
                    "type": ["ResultDescription"],
                    "name": "Assessment score",
                    "resultType": "Percent",
                    "valueMin": "0",
                    "valueMax": "100"
                  }
                ]
              },
              "result": [
                {
                  "type": ["Result"],
                  "resultDescription": "https://mathkingdom.example.edu/results/linear-equations",
                  "value": "92"
                }
              ]
            },
            "credentialStatus": {
              "id": "https://mathkingdom.example.edu/status/3#94567",
              "type": "BitstringStatusListEntry",
              "statusPurpose": "revocation",
              "statusListIndex": "94567",
              "statusListCredential": "https://mathkingdom.example.edu/status/3"
            },
            "proof": {
              "type": "DataIntegrityProof",
              "cryptosuite": "eddsa-rdfc-2022",
              "created": "2026-02-02T00:00:00Z",
              "verificationMethod": "did:web:mathkingdom.example.edu#key-1",
              "proofPurpose": "assertionMethod",
              "proofValue": "{base64url-encoded-signature}"
            }
          },
          "verification": {
            "result": "verified",
            "at": "2026-02-02T00:05:12Z"
          }
        }
      ],
      "record": {
        "status": "active",
        "version": 1,
        "provenance": {
          "assertedBy": {
            "id": "did:web:mathkingdom.example.edu",
            "assurance": "cryptographically-verified"
          },
          "assertedAt": "2026-02-02T00:00:00Z",
          "source": "integration",
          "submittedByClient": {
            "id": "https://mathkingdom.example.edu/clients/hcp",
            "name": "Math Kingdom Assessments",
            "operator": { "id": "https://mathkingdom.example.edu", "name": "Math Kingdom" }
          },
          "authorizedUnder": "urn:uuid:c41e7a90-3b2d-4e6f-8a15-7d9c0b2e5f48",
          "recordedByProvider": "https://provider.example",
          "recordedAt": "2026-02-02T00:05:12Z"
        }
      }
    }

v1's example carried the learner's goal, pacing, learning preferences, and accessibility needs inside the credential. Those are not achievements, and an Open Badges credential without an achievement is not conformant. In v2 they are General Context entries; the education guide shows them ([G2](guides.md#g2-education-guide)).

## 14.5 Securing Credentials

A credential that is an entry's content MUST be secured by one of the following:

| Mechanism | `vc_securing` value | Specification | Verify | Notes |
|----------------------|--------------------------|------------------------|--------------|------------------------------------------|
| Embedded Data Integrity proof | `eddsa-rdfc-2022` | W3C VC Data Integrity EdDSA Cryptosuites | MUST | Requires RDF canonicalization, confined to the credential ([4.1.1](#411-processing-requirements)). Broadest support in current education wallets and verifiers. |
| Embedded Data Integrity proof, selective disclosure | `ecdsa-sd-2023` | W3C VC Data Integrity ECDSA Cryptosuites | SHOULD | Requires RDF canonicalization. A holder can derive a proof revealing only some claims ([14.9](#149-selective-disclosure)). |
| Enveloping proof | `vc-jose-cose` | W3C VC-JOSE-COSE | MAY | JOSE, SD-JWT, or COSE securing. No canonicalization. SD-JWT securing provides selective disclosure ([14.9](#149-selective-disclosure)). |

Implementations conforming to this profile MUST declare which mechanisms they issue and which they verify, in the discovery document as `vc_securing` ([19](#19-discovery-document)).

An implementation MUST verify `eddsa-rdfc-2022`, SHOULD verify `ecdsa-sd-2023`, and MAY verify VC-JOSE-COSE. Two conformant implementations therefore always share one mechanism, and `verifies` always includes `eddsa-rdfc-2022`. An issuer may secure a credential with any mechanism in the table, and the declaration in the discovery document is what allows it to determine whether its credentials will be accepted. A content credential secured with a mechanism the HCP Provider does not verify is rejected as `credential-invalid` ([14.6](#146-ingest)); a supporting credential is kept and marked as failed ([14.8](#148-supporting-credentials)).

The exact serialization of an enveloping proof follows VC-JOSE-COSE and the EnvelopedVerifiableCredential form defined in the VC Data Model; this specification does not restate it.

An issuer's signature secures the integrity of the credential; it does not itself authorize its disclosure ([3.11](#311-actor-invariants), invariant 11). Whether an HCP Provider may release an entry carrying a credential to a given HCP Client is governed entirely by the grant model ([6](#6-authorization)) — a valid proof establishes that the credential is what it claims to be, not that any particular client is entitled to see it.

## 14.6 Ingest

- Cryptographic proofs MUST be validated on ingest. Under end-to-end encrypted storage, they are validated within the Context Subject's trust domain ([4.8](#48-encrypted-storage)). An entry whose content credential fails validation MUST be rejected with credential invalid ([5.5](#55-errors)) rather than stored unverified.
- A content credential fails validation where its proof does not verify, where it is secured with a mechanism the HCP Provider does not verify ([14.5](#145-securing-credentials)), where the verification method cannot be obtained, or where its status shows it revoked or suspended ([14.7](#147-credential-status)). The error's detail names which, and does not reveal the credential's position in a status list.
- Where the issuer is identified by a DID, the HCP Provider MUST resolve it to obtain the verification method used to validate the proof.
- A write MAY omit `assertedBy.id`. The HCP Provider MUST set it from the credential's `issuer`. Where it is supplied and differs, the write is rejected with invalid request.
- An entry whose content credential the HCP Provider has validated is recorded with assurance `cryptographically-verified` ([3.6](#36-asserter-assurance)).
- The HCP Provider records the outcome on each evidence item it verifies, as `verification` ([4.2.2](#422-evidence)).
- An entry whose credential's `validUntil` has passed is `expired` ([4.2.4](#424-status)). It is not disclosed to a Context Client, and it remains visible to the Context Subject.
- A write carrying a credential as its content is `issuer-attested` and is accepted only from an HCP Client authenticated as the issuer, or authorized by it ([3.7](#37-statements-attributed-to-the-context-subject)).

A credential that supports a statement is verified on ingest too, under 14.8, but a failure does not reject the entry.

## 14.7 Credential Status

A credential whose issuer can revoke or suspend it names a status entry in `credentialStatus`. The HCP Provider checks it as follows:

- **Mechanism.** An implementation conforming to this profile MUST support Bitstring Status List v1.0: a `credentialStatus` of type `BitstringStatusListEntry`, with `statusPurpose` `revocation` or `suspension`. The status list credential is itself a credential, and MUST be verified before it is relied on. A content credential naming only a status mechanism the HCP Provider does not support is rejected as `credential-invalid`, because its status cannot be kept.
- **At ingest.** A content credential that is revoked or suspended is rejected ([14.6](#146-ingest)).
- **Before disclosure.** The HCP Provider MUST NOT disclose an entry whose content credential is revoked or suspended. It establishes status from a cached copy of the status list no older than its declared interval, `credential_status_interval` ([19](#19-discovery-document)). The interval MUST NOT exceed 24 hours, or 1 hour under the Health Context Profile ([16.2](#162-health-context-profile)). Where it cannot establish status within the interval, it MUST NOT disclose the entry until it can; the entry's status does not change.
- **Resting states.** A revoked content credential makes the entry `revoked`, and a suspended one makes it `suspended` ([4.2.4](#424-status)). Neither is read by a Context Client. A `revoked` entry leaves that state only by a revision carrying a new credential. A `suspended` entry returns to the state it held when the issuer lifts the suspension.
- **Audit.** The HCP Provider MUST append a `context.credentialStatus` event when it sets or lifts either state, and when it changes the `verification` of a supporting credential for a change of status ([8.1](#81-required-log-events)).

The HCP Provider fetches and caches a status list whole. It MUST NOT fetch status in a way that identifies a credential to its issuer, or that is timed to a disclosure, so that an issuer does not learn when a person's credential is used. A credential without `credentialStatus` cannot be revoked by its issuer, and its expiry is its only end ([4.2.4](#424-status)).

## 14.8 Supporting Credentials

A credential whose `role` is `supports` backs a statement in `content.value` ([4.2.2](#422-evidence)). Under this profile:

- The HCP Provider MUST verify a supporting credential on ingest, as it verifies a content credential ([14.6](#146-ingest)), and MUST record the outcome on the evidence item as `verification` ([4.2.2](#422-evidence)).
- A supporting credential that fails is kept, with `verification.result` `failed`, and the entry is accepted. The entry's content is the asserter's statement, and a failed attachment does not void it.
- The HCP Provider re-establishes the status of a supporting credential under 14.7 and updates `verification` when it changes. A revoked or suspended supporting credential does not change the entry's status.
- `verification` is disclosed with the evidence item ([7.4](#74-disclosures-to-context-clients)), so that a Context Client relying on a supporting credential knows what was checked and when.
- Verification never raises assurance and never confers standing ([3.11](#311-actor-invariants), invariant 15). A `person-declared` entry with a verified supporting credential remains `person-declared`, with the assurance its asserter's identity established ([3.6](#36-asserter-assurance)), and a failed credential does not lower it. Each consumer weighs the credential for itself.

The Health and Education Context Profiles require more of an `issuer-attested` entry's credential ([16.2](#162-health-context-profile), [16.4](#164-education-context-profile)).

## 14.9 Selective Disclosure

A credential secured with `ecdsa-sd-2023`, or with SD-JWT under VC-JOSE-COSE, lets its holder derive a presentation that reveals only some of its claims, verifiable against the issuer's original proof. Where an HCP Provider verifies such a mechanism ([14.5](#145-securing-credentials)):

- When it discloses an entry carrying such a credential to a Context Client, it SHOULD disclose a derived credential in its place, revealing the claims the request's purpose requires ([7.1](#71-category-and-purpose-bound)) and every claim the issuer made mandatory.
- The stored credential is unaltered ([4.2.2](#422-evidence)). Derivation is a property of the disclosure, as minimization is ([7.4](#74-disclosures-to-context-clients)).
- The evidence item disclosed lists the claims revealed, as JSON Pointers into the stored credential, in `revealed` ([7.4](#74-disclosures-to-context-clients)). The `context.read` event records the same list for each entry ([8.2](#82-log-entry-structure)).

A credential secured with `eddsa-rdfc-2022` or plain JOSE securing cannot be derived from, and is disclosed whole. A derived `ecdsa-sd-2023` presentation limits what is revealed, but two presentations of the same credential can still be linked to each other. How a grant names the claims it may receive, and unlinkable disclosure, are later work ([P1](path-to-v2-final.md#p1-roadmap)).

## 14.10 Attestation Authorizations

An attestation authorization is a Verifiable Credential an issuer issues to an HCP Client, saying that the client may write `issuer-attested` entries on the issuer's behalf ([3.7](#37-statements-attributed-to-the-context-subject)).

**Credential: issuer → HCP Client, presented to the HCP Provider**

    {
      "@context": ["https://www.w3.org/ns/credentials/v2"],
      "id": "urn:uuid:{authorization-uuid}",
      "type": ["VerifiableCredential", "HCPAttestationAuthorization"],
      "issuer": "{issuer identifier}",
      "validFrom": "{date-time}",
      "validUntil": "{date-time}",
      "credentialSubject": {
        "id": "{client identifier}",
        "attests": { "categories": ["{category}"], "credentialTypes": ["{credential type}"] }
      },
      "credentialStatus": { },
      "proof": { }
    }

- The client presents the authorization in its registration metadata, as `hcp_attestation_authorizations`, a list of credentials, or with a write. The provider verifies it as it verifies a content credential, with its securing mechanism and status ([14.5](#145-securing-credentials), [14.6](#146-ingest), [14.7](#147-credential-status)), and holds it.
- An `issuer-attested` write under it is accepted only where the authorization is valid and not revoked or suspended, its `credentialSubject.id` is the writing client, the entry's categories are among `attests.categories`, and, where the entry carries a credential, its type is among `attests.credentialTypes` and its issuer is the authorization's issuer. Any other is refused with not authorized ([5.5](#55-errors)).
- The provider records `assertedBy.via` with `kind` `authorization-credential` and the authorization's `id`, and `assertedBy.assurance` `authenticated` ([3.6](#36-asserter-assurance)). Where the written entry's content is itself a credential that passes validation, it is recorded as `cryptographically-verified`, as any other ([14.6](#146-ingest)).
- When the authorization is revoked, suspended or expires, the provider refuses new writes under it and changes nothing already written ([3.7](#37-statements-attributed-to-the-context-subject)).
- An HCP Provider that does not conform to this profile cannot verify an attestation authorization. It may accept a client only under a recorded arrangement, recorded as `unverified` ([3.7](#37-statements-attributed-to-the-context-subject)).
# 15. Memory Manager Profile

## 15.1 Scope

Core defines what happens when two entries conflict, and that they conflict when a `contradicts` relationship links them ([4.2.3](#423-relationships), [4.7](#47-conflicts)). This profile defines how an HCP Provider finds conflicts itself. It is identified as https://hcp.example/spec/profiles/memory-manager/2.0 ([1.7](#17-conformance-identifiers)). An HCP Provider that accepts `model-inferred` entries MUST conform to it ([4.7](#47-conflicts)); an HCP Provider that accepts none need not.

v1's matching rule — two entries with the same category and the same normalized dimension conflict — is removed. Two entries can address the same dimension without contradicting each other, and genuinely contradictory entries can carry different dimensions. A provider never resolves a conflict itself, except where an asserter's later inference deprecates its earlier one ([4.7](#47-conflicts)). It may propose a resolution ([4.7.4](#474-proposals)).

## 15.2 Candidates

A candidate conflict is between an active `model-inferred` entry and an active entry that is `person-declared`, `issuer-attested`, or `model-inferred`: the pairs whose conflicts change status ([4.7](#47-conflicts)). Detection is symmetric and MUST be evaluated on every write, whichever of the two is written second. Under end-to-end encrypted storage, it is evaluated within the Context Subject's trust domain ([4.8](#48-encrypted-storage)).

- The HCP Provider MUST apply a detection method — structural comparison, term overlap, semantic judgment, or any other — and MUST declare it in its discovery document as `conflict_detection` ([19](#19-discovery-document)). The set of values is open.
- Where the method finds that the two entries cannot both be true, the HCP Provider MUST record a `contradicts` relationship between them ([4.2.3](#423-relationships)), with `assertedBy` naming the provider in the role `hcp-provider` ([3.9](#39-audit-participants)).
- `classification.dimension` is a hint. A method MAY use it, but two entries MUST NOT be found to conflict on the basis of sharing a dimension alone. Before comparing two dimensions, a provider SHOULD normalize each: trim surrounding whitespace, lowercase, and collapse internal whitespace to a single underscore. A dimension that is a URI is not normalized; it is compared as an exact string ([4.2](#42-entry)). No dimension vocabulary is registered ([4.2](#42-entry), [P1](path-to-v2-final.md#p1-roadmap)).
- Pairs with no `model-inferred` entry — `person-declared` and `issuer-attested`, or two of either — change no status, and a provider MAY detect them ([4.7](#47-conflicts)).
- Where the provider detects a conflict, it MAY propose a resolution ([4.7.4](#474-proposals)).

Which entry is set to `conflicted` once a conflict is asserted depends on standing, and is defined in Core ([4.7.1](#471-standing), [4.7.2](#472-consequences)). Under v1 the `user-declared` entry always prevailed; under v2 an `unverified` `person-declared` entry does not, and both entries are quarantined until the Context Subject resolves the conflict ([3.7](#37-statements-attributed-to-the-context-subject)).

## 15.3 Re-evaluation

Detection runs on every write, including a revision. Where a revision of an entry in a conflict means the method no longer finds the conflict, the HCP Provider removes the `contradicts` relationship it asserted, and the resolution rule in 4.7.3 applies: any entry quarantined by the conflict returns to `active`, and a `conflict.resolved` event is appended.
# 16. Health and Education Context Profiles

## 16.1 Scope

This section defines two profiles:

| Profile | Identifier | Category |
|----------------------------|-------------------------------------------------------------|--------------------------------|
| Health Context Profile | https://hcp.example/spec/profiles/health-context/2.0 | `health_context` |
| Education Context Profile | https://hcp.example/spec/profiles/education-context/2.0 | `education_learner_profile` |

- An HCP Provider that accepts `issuer-attested` entries in `health_context` MUST conform to the Health Context Profile. One that accepts `issuer-attested` entries in `education_learner_profile` MUST conform to the Education Context Profile ([18.1](#181-claims)).
- Each profile requires the VC Evidence Profile ([14](#14-vc-evidence-profile)). An implementation claiming either lists the VC Evidence Profile as well.
- An HCP Provider that accepts only `person-declared` and `model-inferred` entries in a category need not claim its profile, and MAY claim it.

## 16.2 Health Context Profile

An implementation conforming to this profile MUST treat all entries in `health_context` as high-sensitivity regardless of content.

Because `health_context` is high-sensitivity, a copy disclosed from it is usable for at most 24 hours ([7.6](#76-use-until)). That is sensitivity's first normative effect, and it is in Core.

Access tokens issued under a grant whose scopes include `health_context` SHOULD NOT have a lifetime exceeding 1 hour, the default in 13.4.

An `issuer-attested` entry in `health_context` MUST carry a credential, as its content or in support of it ([4.2.2](#422-evidence)), and at least one credential it carries MUST pass verification at ingest ([14.6](#146-ingest)). A write that does not is rejected: with invalid request where it carries no credential, and with credential invalid where none passes. Entries the Context Subject declared, and `model-inferred` entries, are unaffected.

The implementation's `credential_status_interval` MUST NOT exceed 1 hour ([14.7](#147-credential-status), [19](#19-discovery-document)).

A `model-inferred` entry in `health_context` MUST NOT be disclosed to a Context Client unless the most recent confirmation record on its current version is `confirmed` ([3.8](#38-confirmation)). Until the Context Subject confirms it, a query does not return it and a get entry by `ref` fails with not authorized, as for an entry that does not exist ([4.2.4](#424-status)). A rejected one is never disclosed. The implementation SHOULD offer the Context Subject a way to review unconfirmed health inferences through a Management Client. An unconfirmed inference about a person's health is new health information about them, which they may never have disclosed, and a wrong one can shape care.

Deployment practice for health pilots, including the reasons for shorter token lifetimes and the custody of documents received before a grant, is in the health guide ([G3](guides.md#g3-health-guide)).

## 16.3 How v1's Commitment Is Met

v1 committed that VC-Extended conformance — now the VC Evidence Profile ([14](#14-vc-evidence-profile)) — would be required for health and education pilots at v2. It is met as follows:

- The claims the commitment is about are institutional ones: a clinician's assessment, an assessing platform's record of mastery. Under these profiles each such claim carries a credential its issuer signed, which the provider verifies and whose status it keeps ([14.6](#146-ingest), [14.7](#147-credential-status)).
- A provider that holds institutional health or education claims claims the profile for that category, and with it the VC Evidence Profile ([16.1](#161-scope)).
- A person's own statements and a model's inferences are not required to carry a credential. Requiring one would put a signature requirement on what a person says about themselves.

## 16.4 Education Context Profile

This profile adds rules for implementations holding institutional education context. It is identified as https://hcp.example/spec/profiles/education-context/2.0 ([1.7](#17-conformance-identifiers)).

An implementation conforming to this profile:

- MUST conform to the VC Evidence Profile ([14](#14-vc-evidence-profile)).
- MUST verify credentials secured with `ecdsa-sd-2023` as well as `eddsa-rdfc-2022` ([14.5](#145-securing-credentials)), the two cryptosuites Open Badges 3.0 verifiers support.
- MUST support the Open Badges 3.0 context for education entries.
- MUST check credential status under 14.7, including the Bitstring Status List entries Open Badges 3.0 credentials carry.

An `issuer-attested` entry in `education_learner_profile` MUST carry a credential, as its content or in support of it ([4.2.2](#422-evidence)), and at least one credential it carries MUST pass verification at ingest ([14.6](#146-ingest)). A write that does not is rejected: with invalid request where it carries no credential, and with credential invalid where none passes. Entries the learner declared, and `model-inferred` entries, are unaffected.

For credentials intended to be verified outside the deployment that issues them, the embedded Data Integrity mechanism has the broadest support among current wallets and verifiers, and 1EdTech notes that less common proof mechanisms may not be accepted everywhere ([G2](guides.md#g2-education-guide)).
# 17. Delegated Authorization Profile

## 17.1 Scope

This profile defines how a person other than the Context Subject acts as Authorizing Principal for them: a parent or guardian for a minor, a guardian or attorney-in-fact for an adult, a caregiver. It is identified as https://hcp.example/spec/profiles/delegated-authorization/2.0 ([1.7](#17-conformance-identifiers)). An implementation that issues a grant whose Authorizing Principal is not the Context Subject MUST conform to it ([3.3](#33-co-location-and-delegation), [18.1](#181-claims)).

- A delegate is a natural person. An organization — a school, a clinic, an employer — is never an Authorizing Principal. It acts through HCP Clients under a grant that the Context Subject, or a delegate, authorized.
- A delegate may delegate further only as 17.10 sets out: one level, to a natural person, where their own delegation allows it. A delegate who wants a service to have access, such as a tutoring service, authorizes a grant to it. That is not a delegation, and needs none.
- The Context Subject is always the person the entries describe ([3.2.1](#321-context-subject)). A delegation changes who may authorize grants for them, not whose context it is.

It absorbs v1 §7.3, multi-party and guardian consent.

## 17.2 Delegations

A delegation records one person's authority to act as Authorizing Principal for the Context Subject. The Authorization Service establishes it, and the HCP Provider holds its record as it holds grants ([6.1.5](#615-grant-representation)).

**Template: a delegation, as the HCP Provider records it**

    {
      "delegationId": "urn:uuid:{delegation-uuid}",
      "subject": { "id": "{subject identifier}" },
      "delegate": { "id": "{identifier}", "name": "{name the person can recognize}" },
      "relationship": "parent-or-guardian | legal-guardian | attorney-in-fact | caregiver | {URI}",
      "basis": {
        "method": "appointed | attested | evidence | delegated | unspecified",
        "description": "{what the authority rests on, shown to the person}",
        "parent": "{delegation id, for a sub-delegation}",
        "evidence": [ ],
        "covers": ["{high-sensitivity category}"],
        "establishedBy": "{authorization-service-identifier}",
        "establishedAt": "{date-time}"
      },
      "scope": {
        "categories": ["{category}"],
        "actions": ["read | write"]
      },
      "term": { "endsAt": "{date-time | null}", "atMajority": true },
      "mayDelegate": false,
      "ended": { "at": "{date-time}", "reason": "majority | expiry | basis-ended | relinquished | ended-by-subject | parent-ended | ended-by-delegate" }
    }

| Member | Rule |
|----------------|------------------------------------------------------------------|
| `delegationId` | Stable for the life of the delegation. Named by every grant issued under it ([17.4](#174-scope-and-grants-under-a-delegation)) and by audit events ([8.2](#82-log-entry-structure)). |
| `subject` | The Context Subject |
| `delegate` | The delegate: a natural person, with a name the Context Subject can recognize |
| `relationship` | The delegate's relationship to the Context Subject. The registered values are listed in A.1; any other is an absolute URI. It confers nothing by itself: what the delegate may do is set by `scope`. |
| `basis` | What the authority rests on, and how the Authorization Service established it ([17.3](#173-basis-of-authority)) |
| `scope` | The categories and actions the delegate may authorize ([17.4](#174-scope-and-grants-under-a-delegation)) |
| `term` | When the delegation ends: at `endsAt`, and at the Context Subject's age of majority where `atMajority` is true. The Authorization Service determines the age of majority under the law that applies. `endsAt` is null where no end is known. |
| `mayDelegate` | True where the delegate may appoint a sub-delegate ([17.10](#1710-sub-delegation)). Absent means false. Recorded by the Authorization Service when it establishes the delegation, as part of what the basis grants; for an `appointed` delegation, the Context Subject decides. |
| `ended` | Absent while the delegation holds. Set when it ends, with the reason ([17.6](#176-ending-a-delegation)). |

- The Authorization Service establishes a delegation and records `basis`. The HCP Provider MUST NOT take `basis`, `scope`, `term` or `mayDelegate` from a request by an HCP Client. It appends a `delegation.established` event when it records a delegation ([8.1](#81-required-log-events)).
- `relationship` on a delegation is distinct from `subject.relationship` on an entry, which stays reserved and uninterpreted ([11.3](#113-relationship)).
- The Context Subject and the delegate can each read the delegation, through a Management Client ([18.4](#184-person-facing-capabilities)). Neither may change it; a change is a new delegation.

## 17.3 Basis of Authority

| `basis.method` | Meaning |
|-------------------|------------------------------------------------------------------|
| `appointed` | The Context Subject appointed the delegate themselves, at the Authorization Service, through a Management Client acting for them. The Context Subject can end the delegation at any time ([17.6](#176-ending-a-delegation)) |
| `attested` | The Authorization Service established the relationship by means outside HCP — an account relationship, an enrollment process, an identity check — and attests it |
| `evidence` | Evidence was presented and is recorded in `basis.evidence`: a credential of guardianship, a court order, a power of attorney, an enrollment record |
| `delegated` | A delegate appointed the delegate, under a delegation whose `mayDelegate` is true. `basis.parent` names that delegation ([17.10](#1710-sub-delegation)) |
| `unspecified` | The basis is not known. Used only for a delegation converted from v1 ([17.8](#178-grants-carried-over-from-v1)) |

- Evidence that is a Verifiable Credential is held whole, as an evidence item is ([4.2.2](#422-evidence)). Where the implementation conforms to the VC Evidence Profile, it is verified and its status kept as for a supporting credential ([14.8](#148-supporting-credentials)).
- The basis records how authority was established. It does not require strong evidence, and it is not a judgment of the delegate's fitness to hold the authority, which belongs to the law and the deployment.
- A basis that was not established MUST NOT be recorded as established, and an `unspecified` basis MUST NOT be presented to anyone as `attested` ([3.11](#311-actor-invariants), invariant 15).
- The Context Subject and the delegate are shown `relationship`, `basis.method` and `basis.description`.

## 17.4 Scope and Grants Under a Delegation

**Scope.** A delegation's scope lists the categories and actions the delegate may authorize. It names each category; there is no wildcard.

- A high-sensitivity category ([4.5](#45-category-vocabulary)), and any custom category whatever sensitivity is declared for it, MAY be in scope only where it is listed in `basis.covers`, recording that the basis extends to it. A parent's authority over a minor's learning context does not by itself extend to their `health_context`.
- A grant authorized by the delegate MUST NOT reach a category or action outside the delegation's scope, or one a standing rule denies ([6.3](#63-standing-rules)). A request for one is refused at issuance. A delegate may set standing rules within the delegation's scope, which the Context Subject can remove ([6.3](#63-standing-rules)).
- Governance operations ([5.4](#54-governance-operations)) performed by a delegate, through a Management Client acting for them, reach only entries in categories within scope.

**Grants.** A grant authorized by a delegate is an ordinary grant ([6.1.5](#615-grant-representation)), with these differences:

**Template: the grant's `authorizingPrincipal` member under a delegation**

    "authorizingPrincipal": {
      "id": "{identifier of the delegate, specific to the HCP Client}",
      "delegation": "urn:uuid:{delegation-uuid}"
    }

- `authorizingPrincipal` identifies the delegate, by an identifier specific to the HCP Client, and `delegation` names the delegation. Where the Context Subject authorizes a grant themselves, `delegation` is absent.
- Before the approving act ([6.1.6](#616-authorization-is-distinct-from-authentication)), the delegate MUST also be told that they are authorizing on the Context Subject's behalf, and when the delegation ends.
- A temporary grant's `expiresAt` MUST NOT be later than the delegation's `term.endsAt`. Every grant under a delegation ends when the delegation ends ([17.6](#176-ending-a-delegation)).
- The `grant.issued` event names the delegation ([8.2](#82-log-entry-structure)).
- A Context Client reading its own grant ([5.2.6](#526-read-own-grant)) is not shown `delegation`. The delegation's identifier is the same in every grant made under it, and showing it would let two clients link the person.

## 17.5 The Context Subject's Override

- The Context Subject MUST be able to revoke any grant made for them, including every grant a delegate authorized, at any time, through a Management Client or the person-facing capabilities required by 18. Revocation by the Context Subject MUST NOT be conditioned on the delegate's agreement, and is never rate limited ([6.2.1](#621-revocation-by-the-authorizing-principal)).
- The delegate is told of the revocation. A new grant for the same client is a new approving act, recorded as `grant.issued`, and the Context Subject sees it.
- A delegate MAY revoke any grant within the delegation's scope.
- Where the delegation's `basis.method` is `appointed`, the Context Subject MUST be able to end the delegation itself at any time, through a Management Client ([17.6](#176-ending-a-delegation)). A delegation resting on any other basis — a court order, a parent's authority, an attested relationship — is ended only as 17.6 sets out, though its grants can always be revoked.
- Whether the Context Subject may also authorize grants while a delegation holds, and from what age, is set by the deployment under the law that applies to it. A grant the Context Subject authorizes is a Core grant, whether or not a delegation holds.
- The Context Subject MUST be able to read their whole audit log at any time ([8.3](#83-access-to-the-audit-log)).

## 17.6 Ending a Delegation

A delegation ends:

- at `term.endsAt` (reason `expiry`), or at the age of majority where `term.atMajority` is true (reason `majority`);
- when the Authorization Service records that the basis has ended (reason `basis-ended`);
- when the delegate relinquishes it, through a Management Client (reason `relinquished`); or
- where its basis is `appointed`, when the Context Subject ends it, through a Management Client (reason `ended-by-subject`);
- for a sub-delegation, when the delegation it came from ends (reason `parent-ended`), or when the delegate who made it ends it (reason `ended-by-delegate`) ([17.10](#1710-sub-delegation)).

When a delegation ends:

- Every grant authorized under it ends at that moment. Its `status` becomes `expired`, and the HCP Provider appends `grant.expired` with reason `delegation-ended` ([8.2](#82-log-entry-structure)). Invalidation and notification follow 6.2.2–6.2.4, as for a revocation.
- The HCP Provider appends a `delegation.ended` event, and sets `ended`.
- Entries written under the delegation's grants are unaffected. They are the Context Subject's, and their provenance shows the grant under which each was written ([3.5](#35-provenance-layers)).
- No grant carries over. The Context Subject authorizes any access they want to continue.

**At the age of majority.** Where a delegation ends for the reason `majority`, the HCP Provider MUST show the person, the first time they use a Management Client afterwards, a summary of the delegated period: the delegate, the grants made, and for each the client, its Client Operator, the categories, the purposes and the period, from the disclosure summary ([8.6](#86-disclosure-summary)). The summary says that the former delegate can read the record of the grants they authorized ([17.7](#177-audit-access)).

## 17.7 Audit Access

| Party | Reads |
|-------------------------------|------------------------------------------------------------------|
| The Context Subject | The whole audit log, at any time ([8.3](#83-access-to-the-audit-log)) |
| A delegate, while the delegation holds | Every event of a grant they authorized, and of a governance operation performed for them, and the same for any sub-delegate they appointed ([17.10](#1710-sub-delegation)). Not the events of grants the Context Subject authorized |
| A former delegate | The events of grants they authorized: issued, revoked, and expired, and the reads and writes made under them. Each shows the event type, time, client, Client Operator, category, and purpose. Never `entryId`, `relatedEntryId`, `disclosed`, or the `data` of a `context.*` event, and never an event in a category outside the delegation's scope |
| Anyone else | Nothing |

- A former delegate's access lasts as long as the audit log is kept ([8.4](#84-durability)). It exists because a person who consented on someone else's behalf stays accountable for what they approved.
- The Context Subject cannot end a former delegate's access, and MUST be told that it exists, in the summary at the age of majority and wherever their audit log is presented.
- A delegate's or former delegate's read of the log is a governance operation ([5.4](#54-governance-operations)), performed through a Management Client acting for them.

## 17.8 Grants Carried Over from v1

v1 required `grantor` to be recorded where the party authorizing a grant was not its subject. An HCP Provider that continues such a grant under v2 converts it:

- A delegation is created with `delegate` set from `grantor`, `basis.method` `unspecified`, `scope` set to the categories and actions of the grants converted, and `term.endsAt` null unless the provider knows an end.
- Each grant is converted with `authorizingPrincipal` identifying the delegate and naming that delegation. Its expiry is unchanged.
- The converted delegation authorizes no new grant. A new grant needs a delegation established under 17.2.
- The Context Subject is shown each converted delegation and its grants, with its basis as unspecified, through a Management Client.
- Nothing is upgraded: an `unspecified` basis remains so until a new delegation replaces it ([3.11](#311-actor-invariants), invariant 15).

## 17.9 Why in the Protocol (Informative)

Learning Economy Foundation reviewers observed during v1 review that guardian consent can be handled in the wallet or holder application rather than in the protocol between them, and for v1 that is what was required. What the application layer cannot do is make a guardian-approved act legible in the person's own audit log, or carry the relationship when a person moves from one HCP instance to another. Those two properties are why v2 takes the question up rather than leaving it at the application layer permanently.

## 17.10 Sub-delegation

A delegate whose delegation has `mayDelegate` true MAY appoint a sub-delegate: a parent who asks a grandparent to look after a child's learning context while they travel, for instance. The delegate appoints them at the Authorization Service, through a Management Client acting for the delegate. The result is a delegation like any other ([17.2](#172-delegations)), with these limits:

- `basis.method` is `delegated`, and `basis.parent` names the delegation it came from. Its `delegate` is a natural person.
- Its `scope` is within the parent's scope, its `term.endsAt` is no later than the parent's, and it ends at the age of majority wherever the parent does.
- Its `mayDelegate` is false. A sub-delegate cannot delegate further.
- It ends when the parent ends (reason `parent-ended`), and the delegate who appointed it may end it at any time (reason `ended-by-delegate`). The Context Subject may end it wherever they may end the parent ([17.5](#175-the-context-subjects-override)).
- The Context Subject's override reaches every grant a sub-delegate authorizes ([17.5](#175-the-context-subjects-override)), and so does the revocation of the delegate who appointed them.
- It appears among the Context Subject's delegations and in their audit log ([8.3](#83-access-to-the-audit-log)). The Management Client SHOULD notify the Context Subject when one is made.
- A delegate stays accountable for the sub-delegates they appoint: they read the events of their grants ([17.7](#177-audit-access)).

Further levels of delegation are later work ([P1.4](path-to-v2-final.md#p14-later)).
# Part IV — Conformance

This Part states how an implementation claims conformance ([18](#18-conformance-claims-and-packages)), how it describes itself ([19](#19-discovery-document)), and how its claims are tested ([20](#20-conformance-testing)). Its requirements apply to every implementation that makes a claim. The Part has no conformance identifier of its own and is not itself claimed ([1.1](#11-parts)).

# 18. Conformance Claims and Packages

## 18.1 Claims

An implementation states what it conforms to as a `conformsTo` list of conformance identifiers ([1.7](#17-conformance-identifiers)) in its discovery document ([19](#19-discovery-document)).

- An implementation claiming any HCP conformance MUST list Core, and MUST list every binding and every profile it claims.
- An implementation MUST NOT list an identifier unless it satisfies every requirement of that Part. A binding or profile is claimed whole.
- An implementation that accepts `model-inferred` entries MUST list the Memory Manager Profile ([4.7](#47-conflicts)).
- An implementation that accepts `issuer-attested` entries in `health_context` MUST list the Health Context Profile, and one that accepts them in `education_learner_profile` MUST list the Education Context Profile. Either requires listing the VC Evidence Profile ([16.1](#161-scope)).
- An implementation that issues a grant whose Authorizing Principal is not the Context Subject MUST list the Delegated Authorization Profile ([17.1](#171-scope)).

The `conformsTo` list is authoritative. A client determines what an implementation supports from that list, whatever is claimed for the implementation elsewhere ([12.2](#122-requirements)).

In this draft a claim is made for an HCP Provider, together with the Authorization Service where the two are deployed together ([3.2.5](#325-authorization-service)), with one exception. An HCP Client MAY claim to follow directives ([6.4](#64-directives)), with the client conformance identifier in 1.7, declared at registration and recorded on its grants ([6.1.5](#615-grant-representation)). It is the only client claim in this draft. Requirements this specification places on HCP Clients, such as the actor invariants ([3.11](#311-actor-invariants)) and onward disclosure ([3.12](#312-onward-disclosure)), apply to every client wherever they are stated, whether or not it makes a claim. Further client claims, and attestation of them, are later work ([P1.4](path-to-v2-final.md#p14-later)).

## 18.2 Packages

A package names a combination of Parts that implementations commonly claim. A package has no identifier of its own: an implementation claims a package by listing every identifier the package comprises.

| Package | Lists in `conformsTo` | Bindings | v1 equivalent |
|-----------------|------------------------------------------------------|------------------------------------------|----------------|
| First-Party | Core, General Context, First-Party Authorization, and each binding exposed | Either or both; MCP over either transport | Core |
| Provider Interop | Core, General Context, HTTP Binding, OAuth Interop | HTTP required; MCP permitted | Interop |
| Agent Interop | Everything Provider Interop lists, and the MCP Binding | HTTP, and MCP over Streamable HTTP | None |
| VC Evidence | The VC Evidence Profile, added to any package above | As for that package | VC-Extended |

- **First-Party.** For an implementation whose HCP Clients are all operated by its own Provider Operator ([12.1](#121-scope)). Grants are obtained under the First-Party Authorization Profile ([12](#12-first-party-authorization-profile)), and the implementation may expose any one binding or both.
- **Provider Interop.** The common provider baseline. The HTTP Binding carries both the context and the governance planes ([1.6](#16-context-plane-and-governance-plane)), and grants are obtained under the OAuth Interop Profile ([13](#13-oauth-interop-profile)).
- **Agent Interop.** Provider Interop with agent-native access added. The MCP Binding runs over Streamable HTTP, with MCP's authorization mapped onto the OAuth Interop Profile ([10.1](#101-scope), [13.5](#135-mcp-authorization)). MCP over stdio does not qualify ([10.1](#101-scope)).
- **VC Evidence.** Adds entries whose content is a credential to any package ([14](#14-vc-evidence-profile)).

The Memory Manager Profile ([15](#15-memory-manager-profile)), the Health and Education Context Profiles ([16](#16-health-and-education-context-profiles)), and the Delegated Authorization Profile ([17](#17-delegated-authorization-profile)) are added to any package where they apply ([18.1](#181-claims)). Each of the Health and Education Context Profiles brings the VC Evidence Profile with it.

## 18.3 When Provider Interop Is Required

An implementation that accepts, or holds itself out as accepting, authorization requests from any HCP Client whose Client Operator is not its own Provider Operator MUST claim the Provider Interop package.

It follows that:

- The HTTP Binding is required of every implementation that accepts HCP Clients operated by others. An implementation whose only binding is MCP accepts first-party clients only.
- An implementation claiming the First-Party Authorization Profile cannot claim Provider Interop or Agent Interop ([12.2](#122-requirements)).

Under v1, an implementation accepting outside clients over MCP alone could claim Interop. Under this draft it cannot.

## 18.4 Person-Facing Capabilities

Each capability below MUST be available through at least one modality the implementation supports. These are capabilities, not interface requirements; natural language is a conformant modality ([18.5](#185-natural-language-access-in-llm-mediated-contexts)).

- The Context Subject can enumerate all stored entries, including those whose `record.status` is `conflicted`.
- The Context Subject can correct or delete any entry, and can request hard deletion ([5.4.2](#542-hard-deletion)).
- The Context Subject can resolve a conflict by rejecting, accepting, or superseding an entry ([4.7.3](#473-resolution)).
- The Authorizing Principal can enumerate and revoke all active grants, represented per 6.1.5, with the approved purposes shown ([6.1.5.2](#6152-purposes)) and any narrowing reflected per 6.1.5.1.
- The Authorizing Principal can view the audit log ([8.3](#83-access-to-the-audit-log)), and the disclosure summary ([8.6](#86-disclosure-summary)).
- The Authorizing Principal is told when a revocation notification could not be delivered, and when the client's copies stop being usable ([6.2.4](#624-when-notification-fails)).
- The Authorizing Principal is told, before approving and at revocation, which client keeps copies under a declared legal obligation ([6.1.6](#616-authorization-is-distinct-from-authentication), [6.2.5](#625-copies-kept-under-a-legal-obligation)).
- The Context Subject can set and remove standing rules, and is told when one excludes a requested category ([6.3](#63-standing-rules)).
- Authorization interactions make temporary access the default outcome, and electing persistence requires a separate affirmative act ([6.1.4](#614-grant-distinction-temporary-vs-persistent)).
- Where a bounded audit durability window is declared, it is disclosed wherever the audit log is presented ([8.4](#84-durability)).
- Under the Delegated Authorization Profile: the Context Subject and each delegate can read the delegations that name them ([17.2](#172-delegations)); the Context Subject can revoke any grant made for them ([17.5](#175-the-context-subjects-override)); the person is shown the summary of a delegated period at the age of majority ([17.6](#176-ending-a-delegation)), and is told wherever their audit log is presented that a former delegate can read part of it ([17.7](#177-audit-access)).

An implementation exposing the HTTP Binding MAY provide these capabilities through a Management Client over that binding. An implementation whose only binding is MCP, permitted under the First-Party package, provides them through its own person-facing interface ([1.6](#16-context-plane-and-governance-plane)).

## 18.5 Natural Language Access in LLM-Mediated Contexts

In contexts where an LLM is the primary interface — for example, an AI assistant through which a person manages their HCP instance — implementations MAY provide the person-facing capabilities ([18.4](#184-person-facing-capabilities)) through natural language interaction rather than a graphical interface.

This includes operations such as:

- Viewing stored entries (e.g., "show me what you know about my learning preferences")
- Correcting an entry (e.g., "that's wrong; I prefer worked examples, not videos")
- Deleting an entry (e.g., "forget what I said about my schedule constraints")
- Reviewing active grants (e.g., "which apps have access to my health context?")
- Revoking a grant (e.g., "remove access for the recipe app")

Requirements for natural language access:

- The underlying operations MUST map to the Core operations defined in 5 and the grant operations defined in 6.
- The audit log MUST capture these operations identically to their equivalents in a binding; the interface modality does not change the audit requirement.
- The implementation MUST confirm the action to the person in natural language before executing writes, updates, or deletions.
- The implementation MUST NOT execute irreversible operations (hard deletion, grant revocation) without explicit confirmation by the person in the same interaction.

Where the LLM-mediated interface is an HCP Client, it reaches governance operations as a Management Client over the HTTP Binding ([1.6](#16-context-plane-and-governance-plane)). The Management Client's credentials are held by the client, never by the model ([10.5](#105-who-holds-the-grant)), and a confirmation is the person's own act: a model's judgment that the person would agree does not satisfy it ([3.11](#311-actor-invariants), invariant 6).

HCP is a protocol, not a user experience pattern, and implementations are free to design elicitation and interaction flows appropriate to their context (Guides). This section establishes only that natural language is a conformant modality for the operations listed above, subject to the requirements stated here.
# 19. Discovery Document

## 19.1 Publication

Every implementation claiming HCP conformance MUST publish a discovery document, as JSON.

- An implementation exposing the HTTP Binding publishes it at `/.well-known/hcp-configuration` relative to its base URL ([9.1](#91-scope)).
- An implementation whose only binding is MCP publishes it at an HTTPS URL, and names that URL in the `discovery` setting of its MCP extension ([10.2](#102-identifying-an-hcp-server)).

Where the `conformsTo` list in an MCP server's extension settings ([10.2](#102-identifying-an-hcp-server)) differs from the discovery document's, the discovery document governs.

Conformance identifiers in the document are compared as exact strings and need not resolve ([1.7](#17-conformance-identifiers)).

## 19.2 Example

**Response body: HCP Provider → any client (discovery, HTTP)**

    {
      "hcp_version": "2.0",
      "provider": "{base-url}",
      "provider_operator": { "id": "{operator-identifier}", "name": "{organization name}" },
      "conformsTo": [
        "https://hcp.example/spec/core/2.0",
        "https://hcp.example/spec/bindings/http/2.0",
        "https://hcp.example/spec/bindings/mcp/2.0",
        "https://hcp.example/spec/profiles/general-context/2.0",
        "https://hcp.example/spec/profiles/oauth-interop/2.0",
        "https://hcp.example/spec/profiles/memory-manager/2.0",
        "https://hcp.example/spec/profiles/vc-evidence/2.0",
        "https://hcp.example/spec/profiles/delegated-authorization/2.0"
      ],
      "bindings": ["http", "mcp"],
      "protected_resource_metadata": "{base-url}/.well-known/oauth-protected-resource",
      "jwks_uri": "{base-url}/.well-known/jwks.json",
      "entries_endpoint": "{base-url}/v2/entries",
      "grants_endpoint": "{base-url}/v2/grants",
      "audit_endpoint": "{base-url}/v2/audit",
      "export_endpoint": "{base-url}/v2/export",
      "delegations_endpoint": "{base-url}/v2/delegations",
      "rules_endpoint": "{base-url}/v2/rules",
      "directives_endpoint": "{base-url}/v2/directives",
      "shares_endpoint": "{base-url}/v2/shares",
      "mcp_endpoint": "{base-url}/mcp",
      "supported_categories": [
        { "id": "general_preferences", "name": "General preferences",
          "description": "Communication style, formatting, language preferences",
          "sensitivity": "low", "registry": "1" },
        { "id": "https://clinic.example/categories/maternal-care", "name": "Maternal care",
          "description": "Antenatal and postnatal care plans and appointments",
          "sensitivity": "high", "definer": "https://clinic.example" }
      ],
      "category_registry": "1",
      "accepts_entry_schemas": ["https://hcp.example/spec/entry/2.0"],
      "minimization_method": "semantic",
      "conflict_detection": "semantic",
      "audit_durability": {
        "default": "synchronous",
        "bounded": { "context.read": 5000 }
      },
      "audit_integrity": "hash-chained",
      "storage_encryption": "server",
      "pagination": { "audit": "cursor" },
      "problem_type_base": "https://hcp.example/problems/",
      "rate_limits": { "documentation_url": "{url}" },
      "vc_securing": {
        "issues": ["eddsa-rdfc-2022"],
        "verifies": ["eddsa-rdfc-2022", "ecdsa-sd-2023", "vc-jose-cose"]
      },
      "credential_status_interval": 3600
    }

The example is an Agent Interop implementation that also claims VC Evidence and the Delegated Authorization Profile, and that accepts `model-inferred` entries and so claims the Memory Manager Profile ([18.1](#181-claims), [18.2](#182-packages)).

## 19.3 Members

| Member | Presence | Meaning |
|--------------------------|----------------------------------------|----------------------------------------------------------|
| `hcp_version` | Required | The protocol version. Every HTTP response carries it in the `HCP-Version` header ([9.3](#93-general-requirements)). |
| `provider` | Required | The HCP Provider's base URL. Named so that "issuer" refers only to a credential issuer ([3.2.6](#326-context-asserter)). |
| `provider_operator` | Required | The Provider Operator: an identifier and a name the person can recognize ([3.2.8](#328-client-operator-and-provider-operator)). |
| `conformsTo` | Required | The conformance claims ([18.1](#181-claims)) |
| `bindings` | Required | The bindings exposed: `http`, `mcp`, or both ([1.5](#15-bindings-and-transports)). Each binding listed here has its identifier in `conformsTo`, and each binding claimed there is listed here. |
| `protected_resource_metadata` | Required under the OAuth Interop Profile ([13](#13-oauth-interop-profile)) | The URL of the provider's OAuth 2.0 Protected Resource Metadata (RFC 9728), which names its Authorization Service ([13.5](#135-mcp-authorization)) |
| `entries_endpoint`, `grants_endpoint`, `audit_endpoint`, `export_endpoint` | Required where the HTTP Binding is exposed | The HTTP Binding's endpoints ([9.2](#92-endpoints)) |
| `mcp_endpoint` | Required where the MCP Binding runs over Streamable HTTP | The MCP endpoint ([10.1](#101-scope)) |
| `delegations_endpoint` | Required under the Delegated Authorization Profile where the HTTP Binding is exposed | The delegations endpoint ([9.4.13](#9413-delegations)) |
| `rules_endpoint` | Required where the HTTP Binding is exposed | The standing rules endpoint ([9.4.14](#9414-standing-rules)) |
| `directives_endpoint` | Required where the HTTP Binding is exposed | The directives endpoint ([9.4.15](#9415-directives)) |
| `shares_endpoint` | Required where the HTTP Binding is exposed and the implementation issues grants with `onwardSharing` | The onward-sharing endpoint ([9.4.16](#9416-onward-sharing)) |
| `jwks_uri` | Required | The JSON Web Key Set holding the keys that sign revocation notifications ([9.9](#99-revocation-notification-delivery)) |
| `supported_categories` | Required | The categories the implementation holds, registered and custom, each with `id`, `name`, `description`, and `sensitivity` (`low`, `medium`, or `high`), and with `registry` for a registered category or `definer` for a custom one. A custom category's `sensitivity` is never `low` ([4.5](#45-category-vocabulary)). |
| `category_registry` | Required | The version of the category registry used ([4.5](#45-category-vocabulary), [A.1](#a1-registries)) |
| `accepts_entry_schemas` | Required | The entry schemas accepted: this draft's, and any v1 forms accepted on import ([4.3](#43-one-form-and-conversion-from-v1)). Entries are always emitted in the form of 4.2. |
| `minimization_method` | Required | The relevance method determining the final ordering of query results ([7.3](#73-relevance-ordering)). The set of values is open. `none` is not a valid declaration, because a query always applies an ordering. |
| `conflict_detection` | Required under the Memory Manager Profile; omitted otherwise | The method by which the provider finds conflicts ([15.2](#152-candidates)). The set of values is open. |
| `audit_durability` | Required | `default` is `synchronous`. `bounded` declares a durability window in milliseconds; it MAY be declared only for `context.read`, within the limit in 8.4. An implementation with no window omits `bounded`. |
| `audit_integrity` | Required | The integrity level of the Context Subject's audit log: `append-only`, `hash-chained`, `signed-checkpoints`, or `anchored` ([8.7](#87-integrity)) |
| `storage_encryption` | Required | How entry content is stored: `server`, readable by the provider, or `e2e`, encrypted under keys the provider does not hold ([4.8](#48-encrypted-storage)) |
| `pagination` | Required where the HTTP Binding is exposed | Pagination of the audit log ([9.5](#95-pagination)) |
| `problem_type_base` | Required where the HTTP Binding is exposed | The base of the problem types ([9.7](#97-errors)) |
| `rate_limits` | Recommended | The rate limit policy ([9.8](#98-rate-limiting)) |
| `vc_securing` | Required under the VC Evidence Profile; omitted otherwise | The securing mechanisms issued and verified ([14.5](#145-securing-credentials)): `eddsa-rdfc-2022`, `ecdsa-sd-2023`, `vc-jose-cose`. `verifies` always includes `eddsa-rdfc-2022`. |
| `credential_status_interval` | Required under the VC Evidence Profile; omitted otherwise | The greatest age, in seconds, of the status list copy from which credential status is established: at most 86400, or 3600 under the Health Context Profile ([14.7](#147-credential-status), [16.2](#162-health-context-profile)) |

## 19.4 Changes from v1

| v1 member | v2 |
|--------------------------|------------------------------------------------------------------|
| `conformance_level` | Replaced by `conformsTo` ([18.1](#181-claims)) |
| `supported_transports` | Replaced by `bindings` ([1.5](#15-bindings-and-transports)) |
| `authorization_profile` | Removed. `conformsTo` names the authorization profile ([12.2](#122-requirements), [13.1](#131-scope)) |
| `mcp_manifest_endpoint` | Removed. An MCP server identifies itself through `server/discover` ([10.2](#102-identifying-an-hcp-server)) |
| — | `provider_operator` added ([3.2.8](#328-client-operator-and-provider-operator)) |
| — | `mcp_endpoint` added |
| `issuer` | Renamed `provider` ([3.2.6](#326-context-asserter)) |
| `preferences_endpoint` | Renamed `entries_endpoint` |
| `envelope_form` | Replaced by `accepts_entry_schemas` ([4.3](#43-one-form-and-conversion-from-v1)) |
| `tier2_securing` | Renamed `vc_securing` ([14.5](#145-securing-credentials)). `data-integrity` becomes `eddsa-rdfc-2022`; `ecdsa-sd-2023` is added |
| — | `category_registry` and `conflict_detection` added |
| `supported_categories` | Each category is described, not only named ([4.5](#45-category-vocabulary)) |
| — | `directives_endpoint` added ([9.4.15](#9415-directives)) |
| — | `storage_encryption` added ([4.8](#48-encrypted-storage)) |
| `authorization_endpoint`, `token_endpoint`, `revocation_endpoint` | Replaced by `protected_resource_metadata` ([13.5](#135-mcp-authorization)) |
| — | `jwks_uri` and `audit_integrity` added |
| — | `credential_status_interval` added ([14.7](#147-credential-status)) |
| — | `delegations_endpoint` added ([9.4.13](#9413-delegations)) |
| — | `rules_endpoint` added ([9.4.14](#9414-standing-rules)) |
| — | `shares_endpoint` added ([9.4.16](#9416-onward-sharing)) |

The member name `storage_encryption` is reserved for the declaration of end-to-end encrypted storage that v1 placed on record ([P1](path-to-v2-final.md#p1-roadmap)).
# 20. Conformance Testing

This section describes the HCP Conformance Test Suite. It places no requirement on implementations beyond those in the sections it cites.

## 20.1 Scope of the Suite

The suite, to be published alongside this specification, will provide:

- Automated schema validation of entries against the published JSON Schema ([4.1.1](#411-processing-requirements), [Appendix A](#appendix-a-registries-and-published-artifacts)), and of credentials under the VC Evidence Profile ([14](#14-vc-evidence-profile)).
- Grant semantics tests — category scoping, temporary-by-default, expiry bounds, revocation propagation, and the prohibition on silent scope expansion — applicable to all implementations, verified against the grant representation in 6.1.5.
- An OAuth 2.0 grant flow test harness, applicable to implementations claiming the OAuth Interop Profile ([13](#13-oauth-interop-profile)).
- Minimization tests: out-of-scope entries are not returned ([7.1](#71-category-and-purpose-bound)); the quantity bound holds and results are not padded, verified against seeded fixtures in which the number of matching entries is known ([7.2](#72-quantity-bound)); the declared relevance method matches the discovery document ([7.3](#73-relevance-ordering)); redacted fields are absent from responses to a Context Client and reported in `redactedFields` ([7.4](#74-disclosures-to-context-clients), [7.5](#75-reporting)).
- Audit log completeness tests ([8.1](#81-required-log-events)), including the participants each event names ([3.9](#39-audit-participants)).
- Revocation propagation tests ([6.2](#62-revocation)).
- Provenance tests: fields the HCP Provider sets are not taken from a request, and assurance is never recorded higher than was established (3.5–3.7).
- Governance plane tests: every governance operation fails with not authorized for a Context Client, and the MCP Binding carries none ([6.1.9](#619-governance-operations), [10.1](#101-scope)).
- Binding tests: each claimed binding maps the Core operations and errors as specified ([9](#9-http-binding), [10](#10-mcp-binding)).

The suite exercises a materially larger surface than the June 2026 draft of v1 implied: v1 entries converted on import ([4.3](#43-one-form-and-conversion-from-v1)); grant semantics verified against a grant representation that includes narrowed grants ([6.1.5](#615-grant-representation), [6.1.5.1](#6151-narrowed-grants)); a four-part minimization contract requiring seeded fixtures ([7](#7-disclosure-and-minimization)); conflict outcomes in Core ([4.7](#47-conflicts)) and conflict detection, including dimension normalization, under the Memory Manager Profile ([15](#15-memory-manager-profile)); three declaration types and three assurance values ([4.4](#44-declaration-types), [3.6](#36-asserter-assurance)); one mandatory securing mechanism among three, and credential status against seeded status lists ([14.5](#145-securing-credentials), [14.7](#147-credential-status)); and two bindings ([9](#9-http-binding), [10](#10-mcp-binding)).

Schema validation is the suite's first function, so the suite depends on the entry JSON Schema being published ([Appendix A](#appendix-a-registries-and-published-artifacts)).

## 20.2 Test Hook for First-Party Implementations

An implementation claiming the First-Party Authorization Profile still requires a means for the suite to obtain a credential and trigger grant creation ([12.2](#122-requirements)). The suite specification defines a test hook for this purpose.

A grant created through the hook is not created by an act of the Authorizing Principal. A deployment holding any real person's context therefore cannot offer the hook without failing 6.1.6.

## 20.3 Pilots

Pilot implementations are expected to run the test suite before integration with field pilots ([G1](guides.md#g1-pilot-onboarding)).
# Part V — Security and Privacy Considerations

This Part is informative. It explains what the Specification protects against and what it leaves to others.

# 21. Security and Privacy Considerations

This section is informative. It explains what each part of HCP protects against, what remains, and who acts on what remains. Its requirements are stated in the sections it cites, not here. It is organized by HCP's building blocks — entries, grants, disclosure, rules, audit, and discovery — and then by topics that cut across them.

## 21.1 What HCP Does Not Prevent

HCP limits what context reaches a client, records what it did, and lets the person see and undo it. It does not govern what happens beyond that.

- **A model's other capabilities.** HCP limits what context a model receives and what it may write. A general-purpose model with tools can act destructively whether or not its client conforms to HCP.
- **What a client does with context it received.** The provider cannot observe use after disclosure. Purposes ([6.1.5.2](#6152-purposes)), use-until ([7.6](#76-use-until)), onward disclosure ([3.12](#312-onward-disclosure)), and directives ([6.4](#64-directives)) are obligations a client takes on; HCP records them, and accountability for keeping them lies with the client and its operator.
- **Whether a client tells the truth about itself.** Its purposes, its claim to follow directives ([18.1](#181-claims)), and its declared legal retention ([6.2.5](#625-copies-kept-under-a-legal-obligation)) are declarations. HCP makes each one visible to the person and records it; it cannot verify it.

HCP's protections are therefore of two kinds: limits that the provider enforces, and records that make a broken obligation visible to the person and to anyone holding a client to account.

## 21.2 Entries

- **False attribution.** A client can claim that the person said something they did not. Such an entry is recorded as `unverified` until the person confirms it, and has no standing in a conflict ([3.7](#37-statements-attributed-to-the-context-subject), [4.7.1](#471-standing)).
- **Inferences presented as facts.** A model's guess is labelled `model-inferred`, carries the asserter's own confidence and, ideally, its basis ([4.2.5](#425-basis)). It cannot outrank the person or an attestation ([4.7](#47-conflicts)). In health it is withheld until confirmed ([16.2](#162-health-context-profile)).
- **Institutional records.** An attestation is never quarantined or deprecated by a conflict or by the person's acceptance of another entry ([4.4](#44-declaration-types), [4.7.3](#473-resolution)). The person's correction therefore cannot silently rewrite it, and it cannot silently override the person.
- **Proposals that steer.** A proposal for resolving a conflict comes with its author's reasons and changes nothing until the person acts ([4.7.4](#474-proposals)). A provider or client that proposes the same outcome every time can still steer a person who accepts by habit. The audit log records who proposed what, and pilots report how often proposals were accepted ([G1.2](guides.md#g12-what-pilots-should-record)).
- **What a basis reveals.** `assertion.basis` is free text written by a client, and it is disclosed with the entry. The rule that it identifies no one but the person cannot be checked by the provider ([4.2.5](#425-basis)).
- **Export integrity.** An export is not yet signed. A receiving provider cannot tell whether it was altered on the way ([P1.4](path-to-v2-final.md#p14-later)).

## 21.3 Grants

- **Misleading consent screens.** A client could describe its request in flattering terms. Categories are described to the person as the provider describes them, not as the client does ([4.5](#45-category-vocabulary)), and purposes are shown before approval ([6.1.6](#616-authorization-is-distinct-from-authentication)). How screens are designed to avoid consent fatigue is guidance ([G4](guides.md#g4-authorization-interaction-patterns)).
- **How strongly the person was identified.** A grant is only as strong as the sign-in behind it. A sign-in through a messaging application rests on a phone number, which can be moved to another SIM card. The strength of the authentication behind each grant is recorded in `grant.issued` as `acr`, and a grant reaching a High-sensitivity category is expected to rest on more than a messaging sign-in alone ([6.1.6](#616-authorization-is-distinct-from-authentication)). Deployments with low connectivity may decide otherwise, and give up that assurance.
- **Stolen tokens.** Access tokens are short-lived, audience-restricted, and checked against the grant's status on every request ([13.4](#134-token-lifetime), [13.6](#136-security-baseline)). Refresh tokens for public clients are sender-constrained or rotated.
- **Delegates.** A delegate's authority is bounded by scope, term, `basis.covers`, and standing rules ([17.4](#174-scope-and-grants-under-a-delegation)). A sub-delegate's is bounded by its delegate's, and reaches one level only ([17.10](#1710-sub-delegation)). The person can revoke every grant either authorizes ([17.5](#175-the-context-subjects-override)).
- **Revocation and copies.** Revocation ends access and makes disclosed copies unusable once the client is notified ([6.2.2](#622-revocation-propagation)). It cannot recall a copy a client keeps unlawfully, and does not reach a copy kept under a declared legal obligation ([6.2.5](#625-copies-kept-under-a-legal-obligation)).

## 21.4 Disclosure

- **Sweeping a category.** A client that asks many rephrased queries can gather more than any one query returns. The quantity bound limits each response, and a provider may rate-limit a pattern of rephrased queries ([7.2](#72-quantity-bound)).
- **Linking a person across clients.** A disclosure carries a grant-scoped reference rather than the entry's identifier, and withholds the provenance that names other clients ([7.4](#74-disclosures-to-context-clients)). Two clients comparing notes can still match content itself. Provenance on request reveals the names of contributing clients only to the person's own assistant ([7.4.1](#741-provenance-on-request)).
- **Copies outliving their use.** Use-until is an obligation, not a technical control ([7.6](#76-use-until)). A client without a notification endpoint receives short-lived copies.
- **Onward sharing.** Where the person allowed it, a client may tell other organizations what a task needs from Low-sensitivity context ([3.12](#312-onward-disclosure)). The receiving organization is outside HCP: no grant, use-until or revocation reaches it. The protections are the limits on what may pass (Low sensitivity only, the client's own words, no entries or credentials), the person's separate election ([6.1.4](#614-grant-distinction-temporary-vs-persistent)), standing rules and directives, and the report of each share in the person's log ([5.2.8](#528-report-onward-sharing)). A client that shares without reporting cannot be detected by the provider, but has broken a rule it took on ([21.1](#211-what-hcp-does-not-prevent)).
- **Receiving systems.** Before approval, a person can know a client's operator, its purposes, its claims, and any legal retention ([6.1.6](#616-authorization-is-distinct-from-authentication)). They cannot yet require evidence of how the receiving system protects what it receives. Recipient assurance — attested environments, declared protection regimes, trust registries — is later work ([P1.4](path-to-v2-final.md#p14-later)).

## 21.5 Rules

- **Standing rules** are enforced by the provider, and apply across every grant from the moment they are set ([6.3](#63-standing-rules)).
- **Directives** bind only a client that claims to follow them, and only as far as it keeps its claim ([6.4](#64-directives)). The provider cannot observe compliance. Directives are delivered with every disclosure, so a client cannot say it did not know them.
- **What a directive's text reveals.** A directive's wording reaches every client it applies to. "Never share my HIV status" discloses what it means to protect. The Management Client is expected to warn the person, and to suggest scoping such a directive to its category ([6.4](#64-directives)).
- **Unknown actions.** A client that does not recognize a directive's action is not to treat it as a permission ([6.4](#64-directives)). It can still misread the person's words.

## 21.6 Audit

- **Tampering.** Append-only means the log cannot be altered through HCP; it does not detect alteration made outside it. Providers declare the log's integrity ([8.7](#87-integrity)). A provider holding High-sensitivity categories is expected to declare at least `hash-chained`. A common format for chains and checkpoints is later work ([P1.4](path-to-v2-final.md#p14-later)).
- **Joining the two logs.** The controller-side log may outlive a person's data, and is designed so that it cannot be joined to the person's own log to reconstruct content or infer it from access patterns ([8.5](#85-controller-side-logging)). A pseudonym stable across the operator's whole population would allow that join; a per-person or rotating pseudonym resists it.
- **Who reads the log.** Clients never do ([8.3](#83-access-to-the-audit-log)). A delegate reads the events of grants they or their sub-delegates authorized, and a former delegate keeps a limited view, because consenting for someone else carries accountability ([17.7](#177-audit-access)).
- **Volume.** Read logging is costly, and compaction waits for evidence of what it costs ([P1.4](path-to-v2-final.md#p14-later)).

## 21.7 Discovery and Identity

- **Who a client is.** A client is identified by its registration, which names its operator ([3.2.8](#328-client-operator-and-provider-operator)). A client that writes `issuer-attested` entries, or claims to follow directives, is expected to authenticate with an asymmetric key rather than a shared secret ([13.6](#136-security-baseline)). Identifying a client by a metadata document at an HTTPS URL, as MCP and other agent protocols do, lets a provider see who a client is without prior registration. It does not tell the provider whether the client is trustworthy.
- **Who an issuer is.** An issuer's key is found from its identifier, by DID resolution where it is a DID ([14.6](#146-ingest)). An issuer authorizes a client to attest for it by a credential the provider can verify ([14.10](#1410-attestation-authorizations)). A recorded arrangement is recorded as `unverified`, because the provider has only its own word for it ([3.7](#37-statements-attributed-to-the-context-subject)).
- **Wallets.** A wallet that holds a person's credentials or keys is part of their trust domain where it acts only for them ([4.8](#48-encrypted-storage)). How a wallet proves what it is to a provider is not specified.
- **Discovery documents.** A discovery document is served over HTTPS from the provider's base URL. A client trusts it as far as it trusts that origin ([19](#19-discovery-document)).

## 21.8 Keys

| Key | Held by | What its compromise allows |
|----------------------------|--------------------------------|------------------------------------------------------------------|
| Revocation notification signing key | HCP Provider ([9.9](#99-revocation-notification-delivery)) | Forged revocation notices, which make clients discard copies they could lawfully use. A forged notice cannot grant access. |
| Issuer signing key | Issuer | Forged credentials that verify, until the issuer revokes the key or its credentials ([14.7](#147-credential-status)) |
| Attestation authorization | Client, issued by the issuer ([14.10](#1410-attestation-authorizations)) | Writes attributed to the issuer, within the authorization's scope, until it is revoked |
| Content keys under `e2e` | The Context Subject's trust domain ([4.8](#48-encrypted-storage)) | Reading the person's content. Losing every copy loses the content ([G1.4](guides.md#g14-end-to-end-encrypted-deployments)). |
| Client credentials | Client | Acting as the client within its grants, until revoked ([6.2](#62-revocation)) |

Rotation, storage in hardware where available, and recovery that does not hand keys to an operator are deployment matters. The table says what each key protects, so that a deployment knows what is at stake.

## 21.9 The Trust Domain

Under end-to-end encrypted storage, the component that holds the person's keys does the work that reads content ([4.8](#48-encrypted-storage)). It becomes a target in its own right.

- **Compromise.** Whoever controls the component can read the person's content and answer queries as it chooses. It runs on a device or service the person controls, so its security is theirs to keep, with whatever help the deployment gives.
- **Vouching for a forgery.** The component verifies credentials for the provider, and the result is recorded with `verification.by` `trust-domain` ([4.2.2](#422-evidence)). Where a person stands to gain from a forged credential — an age threshold, eligibility — a component under their control could vouch for one. A client making a consequential decision on a credential is expected to verify it itself, under either storage posture ([3.6](#36-asserter-assurance)).
- **Unavailability.** A query that needs an unreachable component fails with subject unavailable ([5.5](#55-errors)). An attacker who can keep the component offline can deny service, but cannot obtain weaker answers.
- **What remains visible.** The operator still sees categories, timing, and provenance ([4.8](#48-encrypted-storage)). For some people, holding a category at all is sensitive.

## 21.10 Models

- **Context as untrusted input.** An entry's content was written by some client, and may carry text crafted to steer a model that later reads it: an instruction hidden in a note, a "directive" that is not one. A client is expected to present disclosed content, and the text of directives, to a model as data and never as instructions ([7.4](#74-disclosures-to-context-clients)).
- **Directives and models.** Directives bind the client, not the model. Under the MCP Binding the host applies them; placing a directive in a model's context is not following it ([10.5](#105-who-holds-the-grant)).
- **What models write.** A model's inferences are labelled as such and carry no standing against the person ([4.4](#44-declaration-types), [4.7](#47-conflicts)). A model that writes repeatedly can still crowd a category with guesses; where inferences from the same asserter contradict each other and neither is confirmed, the later one prevails ([4.7](#47-conflicts)).
- **Intermediaries.** A model or service between the person and a client may owe the person no duty at all. Loyalty obligations for such intermediaries are the subject of fiduciary governance work outside HCP ([I10](introduction.md#i10-related-work)).

## 21.11 Which Values the Defaults Put First

Every default in HCP favours some values over others. Learning Economy Foundation reviewers, raising a point from Carissa, asked that this be said plainly.

HCP's defaults put the person's autonomy and privacy first:

- No client receives context without a grant the person approved, for purposes they saw ([6.1.6](#616-authorization-is-distinct-from-authentication)).
- Copies are short-lived by default, and shorter for sensitive categories ([7.6](#76-use-until)).
- Standing rules only deny, and directives only narrow ([6.3](#63-standing-rules), [6.4](#64-directives)).
- Inferences wait for the person in health, and never outrank them ([16.2](#162-health-context-profile), [4.7](#47-conflicts)).
- Conflicts are settled by the person, not by the provider ([4.7.3](#473-resolution)).

These choices have costs, and the costs fall on others as well as on the person:

- **Care coordination.** A clinic, a caregiver, or a teacher may not see context that would help, because the person never granted it, or granted it briefly.
- **Emergencies.** HCP has no emergency access. A clinician cannot reach context the person has not granted, however urgent the need. Emergency access is later work ([P1.4](path-to-v2-final.md#p14-later)).
- **The work of consent.** Every grant is a decision the person makes. People asked too often stop reading what they approve ([G4](guides.md#g4-authorization-interaction-patterns)).
- **Relationships.** Rules that only deny cannot express "share this with my family". A delegate or a grant does that work, more slowly.

A deployment may tune some of these within the specification: use-until within its floor and ceilings, how consent is presented ([G4](guides.md#g4-authorization-interaction-patterns)), and how delegations are set up ([17](#17-delegated-authorization-profile)). It may not tune away the grant, the audit log, or the person's power to revoke.
# Appendix A. Registries and Published Artifacts

This appendix records the registries and published artifacts this specification depends on. Only the registries are normative ([1.1](#11-parts)).

## A.1 Registries

Each registry lists the values defined in this draft. The meaning of each value is defined in the section cited, and that definition governs. Until registries are published separately, this table is the registry.

| Registry | Values | Defined in | Open to new values |
|------------------------------|------------------------------------------------------------------|--------------|------------------------------|
| Conformance identifiers | One per Part, as listed | 1.7 | By later versions of this specification |
| Categories | Version 1: `general_preferences`, `goals_and_constraints`, `health_context`, `education_learner_profile`, `work_context`, `purchase_history_preferences`, `values_and_ethics`, `location_context`, `coordination_context` | 4.5 | By a new version of the category registry, versioned separately ([4.5](#45-category-vocabulary)). Custom categories are URIs and are not portable |
| Declaration types | `person-declared`, `model-inferred`, `issuer-attested` | 4.4 | No |
| Entry status | `active`, `deprecated`, `conflicted`, `expired`, `revoked`, `suspended`, `deleted` | 4.2, 4.2.4 | No |
| Entry schemas | `https://hcp.example/spec/entry/2.0` | 4.2, 4.3 | By later versions of this specification |
| Export schemas | `https://hcp.example/spec/export/2.0` | 5.4.1 | By later versions of this specification |
| Content profiles | The General Context Profile ([11](#11-general-context-profile)) and VC Evidence Profile ([14](#14-vc-evidence-profile)) identifiers | 4.2 | Yes, as URIs |
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

No vocabulary is registered for `classification.dimension` ([4.2](#42-entry)), `record.metadata` ([4.2](#42-entry)), the keys of a narrowed grant's `narrowedTo` ([6.1.5.1](#6151-narrowed-grants)), or `subject.relationship` ([11.3](#113-relationship)). Each is a candidate for a later registry ([P1](path-to-v2-final.md#p1-roadmap)).

## A.2 Published Artifacts

Identifiers use the placeholder namespace ([1.7](#17-conformance-identifiers)). Dates are given in each draft's memo, not here.

| Artifact | Identifier | Needed for | Notes |
|----------------------------|-------------------------------------------|----------------------------------------------|---------------------------------------------------|
| Entry JSON Schema | https://hcp.example/schemas/2.0-draft-3/entry.json | Validating entries ([4.1.1](#411-processing-requirements), [11.1](#111-scope)) | The suite's first function depends on it ([20](#20-conformance-testing)) |
| Core schemas | https://hcp.example/schemas/2.0-draft-3/ | The MCP tools' `inputSchema` and `outputSchema` ([10.3](#103-tools)) | One request and one result schema per operation ([5](#5-operations-and-errors)) |
| Audit event and discovery schemas | https://hcp.example/schemas/2.0-draft-3/audit-event.json, .../discovery.json | Testing the audit log ([8.2](#82-log-entry-structure)) and the discovery document ([19](#19-discovery-document)) | Used by the conformance suite ([20](#20-conformance-testing)) |
| Problem-type namespace | https://hcp.example/problems/ | HTTP error responses ([9.7](#97-errors)) | The type names are normative here and testable without the namespace resolving |
| JSON-LD context | https://hcp.example/contexts/v2 | The `@context` of every entry ([4.2](#42-entry)) | Not a processing requirement ([4.1.1](#411-processing-requirements)) |
| Conformance identifiers | https://hcp.example/spec/... | Conformance claims ([18.1](#181-claims)) | Compared as exact strings; need not resolve ([1.7](#17-conformance-identifiers)) |

**Core schemas.** One schema each for the request and the result of query, get entry, create, revise, withdraw, reading one's own grant, relinquishing it, and reporting onward sharing ([5.2](#52-context-operations)), of import, the disclosure summary, and the delegations list ([5.4.3](#543-import), [8.6](#86-disclosure-summary), [9.4.13](#9413-delegations)), plus the entry ([4.2](#42-entry), [11](#11-general-context-profile), [14](#14-vc-evidence-profile)), the export ([5.4.1](#541-export)), the disclosure ([7.4](#74-disclosures-to-context-clients)), the grant ([6.1.5](#615-grant-representation)), the delegation ([17.2](#172-delegations)), the standing rule ([6.3](#63-standing-rules)), the directive ([6.4](#64-directives)), the minimization report ([7.5](#75-reporting)), and the Core error ([5.5](#55-errors)), with HTTP problem details ([9.7](#97-errors)). Schemas are written in JSON Schema 2020-12, under a base that names the draft. They are open: they admit members this specification does not define, which an HCP Provider preserves ([A.3](#a3-extension-points)). Where a schema and the text of this specification differ, the text governs.

**JSON-LD context.** The context is published for semantic interoperability. Conformance requires no JSON-LD processing ([4.1.1](#411-processing-requirements)), and a credential in `evidence` does not reference the HCP context ([14.2](#142-credential-and-signature-boundary)), so no conformance requirement depends on the context resolving. A draft of the key terms, updated for this draft's entry structure:

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

`capturedBy` and `userVerified` are removed ([3.5](#35-provenance-layers)). `credentialType`, `NLPreference`, `VerifiablePreference`, and `claim` are removed with the tiers ([4.2](#42-entry)).

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
# References

A normative reference is one an implementation needs in order to conform. Where a reference names no version, the version current at this draft's date applies. The last column lists where each is cited, by section.

## Normative References

| Reference | Title | Cited in |
|----------------|------------------------------------------------------------|----------------|
| BCP 14 | Key words for use in RFCs to Indicate Requirement Levels (RFC 2119) and Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174), IETF. https://www.rfc-editor.org/info/bcp14 | 1.8 |
| RFC 3339 | Date and Time on the Internet: Timestamps, IETF. https://www.rfc-editor.org/rfc/rfc3339 | 1.10 |
| RFC 9562 | Universally Unique IDentifiers (UUIDs), IETF. https://www.rfc-editor.org/rfc/rfc9562 | 4.2 |
| RFC 6749 | The OAuth 2.0 Authorization Framework, IETF. https://www.rfc-editor.org/rfc/rfc6749 | I9, 13.1, 13.3 |
| RFC 7523 | JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants, IETF. https://www.rfc-editor.org/rfc/rfc7523 | 13.6 |
| RFC 7636 | Proof Key for Code Exchange by OAuth Public Clients, IETF. https://www.rfc-editor.org/rfc/rfc7636 | I9, 13.6 |
| RFC 8417 | Security Event Token (SET), IETF. https://www.rfc-editor.org/rfc/rfc8417 | I9, 6.2.3, 9.9 |
| RFC 8628 | OAuth 2.0 Device Authorization Grant, IETF. https://www.rfc-editor.org/rfc/rfc8628 | I9, 13.2, 13.3 |
| RFC 8705 | OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens, IETF. https://www.rfc-editor.org/rfc/rfc8705 | 13.6 |
| RFC 8707 | Resource Indicators for OAuth 2.0, IETF. https://www.rfc-editor.org/rfc/rfc8707 | I9, 13.3 |
| RFC 8935 | Push-Based Security Event Token (SET) Delivery Using HTTP, IETF. https://www.rfc-editor.org/rfc/rfc8935 | I9, 9.9 |
| RFC 9396 | OAuth 2.0 Rich Authorization Requests, IETF. https://www.rfc-editor.org/rfc/rfc9396 | I9, I10, 2.8, 6.1.5, 13.3 |
| RFC 9457 | Problem Details for HTTP APIs, IETF. https://www.rfc-editor.org/rfc/rfc9457 | I9, 9.7 |
| RFC 9700 | Best Current Practice for OAuth 2.0 Security, IETF. https://www.rfc-editor.org/rfc/rfc9700 | I9, 13.1, 13.6 |
| RFC 9728 | OAuth 2.0 Protected Resource Metadata, IETF. https://www.rfc-editor.org/rfc/rfc9728 | I9, 13.5, 19.3 |
| VC Data Model 2.0 | Verifiable Credentials Data Model v2.0, W3C. https://www.w3.org/TR/vc-data-model-2.0/ | I9, 2.8, 3.2.10, 14.2, 14.5 |
| VC Data Integrity | Verifiable Credential Data Integrity 1.0, W3C. https://www.w3.org/TR/vc-data-integrity/ | I9, 14.5 |
| VC DI EdDSA | Data Integrity EdDSA Cryptosuites v1.0, W3C. https://www.w3.org/TR/vc-di-eddsa/ | I9, 14.4, 14.5, 14.9, 16.4, 19.2, 19.3, 19.4, … |
| VC DI ECDSA | Data Integrity ECDSA Cryptosuites v1.0, W3C. https://www.w3.org/TR/vc-di-ecdsa/ | I9, 14.5, 14.9, 16.4, 19.2, 19.3, 19.4, A.1, … |
| VC-JOSE-COSE | Securing Verifiable Credentials using JOSE and COSE, W3C. https://www.w3.org/TR/vc-jose-cose/ | I9, 14.5, 14.9, G3.5, P1.5 |
| Bitstring Status List | Bitstring Status List v1.0, W3C. https://www.w3.org/TR/vc-bitstring-status-list/ | I9, 14.7, 16.4 |
| JSON-LD 1.1 | JSON-LD 1.1, W3C. https://www.w3.org/TR/json-ld11/ | I9, 4.1.1, 5.4.1, 8.3, 14.2, A.2 |
| DID 1.0 | Decentralized Identifiers (DIDs) v1.0, W3C. https://www.w3.org/TR/did-1.0/ | I4, I10, 4.2, 14.6, 21.7 |
| JSON Schema 2020-12 | JSON Schema, draft 2020-12 (Core and Validation). https://json-schema.org/draft/2020-12 | 1.10, 4.1.1, 11.1, 20.1, A.2 |
| MCP 2026-07-28 | Model Context Protocol, revision 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28 | I3, I4, I6, I9, I10, I11, I12, 1.1, … |
| Open Badges 3.0 | Open Badges Specification 3.0, 1EdTech. https://www.imsglobal.org/spec/ob/v3p0/ | I4, I9, I10, 1.3, 4.1, 14.4, 16.4, G2.1, … |
| OpenID Connect Core 1.0 | OpenID Connect Core 1.0, OpenID Foundation. https://openid.net/specs/openid-connect-core-1_0.html | 6.1.6 |

## Informative References

| Reference | Title | Cited in |
|----------------|------------------------------------------------------------|----------------|
| ISO 8601 | Date and time — Representations for information interchange (ISO 8601-1:2019), ISO. https://www.iso.org/standard/70907.html | 1.10 |
| RFC 7662 | OAuth 2.0 Token Introspection, IETF. https://www.rfc-editor.org/rfc/rfc7662 | 6.2.2 |
| RFC 9111 | HTTP Caching, IETF. https://www.rfc-editor.org/rfc/rfc9111 | 7.6 |
| RFC 9901 | Selective Disclosure for JSON Web Tokens (SD-JWT), IETF. https://www.rfc-editor.org/rfc/rfc9901 | 14.5, 14.9, P1.5 |
| VC DI BBS | Data Integrity BBS Cryptosuites v1.0, W3C. https://www.w3.org/TR/vc-di-bbs/ | P1.4 |
| UMA 2.0 | User-Managed Access (UMA) 2.0 Grant for OAuth 2.0 Authorization, Kantara Initiative. https://docs.kantarainitiative.org/uma/wg/rec-oauth-uma-grant-2.0.html | 2.8, 3.2.10 |
| CLR 2.0 | Comprehensive Learner Record Standard 2.0, 1EdTech. https://www.imsglobal.org/spec/clr/v2p0/ | I10, G2.3 |
| CASE | Competencies and Academic Standards Exchange (CASE), 1EdTech. https://www.imsglobal.org/activity/case | G2.3 |
| HL7 FHIR | Fast Healthcare Interoperability Resources, HL7. https://hl7.org/fhir/ | I9, G3.7 |
| SNOMED CT | SNOMED CT, SNOMED International. https://www.snomed.org/ | 4.2, G3.7 |
| ISO/IEC 18013-5 | Personal identification — ISO-compliant driving licence — Part 5: Mobile driving licence (mDL) application, ISO/IEC. https://www.iso.org/standard/69084.html | P1.5 |
| Personal Agent Protocol 0.3 | Personal Agent Protocol, draft 0.3, Sierra and Meta. https://personalagentprotocol.org/docs/0.3/spec | I4, I11 |
| A2A 1.0 | Agent2Agent (A2A) Protocol 1.0, Linux Foundation. https://a2a-protocol.org/ | I4, I11 |
| Solid Protocol 0.11 | Solid Protocol, version 0.11, W3C Solid Community Group. https://solidproject.org/TR/protocol | I11 |
| Open Memory Protocol | Open Memory Protocol, early drafts, Open Memory Protocol Initiative (AI Disclosures Project, co-hosted by Mozilla and IBM). https://github.com/SMJAI/open-memory-protocol | I4, I11 |
| TPLC | Trusted Portable Learning Context, 1EdTech. https://www.1edtech.org/ai/tplc | I10, I11 |
| PDPP | Personal Data Portability Protocol, PDP-Connect (Linux Foundation Decentralized Trust). https://pdpp.dev/ | I10, I11, 6.1.5.2 |

---

The specification text is licensed under CC BY 4.0 ([LICENSE-SPEC.md](../../LICENSE-SPEC.md)). These pages are built from the same source as the Word document by `tools/make_pages.py`; where they differ, please report it as an issue.
