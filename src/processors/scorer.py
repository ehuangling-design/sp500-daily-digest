"""
评分计算：时间衰减、极端事件保护、综合分数
"""
from typing import List, Dict
from src.config import (
    TIME_DECAY,
    EXTREME_IMPORTANCE_THRESHOLD,
    EXTREME_NET_ABS_THRESHOLD,
    EXTREME_MULTIPLIER,
)
from src.utils.time_utils import hours_ago, get_time_decay_weight, now_utc


def calculate_scores(items: List[Dict]) -> Dict:
    """
    输入：AI 返回的已排序 15 条新闻（包含 positive_score, negative_score, importance 等）
    输出：完整的最终结果字典（含 overall_score, overall_label 等）
    """
    now = now_utc()
    total_weight = 0.0
    weighted_net_sum = 0.0

    processed_items = []

    for idx, item in enumerate(items, 1):
        pos = int(item.get("positive_score", 3))
        neg = int(item.get("negative_score", 3))
        importance = float(item.get("importance", 5.0))

        net_score = pos - neg
        impact_strength = round((pos + neg) / 2, 1)

        # 时间衰减
        pub_str = item.get("published_at")
        hours = 12.0  # 默认中间值
        if pub_str:
            try:
                from dateutil import parser as date_parser
                pub_dt = date_parser.parse(pub_str)
                hours = hours_ago(pub_dt, now)
            except Exception:
                pass

        time_weight = get_time_decay_weight(hours, TIME_DECAY)

        # 极端事件保护
        extreme_multiplier = 1.0
        if importance >= EXTREME_IMPORTANCE_THRESHOLD and abs(net_score) >= EXTREME_NET_ABS_THRESHOLD:
            extreme_multiplier = EXTREME_MULTIPLIER

        effective_weight = importance * time_weight * extreme_multiplier

        weighted_net_sum += effective_weight * net_score
        total_weight += effective_weight

        processed_items.append({
            "rank": idx,
            "title_zh": item.get("title_zh", ""),
            "analysis_zh": item.get("analysis_zh", ""),
            "positive_score": pos,
            "negative_score": neg,
            "importance": round(importance, 1),
            "net_score": net_score,
            "impact_strength": impact_strength,
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "published_at": item.get("published_at", ""),
            "original_title": item.get("original_title", item.get("title", "")),
        })

    # 计算 overall_score (0~100)
    if total_weight > 0:
        weighted_net = weighted_net_sum / total_weight  # -4 ~ +4
    else:
        weighted_net = 0.0

    overall_score = round((weighted_net + 4) * 12.5, 1)
    overall_score = max(0.0, min(100.0, overall_score))

    # 标签映射
    if overall_score >= 80:
        label = "强烈偏多"
    elif overall_score >= 65:
        label = "偏多"
    elif overall_score >= 55:
        label = "轻微偏多"
    elif overall_score >= 45:
        label = "中性"
    elif overall_score >= 35:
        label = "轻微偏空"
    elif overall_score >= 20:
        label = "偏空"
    else:
        label = "强烈偏空"

    # 简单生成 overall_summary（可后续用 AI 再润色）
    summary = f"今日综合评分为 {overall_score} 分（{label}）。"

    return {
        "overall_score": overall_score,
        "overall_label": label,
        "overall_summary": summary,
        "items": processed_items,
    }
