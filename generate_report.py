#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import date

DATA_FILE = "ip_data.json"
TEMPLATE = "template.html"
OUTPUT = "ip_report.html"

START = date(2025, 1, 1)
END = date.today()

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    # 日期轴：2025-01-01 到今天
    dates = []
    cur = START
    while cur <= END:
        dates.append(cur.isoformat())
        cur += __import__("datetime").timedelta(days=1)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False))
    html = html.replace("__HISTORY_DATES__", json.dumps(dates))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"report generated: {OUTPUT}")
    print(f"items={len(items)}, dates={len(dates)}")

if __name__ == "__main__":
    main()
