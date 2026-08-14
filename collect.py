#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识产权·商标专利 主题资讯工作台 —— 采集引擎（每日拉取真实数据）

本脚本把"检索"自动化：调用一个联网搜索源，抓取四个维度的资讯，
按关键词归类为 国家政策 / 动态 / 热点 / 行业基本面，写出 data/ip_data.json。

支持四种后端（任选其一，用环境变量配置）：
  0) RSS（推荐·零成本·免密钥）: SEARCH_ENGINE=rss
       在你自己机器（正常网络）上，用 Bing / Google News 的 RSS 抓取，
       沙箱网络受限时 RSS 可能拿不到数据，但本机 crontab 跑完全没问题。
  1) Bing Web Search : SEARCH_ENGINE=bing   + BING_SUBSCRIPTION_KEY
  2) SerpAPI         : SEARCH_ENGINE=serpapi + SERPAPI_KEY
  3) Google CSE      : SEARCH_ENGINE=gcse    + GOOGLE_CSE_KEY + GOOGLE_CSE_CX

为什么沙箱里推荐"联网搜索（我每天吃）"而不是自动脚本？
  沙箱内 Bing News RSS 失效、Google News 被屏蔽、官网为 JS 渲染分页，
  自动脚本在沙箱里抓不到数据；但它放在你自己的服务器/本机 crontab 上即可无人值守。

维度查询（与人工调研一致的检索式）：
  动态 : 知识产权 商标 专利 动态
  热点 : 知识产权 商标 专利 热点 抢注 纠纷
  行业基本面 : 知识产权 商标 专利 行业 市场 申请量 质押融资
  国家政策 : 知识产权 商标 专利 政策 规划 商标法 修订

说明：
  - 抓取结果以中文为主；titleEn/sumEn 留空，由前端在 ?lang=en 时回退中文。
  - 若你额外配置了翻译（如 OPENAI_API_KEY + 翻译开关），可扩展本脚本补全英文。

用法：
  python3 collect.py                 # 用环境变量里的 Key，写 data/ip_data.json
  python3 collect.py --top 8         # 每维度取前 8 条
  python3 collect.py --dry           # 只打印不写文件
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
OUT = BASE / "ip_data.json"

# 维度 -> 检索式（联网搜索）
QUERIES = {
    "dynamic": "知识产权 商标 专利 动态",
    "hot": "知识产权 商标 专利 热点 抢注 纠纷",
    "fund": "知识产权 商标 专利 行业 市场 申请量 质押融资",
    "policy": "知识产权 商标 专利 政策 规划 商标法 修订",
}

# 归类关键词（命中即归为该维度；优先级 policy>hot>fund>dynamic）
CLASSIFY = {
    "policy": ["规划", "纲要", "修订", "条例", "办法", "局令", "政策", "法规", "人大", "国务院", "印发", "立法", "草案", "十五五"],
    "hot": ["抢注", "纠纷", "诉讼", "争议", "热点", "生成式", "大模型", "AI", "驳回", "处罚", "事件"],
    "fund": ["营收", "市场", "规模", "质押", "融资", "申请量", "有效量", "代理", "服务业", "统计", "数据", "营收"],
}
DIM_ORDER = ["dynamic", "hot", "fund", "policy"]


def classify(text: str, preferred: str) -> str:
    for dim in ("policy", "hot", "fund"):
        if any(k in text for k in CLASSIFY[dim]):
            return dim
    return preferred  # 未命中则归入发起查询的维度


def fetch_rss(q: str, top: int):
    """免密钥 RSS 抓取：优先 Google News RSS，回退 Bing News RSS。
    在本机（正常网络）可用；沙箱网络受限时可能为空，属正常现象。"""
    import urllib.parse
    from xml.etree import ElementTree as ET
    feeds = [
        ("https://news.google.com/rss/search?q=" +
         urllib.parse.quote(q) + "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        ("https://www.bing.com/news/search?q=" +
         urllib.parse.quote(q) + "&format=rss&setlang=zh-CN"),
    ]
    out = []
    for url in feeds:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for it in root.iter("item"):
                def g(tag):
                    e = it.find(tag)
                    return (e.text or "").strip() if e is not None else ""
                title = g("title")
                # 来源处理：优先用 <source> 标签；若标题形如 "正文 - 来源" 则拆出
                src = g("source")
                if src and title.endswith(" - " + src):
                    title = title[:-(len(src) + 3)]
                elif " - " in title and not src:
                    title, src = title.rsplit(" - ", 1)
                out.append({
                    "title": title,
                    "url": g("link"),
                    "snippet": g("description"),
                    "date": g("pubDate"),
                    "source": src,
                })
            if out:
                break  # 第一个可用源即可
        except Exception as e:
            print(f"[rss]   feed 失败 {url[:60]}…: {e}", file=sys.stderr)
            continue
    return out[:top]


def fetch_bing(q: str, key: str, top: int):
    url = "https://api.bing.microsoft.com/v7.0/news/search"
    r = requests.get(url, params={"q": q, "count": top, "mkt": "zh-CN", "sortBy": "Date"},
                     headers={"Ocp-Apim-Subscription-Key": key}, timeout=25)
    r.raise_for_status()
    out = []
    for v in r.json().get("value", []):
        out.append({
            "title": v.get("name", ""),
            "url": v.get("url", ""),
            "snippet": v.get("description", ""),
            "date": v.get("datePublished", ""),
            "source": (v.get("provider") or [{}])[0].get("name", ""),
        })
    return out


def fetch_serpapi(q: str, key: str, top: int):
    r = requests.get("https://serpapi.com/search.json",
                     params={"engine": "google_news", "q": q, "hl": "zh-cn", "gl": "cn", "api_key": key},
                     timeout=25)
    r.raise_for_status()
    out = []
    for v in r.json().get("news_results", []):
        out.append({
            "title": v.get("title", ""),
            "url": v.get("link", ""),
            "snippet": v.get("snippet", ""),
            "date": v.get("date", ""),
            "source": v.get("source", ""),
        })
    return out


def fetch_gcse(q: str, key: str, cx: str, top: int):
    r = requests.get("https://www.googleapis.com/customsearch/v1",
                     params={"key": key, "cx": cx, "q": q, "lr": "lang_zh", "num": min(top, 10)},
                     timeout=25)
    r.raise_for_status()
    out = []
    for v in r.json().get("items", []):
        out.append({
            "title": v.get("title", ""),
            "url": v.get("link", ""),
            "snippet": v.get("snippet", ""),
            "date": v.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", ""),
            "source": v.get("displayLink", ""),
        })
    return out


def norm_date(s: str) -> str:
    if not s:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s[:len(fmt) + 4], fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def collect(top: int = 8):
    engine = os.getenv("SEARCH_ENGINE", "").lower()
    if engine == "rss":
        fetcher = lambda q: fetch_rss(q, top)
    elif engine == "bing":
        key = os.getenv("BING_SUBSCRIPTION_KEY")
        fetcher = lambda q: fetch_bing(q, key, top)
    elif engine == "serpapi":
        key = os.getenv("SERPAPI_KEY")
        fetcher = lambda q: fetch_serpapi(q, key, top)
    elif engine == "gcse":
        key, cx = os.getenv("GOOGLE_CSE_KEY"), os.getenv("GOOGLE_CSE_CX")
        fetcher = lambda q: fetch_gcse(q, key, cx, top)
    else:
        raise SystemExit("未配置搜索后端。请设置环境变量 SEARCH_ENGINE=bing|serpapi|gcse 并附对应 Key。")

    items, seen = [], set()
    for dim, q in QUERIES.items():
        print(f"[collect] {dim:8s} 检索: {q}")
        try:
            rows = fetcher(q)
        except Exception as e:
            print(f"[collect]   {dim} 失败: {e}", file=sys.stderr)
            continue
        for r in rows:
            u = r["url"]
            if not u or u in seen:
                continue
            seen.add(u)
            text = (r["title"] + " " + r["snippet"])
            items.append({
                "dim": classify(text, dim),
                "date": norm_date(r["date"]),
                "srcZh": r["source"] or "",
                "srcEn": r["source"] or "",
                "url": u,
                "titleZh": r["title"],
                "titleEn": "",
                "sumZh": r["snippet"],
                "sumEn": "",
            })
        print(f"[collect]   -> 本维拿到 {len(rows)} 条")
    items.sort(key=lambda x: x["date"], reverse=True)
    print(f"[collect] 合计 {len(items)} 条")
    return items


def main():
    args = sys.argv[1:]
    top = 8
    dry = "--dry" in args
    for a in args:
        if a.startswith("--top="):
            top = int(a.split("=")[1])
    items = collect(top)
    if dry:
        print(json.dumps(items[:3], ensure_ascii=False, indent=2), "...")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # 合并策略：保留历史已整理条目，仅追加本次新抓到且未收录的，避免冲掉历史真实数据
    existing = []
    if OUT.exists():
        try:
            existing = json.loads(OUT.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []
    seen = {it.get("url", "") for it in existing if it.get("url")}
    added = 0
    for it in items:
        if it.get("url") and it["url"] not in seen:
            seen.add(it["url"])
            existing.append(it)
            added += 1
    existing.sort(key=lambda x: x.get("date", ""), reverse=True)
    OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect] 历史保留 {len(existing)-added} 条，本次新增 {added} 条，合计 {len(existing)} 条 -> {OUT}")


if __name__ == "__main__":
    main()
