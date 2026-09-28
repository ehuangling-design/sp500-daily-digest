"""
新闻预处理：时间过滤、关键词过滤、去重
"""
from typing import List, Dict
from datetime import datetime, timedelta
import re

from src.config import KEYWORDS, NEWS_LOOKBACK_HOURS, MAX_CANDIDATES_FOR_AI
from src.utils.time_utils import now_utc, hours_ago


def _contains_keyword(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def _normalize_title(title: str) -> str:
    """简单归一化用于去重"""
    title = title.lower().strip()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title[:80]


def filter_and_dedup(raw_news: List[Dict]) -> List[Dict]:
    """
    1. 过滤过去 NEWS_LOOKBACK_HOURS 小时内的新闻
    2. 关键词粗筛
    3. 标题去重
    4. 限制送给 AI 的数量
    """
    now = now_utc()
    cutoff = now - timedelta(hours=NEWS_LOOKBACK_HOURS)

    filtered = []
    seen_titles = set()

    for item in raw_news:
        # 时间过滤
        pub_dt = item.get("published_dt")
        if pub_dt is None:
            # 没有时间的新闻，谨慎保留或丢弃，这里选择保留但标记
            pass
        else:
            if pub_dt < cutoff:
                continue

        # 关键词过滤
        text_to_check = (item.get("title", "") + " " + item.get("summary", ""))
        if not _contains_keyword(text_to_check):
            continue

        # 去重
        norm_title = _normalize_title(item.get("title", ""))
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)

        filtered.append(item)

    # 按时间倒序
    filtered.sort(key=lambda x: x.get("published_dt") or datetime.min.replace(tzinfo=now.tzinfo), reverse=True)

    # 限制数量
    if len(filtered) > MAX_CANDIDATES_FOR_AI:
        filtered = filtered[:MAX_CANDIDATES_FOR_AI]

    print(f"[INFO] 过滤后候选新闻: {len(filtered)} 条")
    return filtered
