#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查本地知识库记录的上游 commit 是否仍是上游 main 最新提交。
只读检查，不修改工作区；网络不可用时返回明确状态。
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
meta = json.loads((ROOT / 'static/data/meta.json').read_text(encoding='utf-8'))
source = meta.get('knowledgeEngine', {})
repo = source.get('sourceRepository', 'https://github.com/jangviktor-web/nihaixia')
expected = source.get('sourceCommit', '')
try:
    out = subprocess.check_output(['git', 'ls-remote', repo, 'refs/heads/main'], text=True, timeout=20).strip()
    latest = out.split()[0] if out else ''
except (OSError, subprocess.SubprocessError) as exc:
    print(f'UNAVAILABLE: cannot query upstream ({exc})')
    raise SystemExit(2)
if not latest:
    print('UNAVAILABLE: upstream main has no commit')
    raise SystemExit(2)
if expected == latest or (expected and latest.startswith(expected)):
    print(f'UP TO DATE: {latest[:12]}')
    raise SystemExit(0)
print(f'OUT OF DATE: local={expected or "unknown"} upstream={latest[:12]}')
print('Run build_data.py, build_sizhen_rules.py, audits, then update meta.json.')
raise SystemExit(1)
