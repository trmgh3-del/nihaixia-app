#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确保四诊页面只负责采集/展示，辨证逻辑集中在统一引擎。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / 'pages/diagnosis/sizhen.vue').read_text(encoding='utf-8')
engine = (ROOT / 'utils/sizhen-engine.js').read_text(encoding='utf-8')
assert "import { analyzeSizhen } from '@/utils/sizhen-engine.js'" in page, 'page must call central engine'
assert 'analyzeSizhen(this.pick' in page and 'this.result = Object.assign(EMPTY_RESULT(), raw' in page, 'page must use central analysis'
for forbidden in ['formulas.push(', 'mer.add(', 'filterFormulaSafety(', 'evaluateKnowledgeAsync(']:
    assert forbidden not in page, f'legacy inline diagnosis logic remains: {forbidden}'
for required in ['export async function analyzeSizhen', 'filterFormulaSafety', 'evaluateKnowledgeAsync', 'findSimilarCases', 'findFormulaDetails']:
    assert required in engine, f'engine missing {required}'
print('PASS: page delegates diagnosis, formula, safety and evidence logic to central engine')
