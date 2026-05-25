# Report CLI

[![PyPI version](https://img.shields.io/pypi/v/report-cli.svg)](https://pypi.org/project/report-cli/)

查询、分析和下载券商研报的命令行工具。支持行业研报、个股研报、策略报告、宏观研究、券商晨报，可导出 CSV。

---

## 方式一：Skill 安装（推荐）

在 AI Agent（Cursor、Claude Code、Cline、Codex 等）对话框中发送：

```
请帮我安装 skill: https://raw.githubusercontent.com/manymore13/report-cli/refs/heads/master/.claude/skills/report-cli/SKILL.md
```

安装后直接用自然语言交互：

- "帮我查一下游戏行业最近有什么研报"
- "半导体行业最近 5 篇，只看 10 页以上的"
- "贵州茅台最新研报说了什么？"
- "宁德时代最近有什么研报，只看买入评级的"
- "今天的券商晨报说了什么"
- "宏观研究最近有什么新观点"
- "最近有没有看好新能源车的策略报告"
- "光伏和风电行业对比一下"
- "有哪些行业可以查"
- "把这三篇下载到 ./reports 目录"

Agent 会自动区分：你说"查/看/了解"就走查询，说"下载"才下载。

---

## 方式二：CLI 安装

```bash
pip install report-cli
```

### 命令一览

| 命令 | 说明 |
|------|------|
| `report l` | 列出所有行业 |
| `report l -s 关键词` | 搜索行业 |
| `report q -i 行业代码` | 查询行业研报 |
| `report q -t stock -c 股票代码` | 查询个股研报 |
| `report q -t strategy` | 查询策略报告 |
| `report q -t macro` | 查询宏观研究 |
| `report q -t morning` | 查询券商晨报 |
| `report d -i 行业代码 -o 目录` | 下载研报 PDF |
| `report u` | 更新行业列表 |

### 使用示例

```bash
# 列出行业
report l                        # 全部行业
report l -s 游戏                # 搜索包含"游戏"的行业

# 查询研报
report q -i 1046 -s 10          # 游戏行业，10 条
report q -i 1046 --begin 2025-06-01 --end 2025-12-31  # 按日期筛选
report q -t strategy -s 5       # 策略报告
report q -t stock -c 600519     # 茅台个股研报
report q -i 1046 --save-csv     # 导出 CSV

# 下载 PDF
report d -i 1046 -s 5 -o ./reports           # 下载 5 篇
report d -i 1046 -n 1,3,5 -o ./reports       # 只下载第 1、3、5 篇
report d -t stock -c 600519 -o ./reports      # 下载茅台研报
report d -t strategy -s 5 -o ./reports        # 下载策略报告
```

### 主要参数

| 参数 | 说明 |
|------|------|
| `-t` / `--type` | 研报类型：industry / stock / strategy / macro / morning |
| `-i` / `--industry` | 行业代码（用 `report l` 查看） |
| `-c` / `--code` | 股票代码 |
| `-s` / `--pagesize` | 返回数量，默认 20 |
| `-p` / `--page` | 页码，默认 1 |
| `-n` / `--index` | 指定下载第几条，如 `5` 或 `1,3,5` |
| `-o` / `--output` | 输出目录，默认 `./reports` |
| `--begin` / `--end` | 日期筛选，格式 YYYY-MM-DD |
| `--save-csv` | 查询结果保存为 CSV |

---

## License

MIT
