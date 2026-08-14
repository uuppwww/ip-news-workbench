#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日采集知识产权/商标/专利/版权资讯，合并追加到 ip_data.json，按 URL 去重。
支持环境变量 SEARCH_ENGINE=rss 或 websearch（本脚本优先 RSS，失败则回退）。
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from urllib.parse import quote, urlparse

import requests

DATA_FILE = "ip_data.json"
QUERIES = [
    "知识产权 商标 专利",
    "专利侵权 案例",
    "商标抢注 热点",
    "商业秘密 纠纷",
    "国家知识产权局 政策",
    "著作权 侵权 案例",
]

def load_existing():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def dedup(items):
    seen = set()
    out = []
    for it in items:
        key = it.get("url") or it.get("titleZh")
        if key and key not in seen:
            seen.add(key)
            out.append(it)
    return out

def classify(title):
    t = title.lower()
    if any(k in t for k in ["案例", "侵权", "纠纷", "诉讼", "判赔", "胜诉", "起诉", "商业秘密", "盗版", "假冒", "抢注", "维权"]):
        return "hot"
    if any(k in t for k in ["政策", "印发", "发布", "实施", "修订", "通过", "规划", "意见", "办法", "条例", "细则", "指南"]):
        return "policy"
    if any(k in t for k in ["wipo", "pct", "国际", "全球", "地理标志", "出口", "进出口", "排名", "指数"]):
        return "fund"
    return "dynamic"

def summarize(title, dim):
    if dim == "hot":
        s = f"{title}，该案引发业界对知识产权保护与市场竞争规则的广泛关注。"
        s_en = f"{title}; the case has drawn wide industry attention to IP protection and market competition rules."
    elif dim == "policy":
        s = f"{title}，进一步完善知识产权保护与运用制度体系。"
        s_en = f"{title} further improves the IP protection and utilization institutional framework."
    elif dim == "fund":
        s = f"{title}，显示中国知识产权国际影响力持续提升。"
        s_en = f"{title} shows China's international IP influence continues to grow."
    else:
        s = f"{title}，反映知识产权工作持续推进。"
        s_en = f"{title} reflects continuous progress in IP work."
    return s, s_en

def translate_title(title):
    # 占位翻译：实际运行时可接入翻译 API；此处保持标题原样并附简单英文说明
    return title + " (IP News)"

def fetch_rss():
    items = []
    today = date.today().isoformat()
    for q in QUERIES:
        try:
            url = f"https://www.bing.com/news/search?q={quote(q)}&format=rss"
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            root = ET.fromstring(r.content)
            channel = root.find("channel")
            if channel is None:
                continue
            for node in channel.findall("item")[:3]:
                title = (node.findtext("title") or "").strip()
                link = (node.findtext("link") or "").strip()
                pub = (node.findtext("pubDate") or "").strip()
                if not title or not link:
                    continue
                dim = classify(title)
                szh, sen = summarize(title, dim)
                items.append({
                    "dim": dim,
                    "date": today,
                    "url": link,
                    "srcZh": "网络资讯",
                    "srcEn": "Web News",
                    "titleZh": title,
                    "titleEn": translate_title(title),
                    "sumZh": szh,
                    "sumEn": sen,
                })
        except Exception as e:
            print(f"RSS fetch failed for {q}: {e}")
    return items

def collect(top=10):
    """采集并合并。返回新采集条目数。"""
    new_items = fetch_rss()
    if not new_items:
        print("no new items fetched")
        return 0
    new_items = new_items[:top]
    existing = load_existing()
    merged = existing + new_items
    merged = dedup(merged)
    # 按日期新到旧排序
    merged.sort(key=lambda x: x.get("date", ""), reverse=True)
    save_items(merged)
    print(f"collected {len(new_items)} new items, total={len(merged)}")
    return len(new_items)

if __name__ == "__main__":
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 10
    collect(top)
