"""
全局配置文件
"""
import os
from datetime import timedelta

# ====================== 运行时间与时区 ======================
# 目标：每天美东时间 09:00（开盘前30分钟）
TARGET_HOUR_ET = 9
TARGET_MINUTE_ET = 0

# ====================== 新闻源 ======================
RSS_FEEDS = [
    {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"name": "Reuters Company", "url": "https://feeds.reuters.com/reuters/companyNews"},
    {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories/"},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/rss/topstories"},
    {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
]

# Google News 定向搜索（补充）
GOOGLE_NEWS_QUERIES = [
    'S&P 500 OR SPX OR "Federal Reserve" OR FOMC OR "interest rates" when:1d',
    'Nvidia OR Apple OR Microsoft OR Amazon OR Google OR Meta earnings when:1d',
]

# ====================== 过滤关键词 ======================
KEYWORDS = [
    "S&P 500", "SPX", "S&P500", "Federal Reserve", "Fed", "FOMC",
    "interest rate", "interest rates", "inflation", "CPI", "PPI", "nonfarm",
    "Nvidia", "Apple", "Microsoft", "Amazon", "Google", "Alphabet", "Meta",
    "earnings", "tariff", "tariffs", "China", "geopolitics", "war", "oil",
    "Powell", "rate cut", "rate hike", "quantitative", "liquidity"
]

# ====================== 时间窗口 ======================
NEWS_LOOKBACK_HOURS = 30  # 多取一点，后面再精确过滤24h

# ====================== 时间衰减系数 ======================
# (小时下限, 小时上限): 权重
TIME_DECAY = [
    (0, 6, 1.25),
    (6, 12, 1.15),
    (12, 18, 1.05),
    (18, 24, 1.00),
    (24, 999, 0.90),
]

# ====================== 极端事件保护 ======================
EXTREME_IMPORTANCE_THRESHOLD = 9.2
EXTREME_NET_ABS_THRESHOLD = 3
EXTREME_MULTIPLIER = 1.3

# ====================== 评分映射 ======================
# overall_score = (weighted_net + 4) * 12.5  → 0~100

# ====================== AI 相关 ======================
# 使用环境变量
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")  # groq 或 gemini
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# 模型选择（可根据实际情况调整）
GROQ_MODEL = "openai/gpt-oss-20b"  # 或其他可用模型
GEMINI_MODEL = "gemini-1.5-flash"

# ====================== 输出 ======================
OUTPUT_DIR = "output"
LATEST_JSON = os.path.join(OUTPUT_DIR, "latest.json")
HISTORY_DIR = os.path.join(OUTPUT_DIR, "history")

# ====================== 其他 ======================
MAX_CANDIDATES_FOR_AI = 80  # 送给 AI 的最大候选数，防止 token 过多
TOP_N = 15
