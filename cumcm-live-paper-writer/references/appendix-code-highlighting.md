# 附录代码多色语法高亮规范

## 1. 目标与边界

附录关键建模代码默认使用统一的 `code_theme=VS-CODE-LIGHT-MUTED`。该主题参考 VS Code 浅色编辑器的语义区分方式，但为白底论文、打印和 PDF 导出降低饱和度；它不是编辑器截图，也不是逐行任意配色。

- 代码必须保持为可选择、可复制、可搜索的真实文本；不得用截图、整页图片或不可编辑对象替代。
- 同一篇论文的全部附录代码只使用一个 `code_theme`，同一语义角色始终使用同一字体颜色和字形，不得按代码块随机换色。
- `code_theme` 只控制代码语法高亮，与论文图表的 `palette_set/object_color_map` 相互独立；不得为了匹配图表对象而改变关键字、字符串或注释颜色。
- 颜色只是辅助编码。即使转为灰度或色觉发生变化，仍须能从关键字加粗、注释斜体、引号、缩进、标点和代码结构理解语义。
- 当届官方规则明确要求黑白或禁止彩色时，记录 `code_theme=MONOCHROME_OFFICIAL_OVERRIDE` 与规则证据，改用等宽黑色正文、关键字加粗和注释斜体；官方规则优先。

## 2. `VS-CODE-LIGHT-MUTED` 语义色表

| 语义角色 | 色值 | 字形 | 适用对象 |
|---|---|---|---|
| 普通文本、运算符与标点 | `#1F2328` | 常规 | 变量、括号、运算符和未单列语法 |
| 关键字、控制语句与内置类型 | `#264F78` | 加粗 | `if/for/def/class/end/function` 等 |
| 函数与方法名 | `#795E26` | 常规 | 定义和调用处的函数、方法 |
| 类名与装饰器 | `#7A3E9D` | 加粗 | 类、装饰器及同类语言结构 |
| 字符串与路径字面量 | `#A31515` | 常规 | 字符串、路径和格式字符串文本 |
| 注释 | `#2E7D32` | 斜体 | 行注释、块注释；文档字符串按实际语义归类 |
| 数值与常量 | `#098658` | 常规 | 数字、布尔值、空值和命名常量 |
| 行号 | `#6B7280` | 常规 | 可选行号，不得抢过代码正文 |
| 背景与边框 | `#FFFFFF` / `#D1D5DB` | 白底、细边框 | 禁止深色编辑器背景和大面积色块 |

代码片段没有某类 token 时，不必为了“颜色齐全”伪造内容。禁止把整行或整段涂成不同颜色、使用彩虹渐变、荧光色、下划线装饰或深色 VS Code 编辑器背景。

## 3. 字体、字号与分页

- 优先使用 `Consolas`；不可用时按 `Cascadia Mono`、`Source Code Pro`、`Menlo`、`Courier New` 或模板可用的等宽字体顺序回退，并记录实际字体。不得为此临时安装来源不明的字体。
- 字号服从当届模板并以最终 PDF 可读性为准；不得为容纳长代码缩小到不可辨认。
- 保留真实缩进和换行；长行在语义安全位置折行并加续行缩进，不得让代码越出页边界。
- 行号可选。若使用，行号必须连续、低对比且与代码正文分离；跨页后不得重置成造成引用歧义的编号。

## 4. Word 路线

1. 将冻结源代码作为真实文本写入 Word，使用统一的“附录代码”段落样式和等宽字体。
2. 由可信的本地语法分析器、编辑器导出的可编辑富文本，或生成 Word 时的 run 级字体颜色设置完成 token 级高亮；不得粘贴编辑器截图。
3. 清除编辑器界面、文件标签、折叠标记、光标、选择高亮、网页链接和深色背景，只保留代码文本及上述语义色。
4. 抽查至少三处跨颜色复制：粘贴到纯文本后字符、空格、缩进和换行应与冻结源代码一致。
5. PDF 必须由当前冻结 Word 重新导出，并核对颜色、字形、换行、分页和可复制文本没有变化。

## 5. LaTeX 路线

优先使用 `listings` 与 `xcolor` 实现，不依赖 `minted`、shell escape 或新增的运行时高亮服务。基础样式至少应落实以下映射：

```latex
\definecolor{CodeText}{HTML}{1F2328}
\definecolor{CodeKeyword}{HTML}{264F78}
\definecolor{CodeFunction}{HTML}{795E26}
\definecolor{CodeClass}{HTML}{7A3E9D}
\definecolor{CodeString}{HTML}{A31515}
\definecolor{CodeComment}{HTML}{2E7D32}
\definecolor{CodeNumber}{HTML}{098658}
\definecolor{CodeLine}{HTML}{6B7280}
\definecolor{CodeBorder}{HTML}{D1D5DB}
\lstdefinestyle{cumcm-appendix-code}{
  basicstyle=\ttfamily\small\color{CodeText},
  keywordstyle=\color{CodeKeyword}\bfseries,
  commentstyle=\color{CodeComment}\itshape,
  stringstyle=\color{CodeString},
  numberstyle=\scriptsize\color{CodeLine},
  backgroundcolor=\color{white},
  rulecolor=\color{CodeBorder},
  frame=single,breaklines=true,keepspaces=true,
  columns=fullflexible,showstringspaces=false
}
```

`listings` 对函数、类名、数值常量的识别能力依语言配置而异。能可靠识别时使用 `emph/emphstyle` 或语言级 token 配置映射到上表；不能可靠识别时保留普通文本色，不得用不准确的正则把变量批量误染色。配置本身只负责排版，不得改写代码内容。

## 6. 复核清单

- `code_theme` 已记录，全部附录代码使用同一主题；官方黑白例外有规则证据。
- Word 与 PDF 中 token 文本、语义颜色、加粗/斜体、字体、缩进和换行一致。
- 代码可选择、可复制、可搜索；纯文本复制抽查与冻结源代码一致。
- 白底打印清晰，彩色与灰度预览均能区分代码结构；颜色失效时仍有字形和语法冗余。
- 无截图、深色背景、随机配色、彩虹渐变、编辑器界面、水印、裁切、越界或不可读小字。
- 多色高亮没有改变 `CODE-*` 对应的源代码字符，也没有把非核心辅助代码包装成关键建模代码。
