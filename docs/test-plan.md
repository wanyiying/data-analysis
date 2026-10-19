# 验证方案

先跑原 tests 保存基线；核心按手工 fixtures、边界与攻击输入测试；运行三 CLI Demo 检查完整工件；交换 A/B、行重排、合法拆分验证不变性与符号反转；独立复算所有恒等式。最后原 tests 与新增测试全量回归。

对 Agent 用真实 subagents 分角色执行并保存工具返回 ID；Reviewer 最后。报告引用 claims/evidence 通过原 da_verify，数学结果由新检查单独验证。自动化测试不能替代业务确认或真实双系统上线验证。临时目录在 .audit-test-tmp 下，禁用缓存以规避本机历史 pytest 目录 ACL。
