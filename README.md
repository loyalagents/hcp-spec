# Human Context Protocol (HCP)

The Human Context Protocol is an open, person-governed standard for representing, storing, and sharing personal AI memory and preferences across systems. Applications and assistants ask a person's HCP instance for the context they need, under explicit authorization, for a purpose the person approved, and for a limited time. The person can see who accessed what and when, correct what is stored, and revoke access at any time.

**Status.** HCP v2 is a working draft for review. The current draft is **2.0-draft-3** (November 2026). It is not stable: later drafts change the wire format. Do not build production systems against it without following the drafts.

Editor: Beth Porter, Loyal Agents initiative.

## What is here

| Path | Contents |
|------|----------|
| `spec/2.0-draft-3/` | The specification as four pages, for reading here: [Introduction](spec/2.0-draft-3/introduction.md), [Specification](spec/2.0-draft-3/specification.md), [Guides](spec/2.0-draft-3/guides.md) and [Path to v2 Final](spec/2.0-draft-3/path-to-v2-final.md), with their diagrams in `images/`. Introduction section I8 says where each audience should start |
| `spec/2.0-draft-3/source/` | The Markdown source the Word document and the pages are built from, one file per page or section (`tools/restructure.py` lists them in order) |
| `spec/2.0-draft-2/` | Draft 2's source, in its own layout: `title_clean.md` and `s1.md` to `s27.md` |
| `schemas/2.0-draft-3/`, `schemas/2.0-draft-2/` | JSON Schemas (2020-12) for the objects and Core operations the specification lists (Draft 3: A.2; Draft 2: 25.2), plus the audit event, the discovery document and HTTP problem details |
| `tools/` | The build: the Word document, a redline between two drafts, the schemas, and the schema checks |
| `template/` | The Word template the build uses (styles only) |

The Word documents for each draft are attached to its release.

## Design investigations

- [Encryption design review and investigation](docs/design/encryption-review.md):
  Draft 3's storage guarantees, E2E delivery and trust-boundary gaps, related
  lifecycle issues, and the decisions and validation needed for a revision.
  This is a non-normative investigation; proposed changes are not adopted requirements.

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

The schema checks validate every JSON example in the specification. Concrete examples, such as the HTTP Binding's in Draft 3, are validated in full; templates with `{placeholders}` are compared member by member.

## Building and checking

Requires Python 3.10 or later and `jsonschema` (4.18 or later). The tracked-changes round trip also needs LibreOffice.

    pip install jsonschema
    make check     # regenerate the schemas and check them against every JSON example in the specification
                   # (DRAFT=2.0-draft-2 for Draft 2; the default is the current draft)
    make docx      # build the Word document from the Markdown source
    make pages     # rebuild the four pages from the source (Draft 3 on)

`tools/make_schemas.py` generates the schemas. Change it rather than editing the JSON by hand, then run `make check`.

## Licences

- The specification text (`spec/`) is licensed under [Creative Commons Attribution 4.0 International](LICENSE-SPEC.md).
- The schemas, tools and template (`schemas/`, `tools/`, `template/`) are licensed under the [Apache License, Version 2.0](LICENSE).
