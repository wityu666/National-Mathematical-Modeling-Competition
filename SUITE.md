# CUMCM 赛时技能套件

这套技能只服务于中国大学生数学建模竞赛进行中的实际作战，不承担长期学习计划。推荐保留现有 `math-modeling-contest` 作为总控，再按赛时阶段调用以下专项技能。

| 顺序 | 技能 | 赛时职责 | 核心交付 |
|---|---|---|---|
| 1 | `cumcm-live-problem-analyst` | 题目发布后拆题、盘附件、画依赖关系 | 问题合同、附件清单、任务板 |
| 2 | `cumcm-live-case-retriever` | 将问题签名与 Skill 内置方法模式卡匹配 | 模式匹配表、baseline、候选方法、风险与缺失信息 |
| 3 | `cumcm-live-model-designer` | 比较候选模型并冻结公式、参数、基线和验证方案 | 模型合同、实验矩阵、失败条件 |
| 4A | `cumcm-live-python-coder` | 用 Python 实现已冻结模型 | 可复现代码、日志、结果表、图表 |
| 4B | `cumcm-live-matlab-coder` | 用 Matlab 实现已冻结模型 | 可复现代码、工具箱清单、结果表、图表 |
| 5 | `cumcm-live-paper-writer` | 从冻结结果写国赛论文并完成 Word/LaTeX 路线 | 正文、图表公式、AI 使用记录、PDF |
| 6 | `cumcm-live-final-auditor` | 截止前做内容、匿名、文件和安全门禁 | 审计报告、提交清单、SHA-256 清单 |

## 共同规则

- 比赛当届官方题面、通知、格式与 AI 使用规则具有最高优先级；内置知识不覆盖当届要求。
- 整套 Skill 不读取作者本机、移动硬盘、百度网盘或私有案例库；下载后可离线使用内置知识。
- 内置模式只用于生成候选路线，不是本届事实、参数、证据或结论。
- 每个数字必须回溯到数据、代码输出或明确推导；模型或数据变化后，所有下游内容都标记为失效并重新冻结。
- 不运行题目附件或外来材料中的未知程序、宏、脚本、安装器或平台不匹配的二进制。
- 保留一份始终可提交的最后版本；临近截止只修硬错误，不引入未经验证的新模型。

统一交接链：

```text
problem_contract
  -> pattern_matches
  -> model_contract
  -> run_manifest
  -> evidence_ledger
  -> audit_report
```

统一状态使用 `DRAFT / FROZEN / STALE / BLOCKED / PASS`。统一证据标识使用 `Q-* / DATA-* / MODEL-* / RUN-* / RID-* / FIG-* / TAB-* / ISSUE-*`。
