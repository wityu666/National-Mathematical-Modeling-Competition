# CUMCM 重复复核报告

> 复制后填写。首次结果目录只读；修复必须回到生产代码并生成新冻结版本。

## 0. 状态

| 字段 | 值 |
|---|---|
| verification_id | `VER-Q?-###` |
| verification_version | 1 |
| status | DRAFT / FROZEN / STALE / BLOCKED / PASS |
| contest_year |  |
| problem_id |  |
| question_id |  |
| contract_version |  |
| model_contract_version |  |
| model_freeze_id |  |
| run_id |  |
| contribution_ledger_version |  |
| started_at |  |
| finished_at |  |
| switch_deadline |  |
| owner |  |

`PASS` 只表示在本报告声明的输入、假设、容差和覆盖范围内通过复核，不表示对未知数据或未声明情景的绝对保证。

## 1. 冻结输入

| 角色 | 路径/标识 | SHA-256/版本 | 只读 | 备注 |
|---|---|---|---|---|
| 问题合同 |  |  | yes |  |
| 模型合同 |  |  | yes |  |
| 运行清单 |  |  | yes |  |
| 源代码 |  |  | yes |  |
| 配置 |  |  | yes |  |
| 输入数据 |  |  | yes |  |
| 首次结果目录 |  |  | yes |  |
| 亮点账本 |  |  | yes |  |

## 2. 预声明容差与覆盖

| 对象/指标 | evidence_id | 比较口径 | 绝对容差 | 相对容差 | 通过阈值 | 依据 |
|---|---|---|---:|---:|---|---|
|  | `RID/FIG/TAB/CONTRIB-*` |  |  |  |  |  |

- 确定性文件是否要求 SHA-256 完全一致：
- 随机结果比较统计量与重复次数：
- 明确不在本次复核覆盖内的内容：

## 3. Round A：同环境复跑

| 项目 | 首次运行 | 复跑 | 比较方法 | 状态 | 证据 |
|---|---|---|---|---|---|
| 文件集合与 schema |  |  |  | PASS / BLOCKED |  |
| 关键结果 |  |  |  | PASS / BLOCKED |  |
| 表格与图源 |  |  |  | PASS / BLOCKED |  |
| 哈希/数值容差 |  |  |  | PASS / BLOCKED |  |

- 全新进程命令：
- 复跑输出目录：
- `compare_runs.py` JSON 报告：

## 4. Round B：独立方法复核

| check_id | 被核结果 | 独立方法/实现 | 为什么独立 | 首次值 | 复核值 | 差异 | 状态 | 证据 |
|---|---|---|---|---:|---:|---:|---|---|
| `CHECK-Q?-001` | `RID-*` |  |  |  |  |  | PASS / BLOCKED |  |

## 5. 题型硬门

| Gate | 检查 | 通过标准 | 实际结果 | 状态 | 证据 |
|---|---|---|---|---|---|
| V-DATA | schema、单位、范围、泄漏 |  |  |  |  |
| V-MODEL | 公式、目标、约束、边界 |  |  |  |  |
| V-NUMERIC | 精度、收敛、NaN/Inf |  |  |  |  |
| V-RANDOM | seed、重复、区间 |  |  |  |  |
| V-EDGE | 极端与失效情景 |  |  |  |  |
| V-TRACE | RID/FIG/TAB 反向追踪 |  |  |  |  |

## 6. 关键结果复核账本

| evidence_id | 首次值/结论 | Round A | Round B | 硬门/边界 | 最终状态 |
|---|---|---|---|---|---|
| `RID-Q?-###` |  |  |  |  | PASS / BLOCKED |

## 7. 亮点复核

| contrib_id | claim/proof | 专门证据 | 独立复核 | cost_risk/失效边界 | 结论 |
|---|---|---|---|---|---|
| `CONTRIB-Q?-###` |  | `RID/FIG/TAB-*` |  |  | PROVEN / DROPPED / BLOCKED |

没有通过本节复核的亮点不得进入论文。

## 8. 差异与修复循环

| cycle | issue_id | 级别 | 首次值 | 复核值 | 根因 | 上游修复 | 新版本/freeze_id | 复核结果 |
|---:|---|---|---|---|---|---|---|---|
| 1 | `ISSUE-Q?-###` | P0 / P1 / P2 |  |  |  |  |  |  |

任何修复都会使旧轮次与下游产物 `STALE`；新冻结版本必须从 Round A 重做。

## 9. PASS 签核

- [ ] Round A 与 Round B 对应同一冻结版本并通过。
- [ ] 每个小问至少一个最终答案有独立复核。
- [ ] 所有关键结果位于预声明容差内。
- [ ] 硬约束、不变量、单位、边界和随机性检查通过。
- [ ] 所有 P0/P1 已关闭，修复后已完整重跑。
- [ ] 所有 `CONTRIB-PROVEN` 已通过独立复核。
- [ ] 命令、环境、证据路径和哈希完整。
- [ ] 未覆盖范围和失效条件已披露。

## 10. 下游交接

- 可供论文使用的 `RID/FIG/TAB`：
- 可供论文使用的 `CONTRIB-PROVEN`：
- 不得宣称的结果：
- 已知限制与未覆盖范围：
- 报告失效条件：
- 下游接收者：

