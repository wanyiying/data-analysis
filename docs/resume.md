# 简历项目描述

**设计多元经营指标一致性审计 Skill｜Python、pandas、Decimal、pytest｜二次开发 / 本地演示 MVP**

项目链接：https://github.com/wanyiying/data-analysis

- 基于小马学数分 data-analysis，围绕双源经营指标可比性和金额一致性开展二次开发，加入指标/范围合同、唯一键与日期校验、显式聚合及不可比阻断。
- 使用 Decimal 计算匹配差异、双侧未匹配与正负抵消，输出带输入哈希的离线 HTML 和结构化工件，支持导出明细的算术与汇总核验。
- 构建合成案例和公开数据派生的模拟双源演示；本地全量 155 项测试通过，其中上游 74 项、新增跨源与审计测试 81 项，含 14 项审计回归。
- 根据审计反例修复日期错配、时间戳截日、状态篡改漏检及 Reviewer 降级处理问题，并明确业务合同可信性、独立复算与生产验证限制。

以上描述须与本人实际参与一致；开发使用 AI 辅助，个人应能解释合同、差异恒等式、反例和限制。不应描述为从零原创、生产上线、财务审计认证、真实独立双系统验收或收益提升。

复现说明：[reproduce.md](reproduce.md)。实测记录：[release-validation.md](release-validation.md)。原作者及许可：[ATTRIBUTION.md](../ATTRIBUTION.md)。
