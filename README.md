# 中国数学建模竞赛赛时技能套件

一组面向中国大学生数学建模竞赛（CUMCM）比赛进行中的 Codex skills。技能覆盖赛题拆解、内置方法模式匹配、模型设计、Python/MATLAB 实现、论文成稿与提交前终审。

这是“自包含知识版”：通用建模知识已经被原创整理为 Skill 内置的模式卡、决策规则、实现配方和检查表。安装后不需要作者的电脑、移动硬盘、百度网盘或其他私有资料库，也不会在运行时联网检索案例。

这里的“内置”不是对模型权重进行训练或微调。仓库不包含教材、历届论文、商业模板、第三方代码、案例结果或软件安装包；本届题面、附件、官方规则和团队实际运行结果仍须由参赛者在比赛时提供。

## 技能

| 技能 | 作用 |
|---|---|
| `cumcm-live-problem-analyst` | 题目发布后拆题、盘点附件、建立依赖和任务合同 |
| `cumcm-live-case-retriever` | 将当前问题签名与内置原创方法模式卡匹配 |
| `cumcm-live-model-designer` | 比较 baseline 与候选模型，冻结公式、验证和降级方案 |
| `cumcm-live-python-coder` | 把冻结模型实现为可复现的 Python 结果 |
| `cumcm-live-matlab-coder` | 把冻结模型实现为可复现的 Matlab 结果 |
| `cumcm-live-paper-writer` | 从冻结结果完成国赛论文、AI 记录和 PDF QA |
| `cumcm-live-final-auditor` | 提交前检查内容、文件、安全、匿名和可复现性 |

## 安装

```bash
git clone https://github.com/wityu666/National-Mathematical-Modeling-Competition.git
cd National-Mathematical-Modeling-Competition
cp -R cumcm-live-* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

重新打开 Codex 任务后即可调用，例如：

```text
请使用 $cumcm-live-problem-analyst 读取刚发布的赛题和附件，先完成拆题、依赖分析与任务分工。
```

## 自包含知识库

- `problem-analyst` 内置拆题、附件契约和依赖分析规则。
- `case-retriever` 保留原名称以兼容已有调用，但职责已改为离线方法模式匹配。
- `model-designer` 内置模型阶梯、题型路由、验证和降级规则。
- Python/MATLAB Skill 内置可复现工程、数值检查、求解器复核和测试配方。
- 写作与终审 Skill 内置证据账本、成稿一致性和提交审计协议。

内置知识只提供候选路线，不能替代对本届题意、数据和规则的核验，也不能作为论文数值或结论来源。

## 赛时顺序

```text
problem-analyst
  -> case-retriever
  -> model-designer
  -> python-coder 或 matlab-coder
  -> paper-writer
  -> final-auditor
```

## 共同门禁

- 当届官方题面、通知、格式和 AI 使用规则始终具有最高优先级。
- 不把内置模式卡当作历届案例证据；参数、约束和结论必须从本届题面与实际数据重新推导。
- 每个论文数字必须回溯到数据、代码输出或明确推导。
- 不执行题目附件或外来材料中的未知二进制、宏、脚本或安装器。
- 模型、数据或代码变化后，将下游结果标记为失效并重新冻结。

详细调用顺序见 [SUITE.md](SUITE.md)。
