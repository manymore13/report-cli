---
name: report-cli-simple
description: 研报查询下载工具（CLI版）。当用户需要查询、下载行业研报、个股研报、策略报告、宏观研究、券商晨报时使用此 skill。
author: manymore13
license: MIT
repository: https://github.com/manymore13/report-cli
---

# 研报工具

## 安装

```bash
pip install report-cli
```

## 重要：先理解这两个命令的区别

| 用户意图 | 用这个命令 | 说明 |
|----------|-----------|------|
| 查看、搜索、查询、了解、有哪些 | `report query` | 只查看列表，**不下载文件** |
| 下载、保存、下载PDF | `report download` | 下载 PDF 文件到本地 |

**规则：除非用户明确说"下载"或"保存"，否则一律用 `report query`。**

## 命令

### 列出行业

```bash
report list              # 所有行业
report list -s 游戏      # 搜索行业
```

### 查询研报

```bash
# 行业研报
report q -i 1046 -s 5                    # 游戏行业，5条
report q -i 1046 --begin 2025-01-01      # 按日期筛选

# 策略报告
report q -t strategy -s 10

# 宏观研究
report q -t macro -s 10

# 券商晨报
report q -t morning -s 10

# 个股研报
report q -t stock -c 600519 -s 5         # 茅台
report q -t stock -c 000001 -s 5         # 平安银行

# 导出CSV
report q -i 1046 --save-csv
```

### 下载PDF

```bash
report d -i 1046 -s 5 -o ./reports       # 下载游戏行业5篇
report d -i 1046 -s 5 -n 5 -o ./reports  # 查5篇，只下载第5篇
report d -i 1046 -n 1,3,5 -o ./reports   # 只下载第1、3、5篇
report d -t strategy -s 5 -o ./reports   # 下载策略报告
report d -t stock -c 600519 -o ./reports # 下载茅台研报
```

> 如果用户说"下载第X篇"，必须用 `-n X` 参数，不能全部下载。先 `query` 确认序号，再 `download -n`。

### 更新

```bash
report update
```

## 参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| `-t` | 类型: industry/stock/strategy/macro/morning | `-t strategy` |
| `-i` | 行业代码 | `-i 1046` |
| `-c` | 股票代码 | `-c 600519` |
| `-s` | 数量 | `-s 10` |
| `-p` | 页码 | `-p 2` |
| `-o` | 输出目录 | `-o ./reports` |
| `--begin` | 开始日期 YYYY-MM-DD | `--begin 2025-01-01` |
| `--end` | 结束日期 YYYY-MM-DD | `--end 2025-12-31` |
| `-n` | 指定下载第几条 | `-n 5` 或 `-n 1,3` |
| `--save-csv` | 保存为CSV | 加在 query 命令后 |

## 行业代码

| 代码 | 行业 | 代码 | 行业 |
|------|------|------|------|
| 422 | 物流 | 1033 | 电池 |
| 428 | 电力 | 1036 | 半导体 |
| 448 | 通信设备 | 1037 | 消费电子 |
| 451 | 房地产开发 | 1038 | 光学光电子 |
| 457 | 电网设备 | 1040 | 中药Ⅱ |
| 459 | 元件 | 1042 | 医药商业 |
| 465 | 化学制药 | 1044 | 生物制品 |
| 473 | 证券Ⅱ | 1045 | 房地产服务 |
| 474 | 保险Ⅱ | 1046 | 游戏Ⅱ |
| 475 | 银行Ⅱ | 1225 | 服装家纺 |
| 481 | 汽车零部件 | 1231 | 航空装备Ⅱ |
| 482 | 一般零售 | 1232 | 航天装备Ⅱ |
| 538 | 化学制品 | 1238 | IT服务Ⅱ |
| 545 | 通用设备 | 1239 | 白色家电 |
| 727 | 医疗服务 | 1241 | 黑色家电 |
| 736 | 通信服务 | 1250 | 煤炭开采 |
| 737 | 软件开发 | 1252 | 化妆品 |
| 738 | 多元金融 | 1253 | 医疗美容 |
| 910 | 专用设备 | 1257 | 农业综合Ⅱ |
| 1031 | 光伏设备 | 1258 | 饲料 |
| 1032 | 风电设备 | 1259 | 养殖业 |
| 1263 | 摩托车及其他 | 1277 | 白酒Ⅱ |
| 1267 | 造纸 | 1280 | 食品加工 |
| 1271 | 酒店餐饮 | 1281 | 休闲食品 |
| 1282 | 饮料乳品 | 1287 | 工业金属 |

## 升级

```bash
pip install --upgrade report-cli
```

## 注意事项

- 不支持港股研报
- 合理控制频率
- 数据仅供学习研究使用

## 作者 & 开源

- 作者: [manymore13](https://github.com/manymore13)
- 开源地址: [github.com/manymore13/report-cli](https://github.com/manymore13/report-cli)
- 许可: MIT License
- 数据来源: 东方财富网，仅供学习研究