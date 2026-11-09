# OAuth and browser integration lessons

This is **non-normative adoption guidance**, based on Context Router's isolated
C2 experiment. It adds no protocol requirements and does not designate that
experiment, an OAuth library, or a browser as an HCP reference implementation.

The experiment targeted **HCP 2.0-draft-3 at
`2e2939c9bebcefb3bed7bb3522231c0e4d65a315`**, particularly
[authorization (§6)][authorization] and [OAuth interoperability (§13)][oauth-spec].
Normative text governs. Reassess these observations when the draft, library,
browser, or deployment changes.

## Preserve HCP authority through the OAuth flow

Use a maintained OAuth implementation for protocol processing, then explicitly
map its interactions and persistence hooks to the HCP grant. A library login
session, remembered consent, or library object called a "Grant" does not by itself
establish the HCP actors, purposes, narrowing, expiry, and audit obligations.

For a flow creating a grant, bind the approving act to the reviewed request,
authenticated person, client, resource, restrictions, and absolute deadline.
For scope-only requests, collect the person's purposes before approval; do not
infer them from login. Keep human management credentials separate from Context
Client tokens. C2 required a fresh approval for every authorization request; that
is its experiment policy, not a new universal rule about reusing valid grants.

Keep one authoritative grant decision, even if protocol-processing objects live
elsewhere. Commit the grant and its required audit before releasing usable
credentials. Recheck current authority on credential use; cached library state
must not revive a revoked or expired grant. A shared SQLite transaction was C2's
implementation choice, not an HCP storage requirement.

Derive granted authorization details from that approved authority at code
creation, token persistence, and token response. Check scope-only approvals as
well as Rich Authorization Requests (RAR). Preserve narrowing in client output;
follow the own-grant privacy rules rather than exposing internal entry IDs.
[The C2 adapter and hooks][oauth-code] provide a concrete, bounded example.

## Qualify library configuration and advertised capabilities

C2 pinned **oidc-provider 9.13.3**, upstream commit
`7b21c6da77f61fb66adfec72e0d8247dda7248e6`. These are version-specific findings,
not defects in HCP or guarantees about other releases:

| Observation | Integration lesson |
| --- | --- |
| Enabling RAR globally was insufficient: each controlled client also needed the HCP type in `authorization_details_types`. | Test client registration, request validation, approved details, and returned details together. |
| Overriding `issueRefreshToken` caused refresh support to be advertised even when the replacement always returned false. | Check actual metadata and token behavior. For its no-refresh scope, C2 retained the native predicate, omitted `offline_access`, and registered authorization-code-only clients. |
| Resource fallback and permissive token parameters did not supply the experiment's explicit binding checks. | Validate the accepted request fields and resource binding; do not assume a library's successful exchange proves HCP authority. |
| RAR grant-source and access-token hooks run before adapter persistence. | Populate details from the committed HCP grant, enforce the deadline in storage, and check again before returning a successful token response. |

The refresh observation is grounded in the pinned upstream
[configuration logic][library-config] and [native predicate][library-defaults].
C2 required the exact configured resource at both authorization and token exchange
and rejected extra token fields; that strict input set is an experiment choice,
not a general HCP extension policy. Unsupported narrowing still follows §6.1.5.1.

Test metadata against capabilities actually implemented. C2 selected Code + S256
PKCE, temporary grants, opaque tokens, and `form_post`, with no refresh. Its
one-hour access-token ceiling is stricter than the draft's maximum. Those choices
do not establish a minimum conforming feature set or resolve the
[existing question about required OAuth flows][flow-question].

For Authorization Code, apply the existing §13.6 requirements: PKCE for every
client, including confidential clients, and exact redirect matching. Do not rely
on a library default that requires PKCE only for public clients. C2 explicitly
required PKCE for every registered client and tested wrong or missing verifiers.

## Test cookies, redirects, and CSRF in a real browser

**Different ports do not isolate cookies.** Cookies are shared across ports on
the same host ([RFC 6265 §8.5][cookies]). C2 used distinct controlled hosts for the
Authorization Service and each client callback, all mapped only to loopback,
with certificates covering those hostnames. Listeners bound to `127.0.0.1` and
validated their configured Host; they did not trust forwarded host headers.

Use host-only cookies without a parent `Domain`. C2's human cookie used the
`__Host-` prefix, `Path=/`, `Secure`, `HttpOnly`, and `SameSite=Strict`.
Distinct sibling hosts may still be same-site: SameSite alone does not provide
origin checking or CSRF protection. Verify actual callback request headers for
authorization-service and human-cookie leakage.

C2 used `form_post` to keep authorization codes out of callback URLs and checked
state and issuer before exchange. That response mode is an experiment choice.
Inspect real navigations, callback bodies, and cookie dispatch; a Node HTTP
driver alone cannot establish browser behavior.

In the tested Chromium build, `Referrer-Policy: no-referrer` caused form POSTs
to carry `Origin: null`, conflicting with the same-origin CSRF check. C2 used
`strict-origin` and retained exact Origin, CSRF-token, and session/request checks.
That policy sends origin information, not paths or query strings. Do not fix the
interaction by generally accepting a null Origin. Re-test the complete flow in
each supported browser. See the [human controls][http-code] and
[browser fixture][browser-test].

## Verify TLS without weakening the test

Use a disposable browser profile and an owned test CA; leave TLS verification
enabled and preserve personal profiles and system trust. Establish that a fresh
profile rejects the CA, then that the intended profile trust configuration allows
the valid leaf. Confirm wrong-hostname and expired leaves still fail before an
HTTP request reaches the listener.

C2 exercised Chromium **153.0.8010.12 / revision 1243** with Playwright **1.63.0**
on macOS and Linux. Its fixture writes the pinned browser's per-profile trust
database while the browser is stopped. Treat that mechanism as a version-bound
test detail to requalify, not a stable browser API or production trust recipe.
Validate TLS configuration before acquiring persistent-store ownership, or
ensure synchronous TLS-construction failure releases that ownership.

## Carry failure and time tests alongside the happy path

Useful adoption tests include:

| Boundary | Evidence to seek |
| --- | --- |
| Consent | Login alone creates no grant; missing purposes require selection; changed policy or stale review cannot silently approve broader authority. |
| Client/grant separation | Two grants for client A and a grant for client B remain independently inspectable/revocable; human credentials and client tokens cannot substitute for each other. |
| Protocol binding | Wrong resource, redirect, verifier, actor substitutions, unsupported flows, and replay fail; token details match the granted restriction. |
| Concurrent code replay | A stale pre-consumption snapshot cannot leave a usable winner after replay invalidation. Commit required revocation before returning an error; an exception inside the same transaction must not roll it back. |
| Commit and expiry | Audit/commit failure releases no new authority; crossing token or grant expiry during persistence suppresses release. Restart never moves the absolute deadline. |
| Browser and cleanup | Real callbacks contain no AS/human cookies; invalid certificates fail; failed TLS startup permits same-process store reopen/reset; owned processes/profiles are cleaned up. |

Grant expiry, token expiry, and a disclosed copy's `useUntil` are distinct. Grant
expiry stops future retrieval without automatically shortening a previously
disclosed copy's deadline; revocation has separate obligations. Dormant-provider
audit timing remains unresolved in [issue #3][expiry-evidence]. The C2 recovery
tests are additional application evidence, not an amendment to that deadline.

## Evidence and limits

These lessons come from [Context Router PR #205][cr-pr], qualified head
`71d8433215009e4f2430ac6631a1f5392fb4c7ab`, tested by
[regular CI][cr-ci] and [source/UI/packaging qualification][cr-qualification].
The [native HTTPS tests][https-test], [process-recovery tests][recovery-test],
and [browser fixture][browser-test] identify what was exercised. See the
[application record][cr-record] for configuration and review findings.

C2 used synthetic actors and controlled clients. It did not implement public
entry query/get, content-disclosure coordination, notification delivery, an
installed-app integration, or complete profile/package conformance. Its
process-loss and controlled-clock tests do not establish physical power-loss or
cross-boot behavior. A working local consent flow does not settle production
local discovery/trust or another assistant host's responsibilities.

[authorization]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s6.md
[oauth-spec]: https://github.com/loyalagents/hcp-spec/blob/2e2939c9bebcefb3bed7bb3522231c0e4d65a315/spec/2.0-draft-3/source/s13.md
[library-config]: https://github.com/panva/node-oidc-provider/blob/7b21c6da77f61fb66adfec72e0d8247dda7248e6/lib/helpers/configuration.js#L476
[library-defaults]: https://github.com/panva/node-oidc-provider/blob/7b21c6da77f61fb66adfec72e0d8247dda7248e6/lib/helpers/defaults.js#L306
[cookies]: https://www.rfc-editor.org/rfc/rfc6265.html#section-8.5
[oauth-code]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/apps/backend/src/infrastructure/hcp-experiment/oauth.ts
[http-code]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/apps/backend/src/infrastructure/hcp-experiment/http.ts
[browser-test]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/apps/web/test/hcp-oauth-browser.test.mjs
[https-test]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/apps/backend/test/local-database/hcp-experiment/oauth.test.cjs
[recovery-test]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/apps/backend/test/local-database/hcp-experiment/recovery.test.cjs
[flow-question]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/docs/plans/active/hcp-alignment/spec-questions.md#cr-q4
[expiry-evidence]: https://github.com/loyalagents/hcp-spec/issues/3#issuecomment-6747676430
[cr-pr]: https://github.com/loyalagents/context-router/pull/205
[cr-ci]: https://github.com/loyalagents/context-router/actions/runs/42585776971
[cr-qualification]: https://github.com/loyalagents/context-router/actions/runs/42585776883
[cr-record]: https://github.com/loyalagents/context-router/blob/71d8433215009e4f2430ac6631a1f5392fb4c7ab/docs/plans/active/hcp-alignment/README.md#c2-implementation-checkpoint-2026-11-09
