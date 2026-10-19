# 来源、许可与贡献边界

原项目：[xiaomaxueshufen/data-analysis](https://github.com/xiaomaxueshufen/data-analysis)。原作者：小马学数分。基线 commit：e9821ed5c05dbcd29d215f55c28e64a052ef96e5。保留完整 Git 历史和 LICENSE，不将原项目功能或测试计为衍生作者原创。

Required Notice: Copyright 小马学数分 (xiaomaxueshufen, https://github.com/xiaomaxueshufen)

原项目贡献：模型主导的单源分析、分析算子、角色流程规范、真实性校验与 HTML 渲染，以及原 74 项测试。二次开发增量：scripts/reconcile、跨源 CLI、合同与对齐阻断、金额差异分解、输入/合同哈希、导出明细算术核验、模拟数据和新增 81 项回归测试；集成入口与方法说明有相应修改。开发过程使用 AI 辅助，个人职责应以实际参与及可解释程度表述。

许可：完整条款见 LICENSE（PolyForm Noncommercial 1.0.0）。本仓库不另行授予覆盖上游的商业授权。

公开样本：Daqing Chen，Online Retail II，UCI Machine Learning Repository，DOI https://doi.org/10.24432/C5CG6D，数据页面 https://archive.ics.uci.edu/dataset/502/online+retail+ii ，CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）。跨源样本抽取首 2000 行、移除客户标识并生成两种视图，对 B 人工注入 +7.25 GBP，详见 examples/cross_audit/public_retail/provenance.json。上游 case_study 聚合样本属于原作者示例，不计为本次原创。
