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

    # 日期轴：仅采用数据里真实存在的日期（倒序），不做无数据的铺满
    dates = sorted({it["date"] for it in items}, reverse=True)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False))
    html = html.replace("__HISTORY_DATES__", json.dumps(dates))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"report generated: {OUTPUT}")
    print(f"items={len(items)}, real_dates={len(dates)}")

if __name__ == "__main__":
    main()
