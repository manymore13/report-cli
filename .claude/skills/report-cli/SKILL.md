---
name: report-cli
description: 研报查询下载工具。当用户需要查询、下载、分析行业研报、个股研报、策略报告、宏观研究、券商晨报时使用此 skill。
---

# 研报工具

## 核心原则

**全部操作通过 HTTP 完成，无需安装任何 CLI。**

| 操作 | 方式 |
|------|------|
| 查询研报列表 | WebFetch → 东方财富 API（返回 JSON） |
| 看摘要/页数 | WebFetch → 研报详情页（提取正文） |
| 下载 PDF | WebFetch 详情页拿 PDF 链接 → curl 下载 |

---

## 一、查询研报列表 — API 端点

### 行业研报

```
GET https://reportapi.eastmoney.com/report/list?pageSize=20&pageNo=1&beginTime=2025-01-01&endTime=2025-12-31&qType=1&industryCode=1046&industry=*&rating=*
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `pageSize` | 每页条数 | 20 |
| `pageNo` | 页码，从 1 开始 | 1 |
| `beginTime` | 开始日期 | 2025-01-01 |
| `endTime` | 结束日期 | 2025-12-31 |
| `qType` | 固定 1 | 1 |
| `industryCode` | 行业代码 | 1046 |

### 个股研报

```
POST https://reportapi.eastmoney.com/report/list2
Content-Type: application/json
```

```json
{"pageSize": 20, "pageNo": 1, "beginTime": "2025-01-01", "endTime": "2025-12-31", "code": "600519"}
```

| body 字段 | 说明 | 示例 |
|-----------|------|------|
| `code` | 股票代码 | 600519 |
| `pageSize` | 每页条数 | 20 |
| `pageNo` | 页码 | 1 |

### 策略 / 宏观 / 晨报

```
GET https://reportapi.eastmoney.com/report/jg?pageSize=20&pageNo=1&beginTime=2025-01-01&endTime=2025-12-31&qType={qType}
```

| 类型 | qType |
|------|-------|
| 策略报告 | 2 |
| 宏观研究 | 3 |
| 券商晨报 | 4 |

### 响应关键字段

| 字段 | 含义 | 接口 |
|------|------|------|
| `data` | 研报数组 | 全部 |
| `hits` | 总条数 | 全部 |
| `TotalPage` | 分页总页数 | 全部 |
| `title` | 标题 | 全部 |
| `orgSName` | 券商简称 | 全部 |
| `publishDate` | 发布日期 | 全部 |
| `emRatingName` | 评级 | 全部 |
| `encodeUrl` | 详情页标识（**重要**） | 全部 |
| `infoCode` | 研报编码 | list / list2 |
| **`attachPages`** | **研报页数** | list / list2 |
| `attachSize` | 文件大小(KB) | list / list2 |
| `stockName` | 股票名称 | list2 |
| `industryName` | 行业名称 | list |

---

## 二、按页数筛选

API 返回的 `attachPages` 字段即研报页数。

- **行业和个股研报**: `attachPages` 直接在 JSON 里，直接筛选
- **策略/宏观/晨报**: API 不返回 `attachPages`，需访问详情页后根据正文长度判断

**默认跳过 ≤ 2 页的研报**（通常无实质内容）。用户可指定阈值，如"只看10页以上的"。

---

## 三、获取摘要 — 详情页

### URL 拼接

用 API 返回的 `encodeUrl` 字段，拼到对应 URL 模板：

| 研报类型 | 详情页 URL |
|---------|-----------|
| 行业 | `https://data.eastmoney.com/report/zw_industry.jshtml?encodeUrl={encodeUrl}` |
| 个股 | `https://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl={encodeUrl}` |
| 策略/宏观/晨报 | `https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={encodeUrl}` |

### 页面提取规则

用 WebFetch 访问详情页后：

| 目标 | 提取方式 | 用途 |
|------|---------|------|
| 正文摘要 | `div.ctx-content` 内所有 `<p>` 标签文本，取前 800 字 | 判断内容质量、呈现核心观点 |
| PDF 下载链接 | `a.pdf-link` 的 `href` 属性 | 下载完整 PDF |
| 标题 | `h1` | 确认页面正确 |
| 页数（策略/宏观/晨报） | 正文字数 < 500 → 推断 1-2 页 | 补 API 无 attachPages 的缺口 |

---

## 四、下载 PDF

### 步骤

1. **拿 PDF 链接**：从详情页提取 `a.pdf-link` 的 `href`，格式如：
   ```
   https://pdf.dfcfw.com/pdf/H3_AP202505251678987843_1.pdf?1748207582000.pdf
   ```

2. **下载到本地**（跨平台 curl）：
   ```bash
   curl -L -o "研报标题.pdf" \
     -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     "https://pdf.dfcfw.com/pdf/H3_XXX.pdf"
   ```

   - `-L`: 跟随重定向
   - `-o`: 指定保存路径
   - `-A`: 设置 User-Agent 绕过反爬
   - macOS / Linux 自带 curl，Windows 10+ 内置 curl

3. **校验文件**：检查文件前 4 字节是否为 `%PDF`，确保下载的是真 PDF 而非拦截页面。

4. **文件命名**：用研报标题做文件名，去除 `\/:*?"<>|` 等非法字符，限制 100 字符内。

### 批量下载

从 API 列表筛选出目标后，对每篇重复上述步骤。建议每篇间隔 1-2 秒。

---

## 五、Agent 工作流

### 查研报列表 + 页数过滤

```
1. WebFetch 调对应 API → JSON
2. 过滤 attachPages > 2（或用户指定阈值）
3. 列出：序号 + 标题 + 券商 + 日期 + 页数 + 评级
4. 问用户想看哪篇摘要
```

### 看摘要

```
1. 用 encodeUrl 拼详情页 URL
2. WebFetch → 提取 div.ctx-content 前 800 字
3. 总结核心观点呈现给用户
4. 问用户是否需要下载完整 PDF
```

### 下载 PDF

```
1. 从详情页提取 a.pdf-link 的 href
2. curl -L -o 下载到用户指定目录
3. 校验文件是 PDF
```

### 策略/宏观/晨报筛选

```
1. WebFetch /jg API → JSON
2. 取前 N 条的 encodeUrl 逐篇 WebFetch 详情页
3. 按正文长度过滤（<500 字跳过）
4. 输出摘要 → 按需下载
```

---

## 六、行业代码速查

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

---

## 注意事项

- 不支持港股研报
- 合理控制请求频率
- 数据仅供学习研究使用
