"""
主入口：每日标普500新闻分析
"""
import os
import sys
import traceback
from datetime import datetime

# 确保能找到 src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.rss_collector import collect_rss
from src.processors.filter import filter_and_dedup
from src.processors.ai_analyzer import ai_analyze
from src.processors.scorer import calculate_scores
from src.utils.time_utils import get_et_date_str, now_utc
from src.utils.json_utils import save_json, validate_result
from src.config import LATEST_JSON, HISTORY_DIR, OUTPUT_DIR


def main():
    print("=" * 60)
    print(f"开始运行标普500每日分析 - {now_utc().isoformat()}")
    print("=" * 60)

    try:
        # 1. 采集
        print("\n[1/5] 采集新闻...")
        raw_news = collect_rss()

        # 2. 预处理
        print("\n[2/5] 过滤与去重...")
        candidates = filter_and_dedup(raw_news)

        if len(candidates) < 5:
            print("[WARN] 候选新闻过少，可能影响分析质量")

        # 3. AI 分析
        print("\n[3/5] AI 分析中...")
        analyzed_items = ai_analyze(candidates)

        # 4. 计算综合分数
        print("\n[4/5] 计算综合评分...")
        scored = calculate_scores(analyzed_items)

        # 5. 组装最终结果
        result = {
            "date": get_et_date_str(),
            "generated_at": now_utc().isoformat().replace("+00:00", "Z"),
            "timezone": "UTC",
            "overall_score": scored["overall_score"],
            "overall_label": scored["overall_label"],
            "overall_summary": scored["overall_summary"],
            "item_count": len(scored["items"]),
            "items": scored["items"],
        }

        if not validate_result(result):
            raise ValueError("结果校验失败")

        # 6. 保存
        print("\n[5/5] 保存结果...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(HISTORY_DIR, exist_ok=True)

        save_json(result, LATEST_JSON)

        # 同时保存历史
        history_path = os.path.join(HISTORY_DIR, f"{result['date']}.json")
        save_json(result, history_path)

        print("\n" + "=" * 60)
        print(f"分析完成！综合评分: {result['overall_score']} ({result['overall_label']})")
        print(f"新闻条数: {result['item_count']}")
        print("=" * 60)

        return 0

    except Exception as e:
        print("\n[ERROR] 运行失败:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
