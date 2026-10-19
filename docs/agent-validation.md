# 历史角色审查声明及其限制

此前开发记录声称使用 Locator、Mechanism、Falsifier、Reviewer 四角色并发审查，并保留本地 execution.json。后续独立审计无法从这些可修改的 JSON 认证实际执行，本次发布准备也未调用子 Agent。因此不把历史文件当作真实独立执行证明。

本次公开候选排除旧 agent-reviewed 角色工件，原本地工作区记录保留。四个当前 Demo 均为 CLI 确定性执行，报告保持 degraded。角色 schema 与数字检查仅是工件检查，不能证明来源独立、角色真实运行或根因成立。

实际测试证据见 release-validation.md；原始审计边界见 independent-audit.md。尚未验证真实双系统、独立原始输入复算或生产环境。
