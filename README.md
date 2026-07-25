# 中国数学建模竞赛赛时技能套件

一组面向中国大学生数学建模竞赛（CUMCM）比赛进行中的 Codex skills。本套件只支持国赛 A、B、C 题，不支持 D、E 题。技能覆盖赛题拆解、内置方法模式匹配、模型设计、Python/MATLAB 实现、首次结果重复复核、论文成稿、重复排版复核与提交前终审，并用 `CONTRIB-*` 亮点账本把可验证的差异化成果贯穿全链路。

这是“自包含知识版”：通用建模知识已经被原创整理为 Skill 内置的模式卡、决策规则、实现配方和检查表。安装后不需要作者的电脑、移动硬盘、百度网盘或其他私有资料库，也不会在运行时联网检索案例。

这里的“内置”不是对模型权重进行训练或微调。仓库不包含教材、历届论文、商业模板、第三方代码、案例结果或软件安装包；本届题面、附件、官方规则和团队实际运行结果仍须由参赛者在比赛时提供。

## 技能

| 技能 | 作用 |
|---|---|
| `cumcm-live-problem-analyst` | 题目发布后拆题、盘点附件、建立依赖和任务合同 |
| `cumcm-live-case-retriever` | 将当前问题签名与内置原创方法模式卡匹配 |
| `cumcm-live-model-designer` | 比较 baseline 与候选模型，登记并验证 `CONTRIB-*` 亮点，冻结公式、验证和降级方案 |
| `cumcm-live-python-coder` | 把冻结模型实现为可复现的 Python 结果 |
| `cumcm-live-matlab-coder` | 把冻结模型实现为可复现的 Matlab 结果 |
| `cumcm-live-result-verifier` | 首次结果冻结后执行复跑、独立重算、边界检查和差异修复闭环 |
| `cumcm-live-paper-writer` | 从冻结结果完成国赛论文、AI 记录和 PDF QA |
| `cumcm-live-layout-verifier` | 成稿后重复检查 Word/LaTeX 源和真实 PDF 排版，闭环修复裁切、重叠、分页、字体与可读性问题 |
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

维护者修改合同或门禁后，可在套件根目录运行：

```bash
python3 -m pytest -q
```

## 自包含知识库

- `problem-analyst` 内置拆题、附件契约和依赖分析规则。
- `case-retriever` 保留原名称以兼容已有调用，但职责已改为离线方法模式匹配。
- `model-designer` 内置模型阶梯、题型路由、验证和降级规则。
- Python/MATLAB Skill 内置可复现工程、数值检查、求解器复核和测试配方。
- `result-verifier` 在首次求解后用重复复跑与独立方法交叉核验关键结果。
- `layout-verifier` 在成稿后把静态预检、真实 PDF 逐页查看和修复后重查串成闭环。
- 写作与终审 Skill 内置证据账本、亮点真实性门、成稿一致性和提交审计协议。

内置知识只提供候选路线，不能替代对本届题意、数据和规则的核验，也不能作为论文数值或结论来源。

## 赛时顺序

```text
problem_contract -> pattern_matches -> model_contract
                                      ├─> run_manifest ──────────────────────┐
                                      └─> contribution_ledger (CANDIDATE) ───┤
                                                                             └─> result_verifier
                                                                                  ├─> verification_report -> evidence_ledger ─┐
                                                                                  └─> contribution_ledger (PROVEN/DROPPED) ────┴─> paper
                                                                                                                               -> layout_verifier
                                                                                                                               -> layout_report
                                                                                                                               -> final_auditor
                                                                                                                               -> audit_report
```

## 共同门禁

- 当届官方题面、通知、格式和 AI 使用规则始终具有最高优先级。
- 本套件只支持 A、B、C 题；题号为 D、E 或其他竞赛时，`problem-analyst` 输出 `BLOCKED_SCOPE` 并终止，不进入下游阶段。
- 不把内置模式卡当作历届案例证据；参数、约束和结论必须从本届题面与实际数据重新推导。
- 每个论文数字必须回溯到数据、代码输出或明确推导。
- 首次运行成功不等于结果正确；关键答案必须同时通过同版本复跑与独立方法复核。
- 编译成功不等于排版正确；当前 PDF 必须通过自动预检和真实逐页渲染复核，且修复后从头重查。
- 正文不得超过 30 页，附录页数不设上限；必须按最终 PDF 记录正文起始页、附录起始页和实测正文页数，超限即 `BLOCKED`。
- 论文图默认使用固定的低饱和莫兰迪色板 `cumcm-morandi-v1`；颜色之外必须同时使用线型、标记或直接标签保证灰度与色觉缺陷下可辨。
- 亮点是被证明的差异，不是被主张的复杂度；只有绑定当前冻结证据的 `CONTRIB-PROVEN` 才能进入论文。
- 每个小问都必须有可提交的实质答案；临近截止时全局配平优先于单点最优。
- 不执行题目附件或外来材料中的未知二进制、宏、脚本或安装器。
- 模型、数据或代码变化后，将下游结果标记为失效并重新冻结。

统一证据标识使用 `Q-* / DATA-* / MODEL-* / RUN-* / VER-* / RID-* / FIG-* / TAB-* / CONTRIB-* / LAYOUT-* / ISSUE-*`。亮点记录使用 `CANDIDATE / PROVEN / DROPPED`；套件产物仍使用 `DRAFT / FROZEN / STALE / BLOCKED / PASS`。

详细调用顺序见 [SUITE.md](SUITE.md)。
