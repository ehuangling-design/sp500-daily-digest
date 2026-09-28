"""
AI 分析模块：构建 Prompt、调用大模型、解析结果
"""
import json
import os
from typing import List, Dict
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import AI_PROVIDER, GROQ_API_KEY, GEMINI_API_KEY, GROQ_MODEL, TOP_N


PROMPT_TEMPLATE = """你是一位专注于美股大盘（尤其是标普500指数）的专业分析师。你的核心任务是评估新闻对标普500指数整体走势、估值、风险偏好和流动性的潜在影响，保持客观、平衡、专业。

【任务】
我会提供一组过去24小时内的英文新闻候选列表。请你完成以下工作：

1. 从中筛选出对标普500指数最重要的{top_n}条新闻（按重要性从高到低排序）。
2. 对这{top_n}条新闻分别进行以下处理：
   - 翻译成准确、自然的中文标题
   - 用中文写2-4句专业分析，说明该事件为什么重要，以及对标普500可能产生的影响
   - 给出积极影响分（positive_score）：1-5分整数
   - 给出消极影响分（negative_score）：1-5分整数
   - 给出重要性分数（importance）：0-10分，保留1位小数

【评分标准】

重要性（importance，0-10）：
- 9.0-10.0：极高重要性，可能显著影响指数走势
- 7.5-8.9：高重要性，对指数有清晰影响
- 6.0-7.4：中等偏上，值得关注
- 4.0-5.9：中等，影响有限
- 0-3.9：低重要性（尽量不要选入最终{top_n}条）

积极影响分（positive_score，1-5）：
评估该事件对标普500的潜在利好程度（提升风险偏好、改善盈利预期、增加流动性等）。

消极影响分（negative_score，1-5）：
评估该事件对标普500的潜在利空程度（增加风险溢价、压制估值、引发避险等）。

注意：一条新闻可以同时有较高的积极分和消极分（例如喜忧参半的事件）。

【输出要求】
必须严格返回以下JSON格式，不要添加任何额外解释或 markdown 标记：

{{
  "items": [
    {{
      "rank": 1,
      "title_zh": "",
      "analysis_zh": "",
      "positive_score": 0,
      "negative_score": 0,
      "importance": 0.0,
      "source": "",
      "url": "",
      "published_at": "",
      "original_title": ""
    }}
  ]
}}

说明：
- 按 importance 从高到低排序，rank 从1开始。
- 所有用户可见内容必须使用中文。
- 只基于我提供的新闻内容进行判断，不要添加外部知识或臆测。
- source、url、published_at、original_title 请直接使用我提供的原始数据。

【新闻候选列表】
{news_list}
"""


def _build_news_list_text(candidates: List[Dict]) -> str:
    lines = []
    for i, item in enumerate(candidates, 1):
        lines.append(
            f"{i}. 标题: {item.get('title', '')}\n"
            f"   来源: {item.get('source', '')}\n"
            f"   链接: {item.get('url', '')}\n"
            f"   时间: {item.get('published_at', '')}\n"
            f"   摘要: {item.get('summary', '')[:120]}\n"
        )
    return "\n".join(lines)


def _get_client():
    if AI_PROVIDER.lower() == "groq":
        if not GROQ_API_KEY:
            raise ValueError("缺少 GROQ_API_KEY 环境变量")
        return OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
    else:
        # 简单示例，实际 Gemini 需要用 google-generativeai 或 OpenAI 兼容接口
        raise NotImplementedError("当前框架优先支持 Groq，Gemini 可后续扩展")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def ai_analyze(candidates: List[Dict]) -> List[Dict]:
    """调用大模型完成筛选与分析"""
    if not candidates:
        raise ValueError("候选新闻为空，无法进行分析")

    news_text = _build_news_list_text(candidates)
    prompt = PROMPT_TEMPLATE.format(top_n=TOP_N, news_list=news_text)

    client = _get_client()

    print(f"[INFO] 正在调用 AI 分析（候选 {len(candidates)} 条）...")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "你是一个严谨的金融分析助手，只输出合法的 JSON。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    items = data.get("items", [])
    if not items:
        raise ValueError("AI 返回的 items 为空")

    # 补充原始字段（防止 AI 漏掉）
    url_map = {c["url"]: c for c in candidates}
    for item in items:
        orig = url_map.get(item.get("url", ""))
        if orig:
            item.setdefault("source", orig.get("source", ""))
            item.setdefault("published_at", orig.get("published_at", ""))
            item.setdefault("original_title", orig.get("title", ""))

    print(f"[INFO] AI 分析完成，返回 {len(items)} 条")
    return items[:TOP_N]
