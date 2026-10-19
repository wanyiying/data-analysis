# 源码阅读与面试学习指南

## 先理解原工作流

原 SKILL.md 让模型识别问题、选择方法、建立语义合同、调用可选探针，再按 harness 做四角色审查，使用 da_verify 检查结论证据，da_report 渲染六段 HTML。不是把所有算子串成固定流水线。先读 SKILL、intent-routing、harness，再看 da_ops.main 的单文件入口、da_reconcile.main 的表内合计边界。

## 新增数据怎样流动

从 `scripts/da_cross_reconcile.py:main` 开始：参数→UUID 新目录→读取 config→两个 load→profile→audit→emit。`load` 保留 CSV 文本 ID，Excel 日期保留原生类型；`list_bounded` 限制行列和单元格尺寸。异常分为业务 AuditError 和输入 ERROR，仍输出 degraded HTML。

`contract.validate` 验证 confirmed、加总定义、规范单位/币种、日期含义、范围、截止、粒度。字段名字相似不代表指标一样。合同不成立就不会进入金额比较。`decimal` 拒绝非有限值、隐式千分位和超精度数值。

`normalization.normalize` 执行明确日期解析、闭区间、筛选、原 grain 空值与唯一性、显式倍率。Excel native datetime 直接取业务日；文本按 format 解析。`__source_row__` 为内部行号，合同禁止保留字段名；这是反向审查发现假一致后加入的防护。

`alignment.plan` 给五态中的就绪态；阻断与待确认由合同异常携带状态。`matching.aggregate` 在唯一明细粒度验证后按较粗比较键 Decimal 求和，再以字典唯一键外连接，避免 merge 多对多膨胀。`comparison.compare` 独立保存两侧金额，单侧缺失不填零，逐键差额始终 A−B，累计正负及绝对差异，并验证完整恒等式。

`engine.audit` 组织这些纯计算阶段，128 位局部 Decimal 上下文保证预算内求和；`diagnostics.diagnose` 只生成观察事实与待检验候选。没有系统事件日志就不声称退款、延迟或某人处理错误是根因。

`evidence.emit` 保存原始金额字符串、血缘、合同、独立状态与报告规格，调用原 da_report。evidence 的 exact_values 是精确值，values 是给原 da_verify 的数值适配副本；原验证器不读取数字字符串，而且其 float 容差不能替代确定性 Decimal 审计。`verify_cross_audit_run.verify` 独立核验输入哈希、导出明细的金额与状态和汇总恒等式，不证明业务真值。

## 如何复现和扩展

安装 requirements-audit-dev.txt 后执行 `python scripts/generate_cross_audit_cases.py`、`python scripts/run_cross_audit_demos.py`，读取输出 index.json 找各次 report.html。测试用 `PYTHONUTF8=1`，Windows PowerShell 见 testing.md。阅读 tests/test_cross_audit.py 的手工答案测试，再看交换、重排、拆分性质测试；不要让 expected 调用生产算法。

新增指标先判断能否加总；比率/去重/MRR 不能直接加入 sum。新增粒度要先增加确认合同和阻断测试，再添加转换，不能为了跑通删除重复记录或扩大容差。扩展来源不要把自定义代码或表达式放配置执行。

## 如何解释个人贡献

如实说：在小马学数分原模型主导 Skill 上，新增独立双源确定性审计、业务可比性合同、唯一粒度安全匹配、金额恒等式、状态协议、可复现案例、回归性质测试与四角色实证。报告渲染、原分析方法和基础角色框架属于原作者。展示“总额差零但正负抵消十元”和“口径不同安全阻断”，更能说明工程判断。

不要说已在真实企业部署、自动找到真实根因、减少多少人工时间；本项目没有这些证据。公开样本来自同一 UCI 数据派生的两个模拟视图，交易金额不等于会计收入。许可证限制和当前资源边界都是作品说明的一部分。
