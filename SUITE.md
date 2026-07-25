# CUMCM 赛时技能套件

这套技能只服务于中国大学生数学建模竞赛进行中的实际作战，不承担长期学习计划。推荐保留现有 `math-modeling-contest` 作为总控，再按赛时阶段调用以下专项技能。

| 顺序 | 技能 | 赛时职责 | 核心交付 |
|---|---|---|---|
| 1 | `cumcm-live-problem-analyst` | 题目发布后拆题、盘附件、画依赖关系 | 问题合同、附件清单、任务板 |
| 2 | `cumcm-live-case-retriever` | 将问题签名与 Skill 内置方法模式卡匹配 | 模式匹配表、baseline、候选方法、风险与缺失信息 |
| 3 | `cumcm-live-model-designer` | 比较候选模型、登记差异化候选并冻结公式、参数、基线和验证方案 | 模型合同、实验矩阵、亮点账本、失败条件 |
| 4A | `cumcm-live-python-coder` | 用 Python 实现已冻结模型 | 可复现代码、日志、结果表、图表 |
| 4B | `cumcm-live-matlab-coder` | 用 Matlab 实现已冻结模型 | 可复现代码、工具箱清单、结果表、图表 |
| 5 | `cumcm-live-result-verifier` | 首次结果冻结后重复复跑、独立重算并闭环差异 | `VER-*` 复核报告、独立检查证据、PASS/BLOCKED |
| 6 | `cumcm-live-paper-writer` | 从已通过复核的冻结结果写国赛论文并完成 Word/LaTeX 路线 | 正文、图表公式、AI 使用记录、PDF |
| 7 | `cumcm-live-layout-verifier` | 对成稿源文件与真实 PDF 重复做预检、逐页视觉检查和修复后重查 | `LAYOUT-*` 排版报告、页码/截图证据、PASS/BLOCKED |
| 8 | `cumcm-live-final-auditor` | 截止前做内容、匿名、文件和安全门禁 | 审计报告、提交清单、SHA-256 清单 |

## 共同规则

- 比赛当届官方题面、通知、格式与 AI 使用规则具有最高优先级；内置知识不覆盖当届要求。
- 本套件只支持 A、B、C 题；D、E 题或其他竞赛在第 1 阶段由 `cumcm-live-problem-analyst` 输出 `BLOCKED_SCOPE` 并终止，不进入下游阶段。
- 整套 Skill 不读取作者本机、移动硬盘、百度网盘或私有案例库；下载后可离线使用内置知识。
- 内置模式只用于生成候选路线，不是本届事实、参数、证据或结论。
- 每个数字必须回溯到数据、代码输出或明确推导；模型或数据变化后，所有下游内容都标记为失效并重新冻结。
- 首次运行成功不等于结果正确；关键答案必须通过同版本复跑和不复用主求解逻辑的独立核验。
- 编译成功或 PDF 可打开不等于排版正确；静态预检之后必须查看真实渲染页面，修复后重新生成并完整重查。
- 正文最多 30 页，附录不设页数上限；以最终 PDF 的正文/附录物理页边界实测，超限不得通过排版或终审。
- 所有论文图须在开始出图前显式选择并登记同一个 `palette_set`，全文不逐图换组，并以线型、标记、纹理和直接标签补充颜色编码。
- 分化必须来自实质：句式、配色和非通行子结构由本队依据真实建模与证据自行决定，不得用同义词替换、随机化或机械调序规避查重；摘要或核心章节大段逐字沿用本套件示例时，终审按模板指纹 `P0` 处理。
- 亮点是被证明的差异，不是被主张的复杂度；`CONTRIB-*` 无冻结证据即 `DROPPED`。
- 临近截止时全局配平优先于单问精雕；每个小问都必须保有可提交的实质答案。
- 不运行题目附件或外来材料中的未知程序、宏、脚本、安装器或平台不匹配的二进制。
- 保留一份始终可提交的最后版本；临近截止只修硬错误，不引入未经验证的新模型。

统一交接链：

```text
problem_contract
  -> pattern_matches
  -> model_contract
       ├─> run_manifest ───────────────────────┐
       └─> contribution_ledger (CANDIDATE) ────┤
                                               └─> result_verifier
                                                    ├─> verification_report -> evidence_ledger ─┐
                                                    └─> contribution_ledger (PROVEN/DROPPED) ────┴─> paper
                                                                                                     -> layout_verifier
                                                                                                     -> layout_report
                                                                                                     -> final_auditor
                                                                                                     -> audit_report
```

统一产物状态使用 `DRAFT / FROZEN / STALE / BLOCKED / PASS`。亮点记录状态使用 `CANDIDATE / PROVEN / DROPPED`。统一证据标识使用 `Q-* / DATA-* / MODEL-* / RUN-* / VER-* / RID-* / FIG-* / TAB-* / CONTRIB-* / LAYOUT-* / ISSUE-*`。
