# 发布副本验证（2026-10-19，Asia/Shanghai）

实际复测：**155 passed，0 failed，0 errors，0 skipped，114.965 秒**。环境：Windows / Python 3.11.5，使用现有环境，未新装依赖。JUnit：release-tests.xml。本次复测不同于此前 independent-audit-tests.xml 历史记录。

命令：PYTHONUTF8=1，python -m pytest -q -p no:cacheprovider --basetemp .audit-test-tmp/release-rerun --junitxml outputs/release-tests.xml。首次运行未先创建 .audit-test-tmp 父目录，导致 73 个 setup errors、82 项通过；补建目录后完整重跑得到上述结果。复现说明已补建目录步骤。

四个 CLI Demo 实际执行并核对预期退出码 0/1/3/1；一致、差异、口径阻断、同源公开派生样本均符合预期。工件核验分别 pass/pass/not_assessed/pass。新版静态快照在 demos/，保留 degraded 标记。复核范围是输入哈希和导出明细的算术/汇总，不是从原始数据独立重算，也不认证真实 Agent 执行。

为公开展示，仅对 JSON 路径和 XML 机器名/路径脱敏：移除本机仓库前缀、将解释器路径写作 python、机器名改为 redacted-for-publication；不更改测试结论、时长、金额、输入哈希。原始记录在本地源目录及 ignored outputs 保留。快照跨机器应重新生成，历史路径不是可移植验收凭证。

完整保留 LICENSE 原文和 Required Notice；未添加商业授权。已排除原始大数据、IDE、缓存和 day1/day2/day3 学习结果。扫描当前候选及所继承 Git 历史的常见密钥格式未命中；模式扫描不能证明绝无秘密。公开数据源及改造规则见 ATTRIBUTION.md。上述测试发生在本地发布准备阶段；随后经用户授权发布至 wanyiying/data-analysis。
