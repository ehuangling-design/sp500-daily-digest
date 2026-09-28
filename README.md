# S&P 500 Daily Digest

每天美东时间 09:00（开盘前30分钟）自动生成标普500相关重要新闻中文分析。

## 功能

- 自动采集英文权威财经与地缘新闻
- AI 筛选最重要的 15 条
- 中文标题 + 专业分析
- 积极分 / 消极分 / 重要性评分
- 综合推荐分数（0-100）+ 标签
- 支持时间衰减与极端事件保护

## 快速开始

### 1. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

- `GROQ_API_KEY`：你的 Groq API Key（免费申请：https://console.groq.com）

### 2. 手动测试

在 Actions 页面点击 “Daily S&P 500 Digest” → “Run workflow” 手动触发一次。

### 3. 查看结果

成功后会在 `output/latest.json` 生成最新分析结果。

APP 可直接请求：

```
https://raw.githubusercontent.com/ehuangling-design/sp500-daily-digest/main/output/latest.json
```

## 目录结构

```
src/
├── collectors/      # 新闻采集
├── processors/      # 过滤、AI分析、评分
├── utils/           # 工具函数
└── main.py          # 主入口
```

## 许可证

MIT
