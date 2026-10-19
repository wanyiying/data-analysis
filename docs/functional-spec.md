# 输入输出接口

CLI：`python scripts/da_cross_reconcile.py --source-a A.csv --source-b B.xlsx --config contract.json --output-root outputs/cross-audit`。每次创建 UUID 子目录，禁止复用已有运行目录；参数路径是操作者授权的本地路径，配置不能指定输出文件。

配置 v1：`confirmed`、`mode` (exact/aggregate/total)、`keys`、`metrics`、`sources.a/b`。每个 source 有 canonical→physical `fields`、原始唯一粒度 `grain`、date 的 field/format/meaning、scope 的 start/end/population/cutoff/filters、metrics 的 definition/unit/currency/aggregation/multiplier。filters 是字段→允许文本值列表，仅执行白名单相等过滤。日期范围闭区间；截止使用带时区 ISO 时间。

状态：execution success/error；alignment READY_EXACT/READY_AGGREGATE/AGGREGATE_ONLY/NEEDS_CONFIRMATION/BLOCKED；consistency consistent/different/not_assessed。退出码 0 一致，1 差异，2 程序或输入错误，3 业务阻断，4 待确认。总量模式不声明逐笔一致，仅 aggregate_consistent/aggregate_different。

每指标输出两侧总额、matched_difference、only_a_total、only_b_total、net_difference、absolute_difference、positive_difference、negative_difference、mismatch_count 与 identity_valid。差额固定 A−B；未匹配单侧金额不伪造另一侧零；absolute_difference 包括未匹配绝对金额。行绝对容差和全局绝对容差分开配置，两者必须同时通过。原值不截断，有限 Decimal 运算拒绝超出精度预算。

工件：manifest/profile/contract/alignment/details.csv/summary/checks/errors/evidence/agent-review/verification/report_spec/report.html。未执行角色标 pending，不伪造角色文件。报告在角色门禁完成前 degraded。schema_version=1。

安全限额：CSV/XLSX输入20MB、100000条数据行、100列、单元格10000字符，Excel解压成员总大小100MB；不支持.xls、URL或宏输入。日期/数字解析失败不跳过。配置1MB上限，不执行表达式。金额单值最多24有效位、绝对十进制数量级≤24；正倍率同预算，核心上下文128位。业务ID原有文本保真，Excel已数值化丢失的前导零无法恢复。

canonical字段别名不得使用内部__前缀/source_rows或公式前缀=、+、-、@；来源真实列名不受该别名限制，通过fields映射到安全别名，避免CSV保护前缀改变指标标识后影响独立复核。

evidence 精确值在 exact_values、原摘要在 summary.json；values 是原 da_verify 所需 float 数值副本，仅用于声明溯源，不替代 Decimal 数学检查。observed日期不要求两侧每个日期都存在，缺失日期是待定位覆盖差异；合同范围与截止必须一致，观察到区间外数据直接阻断。CLI不证明提取完整性。
