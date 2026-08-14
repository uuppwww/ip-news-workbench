#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识产权·商标专利 主题资讯工作台 —— 生成引擎

功能：读取 template.html 与 ip_data.json，注入资讯数据 + 历史日期轴，
      输出单文件、可离线、中英双语的 ip_report.html。

      历史快照在页面内实时渲染「截至所选日期已发生的真实资讯汇总」，
      因此任意日期都有真实内容，不为空白；日期轴从 2025-01-01 到今天。

用法：
    python3 generate_report.py                 # 默认读 ip_data.json
    python3 generate_report.py today.json      # 指定数据文件
    python3 generate_report.py --check         # 仅校验数据不写文件

依赖：仅标准库（json / datetime / pathlib / sys / os）
"""
import json
import sys
import os
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "template.html"
DATAFILE = BASE / "ip_data.json"
OUTFILE = BASE / "ip_report.html"
HISTORY_START = date(2025, 1, 1)

# 维度顺序（决定页面分组顺序）
DIM_ORDER = ["dynamic", "hot", "fund", "policy"]


def load_items(path: Path):
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("数据文件顶层必须是数组")
    required = ["dim", "date", "url", "titleZh", "sumZh", "srcZh"]
    for i, it in enumerate(items):
        miss = [k for k in required if k not in it]
        if miss:
            raise ValueError(f"第 {i} 条缺少字段: {miss}")
        if it["dim"] not in DIM_ORDER:
            raise ValueError(f"第 {i} 条 dim 非法: {it['dim']}")
    return items


def date_range(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def build(items, history_dates):
    items = sorted(items, key=lambda x: x["date"], reverse=True)  # 双保险
    payload = json.dumps(items, ensure_ascii=False)
    dates_payload = json.dumps(history_dates, ensure_ascii=False)
    template = TEMPLATE.read_text(encoding="utf-8")
    for ph in ("__ITEMS_JSON__", "__ARCHIVE_JSON__", "__HISTORY_DATES__"):
        if ph not in template:
            raise RuntimeError(f"template.html 缺少 {ph} 占位符")
    t = template.replace("__ITEMS_JSON__", payload)
    t = t.replace("__ARCHIVE_JSON__", "[]")          # 历史视图改为前端实时渲染
    t = t.replace("__HISTORY_DATES__", dates_payload)
    return t


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    today = os.environ.get("TODAY") or date.today().isoformat()
    datafile = DATAFILE
    for a in args:
        if a.startswith("--"):
            continue
        datafile = Path(a)
        if not datafile.is_absolute():
            datafile = BASE / datafile

    items = load_items(datafile)
    print(f"[generate] 读取 {len(items)} 条资讯，来自 {datafile.name}")

    if check_only:
        print("[generate] --check 模式，未写文件")
        return

    history_dates = [d.isoformat() for d in date_range(HISTORY_START, date.fromisoformat(today))]
    history_dates.sort(reverse=True)

    html = build(items, history_dates)
    OUTFILE.write_text(html, encoding="utf-8")
    print(f"[generate] 主报告 {OUTFILE.name} ({len(html)} bytes), 整理日期 {today}")
    print(f"[generate] 历史日期轴 {len(history_dates)} 天 ({history_dates[-1]} ~ {history_dates[0]})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[generate] 失败: {e}", file=sys.stderr)
        sys.exit(1)
