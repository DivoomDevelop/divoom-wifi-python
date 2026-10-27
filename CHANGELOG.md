# Changelog

## 0.1.2 — 2026-10-27

- Apply the maintainer-confirmed LAN token requirement only to hardware 90, 92 and 400.
- Inject `DeviceToken` for PIXOO64 90/92 and `LocalToken` for TimeGate 400 from the shared
  `local_token` argument or `DIVOOM_LOCAL_TOKEN` environment variable.
- Keep tokens out of other hardware, cloud and discovery requests. Apply the same rule to CLI prompts
  and the direct LAN diagnostic tool, with hardware-specific regression coverage.
- Preserve partial RGB updates when a request contains no token field.

## 0.1.1 — 2026-10-27

- Fix mandatory LocalToken validation/prompting for TimeGate hardware 402. Hardware 400 still
  requires a token; supplied tokens remain supported on both variants.
- Add opt-in direct LAN read checks with business-field validation and acknowledgement-only reporting.
- Record live LAN reads across PIXOO64, TimeGate, TimeFrame and AstroToo. Local IP reports stay local.

## 0.1.0 — 2026-10-27

- Initial Python SDK and CLI for four Divoom WiFi product families, with discovery, 138 operations,
  documentation, examples, protocol tests and cross-platform CI.
