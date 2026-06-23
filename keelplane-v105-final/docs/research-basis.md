# Research and Standards Basis

Checked 2026-06-23.

Primary references used for this proposal:

- OpenAI Codex subagents and custom agent configuration:
  https://developers.openai.com/codex/subagents
- OpenAI Codex configuration reference:
  https://developers.openai.com/codex/config-reference
- OpenAI Codex AGENTS.md guidance:
  https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex hooks:
  https://developers.openai.com/codex/hooks
- Anthropic Claude Code subagents:
  https://code.claude.com/docs/en/sub-agents
- Anthropic Claude Code Agent Teams:
  https://code.claude.com/docs/en/agent-teams
- Anthropic Claude Code hooks:
  https://code.claude.com/docs/en/hooks
- OpenTelemetry GenAI semantic conventions:
  https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenTelemetry GenAI agent spans:
  https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/
- W3C Trace Context:
  https://www.w3.org/TR/trace-context/
- in-toto attestation framework:
  https://github.com/in-toto/attestation/tree/main/spec/v1
- SLSA provenance:
  https://slsa.dev/spec/v1.1/provenance
- DSSE protocol:
  https://github.com/secure-systems-lab/dsse/blob/master/protocol.md
- Sigstore attestations:
  https://docs.sigstore.dev/cosign/signing/attestation/

Design implications:

- Native subagent/team features are harness capabilities, not portable truths.
- Claude Agent Teams is experimental and should remain opt-in.
- Trace correlation is useful but does not establish provenance.
- Hashes and local seals provide integrity, while stronger origin requires
  trusted custody or signed attestation.
- External parameter/provenance fields must be treated as untrusted unless
  verified under an attestation policy.
