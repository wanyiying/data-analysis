# 原仓库基线

日期 2026-10-19；Windows / Python 3.11.5；origin https://github.com/xiaomaxueshufen/data-analysis.git；commit e9821ed5c05dbcd29d215f55c28e64a052ef96e5。开发分支 feature/multi-source-kpi-audit。

初始工作区不干净：day1_outputs、day2_outputs 的已暂存和未暂存学习文件；examples/case_study/run/contribution_config.json 与 window_table.csv；.idea、day3_outputs 和其他 day1 JSON/HTML 未跟踪。均保留，不作为本次贡献。

已读 SKILL、intent-routing、harness、evidence-contract、ops-catalog、da_ops、da_reconcile、da_verify、da_report、tests、examples、README、LICENSE。原框架为模型主导分析，da_ops 单数据文件，da_reconcile 表内汇总，da_verify 校验声明证据，da_report 可复用六段 HTML。新增跨源包不替换原接口。PolyForm Noncommercial 原归属保留。

首次 `python -m pytest -q`：29 passed / 45 errors，原因 pytest 历史临时目录权限，非算法断言。独立目录 `python -m pytest -q -p no:cacheprovider --basetemp .audit-test-tmp/baseline2`：71 passed / 3 failed（原 da_reconcile 成功输出时 Windows 编码退出 1）。正在复核编码原因，详见最终 testing.md。
