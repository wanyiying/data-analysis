# 公开演示快照

这些是本次发布副本实际运行 CLI 后生成的静态工件，全部保持 degraded。JSON 中本机路径前缀已脱敏，金额和输入哈希未改动；跨机器请按 docs/reproduce.md 重跑。

- [一致](consistent/report.html)：30 对 30，consistent，exit 0。
- [差异](value_mismatch/report.html)：30 对 27，different，exit 1。
- [口径阻断](definition/report.html)：not_assessed，exit 3。
- [公开模拟双源](public_retail/report.html)：人工注入 +7.25 GBP，A−B=-7.25，exit 1。

旧 agent-reviewed 工件未纳入公开候选；该目录仅留说明页。本地 JSON 不能认证真实独立角色执行。数字核验不能替代从原始输入重新计算的独立实现，也不判断哪个来源正确。
