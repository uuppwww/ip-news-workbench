# -*- coding: utf-8 -*-
"""
合并所有真实种子数据并产出最终 ip_data.json。

策略：
- 全部 8 个维度条目均来自真实网络检索（URL/来源/标题/摘要均真实，precise=True）。
- 除 edu/view 外，其余维度（ip/patent/trademark/project/policy/hot）保留真实发布日期。
- edu(科普)/view(观点) 维度：按用户选定策略"真实常青文章补足"，将真实常青文章
  归入"近三个月"窗口（2026-05-15 ~ 2026-08-14，共 92 天），使每天 edu+view 合计 >= 10 条。
  文章内容 100% 真实，仅展示日期为策展归入日期（常青内容时效无关）。
"""
import json
import random
from collections import Counter
from datetime import date, timedelta

BASE = "ip_data.json"
OUT = "ip_data.json"

# 1. 基础种子（来自 generate_data.py 生成的 ip_data.json，含 6 基础维度 + 原有少量 edu/view）
base = json.load(open(BASE, encoding="utf-8"))

# 2. 加载所有 _ev*.json（真实 edu/view 采集结果）
evs = []
for n in range(1, 20):
    fn = f"_ev{n:02d}.json"
    try:
        evs += json.load(open(fn, encoding="utf-8"))
    except FileNotFoundError:
        pass

# 3. 合并 + 按 url 去重（保留首次出现）
seen = set()
merged = []
for it in base + evs:
    u = it.get("url")
    if u in seen:
        continue
    seen.add(u)
    merged.append(it)

# 4. 维度分离
WIN0 = date(2026, 5, 15)
WIN1 = date(2026, 8, 14)  # 含当日


def in_window(it):
    y, m, d = map(int, it["date"].split("-"))
    dt = date(y, m, d)
    return WIN0 <= dt <= WIN1


ev_items = [i for i in merged if i["dim"] in ("edu", "view")]
other = [i for i in merged if i["dim"] not in ("edu", "view")]

# 5. 策展：把 edu/view 归入窗口，每天合计 >= 10
in_win = [i for i in ev_items if in_window(i)]
out_win = [i for i in ev_items if not in_window(i)]

days = []
cur = WIN0
while cur <= WIN1:
    days.append(cur.strftime("%Y-%m-%d"))
    cur += timedelta(days=1)
N = len(days)

count_edu = {d: 0 for d in days}
count_view = {d: 0 for d in days}
for i in in_win:
    if i["dim"] == "edu":
        count_edu[i["date"]] += 1
    else:
        count_view[i["date"]] += 1

random.seed(20260815)
random.shuffle(out_win)


def total(d):
    return count_edu[d] + count_view[d]


for it in out_win:
    # 优先补到未满 10 的天；若都已满则均匀分配到任意一天（保留全部真实文章）
    candidates = [d for d in days if total(d) < 10]
    if not candidates:
        candidates = days
    # 取总数最小者；并列时按"补哪类更平衡"打破平局
    c = min(
        candidates,
        key=lambda d: (
            total(d),
            count_view[d] if it["dim"] == "edu" else count_edu[d],
        ),
    )
    it["date"] = c
    if it["dim"] == "edu":
        count_edu[c] += 1
    else:
        count_view[c] += 1

curated_ev = in_win + out_win
final = other + curated_ev
final.sort(key=lambda x: x["date"], reverse=True)

# 6. 写出
json.dump(final, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 7. 报告
perday = Counter(i["date"] for i in curated_ev)
ge10 = sum(1 for d in days if perday.get(d, 0) >= 10)
print("total items:", len(final))
print("by dim:", dict(Counter(i["dim"] for i in final)))
print("window days:", N, "| days >=10 edu+view:", ge10, "| min/day:", min(perday.get(d, 0) for d in days))
print("window edu/view total (curated):", len(curated_ev))
print("edu in window:", sum(count_edu.values()), "| view in window:", sum(count_view.values()))
