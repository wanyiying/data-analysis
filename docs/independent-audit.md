# 独立项目审计与缺陷修复

日期：2026-10-19（Asia/Shanghai）。对象：本目录中的实际工作区，含尚未提交的跨源扩展。审计者本轮没有参与前轮开发；没有启动或伪称启动独立子 Agent。本轮是代码与数据质量审计，不构成财务审计意见。

结论：可作为**有明确限制的本地确定性对账 MVP / 求职演示**；尚未达到可信生产审计、真实独立系统验收或自动正式发布标准。测试通过不认证业务合同、输入完整性和 Agent 执行真实性。以下区分已修复问题、设计边界与未解决风险。

## 检查范围与方法

实际阅读了 `scripts/reconcile/` 全部模块（contract、loader、normalization、profiler、alignment、matching、comparison、diagnostics、engine、evidence）、跨源 CLI、工件复算器、finalize 收尾脚本、案例生成器、公开数据构建器与 Demo 执行器；检查原 `da_verify` 角色门禁及 `da_report` 转义路径，读取现有五个原测试模块及跨源测试并实际执行。核对 README、LICENSE、requirements、SKILL 与跨源方法文档，但不以它们的完成声明作为验证证据。

检查既有 `outputs/cross-audit`、公开样本、`docs/demos/agent-reviewed/agents/execution.json` 等留存工件；随后重新执行四个 CLI Demo，读取其 JSON/CSV/HTML 输出。旧 execution.json 中的角色路径仅是本地声明，本轮无法认证旧会话实际调用。没有把前轮 Reviewer 的通过视作本轮审计通过。

工作区开始即有暂存、未暂存和未跟踪文件。本轮未重置、提交、推送或改写原学习成果；未修改 LICENSE、原单源算子、原五个测试模块或原报告渲染器。新增问题均在 `tests/test_independent_audit.py` 留下可执行回归。

## 缺陷、复现与修复

严重度：P1 为可能错误放行或错误呈现审查结果；P2 为重要边界与错误处理缺口。以下位置为修复后的源码定位。

| ID | 严重度 | 复现条件与业务影响 | 代码位置 | 修复及测试 |
|---|---|---|---|---|
| A01 | P1 | exact 同 id、同金额，A 日期 01-01，B 日期 01-02；原输出 consistent，掩盖跨日错配 | `scripts/reconcile/engine.py:17` | 比较共同键双方的规范日期，不同则 `matched_date_mismatch` 阻断；`test_exact_date_disagreement_is_not_consistent` |
| A02 | P1 | 输入 `2026-01-01T23:00:00-08:00` 或 Excel 非零时刻 datetime；原直接 `.date()` 丢失时区/时刻，即使没有业务时区合同也会比较成功 | `scripts/reconcile/normalization.py:13` | V1 明确只接收日历日期，拒绝时间格式、带时区或非零时刻；保留 Excel 午夜日期；两参数时间戳测试及原 native Excel 回归 |
| A03 | P1 | 生成合法工件后，改变 contract 定义、删 manifest 的 b、改 summary.consistency 或 execution；原 verify 仍 pass，证据被改却显示成功 | `scripts/verify_cross_audit_run.py:15`、`:80` | 核对规范合同 SHA256、双方输入条目、指标集合、execution 和顶层 alignment/consistency；四参数篡改测试 |
| A04 | P1 | finalizer 对 Reviewer `downgrade` 继续收尾，且把被接受的 serial_fallback 硬编码为 native_subagents | `scripts/finalize_cross_audit_review.py:16`、`:25`、`:50` | 降级要求修改结论并重新审查，保留原报告且不写 finalization-record；模式来自 manifest，说明本地记录无法认证；两参数收尾测试 |
| A05 | P2 | aggregate 按日期/地区聚合，两个订单金额 10/20 对 5/25，汇总一致但组内差异抵消；原 aggregate limitations 空，容易外推为逐笔一致 | `scripts/reconcile/alignment.py:5`、`evidence.py:84` | 在机器状态及 HTML 附录显式限定分组粒度，说明组内抵消；保留合法聚合行为；`test_aggregate_agreement_discloses_hidden_offsets` |
| A06 | P2 | date.field 被配置为 amount，或物理映射/粒度值为列表、population 空白；可能误覆盖字段、错误分类或接受空白范围标签 | `scripts/reconcile/contract.py:45`、`:67` | date/metric 不得重叠；校验映射和粒度的非空字符串类型、population 去空白；四个相关测试 |

A06 中日期与指标重叠的原实现实际报 `invalid_number`，**没有复现错误成功**；修复属于提前识别非法合同。另三个异常配置反例原本已受控阻断，保留为回归防线，不计作三项新漏洞。

A04 的模式/决策测试为隔离收尾行为，显式 mock 算术与声明校验成功；不代表 mock 角色文件通过真实独立执行认证。真实 CLI 工件的数学校验由四个 Demo 单独执行。

## 对 18 项重点的检查结果

| 重点 | 结果与边界 |
|---|---|
| 1 指标定义 | 合同对 definition/unit/currency/aggregation 做双方一致性校验；仍无法证明用户填入的相同字符串是真实口径 |
| 2 时间/时区/截点 | scope 整体比较，含 cutoff；修复 A01/A02。不自动支持时间戳或判断提取是否真正遵守 cutoff |
| 3 无法对齐强并 | 无公共键阻断；total 必须显式授权；不做模糊连接。键含义真实性仍依赖业务合同 |
| 4 重复/多对多 | grain 重复阻断；字典分组后连接，避免笛卡尔膨胀；原 duplicate/many_to_many 与性质测试通过 |
| 5 空值当零 | 空键和空金额阻断；单侧缺行 difference=None、状态 only_in_a/b，不视为双方零；原测试通过 |
| 6 抵消 | exact 输出正负及绝对差异，净额零不自动一致；aggregate 组内抵消无法凭汇总发现，A05 增加显式边界 |
| 7 模拟冒充独立源 | 公开样本构建代码明确从同一 UCI 表派生且注入 7.25；README 已明确模拟，无真实双系统证据 |
| 8 擅判正确源 | engine 固定 not_determined / not_established；没有权威系统推断路径 |
| 9 精度/容差/负值 | Decimal + 128 位上下文，原始值限制有效数字/指数，局部与总额独立容差；负值、零及累计容差测试通过。证据兼容浮点不能代替 exact_values |
| 10 映射/聚合 | 仅 sum，禁止 metric 入 grain、重复物理映射、保留字段；修复 A06。确认的“可加总”语义仍不能自动识别 |
| 11 版本/证据 | 输入 hash、合同 hash、引擎 hash 和 revision 已落盘，A03 补合同核验；整套工件可同时改写，非签名审计日志 |
| 12 Agent 安全 | 单元格不执行，HTML 转义、CSV 公式防护测试通过；A04 修复收尾决策。提示词约束和本地 JSON schema 不能证明真实独立执行或根因 |
| 13 原能力回归 | 原五个测试模块实际全量回归通过；未改原算子/渲染/验证器生产代码；未删除有价值检查 |
| 14 同源错误逻辑 | 手写固定答案与性质测试保留；新测试指定直接反例。工件复算器复算的是导出的 details，仍缺从原始数据重新计算的第二实现 |
| 15 假成功报告 | A03/A04 修复状态与审核错误放行；blocked 的 execution=success 指流程完成，consistency=not_assessed、exit=3，未记作数学成功 |
| 16 异常/资源 | 原 row/column/file/cell/ZIP expansion 限额、坏 CSV/Excel/配置/编码和公式测试通过；未完成大文件压力、并发换文件、所有畸形嵌套类型穷举 |
| 17 复现 | 默认 pytest 临时路径 ACL 实际失败，使用项目内唯一 basetemp 和 PYTHONUTF8 后可复现；下列命令和 JUnit 可核对 |
| 18 许可/成果 | 原版权与 PolyForm 文本保留；公开数据归属见本地 provenance。没有对外声称原能力属于衍生作者；非商用限制不能被描述成无条件商用许可。未做法律有效性或外部许可现状鉴定 |

## 实际执行记录

从项目根目录 `data-analysis` 执行；本轮没有安装依赖、联网下载数据，也没有伪造执行日志。

1. 首次默认 `python -m pytest -q -p no:cacheprovider`：75 passed / 66 errors，错误为默认临时目录 ACL，不能写成全通过。
2. 新增反例修复前：`tests/test_independent_audit.py` 8 failed / 3 passed（2.45s）。其中日期指标重叠是错误码不符，其余包含真实错误成功路径。
3. 首轮修复全量：150 passed / 2 failed（107.56s），时间戳专用 AuditError 被通用 ValueError 捕获；已修正并保留首轮 JUnit：`independent-audit-first-regression.xml`。
4. 后续全量：153 passed（107.36s）；收尾决策和聚合披露补充后相关测试 81 passed（18.28s），JUnit：`independent-audit-related-tests.xml`。
5. 最终完整回归：**155 passed / 0 failed / 0 errors / 0 skipped，105.71s**，含原项目 74 项、此前跨源 67 项及本轮新增 14 项；JUnit 见同目录 `independent-audit-tests.xml`。新增/修改脚本及测试的 `python -m compileall -q` 通过（exit 0）。实际环境 Python 3.11.5 / pandas 2.0.3 / numpy 1.26.0 / openpyxl 3.0.10 / pytest 7.4.0。

```powershell
$env:PYTHONUTF8='1'
python -m pytest -q -p no:cacheprovider --basetemp .audit-test-tmp/independent-release --junitxml docs/independent-audit-tests.xml
python -m pytest tests/test_cross_audit.py tests/test_independent_audit.py -q -p no:cacheprovider --basetemp .audit-test-tmp/independent-last-related --junitxml docs/independent-audit-related-tests.xml
python scripts/run_cross_audit_demos.py
```

复现时为 basetemp 换新目录名，避免旧目录 ACL。演示 runner 会写新 UUID 运行目录并更新 outputs 下的索引，不覆盖历史运行。实际运行路径、命令与 exit 复制留存在 `independent-audit-demo-results.json`。

| 实际 CLI 场景 | exit | 一致性 | 独立工件校验 |
|---|---|---|---|
| consistent | 0 | consistent | pass |
| value_mismatch | 1 | different | pass |
| definition | 3 | not_assessed / BLOCKED | not_assessed |
| public_retail | 1 | different | pass |

这里 pass 仅为输入哈希与导出明细算术/汇总核对；差异场景的工件数学有效并不代表来源一致。公开样本 -7.25 由原跨源测试实际核对。演示运行早于最后的披露文案改动；最终聚合 HTML 披露另有专门回归，未把旧演示快照冒充最新渲染。HTML 本轮以渲染及转义断言检查，未新开浏览器作视觉验收。

## 未解决风险与发布判断

最薄弱的三个地方：

1. **业务合同及提取可信性**：confirmed=true 和相同口径字符串不是业务批准凭证；同名 id 是否同一命名空间、时区预处理是否正确、截止时点之前的数据是否完整，需系统级证据。
2. **独立复算与血缘闭环不足**：复算器读取 details，不从原始文件独立重建分组；同时篡改明细、汇总和 manifest 可以逃过内部一致性验证。还缺不可变输入快照、签名日志、读入与计算间文件替换防护和端到端第二实现。
3. **Agent 门禁真实性**：本地 JSON 文件可伪造，旧 canonical_task_name 无法凭文件认证；文本注入只能通过数据隔离/转义/提示词约束减轻。真实根因仍需独立系统日志或凭证，四角色意见不能替代。

其他限制：aggregate 允许的组内抵消是信息损失，不能声称逐笔一致；时间戳/跨时区需显式预处理；日期不同会保守阻断，若业务确实允许跨日需重新设计合同而非放宽检查。未验证真实数据库、生产同步、多版本 Python、宣称依赖下限环境、海量数据性能及所有错误分支；当前预装 openpyxl 低于原 requirements 的声明下限，单机通过不能替代安装矩阵。非加总指标、多对多清结算、会计确认和汇率不在 MVP 范围。

本轮修复 A01–A06，增加 14 个参数展开后的审计测试，未删原有检查。对“受控本地文件、已确认合同、可加总指标、人工复核、持续 degraded 输出”的展示 MVP 可放行；对“可信生产审计/自动正式发布”不放行，以上关键可信性缺口尚未解决。

适合求职展示的表述：**在原 data-analysis 项目上增量实现双源经营指标对账原型，加入可比性阻断、金额差异分解、可追溯工件与对抗回归；通过公开单源派生模拟双源展示异常检测，并独立审计修复日期错配和审核门禁问题。** 必须保留原作者归属、非商用许可和模拟数据限制，不得写成独立双系统上线、财务审计认证或业务收益实绩。
