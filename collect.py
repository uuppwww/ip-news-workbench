#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日采集知识产权主题真实资讯，合并追加到 ip_data.json，按 URL 去重。

双通道采集（2026-08 起）：
1) 搜索型 RSS —— Google News 按各维度关键词搜索，标题直接命中，
   稳定产出「热点 / 科普 / 观点」等各维度条目（GitHub Actions 海外环境可用，失败静默跳过）。
2) 权威媒体 RSS —— 人民网 / 新华网 / 中国新闻网 / 钛媒体 / 新浪科技 各频道，
   国内外均稳定可用，作为兜底。

字段 date 采用文章「真实发布日期」；precise=True 表示链接可点击（原文或搜索跳转）。
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, date, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlparse

import requests

DATA_FILE = "ip_data.json"

# ---- 通道2：权威媒体 RSS（稳定兜底，已实测可用）----
FEEDS = [
    ("人民网·时政", "http://www.people.com.cn/rss/politics.xml"),
    ("人民网·财经", "http://www.people.com.cn/rss/finance.xml"),
    ("人民网·法治", "http://www.people.com.cn/rss/legal.xml"),
    ("新华网·时政", "http://www.xinhuanet.com/politics/news_politics.xml"),
    ("新华网·财经", "http://www.xinhuanet.com/fortune/news_finance.xml"),
    ("新华网·科技", "http://www.xinhuanet.com/tech/news_tech.xml"),
    ("中国新闻网", "https://www.chinanews.com.cn/rss/scroll-news.xml"),
    ("钛媒体", "https://www.tmtpost.com/rss.xml"),
    ("新浪科技", "https://rss.sina.com.cn/tech/rollnews.xml"),
]

# ---- 通道1：搜索型 RSS（Google News）—— 重点强化 热点/科普/观点 ----
GOOGLE_QUERIES = [
    ("知识产权 侵权 判赔", "hot"),
    ("专利侵权 判决", "hot"),
    ("商标 抢注 维权", "hot"),
    ("商业秘密 纠纷 案例", "hot"),
    ("知识产权 科普 知识", "edu"),
    ("专利 知识 科普", "edu"),
    ("商标注册 知识 流程", "edu"),
    ("知识产权 趋势 专家", "view"),
    ("知识产权 观点 预测", "view"),
    ("知识产权 政策 发布", "policy"),
    ("高新技术企业 专精特新", "project"),
    ("专利 发明 申请", "patent"),
    ("商标 品牌 保护", "trademark"),
]

# 知识产权「强」关键词（标题命中其一即保留；避免普通时政/财经新闻混入）
KEYWORDS = [
    "知识产权", "商标", "专利", "著作权", "版权", "地理标志", "商业秘密",
    "高新技术企业", "科技型中小企业", "专精特新", "小巨人", "专利奖",
    "数据知识产权", "pct", "外观设计", "实用新型", "发明专利", "惩罚性赔偿",
    "侵权", "知产", "商标注册", "品牌保护", "技术合同", "科技成果转化",
    "集成电路布图", "马德里", "著作权法", "专利法", "商标法",
    # 热点 / 维权 / 竞争法
    "不正当竞争", "反垄断", "恶意抢注", "商标无效", "专利无效", "判赔",
    "盗版", "假冒", "山寨", "维权", "打假", "知识产权纠纷", "垄断",
    # 科普 / 观点（与 IP 强相关组合）
    "知识产权强国", "专利布局", "品牌战略",
]

# 维度判定（优先级从高到低；edu/view 提前，让“专利科普/专家观点”正确归类）
DIM_RULES = [
    ("hot", ["侵权", "纠纷", "诉讼", "判赔", "胜诉", "起诉", "商业秘密", "盗版", "假冒", "抢注", "维权", "获赔", "索赔", "惩罚性赔偿", "判例", "判决", "裁定", "不正当竞争", "反垄断", "恶意抢注", "商标无效", "专利无效", "打假", "山寨", "垄断", "禁令"]),
    ("project", ["高新技术企业", "科技型中小企业", "科小", "专精特新", "小巨人", "瞪羚", "独角兽", "企业技术中心", "入库", "拟认定", "专利奖", "单项冠军", "示范企业", "优势企业"]),
    ("edu", ["科普", "解读", "图解", "什么是", "一文读懂", "如何", "干货", "流程", "步骤", "要点", "实务", "问答", "知识点", "常识", "扫盲", "小知识"]),
    ("view", ["观点", "访谈", "展望", "趋势", "预测", "专家", "教授", "学者", "署名文章", "观察", "研判", "前瞻", "报告", "白皮书", "盘点", "年度", "风口", "机遇", "挑战", "评论", "时评", "快评"]),
    ("trademark", ["商标", "马德里", "集体商标", "地理标志证明商标", "商标审查", "商标注册", "品牌", "老字号", "商标权"]),
    ("patent", ["专利", "pct", "发明专利", "实用新型", "外观设计", "专利审查", "专利导航", "专利转化", "专利布局", "集成电路布图"]),
    ("policy", ["政策", "印发", "发布", "实施", "修订", "通过", "规划", "意见", "办法", "条例", "细则", "指南", "方案", "强国建设", "工作要点", "专项行动"]),
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def load_existing():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)


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
    for dim, kws in DIM_RULES:
        if any(k.lower() in t for k in kws):
            return dim
    return "ip"


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_date(pub):
    """解析 RSS pubDate；失败返回 None。调用方应跳过，而不是假设为今天。"""
    if not pub:
        return None
    try:
        dt = parsedate_to_datetime(pub)
        if dt:
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt.date().isoformat()
    except Exception:
        pass
    return None


def hits_keyword(text):
    t = text.lower()
    return any(k.lower() in t for k in KEYWORDS)


def within_days(d, days=30, today=None):
    try:
        item_date = datetime.strptime(d, "%Y-%m-%d").date()
        return (today - item_date).days <= days
    except Exception:
        return True


def fetch_feed(name, url):
    """通道2：权威媒体 RSS，标题命中强关键词才保留。"""
    items = []
    try:
        r = requests.get(url, timeout=25, headers=UA)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"feed failed [{name}]: {e}")
        return items

    today = date.today()
    nodes = root.findall(".//item")
    for node in nodes:
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        pub = (node.findtext("pubDate") or "").strip()
        desc = (node.findtext("description") or "")
        if not title or not link:
            continue
        if not hits_keyword(title):
            continue
        d = parse_date(pub)
        if not d:
            continue
        if not within_days(d, 30, today):
            continue
        dim = classify(title)
        clean_desc = strip_html(desc)
        host = (urlparse(link).hostname or "").replace("www.", "")
        items.append({
            "dim": dim,
            "date": d,
            "url": link,
            "srcZh": name,
            "srcEn": host or name,
            "titleZh": title,
            "titleEn": title,
            "sumZh": clean_desc[:90] if clean_desc else f"{title}。",
            "sumEn": f"{title} (collected from {name}).",
            "precise": True,
        })
    return items


def fetch_google(query, qdim, limit=8):
    """通道1：Google News 搜索 RSS，标题命中；来源取自 <source>。"""
    items = []
    url = "https://news.google.com/rss/search?q=" + quote(query) + "&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    try:
        r = requests.get(url, timeout=25, headers=UA)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"google search failed [{query}]: {e}")
        return items

    today = date.today()
    nodes = root.findall(".//item")
    got = 0
    for node in nodes:
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        pub = (node.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        if not hits_keyword(title):
            continue
        # 来源名与域名取自 <source url="...">媒体名</source>
        src_name, src_host = "", ""
        src = node.find("source")
        if src is not None:
            src_name = (src.text or "").strip()
            src_host = (urlparse(src.get("url") or "").hostname or "").replace("www.", "")
        d = parse_date(pub)
        if not d:
            continue
        if not within_days(d, 45, today):
            continue
        # 优先用查询自带维度，除非标题能更精确归类
        dim = classify(title)
        if dim == "ip":
            dim = qdim
        desc = (node.findtext("description") or "")
        clean_desc = strip_html(desc)
        items.append({
            "dim": dim,
            "date": d,
            "url": link,
            "srcZh": src_name or qdim,
            "srcEn": src_host or "Google News",
            "titleZh": title,
            "titleEn": title,
            "sumZh": clean_desc[:90] if clean_desc else f"{title}。",
            "sumEn": f"{title} (via Google News).",
            "precise": True,
        })
        got += 1
        if got >= limit:
            break
    return items


def fetch_cnipa():
    """通道3：国家知识产权局官网新闻（HTML，URL 内嵌真实发布日期，稳定兜底）。"""
    items = []
    url = "https://www.cnipa.gov.cn/col/col4/index.html"
    try:
        r = requests.get(url, timeout=25, headers=UA)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
    except Exception as e:
        print(f"cnipa failed: {e}")
        return items

    today = date.today()
    seen = set()
    # 例：<a ... href="/art/2026/8/14/art_57_207729.html" ...>标题</a>
    for m in re.finditer(
        r'<a\b[^>]*href="(/art/(\d{4})/(\d{1,2})/(\d{1,2})/[^"]+)"[^>]*>(.*?)</a>',
        html, re.S,
    ):
        href, y, mo, d = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        tag = m.group(0)
        tm = re.search(r'title=[\'"]([^\'"]+)', tag)
        title = strip_html(tm.group(1) if tm else m.group(5))
        if not title:
            continue
        iso = f"{y:04d}-{mo:02d}-{d:02d}"
        if not within_days(iso, 30, today):
            continue
        full = "https://www.cnipa.gov.cn" + href
        if full in seen:
            continue
        seen.add(full)
        items.append({
            "dim": classify(title),
            "date": iso,
            "url": full,
            "srcZh": "国家知识产权局",
            "srcEn": "CNIPA",
            "titleZh": title,
            "titleEn": title,
            "sumZh": f"{title}。",
            "sumEn": f"{title} (CNIPA).",
            "precise": True,
        })
    return items


def fetch_iprchn(limit=10):
    """通道4：中国知识产权资讯网（HTML，逐条抓文章页取真实发布日期）。"""
    items = []
    try:
        r = requests.get("https://www.iprchn.com/index.html", timeout=25, headers=UA)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
    except Exception as e:
        print(f"iprchn index failed: {e}")
        return items

    today = date.today()
    seen = set()
    for m in re.finditer(
        r'<a\b[^>]*href="(cipnews/news_content\.aspx\?newsId=\d+)"[^>]*>(.*?)</a>',
        html, re.S,
    ):
        href = m.group(1)
        tag = m.group(0)
        tm = re.search(r'title=[\'"]([^\'"]+)', tag)
        title = strip_html(tm.group(1) if tm else m.group(2))
        if not title or title in seen:
            continue
        seen.add(title)
        full = "https://www.iprchn.com/" + href
        # 抓文章页取真实发布日期（文章页首个 2026/8/14 形式即发布日期）
        iso = today.isoformat()
        try:
            ar = requests.get(full, timeout=20, headers=UA)
            ar.encoding = ar.apparent_encoding or "utf-8"
            dm = re.search(r'20(\d{2})[/-](\d{1,2})[/-](\d{1,2})', ar.text)
            if dm:
                iso = f"20{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}"
        except Exception:
            pass
        if not within_days(iso, 30, today):
            continue
        items.append({
            "dim": classify(title),
            "date": iso,
            "url": full,
            "srcZh": "中国知识产权资讯网",
            "srcEn": "China IP News",
            "titleZh": title,
            "titleEn": title,
            "sumZh": f"{title}。",
            "sumEn": f"{title} (China IP News).",
            "precise": True,
        })
        if len(items) >= limit:
            break
    return items


def collect(top=20):
    new_items = []
    # 通道1：搜索型（更精准，优先）
    for q, dim in GOOGLE_QUERIES:
        new_items += fetch_google(q, dim)
    # 通道2：权威媒体 RSS
    for name, url in FEEDS:
        new_items += fetch_feed(name, url)
    # 通道3/4：知识产权垂直官网（HTML 兜底，稳定产出新鲜 IP 资讯）
    new_items += fetch_cnipa()
    new_items += fetch_iprchn()
    if not new_items:
        print("no new items fetched")
        return 0
    new_items = dedup(new_items)[:top]
    existing = load_existing()
    merged = dedup(existing + new_items)
    merged.sort(key=lambda x: x.get("date", ""), reverse=True)
    save_items(merged)
    print(f"collected {len(new_items)} new items (google={len(GOOGLE_QUERIES)}q + feeds={len(FEEDS)} + cnipa + iprchn), total={len(merged)}")
    return len(new_items)


if __name__ == "__main__":
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 20
    collect(top)
