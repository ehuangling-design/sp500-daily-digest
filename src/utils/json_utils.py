"""
JSON 读写与校验
"""
import json
import os
from datetime import datetime
from typing import Any


def save_json(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 已保存: {path}")


def load_json(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_result(data: dict) -> bool:
    """简单校验最终结果结构"""
    required_top = ["date", "generated_at", "overall_score", "overall_label", "items"]
    for key in required_top:
        if key not in data:
            print(f"[ERROR] 缺少字段: {key}")
            return False

    if not isinstance(data["items"], list):
        print("[ERROR] items 不是列表")
        return False

    if len(data["items"]) == 0:
        print("[WARN] items 为空")
        return False

    return True
