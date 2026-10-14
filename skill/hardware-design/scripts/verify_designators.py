#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设计文档位号一致性检查——hardware-design skill 自带工具。

检查 Markdown 设计文档中：
  1. 位号是否出现在多个"本模块元器件表"（跨模块重复 → 用户画图无所适从）
  2. 模块表中出现的位号是否都进了 BOM
  3. BOM 中是否有位号找不到对应模块表（警告）

识别规则：
  - 表格：Markdown 管道表，表头任一单元格含"位号"的表参与检查
  - 带"位号"表头且所在章标题（## 层）含 BOM 的表 → BOM 表
  - 其余带"位号"表头的表 → 模块元器件表
  - 位号格式：字母前缀+数字（R12、C4、Q1、U3、LED2…），支持 SW1~SW3 区间展开
  - 代码块（``` 包裹）内容跳过

用法：
  python verify_designators.py <设计文档.md>

仅用标准库。退出码：0=无错误，1=有错误。
"""
import argparse
import re
import sys

TOKEN = re.compile(r"\b([A-Z]{1,4})(\d{1,3})\b")
RANGE = re.compile(r"\b([A-Z]{1,4})(\d{1,3})\s*[~～]\s*(?:[A-Z]{1,4})?(\d{1,3})\b")
SEP_ROW = re.compile(r"^[\s|:\-]+$")


def extract_designators(cell: str) -> set:
    """从单元格文本提取位号集合，支持 SW1~SW3 / SW1～4 区间展开。"""
    out = set()
    for m in RANGE.finditer(cell):
        prefix, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        if hi >= lo and hi - lo < 50:
            out.update(f"{prefix}{n}" for n in range(lo, hi + 1))
    for m in TOKEN.finditer(cell):
        out.add(m.group(0))
    return out


def parse_tables(path: str):
    """返回 [(章节标签, 表头 cells, 数据行 cells)，仅保留表头含'位号'的表]。"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    tables = []
    h2 = h3 = ""
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        if line.startswith("## ") and not line.startswith("### "):
            h2, h3 = line[3:].strip(), ""
            i += 1
            continue
        if line.startswith("### "):
            h3 = line[4:].strip()
            i += 1
            continue
        if line.lstrip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = []
            for ln in block:
                if SEP_ROW.match(ln):
                    continue
                rows.append([c.strip() for c in ln.strip("|").split("|")])
            if len(rows) >= 2 and any("位号" in c for c in rows[0]):
                label = " / ".join(x for x in (h2, h3) if x)
                tables.append((label, rows))
            continue
        i += 1
    return tables


def main() -> int:
    p = argparse.ArgumentParser(description="设计文档位号一致性检查")
    p.add_argument("doc", help="设计文档 .md 路径")
    a = p.parse_args()

    tables = parse_tables(a.doc)
    module_tables = []  # (章节, 位号集合)
    bom_tables = []

    for label, rows in tables:
        header = rows[0]
        idx = next((k for k, c in enumerate(header) if "位号" in c), None)
        if idx is None:
            continue
        desigs = set()
        for r in rows[1:]:
            if len(r) > idx:
                desigs |= extract_designators(r[idx])
        if not desigs:
            continue
        if "BOM" in label.upper() and "BOM" in label.split(" / ")[0].upper():
            bom_tables.append((label, desigs))
        else:
            module_tables.append((label, desigs))

    errors, warnings = [], []

    owner = {}
    for label, desigs in module_tables:
        for d in desigs:
            owner.setdefault(d, []).append(label)
    for d in sorted(owner):
        if len(owner[d]) > 1:
            errors.append(f"位号 {d} 出现在多个模块表：{ '、'.join(owner[d]) }")

    mod_all = set(owner)
    bom_all = set()
    for _, desigs in bom_tables:
        bom_all |= desigs

    for d in sorted(mod_all - bom_all):
        errors.append(f"位号 {d} 在模块元器件表中，但 BOM 里找不到")
    for d in sorted(bom_all - mod_all):
        warnings.append(f"位号 {d} 在 BOM 中，但没有对应的模块元器件表")

    print(f"文件：{a.doc}")
    print(f"模块元器件表：{len(module_tables)} 个，BOM 表：{len(bom_tables)} 个")
    for label, desigs in module_tables:
        print(f"  [模块] {label}：{len(desigs)} 个位号")
    for label, desigs in bom_tables:
        print(f"  [BOM ] {label}：{len(desigs)} 个位号")
    print()

    if errors:
        print(f"✗ 错误 {len(errors)} 项：")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"⚠ 警告 {len(warnings)} 项：")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("✓ 通过：位号无跨模块重复，模块表与 BOM 一致")
    print()
    print("注意：本工具只查一致性与重复，参数正确性仍需人工按手册核对。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
