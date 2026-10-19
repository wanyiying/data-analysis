# 设计决策

1. 独立双源 CLI，保留 da_ops/da_reconcile/da_verify 接口，避免破坏单源能力。
2. Decimal 原值求和，输出字符串；不使用 float 或默认容差吞差异。最大数位与行数受限确保总精度。
3. 原始 grain 必须唯一，比较 keys 必须为其子集；有意明细拆分须提供真实行键。拒绝猜测去重。
4. 合同已确认才比较；单位不同时只在显式 multiplier 转到相同规范单位后比较；无汇率推断。
5. 总量模式显式授权，不能追溯逐笔，结果单独标 aggregate_consistent。
6. 原 HTML 渲染器复用，通过 report_spec；Agent 未完成始终 degraded。确定性引擎不能自动生成“真实角色执行”记录。
7. 本项目文档属于用户要求的求职交付，保留许可证及原作者归属；不安装覆盖用户原 Skill，不自动 push。
