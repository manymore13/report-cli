# Report CLI

[![PyPI version](https://img.shields.io/pypi/v/report-cli.svg)](https://pypi.org/project/report-cli/)

查询和下载券商研报的命令行工具。

## 使用方式一：Skill 安装（推荐）

### 安装

在 Agent 对话框里直接发送这句话，Agent 会自动下载并安装到对应目录：

```
请帮我安装 skill: https://raw.githubusercontent.com/manymore13/eastmoney/master/SKILL.md
```

> 适用于 Cursor、Cline、Codex、Claude Code 等支持 Skill 的 Agent 工具。

### 使用

安装后，直接用自然语言交互：

- "帮我查一下游戏行业的最新研报"（走 `query`，只查看）
- "下载最近5篇策略报告"（走 `download`，下载PDF）
- "贵州茅台有什么最新分析？"（走 `query`）
- "把新能源行业的研报导出成表格"（走 `query --save-csv`）

> Agent 会自动区分：用户说"查/看/了解"走 `query`，只有明确说"下载"才走 `download`。

Agent 会自动识别关键词（研报、研究报告、行业分析、策略报告、宏观研究、券商晨报等）并调用本工具。

## 使用方式二：CLI 安装

```bash
pip install report-cli
```

### 命令一览

| 命令 | 说明 |
|------|------|
| `report -h` | 帮助文档 |
| `report list` | 列出所有行业 |
| `report list -s <关键词>` | 搜索行业 |
| `report query -i <行业代码>` | 查询行业研报 |
| `report query -t strategy` | 查询策略报告 |
| `report query -t macro` | 查询宏观研究 |
| `report query -t morning` | 查询券商晨报 |
| `report query -t stock -c <股票代码>` | 查询个股研报 |
| `report download -i <行业代码> -o <目录>` | 下载研报 PDF |

### 使用示例

```bash
report list                                    # 列出所有行业
report list -s 游戏                             # 搜索行业
report query -i 1046 -s 5                      # 游戏行业研报
report query -t strategy -s 10                 # 策略报告
report query -t stock -c 600519 -s 5           # 茅台个股研报
report download -t strategy -s 5 -o ./reports  # 下载PDF
report query -i 1046 -s 10 --save-csv          # 导出CSV
```

### 主要参数

| 参数 | 说明 |
|------|------|
| `-t` | 研报类型：industry / strategy / macro / morning / stock |
| `-i` | 行业代码 |
| `-c` | 股票代码 |
| `-s` | 返回数量 |
| `-o` | 输出目录 |
| `--begin` / `--end` | 日期筛选（YYYY-MM-DD） |
| `--save-csv` | 结果保存为 CSV |

## License

MIT
