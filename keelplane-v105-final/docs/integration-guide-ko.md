# Keelplane V105 최종 패키지 이식 가이드

## 1. 먼저 별도 branch

```bash
git switch -c feat/keelplane-v105-trust-contract
```

## 2. 문서 이식

권장 위치:

```text
docs/v105-product-direction-spec.md     <- docs/product-direction-v105.md
docs/v105-threat-model.md               <- docs/threat-model-v1.md
docs/v105-evidence-protocol.md           <- docs/evidence-protocol-v1.md
docs/v105-agent-team-spec.md             <- docs/agent-team-spec-v1.md
docs/v105-evaluation-spec.md             <- docs/evaluation-spec-v1.md
docs/v105-implementation-roadmap.md       <- docs/implementation-roadmap.md
```

기존 V104 spec을 삭제하지 말고 V105 proposal로 추가한 뒤 decision review를
거친다.

## 3. Pack은 처음에는 같은 repo에 둔다

```text
packs/codex/
packs/claude/
profiles/
schemas/
```

Evidence protocol과 릴리즈 주기가 안정될 때만 별도 repo로 분리한다.

## 4. 실제 프로젝트에 pack 시험 설치

```bash
python tools/install_pack.py --target /path/to/test-repo --harness both --dry-run
python tools/install_pack.py --target /path/to/test-repo --harness both
```

기존 `AGENTS.md`/`CLAUDE.md`는 자동 merge하지 않는다.
`.keelplane/install-fragments/` 내용을 사람이 검토해 합친다.

## 5. 첫 실험

`profiles/feature-pipeline.json`을 사용한다.

1. explorer가 code path를 조사한다.
2. implementer 한 명만 수정한다.
3. test verifier와 fresh reviewer가 현재 diff를 독립적으로 본다.
4. 위험 trigger가 있을 때만 security/adversarial reviewer를 추가한다.
5. agent 결과는 staging self-report로만 남긴다.
6. `capture_local.py`가 A1 evidence를 만든다.
7. seal을 검증한다.

## 6. Cross-harness 권장 흐름

```text
Codex 구현 -> Claude Code blind-first review
또는
Claude Code 구현 -> Codex blind-first review
```

reviewer에게 처음에는 acceptance criteria, diff, test receipt만 준다.
implementer 설명은 first findings 뒤에 보여 anchoring을 줄인다.

## 7. Keelplane 코드에 가장 먼저 반영할 사항

1. `check_adversarial` stub이 required claim을 pass하지 못하게 한다.
2. generic adapter를 streaming digest + path limits로 바꾼다.
3. verdict에 decision/assurance를 추가한다.
4. gate marker를 action-bound event로 migration한다.
5. filename 기반 agent counting을 invocation manifest로 대체한다.

## 8. 주의

- local seal은 remote identity 증명이 아니다.
- agent JSON은 receipt가 아니라 claim이다.
- test verifier가 JSON에 exit_code 0을 썼다고 command가 관찰된 것이 아니다.
- Claude Agent Teams는 기본 활성화하지 않는다.
- small fix에는 team을 쓰지 않는다.
