# PDF Page Extractor — Code Wiki

> 一个灵活的 PDF 页面提取工具，支持指定页码、范围、奇偶页、间隔、正则匹配、文件读取以及批量生成等多种提取方式。可作为命令行工具使用，也可作为 Python 模块被其他程序导入调用。

---

## 目录

1. [项目概述](#1-项目概述)
2. [目录结构](#2-目录结构)
3. [整体架构](#3-整体架构)
4. [模块职责](#4-模块职责)
5. [关键函数说明](#5-关键函数说明)
6. [依赖关系](#6-依赖关系)
7. [运行方式](#7-运行方式)
8. [错误处理与边界条件](#8-错误处理与边界条件)
9. [扩展指南](#9-扩展指南)

---

## 1. 项目概述

### 1.1 项目定位

PDF Page Extractor 是一个轻量级、单文件实现的 PDF 页面提取工具。它的核心目标是提供多种灵活的页面选择策略，将用户指定的页面从源 PDF 中抽取出来并写入新的 PDF 文件。

### 1.2 核心能力

| 能力 | 说明 |
|------|------|
| 指定页码 | 提取单个或多个指定页码（如 `1,3,5`） |
| 页码范围 | 提取连续范围（如 `1-5,10-15`） |
| 奇偶页 | 提取全部偶数页或全部奇数页 |
| 间隔提取 | 从起始页开始按固定间隔提取 |
| 正则匹配 | 按页码数字的正则模式匹配提取 |
| 文件列表 | 从文本文件读取页码列表 |
| 批量模式 | 逐行解析范围文件，生成多个输出 PDF |

### 1.3 技术栈

- **语言**：Python 3.7+
- **核心库**：[PyPDF2](https://pypi.org/project/PyPDF2/)（PDF 读写）
- **标准库**：`argparse`、`re`、`pathlib`、`typing`

---

## 2. 目录结构

```
/workspace/
├── SKILL.md                # 技能说明文档（Quick Start、使用示例、依赖）
└── scripts/
    └── pdf_extract.py      # 核心实现：全部页面选择逻辑与 PDF 读写
```

> 该项目为单脚本结构，所有业务逻辑集中在 `scripts/pdf_extract.py` 中，`SKILL.md` 作为对外使用说明。

---

## 3. 整体架构

### 3.1 架构分层

项目采用「页面选择策略 + PDF 读写 + CLI 入口」三段式结构：

```
┌───────────────────────────────────────────────────────┐
│                     CLI 入口层                         │
│              main() / argparse 解析                    │
│   输入校验 → 选择策略 → 调用提取 → 输出结果            │
└───────────────────────┬───────────────────────────────┘
                        │ 调用
┌───────────────────────▼───────────────────────────────┐
│                  页面选择策略层                        │
│  parse_page_ranges / extract_even_pages                │
│  extract_odd_pages / extract_pages_by_interval         │
│  extract_pages_by_regex / extract_pages_from_file      │
│  batch_extract_from_file                               │
│  职责：根据不同策略计算出 List[int] 页码列表           │
└───────────────────────┬───────────────────────────────┘
                        │ 输入页码列表
┌───────────────────────▼───────────────────────────────┐
│                    PDF 读写层                          │
│  get_total_pages / extract_pdf_pages                   │
│  职责：通过 PyPDF2 读取源 PDF、写入目标 PDF            │
└───────────────────────────────────────────────────────┘
```

### 3.2 核心数据流

```
输入 PDF ──► get_total_pages() ──► total_pages
                                        │
                  选择策略函数 ──────────┘
                       │
                       ▼
              List[int] (页码列表，已去重排序)
                       │
                       ▼
              extract_pdf_pages() ──► 输出 PDF
```

- 所有选择策略均以 `total_pages` 为边界约束，最终输出统一的 `List[int]`。
- 页码采用 **1-based** 索引（面向用户），在 `extract_pdf_pages` 内部转换为 **0-based** 索引（PyPDF2 API）。

---

## 4. 模块职责

### 4.1 `scripts/pdf_extract.py`

整个项目的唯一源码文件，承担三类职责：

| 职责分组 | 代表函数 | 说明 |
|----------|----------|------|
| 页面选择策略 | `parse_page_ranges`、`extract_even_pages`、`extract_odd_pages`、`extract_pages_by_interval`、`extract_pages_by_regex`、`extract_pages_from_file` | 根据不同输入方式计算待提取的页码列表 |
| PDF 读写 | `get_total_pages`、`extract_pdf_pages` | 调用 PyPDF2 读取页数、按页码列表组装并写出 PDF |
| 批量处理 | `batch_extract_from_file` | 读取范围文件，逐行生成多个输出 PDF |
| CLI 入口 | `main` | 解析命令行参数、校验输入、调度策略与提取流程 |

### 4.2 `SKILL.md`

技能说明文档，面向使用者。包含 Quick Start、七种提取方式的命令行示例、程序化调用示例以及依赖安装说明。不包含实现细节。

---

## 5. 关键函数说明

### 5.1 页面选择策略函数

#### `parse_page_ranges(ranges_str: str, total_pages: int) -> List[int]`

- **位置**：[pdf_extract.py:8](file:///workspace/scripts/pdf_extract.py#L8-L38)
- **职责**：将形如 `1,3,5-10` 的字符串解析为页码列表。
- **参数**：
  - `ranges_str`：以逗号分隔的页码或范围字符串。范围用 `-` 连接，如 `1-5`；可省略起始或结束，分别默认为 `1` 和 `total_pages`。
  - `total_pages`：源 PDF 总页数，用于边界校验。
- **返回**：去重并升序排序后的页码列表。
- **异常**：
  - `ValueError("Invalid range format: ...")`：范围中 `-` 数量不为 1。
  - `ValueError("Invalid page range: ...")`：起始 < 1、结束 > total_pages 或起始 > 结束。
  - `ValueError("Page X is out of range ...")`：单页越界。
- **实现要点**：按 `,` 拆分 → 逐段判断是否含 `-` → 范围用 `range(start, end+1)` 展开 → 最后 `sorted(list(set(...)))` 去重排序。

#### `extract_even_pages(total_pages: int) -> List[int]`

- **位置**：[pdf_extract.py:41](file:///workspace/scripts/pdf_extract.py#L41-L42)
- **职责**：返回全部偶数页 `[2, 4, 6, ...]`。

#### `extract_odd_pages(total_pages: int) -> List[int]`

- **位置**：[pdf_extract.py:45](file:///workspace/scripts/pdf_extract.py#L45-L46)
- **职责**：返回全部奇数页 `[1, 3, 5, ...]`。

#### `extract_pages_by_interval(total_pages: int, start: int, interval: int) -> List[int]`

- **位置**：[pdf_extract.py:49](file:///workspace/scripts/pdf_extract.py#L49-L50)
- **职责**：从 `start` 页开始，每隔 `interval` 页取一页。
- **实现**：`range(start, total_pages + 1, interval)`。
- **注意**：`start` 和 `interval` 的合法性未在此函数内校验，由调用方（CLI）保证。

#### `extract_pages_by_regex(total_pages: int, pattern: str) -> List[int]`

- **位置**：[pdf_extract.py:53](file:///workspace/scripts/pdf_extract.py#L53-L58)
- **职责**：遍历 1..total_pages，将页码转为字符串后用 `re.search(pattern, str(i))` 匹配，命中则加入结果。
- **示例**：`"1.*"` 匹配 1、10–19、100–199 等；`"5$"` 匹配 5、15、25 等。

#### `extract_pages_from_file(file_path: str, total_pages: int) -> List[int]`

- **位置**：[pdf_extract.py:61](file:///workspace/scripts/pdf_extract.py#L61-L70)
- **职责**：从文本文件逐行读取页码（每行一个整数），过滤越界值后返回去重排序的列表。
- **容错**：非数字行（`line.isdigit()` 为 False）会被静默跳过。

### 5.2 PDF 读写函数

#### `get_total_pages(input_path: str) -> int`

- **位置**：[pdf_extract.py:103](file:///workspace/scripts/pdf_extract.py#L103-L106)
- **职责**：打开 PDF 并返回总页数 `len(reader.pages)`。
- **依赖**：`PyPDF2.PdfReader`。

#### `extract_pdf_pages(input_path: str, output_path: str, pages: List[int]) -> None`

- **位置**：[pdf_extract.py:91](file:///workspace/scripts/pdf_extract.py#L91-L100)
- **职责**：核心提取动作——读取源 PDF，按 `pages` 列表逐页 `add_page`，写出到 `output_path`。
- **索引转换**：`reader.pages[page_num - 1]`（用户 1-based → PyPDF2 0-based）。
- **写入方式**：以二进制写入模式打开输出文件，`writer.write(output_file)`。

### 5.3 批量处理函数

#### `batch_extract_from_file(input_path, file_path, output_prefix, total_pages) -> None`

- **位置**：[pdf_extract.py:73](file:///workspace/scripts/pdf_extract.py#L73-L88)
- **职责**：批量模式。读取 `file_path` 的每一行作为一个页面范围，逐行调用 `parse_page_ranges` 与 `extract_pdf_pages`，生成 `output_prefix_NN.pdf`。
- **命名**：输出文件名使用 `f"{output_prefix}_{idx:02d}.pdf"`，`idx` 从 1 开始。
- **容错**：
  - 空范围行打印 Warning 并跳过。
  - 单行解析失败（`ValueError`）打印 Error 但不中断后续行。

### 5.4 CLI 入口

#### `main() -> int`

- **位置**：[pdf_extract.py:109](file:///workspace/scripts/pdf_extract.py#L109-L228)
- **职责**：
  1. 使用 `argparse` 定义位置参数 `input`、`output` 和互斥的选择策略参数组（`required=True`）。
  2. 校验输入文件存在且扩展名为 `.pdf`。
  3. 调用 `get_total_pages` 获取总页数。
  4. 根据互斥参数选择对应的策略函数得到 `pages` 列表。
  5. 批量模式直接调用 `batch_extract_from_file` 并返回；其余模式调用 `extract_pdf_pages` 写出单个文件。
- **退出码**：成功返回 `0`，任何错误返回 `1`。
- **参数组**（互斥）：`--pages`、`--even`、`--odd`、`--interval START INTERVAL`、`--regex`、`--file`、`--batch`。

---

## 6. 依赖关系

### 6.1 外部依赖

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| Python | 3.7+ | 运行时（使用了类型注解与 f-string） |
| PyPDF2 | 任意稳定版 | PDF 读取（`PdfReader`）与写入（`PdfWriter`） |

安装：

```bash
pip install PyPDF2
```

### 6.2 标准库依赖

| 模块 | 用途 |
|------|------|
| `argparse` | 命令行参数解析 |
| `re` | 正则匹配页码 |
| `pathlib.Path` | 文件路径处理 |
| `typing.List, Union` | 类型注解 |

### 6.3 内部函数调用关系

```
main()
 ├─ get_total_pages()
 ├─ parse_page_ranges()
 ├─ extract_even_pages()
 ├─ extract_odd_pages()
 ├─ extract_pages_by_interval()
 ├─ extract_pages_by_regex()
 ├─ extract_pages_from_file()
 ├─ batch_extract_from_file()
 │    ├─ parse_page_ranges()
 │    └─ extract_pdf_pages()
 └─ extract_pdf_pages()
```

- `extract_pdf_pages` 是最终的写出动作，被 `main` 和 `batch_extract_from_file` 共同调用。
- `parse_page_ranges` 被 `main`（`--pages`）和 `batch_extract_from_file` 共同调用。

---

## 7. 运行方式

### 7.1 环境准备

```bash
# 安装依赖
pip install PyPDF2

# 确认 Python 版本
python --version   # 需要 3.7+
```

### 7.2 命令行用法

```bash
python scripts/pdf_extract.py <input.pdf> <output.pdf> <选择策略>
```

**选择策略（必须且互斥）**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--pages` | 指定页码或范围 | `--pages 1,3,5-10` |
| `--even` | 全部偶数页 | `--even` |
| `--odd` | 全部奇数页 | `--odd` |
| `--interval START INTERVAL` | 间隔提取 | `--interval 1 3` |
| `--regex PATTERN` | 正则匹配页码 | `--regex "5$"` |
| `--file FILE` | 从文件读页码 | `--file pages.txt` |
| `--batch FILE` | 批量生成多文件 | `--batch ranges.txt` |

**批量模式输出**：`output` 参数作为输出前缀，生成 `output_01.pdf`、`output_02.pdf` …

### 7.3 程序化调用

```python
from scripts.pdf_extract import (
    extract_pdf_pages,
    parse_page_ranges,
    extract_even_pages,
    extract_odd_pages,
    extract_pages_by_interval,
    get_total_pages,
)

total = get_total_pages("input.pdf")
pages = parse_page_ranges("1-5,10,15-20", total)
extract_pdf_pages("input.pdf", "output.pdf", pages)
```

### 7.4 帮助信息

```bash
python scripts/pdf_extract.py --help
```

### 7.5 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 成功 |
| `1` | 输入文件不存在 / 非 PDF / 读取失败 / 页码解析错误 / 无选中页面 / 其他异常 |

---

## 8. 错误处理与边界条件

### 8.1 输入校验

| 校验项 | 位置 | 处理 |
|--------|------|------|
| 输入文件存在 | main:160 | 打印错误并返回 1 |
| 扩展名为 `.pdf` | main:164 | 打印错误并返回 1 |
| 页码文件存在（`--file`/`--batch`） | main:196 / 203 | 打印错误并返回 1 |

### 8.2 页码边界

- `parse_page_ranges`：起始 < 1、结束 > total_pages、起始 > 结束 均抛 `ValueError`。
- `extract_pages_from_file`：越界页码被静默过滤。
- `extract_pages_by_interval`：未校验 start/interval，若 start > total_pages 返回空列表。

### 8.3 异常捕获

- `main` 中 `ValueError` 与通用 `Exception` 分别捕获并打印错误信息，返回 1。
- `batch_extract_from_file` 对单行的 `ValueError` 容错，不中断批量流程。

---

## 9. 扩展指南

### 9.1 新增一种页面选择策略

1. 新增策略函数，签名遵循 `(total_pages: int, ...) -> List[int]`，返回已排序页码列表。
2. 在 `main` 的互斥参数组中新增 `group.add_argument(...)`。
3. 在 `main` 的 `if/elif` 链中加入对应分支调用新函数。

### 9.2 新增批量规则

在 `batch_extract_from_file` 中调整对每一行的解析逻辑，或复用 `parse_page_ranges`。

### 9.3 替换 PDF 后端

若需使用 `pypdf` 或 `pdfplumber` 等库，只需修改 `get_total_pages` 与 `extract_pdf_pages` 两个函数，页面选择策略层无需改动。

---

*本 Wiki 基于项目当前版本自动生成，代码位置见 [scripts/pdf_extract.py](file:///workspace/scripts/pdf_extract.py)。*
