# 风险清单（开发前）

|风险|防护与测试|残余限制|
|---|---|---|
|口径相似但不可比|逐项合同一致且确认；定义/范围/截止测试|用户错误确认不能自动识别|
|重复、多对多膨胀|原 grain 唯一性，再聚合字典匹配|不支持真实多对多清结算|
|金额精度、抵消、累计容差|Decimal、恒等式、局部+全局阈值、性质测试|资源预算内精度|
|数据缺失当零|空金额阻断，未匹配另一侧留空|不推测缺失机制|
|提示词/HTML/CSV 注入|单元格只当数据、HTML escaping、CSV 公式前缀|CSV 导出为安全展示，原值见 JSON|
|资源耗尽|文件/行/列/解压大小限制、只读 Excel|不是流式海量引擎|
|路径与覆盖|UUID 新目录、拒绝 symlink 输入、无配置输出路径|调用者有本地文件读取权限|
|虚假 Agent 或真实业务宣传|pending/degraded，保存实际工具 ID|无独立财务真值|
|原修改被覆盖|新分支、记录初始 dirty 状态|同一 checkout 原修改仍存在|

阶段更新见 progress.md；反向审查新增问题必须关联实际回归测试。

## 独立反向审查与修复

- Falsifier 实测内部 `__source_row__` 覆盖金额导致 30/27 被误报 5/5 一致：合同拒绝内部前缀与 source_rows，新增三项保留名称回归。
- Falsifier 实测原生 Excel 日期被字符串化导致 CSV/XLSX 不等价：loader 保留 date/datetime，规范化显式接纳原生类型，新增等价性测试。
- 集成自检发现原 da_verify 不收集 Decimal 字符串：精确值保持 exact_values，增加只用于原声明核验的 float values；新增真实数值绑定测试。Float 核验不得替代精确数学检查。
- 原报告 analysis 区只渲染 tables 数组：适配 tables 并检查 HTML 中确实存在 net_difference，避免有结果但报告遗漏金额。
- 原 Skill 的顶层 compatibility 不被当前官方 quick_validate 接受：移动至 metadata.compatibility，保留原文信息。
