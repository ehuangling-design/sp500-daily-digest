"""
RSS 新闻采集
"""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import RSS_FEEDS, GOOGLE_NEWS_QUERIES
from src.utils.time_utils import parse_datetime, now_utc


def _fetch_one_feed(feed_info: dict) -> List[Dict]:
    """拉取单个 RSS"""
    name = feed_info["name"]
    url = feed_info["url"]
    results = []

    try:
        # 设置超时和 User-Agent，提高成功率
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SP500Digest/1.0; +https://github.com/ehuangling-design/sp500-daily-digest)"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        feed = feedparser.parse(resp.content)

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            published = entry.get("published", entry.get("updated", ""))

            published_dt = parse_datetime(published)

            if not title or not link:
                continue

            results.append({
                "title": title,
                "url": link,
                "summary": summary[:800] if summary else "",
                "source": name,
                "published_at": published_dt.isoformat() if published_dt else None,
                "published_dt": published_dt,
            })

        print(f"[INFO] {name}: 获取到 {len(results)} 条")
    except Exception as e:
        print(f"[WARN] 采集 {name} 失败: {e}")

    return results


def collect_rss() -> List[Dict]:
    """并行采集所有 RSS 源"""
    all_news = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_fetch_one_feed, feed): feed for feed in RSS_FEEDS}
        for future in as_completed(futures):
            try:
                items = future.result()
                all_news.extend(items)
            except Exception as e:
                print(f"[WARN] 某个源采集异常: {e}")

    # Google News 补充（简单实现）
    for query in GOOGLE_NEWS_QUERIES:
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            items = _fetch_one_feed({"name": "Google News", "url": url})
            all_news.extend(items)
        except Exception as e:
            print(f"[WARN] Google News 采集失败: {e}")

    print(f"[INFO] RSS 总计采集: {len(all_news)} 条")
    return all_news
