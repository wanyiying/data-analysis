# 数据方案

第一层合成 fixtures 由 `scripts/generate_cross_audit_cases.py` 固定生成，expected 是手工常量，不调用生产引擎。包含一致、金额、双侧未匹配、粒度、重复、多对多、空键、单位/日期、口径、覆盖、抵消、容差、负零缺失、无键阻断。性质测试以独立 Decimal 求和验证。

第二层优先 UCI Online Retail II；必须先核实官方许可及来源，再下载到独立运行目录，记录 SHA256、版本、抽样与注入清单。交易金额为 Quantity×Price，不能称财务确认净收入；同源派生双视图只验证模拟检测能力。发票不是行唯一键，使用来源行序号作为模拟唯一键；不提交大原始数据。

已执行：[官方数据页](https://archive.ics.uci.edu/dataset/502/online+retail+ii)，Daqing Chen，DOI 10.24432/C5CG6D，CC BY 4.0。官方下载 raw SHA256 `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`。首sheet Year 2009-2010前2000行，导出行号、日期、国家、signed transaction value，未导出客户/发票/描述。B首个日期/国家分组注入+7.25 GBP，已知差额-7.25；provenance.json保存注入前后值。用同一原文件二次运行，a.csv/b.csv/contract.json SHA256完全一致，generated_at时间按实际执行记录不要求相同。
