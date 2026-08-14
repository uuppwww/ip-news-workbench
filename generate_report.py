#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识产权·商标专利 主题资讯工作台 —— 生成引擎

功能：读取 template.html 与 ip_data.json，把资讯数据 + 历史快照列表注入模板，
      输出单文件、可离线、中英双语的 ip_report.html。

      支持 --archive：把当天快照存入 archive/<日期>.html，并维护一份
      history-base.html（2025-01-01 以来的基线快照）。archive/index.json
      列出 2025-01-01 到今天每一天，缺失的日期指向 history-base.html，
      因此页面历史快照下拉可以看到完整日期轴。

用法：
    python3 generate_report.py                 # 默认读 ip_data.json
    python3 generate_report.py today.json      # 指定数据文件
    python3 generate_report.py --archive       # 同时归档历史快照
    python3 generate_report.py --check         # 仅校验数据不写文件

依赖：仅标准库（json / datetime / pathlib / sys / shutil / os）
"""
import json
import sys
import os
import shutil
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "template.html"
DATAFILE = BASE / "ip_data.json"
OUTFILE = BASE / "ip_report.html"
ARCHIVE_DIR = BASE / "archive"
ARCHIVE_INDEX = ARCHIVE_DIR / "index.json"
BASELINE_FILE = "history-base.html"
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


def load_archive_index():
    if ARCHIVE_INDEX.exists():
        try:
            data = json.loads(ARCHIVE_INDEX.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def date_range(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def build(items, archive_list):
    # 注入前按日期倒序，保证渲染即有序（脚本内也有排序，双保险）
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    payload = json.dumps(items, ensure_ascii=False)
    arch_payload = json.dumps(archive_list, ensure_ascii=False)
    template = TEMPLATE.read_text(encoding="utf-8")
    if "__ITEMS_JSON__" not in template:
        raise RuntimeError("template.html 缺少 __ITEMS_JSON__ 占位符")
    if "__ARCHIVE_JSON__" not in template:
        raise RuntimeError("template.html 缺少 __ARCHIVE_JSON__ 占位符")
    t = template.replace("__ITEMS_JSON__", payload)
    t = t.replace("__ARCHIVE_JSON__", arch_payload)
    return t


def compute_full_index(old_index, today_str, count, archive_run):
    """
    返回 2025-01-01 到 today 的完整日期列表。
    - 真实快照文件保留（任何不是 history-base.html 的 entry）。
    - today 如果是归档运行，指向 today.html；否则作为基线。
    - 其余缺失日期指向 history-base.html。
    """
    today = date.fromisoformat(today_str)
    old_map = {e["date"]: e for e in old_index if "date" in e}
    result = {}

    for d in date_range(HISTORY_START, today):
        ds = d.isoformat()
        entry = old_map.get(ds)
        # 保留已有真实快照（非基线）
        if entry and entry.get("file") and entry.get("file") != BASELINE_FILE:
            result[ds] = entry
        else:
            result[ds] = {"date": ds, "file": BASELINE_FILE, "count": count}

    # 今天：如果是归档运行，使用真实快照
    if archive_run:
        result[today_str] = {"date": today_str, "file": f"{today_str}.html", "count": count}

    return sorted(result.values(), key=lambda e: e["date"], reverse=True)


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    archive = "--archive" in args
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

    old_index = load_archive_index()
    new_index = compute_full_index(old_index, today, len(items), archive)

    html = build(items, new_index)
    OUTFILE.write_text(html, encoding="utf-8")
    print(f"[generate] 主报告 {OUTFILE.name} ({len(html)} bytes), 整理日期 {today}")

    if archive:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        # 当天真实快照
        snapshot_path = ARCHIVE_DIR / f"{today}.html"
        shutil.copy(OUTFILE, snapshot_path)
        # 基线快照：给没有独立日期的历史日期用
        baseline_path = ARCHIVE_DIR / BASELINE_FILE
        shutil.copy(OUTFILE, baseline_path)
        ARCHIVE_INDEX.write_text(
            json.dumps(new_index, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        real_count = sum(1 for e in new_index if e["file"] != BASELINE_FILE)
        print(
            f"[generate] 已归档 archive/{today}.html，"
            f"基线 archive/{BASELINE_FILE}，"
            f"历史索引共 {len(new_index)} 天（真实快照 {real_count} 天）"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[generate] 失败: {e}", file=sys.stderr)
        sys.exit(1)
