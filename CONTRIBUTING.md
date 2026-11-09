# Reviewing and contributing to HCP

HCP is a working draft seeking partner feedback. Start with the
[reviewer routes](README.md#reviewing-hcp) and
[current artifact status](README.md#drafts-and-available-artifacts).
Repository access is currently private; publishing the repository or a new
release is a separate maintainer decision.

## Send useful feedback

[Open a specification feedback issue](https://github.com/loyalagents/hcp-spec/issues/new?template=spec-feedback.md)
for questions, missing use cases, ambiguities, and proposed changes. Include:

- The draft identifier and Git commit or commit-specific file link.
- The relevant section numbers and the role, binding, or profile involved.
- A short synthetic scenario showing the problem or differing interpretations.
- The outcome you need, and any suggested wording or alternatives you have.

A proposed solution is optional. Use invented examples rather than personal
context, partner records, or credentials. For feedback you cannot place in an
issue, use your existing contact with the maintainers; do not post sensitive
material merely to complete the template.

The [roadmap](spec/2.0-draft-3/path-to-v2-final.md#p11-before-v2-is-final)
identifies current open questions. Link an existing issue or review when your
feedback concerns the same question. Review findings and proposed remedies are
not adopted requirements.

## Propose a focused change

Small editorial corrections can be proposed directly in a pull request. For a
change to interoperability or a guarantee, explain the problem, the alternatives
considered, compatibility implications, and how the expected behavior could be
checked. An example can be a useful starting point; a new formal proposal system
is not required.

The normative text governs when it differs from a schema. Adopted changes must
update the relevant specification text and affected schemas and examples in the
same change; a discussion or design note is not a second specification.

## Edit and validate

Use Python 3.10 or later and the dependencies in the [README](README.md#building-and-checking).

- Edit current-draft prose in `spec/2.0-draft-3/source/`, then run `make pages`
  and include the generated Markdown and any affected diagrams in the PR.
- Change schema generation in `tools/make_schemas.py`, then run `make check`;
  include generated schemas rather than editing them by hand.
- Check local links and `git diff --check`. When changing an older draft,
  explicitly explain why; do not silently revise a historical release.
- Describe the checks actually performed and remaining gaps. Schema/example
  validation and generated-page consistency do not establish implementation
  conformance, security, or pilot readiness.

CI checks the current draft's schemas and generated reading pages. The
[changelog](spec/2.0-draft-3/path-to-v2-final.md#p3-changelog) summarizes numbered
drafts; commit-specific links identify intervening review corrections. Maintainers
decide when reviewed changes become a new draft or release.
