# ADR-002: Native Harness First, Model Inheritance by Default

Status: Proposed final

## Decision

Reference packs use project-scoped native Codex/Claude agent formats, inherit
the active model, install no API keys/providers/MCP servers, change no global
settings, and do not enable permission bypasses. Claude Agent Teams remains an
opt-in experimental fragment.

Native version/model drift is recorded in evidence when observable and covered
by capability/compatibility tests. Subscription authentication is a declared
fact unless a supported attestation proves it.
