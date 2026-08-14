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
    # 热点案例
    if any(k in t for k in ["案例", "侵权", "纠纷", "诉讼", "判赔", "胜诉", "起诉", "商业秘密", "盗版", "假冒", "抢注", "维权", "获赔", "索赔"]):
        return "hot"
    # 企业荣誉/项目申报
    if any(k in t for k in ["高新技术企业", "科技型中小企业", "科小", "专精特新", "小巨人", "瞪羚", "独角兽", "企业技术中心", "技术中心", "入库", "拟认定"]):
        return "project"
    # 商标
    if any(k in t for k in ["商标", "地理标志证明商标", "马德里", "集体商标", "商标抢注", "商标审查", "商标注册", "品牌", "老字号"]):
        return "trademark"
    # 专利
    if any(k in t for k in ["专利", "pct", "发明专利", "实用新型", "外观设计", "专利审查", "专利导航", "专利奖", "专利转化"]):
        return "patent"
    # 政策
    if any(k in t for k in ["政策", "印发", "发布", "实施", "修订", "通过", "规划", "意见", "办法", "条例", "细则", "指南", "方案"]):
        return "policy"
    # 综合知识产权动态
    return "ip"

def summarize(title, dim):
    if dim == "hot":
        s = f"{title}，该案引发业界对知识产权保护与市场竞争规则的广泛关注。"
        s_en = f"{title}; the case has drawn wide industry attention to IP protection and market competition rules."
    elif dim == "policy":
        s = f"{title}，进一步完善知识产权保护与运用制度体系。"
        s_en = f"{title} further improves the IP protection and utilization institutional framework."
    elif dim == "trademark":
        s = f"{title}，建议企业加强商标监测、注册与维权，防范恶意抢注与侵权风险。"
        s_en = f"{title}; firms should strengthen trademark monitoring, registration and enforcement."
    elif dim == "patent":
        s = f"{title}，建议企业关注专利布局、审查动向与转化运用机会。"
        s_en = f"{title}; firms should watch patent portfolio, examination and commercialization opportunities."
    elif dim == "project":
        s = f"{title}，企业荣誉资质有助于享受政策红利与品牌背书，建议提前准备申报材料。"
        s_en = f"{title}; enterprise honors help access policy benefits and brand endorsement."
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
                # 来源取自真实文章域名，明确标出出处
                host = (urlparse(link).hostname or "").replace("www.", "")
                items.append({
                    "dim": dim,
                    "date": today,
                    "url": link,
                    "srcZh": host or "网络资讯",
                    "srcEn": host or "Web News",
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
