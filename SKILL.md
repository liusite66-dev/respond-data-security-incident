---
name: respond-data-security-incident
description: 数据安全事件应急响应自检。根据事件类型/规模/涉及数据种类，映射向监管的报告义务、报告时限(自动用 datetime 计算截止时间)、报告部门与是否需告知受影响个人，并自动填充模板生成“监管报告书草案”与“个人告知文草案”(DOCX，环境缺 python-docx 时回退 Markdown)。USE WHEN 用户遇到“数据泄露/篡改/丢失/勒索事件怎么办”“数据安全事件要不要上报、几小时内报、报给谁”“要不要通知用户/个人信息主体”“生成数据安全事件监管报告/用户告知书草案”“数据安全事件应急响应处置”等场景。边界：仅做规则化义务判定与草案模板生成，不出具法律意见、不替代应急预案与监管沟通；时限/阈值为示例口径，需按最新法规与主管部门要求核对；不做事件技术取证与溯源。
activation: /respond-data-security-incident
license: MIT
metadata:
  author: liusite66-dev
  version: 1.0.0
  created: 2026-08-31
provenance:
  maintainer: liusite66-dev
  source_references: user-provided skill package
---

# 数据安全事件应急响应 (respond-data-security-incident)

据事件类型、规模、数据种类判定报告义务与时限，并生成监管报告书与个人告知文草案。

## 判定逻辑（规则见 data/reporting_rules.json）
按项检查并累计触发，取最严(最短)时限：
- 涉“重要数据” → 须向主管/网信部门报告（示例 24h）
- 受影响个人 ≥ 100万（大规模） → 须报告（示例 24h）
- 涉“敏感个人信息” → 须报告（示例 72h）
- 均未触发 → 一般事件，按内部流程处置（示例 72h）
- 个人告知：涉个人信息且受影响人数≥阈值 → 应告知个人（示例 72h 内）

级别（重大/较大/一般）与所有阈值、时限均外置在 `data/reporting_rules.json`（含 `version`/`updated_date`）；报告书与告知文段落模板外置在 `data/templates.json`。时限截止时间用 `datetime` 由发现时间推算。

## 输入 (JSON)
```json
{
  "incident_type": "数据泄露",
  "discovered_date": "2024-06-01 10:00",
  "affected_users": 1500000,
  "data_categories": ["个人信息", "敏感个人信息", "重要数据"],
  "cross_border": true,
  "controller_name": "示例科技有限公司"
}
```

## 输出（写入 --outdir）
- `assessment.json`：级别、是否报告、报告部门、报告时限与截止时间、是否告知个人、`decision_trace`（逐条判定依据）、免责声明。
- `regulatory_report.docx`：监管报告书草案（事件概况/影响范围/已采取措施/补救建议/联系方式/免责声明）。
- `individual_notice.docx`：个人告知文草案（事件情况/影响/措施/补救建议/联系方式/免责声明）。
- 无 python-docx 时自动回退为同名 `.md`。

## 命令示例
```bash
python3 scripts/respond_incident.py --input examples/sample_input.json --outdir examples/
```

## 测试
```bash
python3 tests/run_test.py   # 覆盖重大/轻微事件，断言报告义务、时限计算与模板生成，打印 PASS/FAIL
```

## 免责声明
本 Skill 为自检辅助，不构成法律意见，最终以监管口径为准。时限与阈值为示例口径，请按最新法规核对。

## Gotchas

- 发现时间、送达渠道和主管部门要求会影响实际报告期限；缺少可靠事件时间时不得把计算值当成最终截止时间。
- 输出报告和告知文均为草案，不代表事件定级、技术事实或监管机关已接受报告。
