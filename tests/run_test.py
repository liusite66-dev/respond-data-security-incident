#!/usr/bin/env python3
"""respond-data-security-incident 测试。构造重大与轻微事件，断言报告义务、时限、模板生成。"""
import json
import os
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
import respond_incident as ri  # noqa: E402

DATA_DIR = os.path.join(BASE_DIR, "data")
RULES = ri.load_json(os.path.join(DATA_DIR, "reporting_rules.json"))
TEMPLATES = ri.load_json(os.path.join(DATA_DIR, "templates.json"))

results = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    results.append(bool(cond))


def main():
    # 重大事件：150万用户 + 敏感个人信息 + 重要数据
    major = {
        "incident_type": "数据泄露",
        "discovered_date": "2024-06-01 10:00",
        "affected_users": 1500000,
        "data_categories": ["个人信息", "敏感个人信息", "重要数据"],
        "cross_border": True,
        "controller_name": "示例科技有限公司",
    }
    a = ri.assess(major, RULES)
    check("重大事件-需向监管报告", a["must_report_authority"] is True)
    check("重大事件-级别为重大", a["severity"] == "重大")
    check("重大事件-取最严24h时限", a["report_deadline_hours"] == 24)
    # 2024-06-01 10:00 + 24h = 2024-06-02 10:00:00
    check("重大事件-截止时间计算正确", a["report_deadline"] == "2024-06-02 10:00:00")
    check("重大事件-需告知个人", a["notify_individual"] is True)
    check("重大事件-追溯非空", len(a["decision_trace"]) > 0)

    # 轻微事件：小规模一般个人信息，无敏感/重要数据
    minor = {
        "incident_type": "数据丢失",
        "discovered_date": "2024-06-01 10:00",
        "affected_users": 50,
        "data_categories": ["个人信息"],
        "cross_border": False,
        "controller_name": "示例科技有限公司",
    }
    b = ri.assess(minor, RULES)
    check("轻微事件-无强制监管报告义务", b["must_report_authority"] is False)
    check("轻微事件-级别为一般", b["severity"] == "一般")
    # general 时限 72h -> 2024-06-04 10:00:00
    check("轻微事件-一般时限72h截止正确", b["report_deadline"] == "2024-06-04 10:00:00")
    check("轻微事件-仍需告知个人(涉个人信息)", b["notify_individual"] is True)

    # 配置版本字段
    check("配置含 version/updated_date",
          "version" in RULES and "updated_date" in RULES and "version" in TEMPLATES)

    # 模板文件生成
    with tempfile.TemporaryDirectory() as td:
        ctx = ri.build_context(major, a)
        reg = ri.render_doc(TEMPLATES["regulatory_report"], ctx, os.path.join(td, "reg.docx"))
        notice = ri.render_doc(TEMPLATES["individual_notice"], ctx, os.path.join(td, "notice.docx"))
        check("监管报告书文件已生成", os.path.exists(reg) and os.path.getsize(reg) > 0)
        check("个人告知文文件已生成", os.path.exists(notice) and os.path.getsize(notice) > 0)

    total, passed = len(results), sum(1 for r in results if r)
    print("\n汇总：%d/%d PASS" % (passed, total))
    if passed == total:
        print("ALL PASS")
        sys.exit(0)
    else:
        print("SOME FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
