# Human Context Protocol (HCP)

The Human Context Protocol is an open, person-governed standard for representing, storing, and sharing personal AI memory and preferences across systems. Applications and assistants ask a person's HCP instance for the context they need, under explicit authorization, for a purpose the person approved, and for a limited time. The person can see who accessed what and when, correct what is stored, and revoke access at any time.

**Status.** HCP v2 is a working draft for review. The current draft is **2.0-draft-3** (November 2026). It is not stable: later drafts change the wire format. Do not build production systems against it without following the drafts.

This repository is currently private for invited partner review. Public release is a separate decision. Record both the draft identifier and the Git commit when reviewing or experimenting: corrections can land within a draft before the next numbered draft.

Editor: Beth Porter, Loyal Agents initiative.

This working draft has not been formally reviewed or endorsed by Stanford University, Consumer Reports, or any convening partner. Named examples and acknowledgments describe inputs to the draft, not implementation certification or institutional endorsement.

## Reviewing HCP?

| Your goal | Start here |
|-----------|------------|
| Understand the proposal | [HCP in brief](spec/2.0-draft-3/introduction.md#i3-hcp-in-brief), [worked use cases](spec/2.0-draft-3/introduction.md#i5-worked-use-cases), then [open questions](spec/2.0-draft-3/path-to-v2-final.md#p11-before-v2-is-final) |
| Assess an integration | [Audience guide](spec/2.0-draft-3/introduction.md#i8-intended-audiences), [Core, bindings and profiles](spec/2.0-draft-3/specification.md#11-parts), then [pilot guidance](spec/2.0-draft-3/guides.md#g1-pilot-onboarding) and the artifact status below |
| Review a design or propose a correction | [Roadmap](spec/2.0-draft-3/path-to-v2-final.md#p1-roadmap), [security and privacy limits](spec/2.0-draft-3/specification.md#21-security-and-privacy-considerations), and [contribution guidance](CONTRIBUTING.md) |

We particularly welcome feedback on:

- A concrete use case that the roles, grants, or profiles cannot express clearly.
- Where consent, disclosure, revocation, or downstream client obligations are ambiguous.
- Where two independent implementations could reasonably interpret a requirement differently.
- Which unresolved encryption or lifecycle questions would prevent a useful pilot.

[Open a specification feedback issue](https://github.com/loyalagents/hcp-spec/issues/new?template=spec-feedback.md). Include the draft and commit, section numbers, a synthetic example, and the ambiguity or change you want considered. Questions and reports of missing behavior are welcome without a proposed solution. See [CONTRIBUTING.md](CONTRIBUTING.md) for focused corrections and design proposals.

## Drafts and available artifacts

| Artifact | Current status |
|----------|----------------|
| Draft 3 reading pages and schemas | Available in this repository; an unreleased working revision. Use a commit-specific link for a reproducible review. |
| Draft 3 Word document | Buildable from source with `make docx`; no Draft 3 GitHub release or downloadable release document has been published yet. |
| Draft 2 release | [Historical review snapshot](https://github.com/loyalagents/hcp-spec/releases/tag/2.0-draft-2), with links to its Word specification, redline, and revision memo. It remains a working draft even though GitHub displays it as the latest release. |
| Changes and remaining work | [Draft changelog](spec/2.0-draft-3/path-to-v2-final.md#p3-changelog) and [roadmap](spec/2.0-draft-3/path-to-v2-final.md#p1-roadmap). |
| Schema/example checks | Available through `make check`; their scope is described below. They do not test a running provider or certify conformance. |
| Implementations | Projects are listed below with their own compatibility notes. This repository does not designate a validated Draft 3 reference implementation. |
| Behavioral conformance suite | Planned in [section 20](spec/2.0-draft-3/specification.md#20-conformance-testing); not yet published here or linked as an available suite. |

Draft 3's E2E delivery and trust boundaries, and the interaction between hard deletion and response replay, remain under investigation. [PR #18](https://github.com/loyalagents/hcp-spec/pull/18) records the review findings and candidate remedies; they are not adopted protocol changes. The [roadmap](spec/2.0-draft-3/path-to-v2-final.md#p11-before-v2-is-final) summarizes the questions for reviewers.

## What is here

| Path | Contents |
|------|----------|
| `spec/2.0-draft-3/` | The specification as four pages, for reading here: [Introduction](spec/2.0-draft-3/introduction.md), [Specification](spec/2.0-draft-3/specification.md), [Guides](spec/2.0-draft-3/guides.md) and [Path to v2 Final](spec/2.0-draft-3/path-to-v2-final.md), with their diagrams in `images/`. Introduction section I8 says where each audience should start |
| `spec/2.0-draft-3/source/` | The Markdown source the Word document and the pages are built from, one file per page or section (`tools/restructure.py` lists them in order) |
| `spec/2.0-draft-2/` | Draft 2's source, in its own layout: `title_clean.md` and `s1.md` to `s27.md` |
| `schemas/2.0-draft-3/`, `schemas/2.0-draft-2/` | JSON Schemas (2020-12) for the objects and Core operations the specification lists (Draft 3: A.2; Draft 2: 25.2), plus the audit event, the discovery document and HTTP problem details |
| `tools/` | The build: the Word document, a redline between two drafts, the schemas, and the schema checks |
| `template/` | The Word template the build uses (styles only) |

The source files are the editing inputs for both the reading pages and Word builds. See the artifact table above for available downloads.

## Implementation repositories

Projects implementing or exploring HCP. Each repository documents its own scope
and compatibility.

| Repository | Description |
|------------|-------------|
| [Context Router](https://github.com/loyalagents/context-router) | Local-first personal memory application. See its [HCP integration notes](https://github.com/loyalagents/context-router/blob/main/docs/useful/HCP_INTEGRATION.md). |

To add a project, link its repository, briefly describe its purpose, and include
implementation documentation when available.

## The schemas

Section numbers below are Draft 3's. Draft 2's schemas, in `schemas/2.0-draft-2/`, follow Draft 2's numbering (its 25.2 is Draft 3's A.2).

- Each schema's `$id` is under `https://hcp.example/schemas/<draft>/`. `hcp.example` is a placeholder namespace (section 1.7) and does not resolve. Resolve references locally, from the schema directory.
- Schemas are open: members the specification does not define are allowed, because a provider must preserve them (4.2, A.3). Where the text says a member is withheld, as for an entry's `id` in a disclosure (7.4), the schema forbids it.
- Some rules relate members to each other in ways a schema cannot state. Two of them are checked by `tools/check_schemas.py`: a VC Evidence entry's `content.evidence` names an item whose role is `content`, and the credential's subject is the entry's subject (14.2). The rest are left to implementations.
- **Where a schema and the text differ, the text governs** (A.2). Please report a difference as an issue.

| Schema | Section |
|--------|---------|
| `entry.json` | 4.2, 11, 14 |
| `disclosure.json` | 7.4 |
| `grant.json` | 6.1.5 |
| `delegation.json` | 17.2 |
| `standing-rule.json` | 6.3 |
| `directive.json` | 6.4 (Draft 3) |
| `export.json` | 5.4.1 (Draft 3) |
| `minimization-report.json` | 7.5 |
| `error.json`, `problem.json` | 5.5, 10.4; 9.7 |
| `operations/` | 5.2.1 to 5.2.6, 5.2.8, 5.4.3, 8.6, 9.4.13: request and result of query, get entry, create, revise and withdraw; reading one's own grant; reporting onward sharing (Draft 3); import; the disclosure summary; the delegations list |
| `audit-event.json`, `discovery.json` | 8.2, 19 |
| `common.json` | Shared definitions |

The schema checker validates the published schemas and selected examples enumerated in `tools/check_schemas.py`. Selected concrete examples are validated in full; selected templates with `{placeholders}` are compared member by member. Coverage is not exhaustive: some HTTP examples and behavioral requirements are outside these checks. Passing them does not establish implementation conformance.

## Building and checking

Requires Python 3.10 or later and `jsonschema` (4.18 or later). The tracked-changes round trip also needs LibreOffice.

    pip install jsonschema
    make check     # regenerate and validate schemas, then check the selected examples
                   # (DRAFT=2.0-draft-2 for Draft 2; the default is the current draft)
    make docx      # build the Word document from the Markdown source
    make pages     # rebuild the four pages from the source (Draft 3 on)

`tools/make_schemas.py` generates the schemas. Change it rather than editing the JSON by hand, then run `make check`.

Edit Draft 3 text in `spec/2.0-draft-3/source/`, then run `make pages` and include the rebuilt pages in the same PR. CI regenerates the current draft's schemas and pages and fails if their tracked outputs differ. These are document and schema consistency checks, not runtime conformance tests.

## Licences

- The specification text (`spec/`) is licensed under [Creative Commons Attribution 4.0 International](LICENSE-SPEC.md).
- The schemas, tools and template (`schemas/`, `tools/`, `template/`) are licensed under the [Apache License, Version 2.0](LICENSE).
