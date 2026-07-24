# Python 本地来源、兼容性与禁用项

## 根目录与用途

根目录：

`$CUMCM_RESOURCE_ROOT/④Python学习资料及常用模型算法代码`

把 `CUMCM_RESOURCE_ROOT` 设置为包含七个编号资料文件夹的目录；未设置时按 `$HOME/Downloads` 理解。只把该目录用作私有、只读、clean-room 路径索引。不要直接运行、导入、复制或打包其中的代码和二进制。

## 盘点结果

- 约 1.3GB，`rg --files` 可见 3,281 个文件。
- 主要类型：1,439 `.py`、45 `.ipynb`、149 `.xlsx`、30 `.csv`、29 `.docx`、27 `.pdf`。
- 1,439 个 `.py` 中 1,438 个可被 Python AST 静态解析；1 个含 Notebook 查询语法而失败。
- 仅 9 个 `.py` 含 `__main__` guard；260 个含 `plt.show()`，41 个含 `input()`，314 个含常见数据读取调用。
- 没有发现 `requirements.txt`、`pyproject.toml`、Conda 环境文件或其他依赖锁。
- 内容哈希显示约 1,050 组重复，冗余 2,115 个文件、约 555MB。

## 本机审计快照

此快照仅说明技能制作时的测试环境，每次比赛运行仍须重新检测：

- Python 3.13.5
- 已发现：NumPy、Pandas、SciPy、scikit-learn、Matplotlib、SymPy、Statsmodels、NetworkX、CVXPY、Pillow、imbalanced-learn
- 未发现：OpenCV、CVXOPT、XGBoost、LightGBM、hmmlearn、mlxtend、Graphviz Python 包、scikit-fuzzy、TA-Lib、tushare、apyori、qrcode、mplfinance
- CVXPY 1.8.0 可用 solver：`CLARABEL`、`HIGHS`、`OSQP`、`SCIPY`、`SCS`；没有 `GLPK_MI`
- Pandas 2.2.3 没有 `ExcelWriter.save`
- Statsmodels 0.14.4 没有 `sm.tsa.ARMA`

不要把这张快照写死进运行结论；它用于说明为何技能必须先预检再选择路线。

## 可参考路径

以下路径均相对于根目录。只读取必要片段并独立重写：

### 优化

- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/05第5章  线性规划(Python 程序及数据)/Pex5_1.py`
  - 展示 SciPy `linprog` 的最小输入结构；赛时应补充求解状态、容差和独立约束核验。
- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/06第6章  整数规划与非线性规划(Python 程序及数据)/Pex6_1.py`
  - 硬编码 `GLPK_MI`，本机不可用；把它当作 solver 预检与回退反例。

### 评价与图论

- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/09第9章  综合评价方法(Python 程序及数据)/Pex9_1.py`
  - 展示指标正负向和多种标准化；同时会写当前目录并调用旧 `ExcelWriter.save`，不可直接运行。
- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/10第10章  图论模型(Python 程序及数据)/mydijkstra.py`
  - 可用于核对 Dijkstra 的输入输出结构；正式实现优先使用已测试的 NetworkX 并用小图交叉验证。

### 预测与仿真

- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/15第15章  灰色系统预测(Python 程序及数据)/Pex15_1.py`
  - 可用于理解累加序列和拟合误差；需补齐适用性检验、留出验证和不确定性。
- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/16第16章  Monte Carlo模拟(Python 程序及数据)/Pex16_6.py`
  - 可用于识别 Monte Carlo 输出；正式实现使用显式 RNG、seed、重复次数和置信区间。
- `2、数学建模常用python代码包/Python资料 数学建模常用算法（Python 程序及数据）/18第18章  时间序列分析(Python 程序及数据)/Pex18_5_1.py`
  - 使用已移除的 `sm.tsa.ARMA`；正式实现改用现代 `statsmodels.tsa.arima.model.ARIMA`，并先跑朴素 baseline。

### 机器学习案例

`7-机器学习实战案例及代码/源代码汇总` 含 16 章案例，可定位回归、逻辑回归、决策树、随机森林、Boosting、PCA、聚类、推荐、Apriori 和神经网络的旧输入输出。不要把案例数据切分或单次指标原样用于本届。

唯一静态语法失败文件：

`7-机器学习实战案例及代码/源代码汇总/第9章 AdaBoost与GBDT模型/源代码汇总_Pycharm/9.2 案例实战 - AdaBoost信用卡精准营销模型.py`

其中包含 `AdaBoostClassifier?`、`AdaBoostRegressor?`，这是 Notebook 查询语法，不是普通 Python。

## 明确禁用

- 4 个约 134.6MB、内容相同的 `2.exe`，位于背包问题目录。
- `7-机器学习实战案例及代码/源代码汇总/第8章 随机森林模型` 下的 CPython 3.7/3.8 Windows TA-Lib Wheel。
- `6、按赛题类别划分的常用算法代码` 下约 90MB、120MB、207MB 的 ZIP/RAR。
- `5、30个常用算法Python代码` 下约 135MB ZIP。
- 所有 `.pyc`、`.spec`、EXE、Wheel、RAR/ZIP 及无法确认来源和许可证的字体、图片、书籍、PPT。

这些文件既有平台/安全风险，也没有技能分发所需的清晰许可。

## Clean-room 落地原则

1. 从模型合同重新写接口、公式和验证，不从旧案例复制实现。
2. 优先 Python 标准库和已验证的 NumPy/SciPy/scikit-learn/Statsmodels/NetworkX。
3. 每个增强依赖都提供无该依赖时的 baseline 回退。
4. 生成自己的合成冒烟数据；不把原案例数据打包进技能。
5. 保存环境、输入哈希、seed、指标、日志和冻结输出。
