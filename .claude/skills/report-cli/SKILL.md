---
name: report-cli
description: 研报查询下载工具。当用户需要查询、下载、分析行业研报、个股研报、策略报告、宏观研究、券商晨报时使用此 skill。
author: manymore13
license: MIT
repository: https://github.com/manymore13/report-cli
---

# 研报工具

## 触发示例

以下说法会触发此 skill：

- "帮我查一下近一个月的半导体行业研报，只看 10 页以上的"
- "下载茅台最新的 3 份个股研报"
- "最近有没有看好新能源车的策略报告，给我看摘要"
- "宏观研究最近有什么新观点"
- "游戏行业研报有哪些，按页数排个序"

## 核心原则

**全部操作通过 HTTP 完成，无需安装任何 CLI。**

| 操作 | 方式 |
|------|------|
| 行业 / 策略 / 宏观 / 晨报查询 | WebFetch → GET 请求 API（返回 JSON） |
| 个股研报查询 | **bash curl** → POST 请求 API（WebFetch 不支持 POST） |
| 看摘要 / 页数 | WebFetch → 详情页（提取正文） |
| 下载 PDF | WebFetch 拿 PDF 链接 → curl 下载 |

---

## 日期处理

`beginTime` 默认取 **30 天前**，`endTime` 默认取**今天**，格式 `YYYY-MM-DD`。除非用户明确指定日期范围。

```
当前日期由系统提供，不要用写死的日期。
```

---

## 一、查询研报列表 — API 端点

### 行业研报（GET，用 WebFetch）

```
https://reportapi.eastmoney.com/report/list?pageSize=20&pageNo=1&beginTime={30天前}&endTime={今天}&qType=1&industryCode=1046&industry=*&rating=*
```

| 参数 | 说明 | 示例 |
|------|------|------|
| `pageSize` | 每页条数，默认 20 | 20 |
| `pageNo` | 页码，从 1 开始 | 1 |
| `beginTime` | 开始日期，默认 30 天前 | 2025-04-25 |
| `endTime` | 结束日期，默认今天 | 2025-05-25 |
| `qType` | 固定 1 | 1 |
| `industryCode` | 行业代码 | 1046 |

> `industry=*` 和 `rating=*` 为可选参数。若返回结果为空，尝试去掉这两个参数重试。

### 个股研报（POST，必须用 bash curl）

**WebFetch 不支持 POST 请求，个股研报查询必须用 bash curl。**

```bash
curl -s -X POST https://reportapi.eastmoney.com/report/list2 \
  -H "Content-Type: application/json" \
  -d '{"pageSize":20,"pageNo":1,"beginTime":"{30天前}","endTime":"{今天}","code":"600519"}'
```

| body 字段 | 说明 | 示例 |
|-----------|------|------|
| `code` | 6 位股票代码 | 600519 |
| `pageSize` | 每页条数，默认 20 | 20 |
| `pageNo` | 页码，从 1 开始 | 1 |

**股票代码格式：**

沪市 6 开头（600519 贵州茅台），深市主板 0 开头（000858 五粮液），创业板 3 开头（300750 宁德时代）。输入时传 6 位纯数字，不加交易所前缀。

若用户输入的是股票名称而非代码（如"帮我查茅台"），Claude 应凭常识转换为代码；不确定时向用户确认。

### 策略 / 宏观 / 晨报（GET，用 WebFetch）

```
https://reportapi.eastmoney.com/report/jg?pageSize=20&pageNo=1&beginTime={30天前}&endTime={今天}&qType={qType}
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

### 评级对照

| `emRatingName` | 含义 |
|----------------|------|
| 买入 | 强烈看好 |
| 增持 | 看好 |
| 中性 | 观望 |
| 减持 | 看空 |
| 卖出 | 强烈看空 |
| 不评级 | 仅供参考，无评级 |

---

## 二、按页数筛选

API 返回的 `attachPages` 字段即研报页数。

- **行业和个股研报**: `attachPages` 直接在 JSON 里，直接筛选
- **策略 / 宏观 / 晨报**: API 不返回 `attachPages`，需访问详情页后根据正文长度判断

**默认跳过 ≤ 2 页的研报**（通常无实质内容）。用户可指定阈值，如"只看 10 页以上的"。

> `attachPages` 为 `null` 或缺失时，视为未知页数。默认**暂不跳过**，标记为"页数未知"供用户自行判断。

---

## 三、获取摘要 — 详情页

### URL 拼接

用 API 返回的 `encodeUrl` 字段，拼到对应 URL 模板：

| 研报类型 | 详情页 URL |
|---------|-----------|
| 行业 | `https://data.eastmoney.com/report/zw_industry.jshtml?encodeUrl={encodeUrl}` |
| 个股 | `https://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl={encodeUrl}` |
| 策略 / 宏观 / 晨报 | `https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={encodeUrl}` |

> 若详情页返回 404，对 `encodeUrl` 值做 **URL 百分号编码**后再拼接。不同工具对应：JS `encodeURIComponent()`、Python `urllib.parse.quote()`、bash 可调 `python3 -c "import urllib.parse; print(urllib.parse.quote('VALUE'))"`。

### 页面提取规则

用 WebFetch 访问详情页后：

| 目标 | 提取方式 | 用途 |
|------|---------|------|
| 正文摘要 | 提取 `<p>` 标签文本内容，取前 800 字 | 判断内容质量、呈现核心观点 |
| PDF 下载链接 | 优先用 `a.pdf-link` 的 `href` | 下载完整 PDF |
| PDF 链接（备用） | 正则 `https://pdf\.dfcfw\.com/pdf/[^\s"'<>]+\.pdf` | 当 CSS 选择器在 WebFetch 中失效时使用 |
| 标题 | `h1` 或页面 title | 确认页面正确 |
| 页数（策略 / 宏观 / 晨报） | 正文字数 < 500 → 推断 1-2 页 | 补 API 无 attachPages 的缺口 |

---

## 四、下载 PDF

### 步骤

1. **拿 PDF 链接**：从详情页提取。URL 格式：
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

3. **校验文件**：确保下载的是真 PDF 而非拦截页面。
   ```bash
   head -c 4 "研报标题.pdf"    # 应输出: %PDF
   ```

4. **文件命名**：用研报标题做文件名，去除 `\/:*?"<>|` 等非法字符，最长 100 字符。

### 频率控制

- API 查询间隔 ≥ 1 秒
- PDF 下载间隔 ≥ 2 秒
- 单次会话下载不超过 10 份，避免 IP 被临时封禁

---

## 五、Agent 工作流

### 查研报列表 + 页数过滤

```
1. 行业/策略/宏观/晨报 → WebFetch 调 GET API；个股 → bash curl POST API
2. 拿 JSON，过滤 attachPages > 2（或用户指定阈值）
3. 列出：序号 + 标题 + 券商 + 日期 + 页数 + 评级
4. 评级含义参考评级对照表，向用户解释
5. 问用户想看哪篇的摘要
```

### 看摘要

```
1. 用 encodeUrl 拼详情页 URL
2. WebFetch 访问，提取正文前 800 字
3. 总结核心观点呈现给用户
4. 问是否需要下载完整 PDF
```

### 下载 PDF

```
1. 从详情页提取 PDF 链接（优先 CSS 选择器，备用正则匹配）
2. curl -L -o 下载到用户指定目录
3. 校验文件是否为真 PDF
```

### 策略 / 宏观 / 晨报筛选（无 attachPages）

```
1. WebFetch /jg API → JSON
2. 取前 5 条的 encodeUrl（避免请求过多），逐篇 WebFetch 详情页
3. 按正文长度过滤（< 500 字 → 1-2 页，跳过）
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
- 频率控制详见第四节
- 数据仅供学习研究使用

---

## 作者 & 开源

- 作者: [manymore13](https://github.com/manymore13)
- 开源地址: [github.com/manymore13/report-cli](https://github.com/manymore13/report-cli)
- 许可: MIT License
- 数据来源: 东方财富网，仅供学习研究
