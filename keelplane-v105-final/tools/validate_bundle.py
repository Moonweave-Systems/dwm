#!/usr/bin/env python3
"""Validate structure, native agent syntax, schemas, examples, and safety invariants."""
from __future__ import annotations
import hashlib, json, py_compile, re, sys, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def frontmatter(path:Path)->dict[str,str]:
    text=path.read_text(encoding='utf-8')
    if not text.startswith('---\n'): raise ValueError('missing frontmatter')
    _,head,_=text.split('---',2)
    out={}
    for line in head.strip().splitlines():
        if ':' in line:
            k,v=line.split(':',1); out[k.strip()]=v.strip()
    return out

def main()->int:
    issues=[]; checks=0
    required=['README.md','AUDIT-KO.md','FINAL-REVIEW.md','VALIDATION.json','docs/product-direction-v105.md','docs/threat-model-v1.md','docs/evidence-protocol-v1.md','docs/agent-team-spec-v1.md','docs/evaluation-spec-v1.md','docs/implementation-roadmap.md','docs/integration-guide-ko.md','docs/upstream-gap-map.md','docs/ecosystem-positioning.md','tools/install_pack.py','tools/capture_local.py','tools/verify_seal.py']
    for r in required:
        checks+=1
        if not (ROOT/r).is_file(): issues.append(f'missing: {r}')
    # Safety string scan
    forbidden=['OPENAI_API_KEY','ANTHROPIC_API_KEY','dangerously-skip-permissions','bypassPermissions','kp_evidence_curator','kp-evidence-curator']
    # Scan installable/user-facing assets rather than the validator and audit docs,
    # which necessarily name prohibited settings while explaining why they are banned.
    scan_roots = [ROOT/'packs', ROOT/'profiles', ROOT/'examples']
    for scan_root in scan_roots:
        for p in scan_root.rglob('*'):
            if not p.is_file() or p.suffix in {'.zip','.pyc'}:
                continue
            try:
                text=p.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                checks+=1
                if token in text:
                    issues.append(f'forbidden token {token}: {p.relative_to(ROOT)}')
    # Codex TOML
    codex=list(sorted((ROOT/'packs/codex/.codex/agents').glob('*.toml')))
    if len(codex)!=6: issues.append(f'expected 6 Codex agents, got {len(codex)}')
    for p in codex:
        checks+=1
        try: data=tomllib.loads(p.read_text())
        except Exception as e: issues.append(f'TOML {p.name}: {e}'); continue
        for k in ['name','description','developer_instructions']:
            if not data.get(k):
                issues.append(f'{p.name} missing {k}')
        expected_name = p.stem.replace('-', '_')
        if data.get('name') != expected_name:
            issues.append(f'{p.name} name mismatch: {data.get("name")!r} != {expected_name!r}')
        if 'model' in data:
            issues.append(f'{p.name} pins model')
        if data.get('sandbox_mode') not in {'read-only','workspace-write'}:
            issues.append(f'{p.name} bad sandbox')
    # Claude agents
    claude=list(sorted((ROOT/'packs/claude/.claude/agents').glob('*.md')))
    if len(claude)!=7: issues.append(f'expected 7 Claude agents, got {len(claude)}')
    for p in claude:
        checks+=1
        try: fm=frontmatter(p)
        except Exception as e: issues.append(f'frontmatter {p.name}: {e}'); continue
        for k in ['name','description','tools','model','permissionMode']:
            if not fm.get(k):
                issues.append(f'{p.name} missing {k}')
        if fm.get('name') != p.stem:
            issues.append(f'{p.name} name mismatch: {fm.get("name")!r}')
        if fm.get('model') != 'inherit':
            issues.append(f'{p.name} must inherit model')
        if fm.get('permissionMode') not in {'default','plan'}:
            issues.append(f'{p.name} unsafe or unsupported permission mode: {fm.get("permissionMode")!r}')
        if 'Agent' in {part.strip() for part in fm.get('tools','').split(',')}:
            issues.append(f'{p.name} may recursively spawn agents')
    # Native config fragments must parse but are not overwrite-ready files.
    checks += 1
    try:
        codex_fragment = tomllib.loads((ROOT/'packs/codex/.codex/config.fragment.toml').read_text())
        agents_cfg = codex_fragment.get('agents', {})
        if agents_cfg.get('max_threads', 0) > 4 or agents_cfg.get('max_depth') != 1:
            issues.append('Codex config fragment exceeds bounded defaults')
    except Exception as e:
        issues.append(f'Codex config fragment: {e}')
    checks += 1
    try:
        teams_fragment = json.loads((ROOT/'packs/claude/.claude/settings.agent-teams.fragment.json').read_text())
        if teams_fragment.get('env', {}).get('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS') != '1':
            issues.append('Claude Agent Teams fragment is malformed')
    except Exception as e:
        issues.append(f'Claude settings fragment: {e}')

    # JSON and JSON Schema
    try:
        import jsonschema
    except Exception as e:
        issues.append(f'jsonschema unavailable: {e}'); jsonschema=None
    schemas={}
    for p in sorted((ROOT/'schemas').glob('*.json')):
        checks+=1
        try: obj=json.loads(p.read_text()); schemas[p.name]=obj
        except Exception as e: issues.append(f'JSON {p.name}: {e}'); continue
        if jsonschema:
            try: jsonschema.Draft202012Validator.check_schema(obj)
            except Exception as e: issues.append(f'schema {p.name}: {e}')
    mapping={
      'profiles/*.json':'team-profile.schema.json',
      'examples/artifacts/agent-result.example.json':'agent-result.schema.json',
      'examples/artifacts/command-receipt.example.json':'command-receipt.schema.json',
      'examples/artifacts/review.example.json':'review.schema.json',
      'examples/artifacts/gate-event.example.json':'gate-event.schema.json',
      'examples/artifacts/run-contract.example.json':'run-contract.schema.json',
      'examples/artifacts/evidence-manifest.example.json':'evidence-manifest.schema.json',
      'examples/artifacts/seal.example.json':'seal.schema.json',
      'examples/artifacts/compile-report.example.json':'compile-report.schema.json',
      'examples/artifacts/event.example.json':'event.schema.json',
    }
    if jsonschema:
        for pattern,sname in mapping.items():
            for p in ROOT.glob(pattern):
                checks+=1
                try: jsonschema.Draft202012Validator(schemas[sname],format_checker=jsonschema.FormatChecker()).validate(json.loads(p.read_text()))
                except Exception as e: issues.append(f'validation {p.relative_to(ROOT)}: {e}')
    # Python compile
    for p in sorted((ROOT/'tools').glob('*.py')):
        checks+=1
        try: py_compile.compile(str(p),doraise=True)
        except Exception as e: issues.append(f'python {p.name}: {e}')
    # Pack invariants
    if (ROOT/'packs/codex/.codex/config.toml').exists(): issues.append('installer pack must not ship overwrite-ready config.toml')
    if (ROOT/'packs/claude/.claude/settings.json').exists(): issues.append('installer pack must not ship overwrite-ready Claude settings.json')

    # Delivery manifest, when present, must cover every distributable file.
    bundle_manifest = ROOT / 'BUNDLE_MANIFEST.json'
    if bundle_manifest.exists():
        checks += 1
        try:
            manifest_data = json.loads(bundle_manifest.read_text(encoding='utf-8'))
            expected = {entry['path']: entry for entry in manifest_data.get('files', [])}
            actual_paths = sorted(
                path.relative_to(ROOT).as_posix()
                for path in ROOT.rglob('*')
                if path.is_file()
                and path != bundle_manifest
                and '__pycache__' not in path.parts
                and path.suffix != '.pyc'
            )
            if sorted(expected) != actual_paths:
                issues.append('BUNDLE_MANIFEST file set mismatch')
            for relative in actual_paths:
                entry = expected.get(relative)
                if not entry:
                    continue
                path = ROOT / relative
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != entry.get('sha256') or path.stat().st_size != entry.get('size_bytes'):
                    issues.append(f'BUNDLE_MANIFEST digest/size mismatch: {relative}')
        except Exception as e:
            issues.append(f'BUNDLE_MANIFEST: {e}')

    result={'valid':not issues,'checks':checks,'issues':issues,'codex_agents':len(codex),'claude_agents':len(claude),'schemas':len(schemas),'profiles':len(list((ROOT/'profiles').glob('*.json')))}
    print(json.dumps(result,indent=2)); return 0 if not issues else 1
if __name__=='__main__': raise SystemExit(main())
