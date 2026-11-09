# Reviewing and contributing to HCP

HCP is a working draft seeking partner feedback. Start with the
[reviewer routes](README.md#reviewing-hcp) and
[current artifact status](README.md#drafts-and-available-artifacts).

## Send useful feedback

[Open a specification feedback issue](https://github.com/loyalagents/hcp-spec/issues/new?template=spec-feedback.md)
for questions, missing use cases, ambiguities, and proposed changes. Include:

- The draft identifier and Git commit or commit-specific file link.
- The relevant section numbers and the role, binding, or profile involved.
- A short synthetic scenario showing the problem or differing interpretations.
- The outcome you need, and any suggested wording or alternatives you have.

A proposed solution is optional. Use invented examples rather than personal
context, partner records, or credentials. For sensitive feedback, use your
existing contact with the maintainers.

The [roadmap](spec/2.0-draft-3/path-to-v2-final.md#p11-before-v2-is-final)
identifies current open questions. Link an existing issue or review when your
feedback concerns the same question. Review findings and proposed remedies are
not adopted requirements.

## Edit and validate

Small editorial corrections can go directly into a focused PR. Larger technical
questions belong in issues first, with a scenario, alternatives, and the behavior
that needs agreement. The normative text governs when it differs from a schema.

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

The [changelog](spec/2.0-draft-3/path-to-v2-final.md#p3-changelog) summarizes numbered
drafts; commit-specific links identify intervening review corrections.
