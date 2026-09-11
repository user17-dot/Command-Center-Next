# Upstream OmniLab / Android Test Station references

This project studies and adapts architecture patterns from the Android Open Source Project's Android Test Station and TradeFed Cluster projects.

Upstream references:

- Android Test Station / MultiTest Transport: https://android.googlesource.com/platform/tools/multitest_transport/+/refs/heads/multitest-transport-dev
- TradeFed Cluster: https://android.googlesource.com/platform/tools/tradefed_cluster/+/refs/heads/multitest-transport-dev

The upstream projects contain Apache License 2.0 headers. When source is directly reused in the future, its copyright and license headers must remain intact and any required notices must be preserved.

## What we reuse conceptually

- Device inventory and explicit device states
- Command/job lifecycle
- Host events and heartbeats
- Structured test execution instead of arbitrary shell commands
- Test scheduling boundaries
- Result and retry lineage
- Multi-host ownership concepts

## What we intentionally do not vendor

- Docker launcher/runtime
- App Engine / Google Cloud-specific deployment
- MTT web UI
- Google authentication helpers
- Cloud orchestration
- Internal service dependencies

The goal is a smaller native Linux execution service suitable for an office xTS lab where Docker may not be permitted.
