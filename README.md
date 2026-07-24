# 中国数学建模竞赛赛时技能套件

一组面向中国大学生数学建模竞赛（CUMCM）比赛进行中的 Codex skills。技能覆盖赛题拆解、历届案例检索、模型设计、Python/Matlab 实现、论文成稿与提交前终审。

本仓库只包含原创工作流、模板、检查表和安全检索脚本，不包含教材、历届论文、商业模板、第三方代码或软件安装包。

## 技能

| 技能 | 作用 |
|---|---|
| `cumcm-live-problem-analyst` | 题目发布后拆题、盘点附件、建立依赖和任务合同 |
| `cumcm-live-case-retriever` | 从本地资料中检索结构相似案例，不复制获奖论文 |
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

## 本地资料配置

案例检索技能默认在 `$HOME/Downloads` 下寻找以下七个编号文件夹。若资料位于其他位置，设置：

```bash
export CUMCM_RESOURCE_ROOT="/path/to/resource-parent"
```

该目录应包含：

```text
①历届赛题及获奖作品
②零基础入门教程
③建模必学软件及教程
④Python学习资料及常用模型算法代码
⑤Matlab学习资料及常用模型算法代码
⑥数学建模必备教材及课件
⑦写作与排版（含word及latex模板）
```

没有这些私有资料时，除本地案例检索外的赛时流程仍可使用。

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
- 获奖论文只用于结构类比，禁止复制正文、代码、图表、结论或数值。
- 每个论文数字必须回溯到数据、代码输出或明确推导。
- 不执行破解程序、Keygen、补丁、旧 EXE/LNK、未知宏或平台不匹配的 MEX。
- 模型、数据或代码变化后，将下游结果标记为失效并重新冻结。

详细调用顺序见 [SUITE.md](SUITE.md)。
