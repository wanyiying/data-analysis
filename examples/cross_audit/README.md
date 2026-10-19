# 双源审计演示

`python scripts/generate_cross_audit_cases.py` 可重建 22 个小案例，每目录含 a.csv/b.csv/contract.json/expected.json，expected 是手工值。公开样本单独准备，不受小案例生成器覆盖。

`python scripts/run_cross_audit_demos.py` 实际运行一致、差异、不可比和公开样本，并独立复算；每次 UUID 目录，路径见 outputs/cross-audit-demos/index.json。退出码分别 0/1/3/1。

consistent：30 对 30。value_mismatch：30 对 27，键 002 差 3。definition：交易金额与确认收入定义不同，BLOCKED，未计算差额。offset：双方总额 30，相抵 +5/-5，绝对差异 10，仍为 different。

public_retail 来源 [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)，Daqing Chen，DOI 10.24432/C5CG6D，CC BY 4.0。最前 2,000 行明细剔除客户标识后构造按日/国家汇总，在 B 首组明确注入 +7.25 GBP；A−B 应为 -7.25。完整版本、原文件 SHA256、抽样与注入规则见 provenance.json。它是同源派生模拟检测，不是独立财务系统，不是企业真实事故。

重建公开样本到新目录：`python scripts/prepare_public_retail_audit.py --raw outputs/public-raw/online_retail_II.xlsx --destination outputs/public-sample-rebuilt --limit 2000`；不指定 raw 时从官方固定 URL 下载。原始大文件保留在 ignored outputs，不提交。
