---
name: eastmoney-reports
description: 东方财富研报查询下载工具。当用户需要查询、下载、分析行业研报、个股研报、策略报告、宏观研究、券商晨报时使用此 skill。
---

# 东方财富研报工具

## 安装

```bash
pip install eastmoney-reports
```

安装后可用命令：`em`（推荐）、`eastmoney`、`report`

## 触发条件

当用户提到以下关键词时激活：
- 研报、研究报告、行业分析、策略报告、宏观研究、券商晨报、个股研报
- 查询/下载某个行业或股票的研究报告
- 东方财富、eastmoney、em、行业代码

## 可用命令

### 1. 列出行业

```bash
em list              # 列出所有行业
em list -s 游戏      # 搜索包含"游戏"的行业
```

### 2. 查询研报

```bash
# 行业研报
em query -i 1046 -s 5              # 游戏行业，5条
em query -i 1046 --begin 2025-06-01 # 按日期筛选

# 策略报告
em query -t strategy -s 10

# 宏观研究
em query -t macro -s 10

# 券商晨报
em query -t morning -s 10

# 个股研报
em query -t stock -c 600519 -s 5   # 茅台
em query -t stock -c 000001 -s 5   # 平安银行

# 导出CSV
em query -i 1046 --save-csv
```

### 3. 下载PDF

```bash
em download -i 1046 -s 3 -o ./reports     # 下载游戏行业3篇
em download -t strategy -s 5 -o ./reports  # 下载策略报告
em download -t stock -c 600519 -o ./reports # 下载茅台研报
```

### 4. 更新行业列表

```bash
em update
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-t` | 研报类型: industry/stock/strategy/macro/morning | `-t strategy` |
| `-i` | 行业代码 | `-i 1046`(游戏) |
| `-c` | 股票代码 | `-c 600519`(茅台) |
| `-s` | 数量 | `-s 10` |
| `-p` | 页码 | `-p 2` |
| `-o` | 输出目录 | `-o ./reports` |
| `--begin` | 开始日期 YYYY-MM-DD | `--begin 2025-01-01` |
| `--end` | 结束日期 YYYY-MM-DD | `--end 2025-06-01` |
| `--save-csv` | 保存为CSV | 加在 query 命令后 |

## 常用行业代码

| 代码 | 行业 |
|------|------|
| 1046 | 游戏 |
| 1001 | 农林牧渔 |
| 1049 | 医药 |
| 1033 | 半导体 |
| 1038 | 新能源 |
| 1050 | 人工智能 |
| 1036 | 银行 |
| 1030 | 房地产 |

使用 `em list` 查看完整行业列表。

## MCP 使用

本工具也支持 MCP 协议，配置方式：

```json
{
  "mcpServers": {
    "eastmoney": {
      "command": "eastmoney-mcp"
    }
  }
}
```

MCP 提供 4 个工具：`list_industries`、`query_reports`、`download_reports`、`get_industry_code`

## 注意事项

- 接口不支持港股研报
- 合理使用频率，避免短时间大量下载
- 数据来源于东方财富，仅供学习研究使用
