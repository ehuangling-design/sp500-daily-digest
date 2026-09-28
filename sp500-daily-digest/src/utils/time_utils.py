"""
时间处理工具
"""
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
import pytz

ET = pytz.timezone("US/Eastern")
UTC = timezone.utc


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_et() -> datetime:
    return datetime.now(ET)


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        # 假设无时区的时间是 UTC
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def parse_datetime(text: str) -> datetime | None:
    """安全解析各种时间格式，返回 UTC datetime"""
    if not text:
        return None
    try:
        dt = date_parser.parse(text)
        return to_utc(dt)
    except Exception:
        return None


def hours_ago(dt: datetime, now: datetime | None = None) -> float:
    """计算某个时间距离现在多少小时"""
    if now is None:
        now = now_utc()
    delta = now - to_utc(dt)
    return delta.total_seconds() / 3600.0


def get_time_decay_weight(hours: float, decay_table: list) -> float:
    """根据小时数返回时间衰减权重"""
    for low, high, weight in decay_table:
        if low <= hours < high:
            return weight
    return 0.90


def get_et_date_str(dt: datetime | None = None) -> str:
    """返回美东日期 YYYY-MM-DD"""
    if dt is None:
        dt = now_et()
    else:
        dt = dt.astimezone(ET)
    return dt.strftime("%Y-%m-%d")
