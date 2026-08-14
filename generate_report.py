#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识产权·商标专利 主题资讯工作台 —— 生成引擎（重生成只需一条命令）

功能：读取 template.html 与 ip_data.json，把资讯数据注入模板，
      输出单文件、可离线、中英双语的 ip_report.html。

用法：
    python3 generate_report.py                 # 默认读 ip_data.json
    python3 generate_report.py today.json      # 指定数据文件
    python3 generate_report.py --check         # 仅校验数据不写文件

依赖：仅标准库（json / datetime / pathlib / sys）
"""
import json
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "template.html"
DATAFILE = BASE / "ip_data.json"
OUTFILE = BASE / "ip_report.html"

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


def build(items):
    # 注入前按日期倒序，保证渲染即有序（脚本内也有排序，双保险）
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    payload = json.dumps(items, ensure_ascii=False)
    template = TEMPLATE.read_text(encoding="utf-8")
    if "__ITEMS_JSON__" not in template:
        raise RuntimeError("template.html 缺少 __ITEMS_JSON__ 占位符")
    return template.replace("__ITEMS_JSON__", payload)


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    datafile = DATAFILE
    for a in args:
        if a != "--check" and not a.startswith("--"):
            datafile = Path(a)
            if not datafile.is_absolute():
                datafile = BASE / datafile

    items = load_items(datafile)
    print(f"[generate] 读取 {len(items)} 条资讯，来自 {datafile.name}")

    if check_only:
        print("[generate] --check 模式，未写文件")
        return

    html = build(items)
    OUTFILE.write_text(html, encoding="utf-8")
    print(f"[generate] 已生成 {OUTFILE.name} ({len(html)} bytes), 整理日期 {date.today()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[generate] 失败: {e}", file=sys.stderr)
        sys.exit(1)
