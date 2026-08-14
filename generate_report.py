#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识产权·商标专利 主题资讯工作台 —— 生成引擎（重生成只需一条命令）

功能：读取 template.html 与 ip_data.json，把资讯数据 + 历史快照列表注入模板，
      输出单文件、可离线、中英双语的 ip_report.html。
      支持 --archive：除主报告外，额外把当天快照存入 archive/<日期>.html，
      并维护 archive/index.json 供页面"历史快照"下拉使用。

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
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "template.html"
DATAFILE = BASE / "ip_data.json"
OUTFILE = BASE / "ip_report.html"
ARCHIVE_DIR = BASE / "archive"
ARCHIVE_INDEX = ARCHIVE_DIR / "index.json"

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


def compute_new_index(old_index, today, count):
    # 去重（同一天覆盖），再按日期倒序
    new_index = [e for e in old_index if e.get("date") != today]
    new_index.append({"date": today, "file": f"{today}.html", "count": count})
    new_index.sort(key=lambda e: e["date"], reverse=True)
    return new_index


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

    # 构造完整历史列表（内存），主报告与快照都内联它，下拉即可翻历史
    old_index = load_archive_index()
    new_index = compute_new_index(old_index, today, len(items))

    html = build(items, new_index)
    OUTFILE.write_text(html, encoding="utf-8")
    print(f"[generate] 主报告 {OUTFILE.name} ({len(html)} bytes), 整理日期 {today}")

    if archive:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(OUTFILE, ARCHIVE_DIR / f"{today}.html")
        ARCHIVE_INDEX.write_text(
            json.dumps(new_index, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[generate] 已归档 archive/{today}.html，共 {len(new_index)} 个历史快照")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[generate] 失败: {e}", file=sys.stderr)
        sys.exit(1)
