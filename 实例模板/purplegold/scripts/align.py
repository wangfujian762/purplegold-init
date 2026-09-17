#!/usr/bin/env python3
"""对齐脚本：扫描 project/ 模块树，重新生成根模块 ALLOY.md 的派生区。

用法：python3 purplegold/scripts/align.py [项目根路径]
本文件同时承载两个脚本共用的合金文档解析逻辑（validate.py 会 import 本文件）。
"""

import os
import re
import sys
from pathlib import Path

MARKER = "<!-- 派生区 · 以下由对齐脚本自动生成，禁止手工编辑 -->"
REQUIRED_SECTIONS = ["模块简介", "子模块指针", "内部关系", "边界关系", "父模块指针", "接口与行为约定", "其他信息"]

H1_RE = re.compile(r"^# 合金文档 · (.+?)\s*$")
TS_RE = re.compile(r"^> 最后修改：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s*$")
H2_RE = re.compile(r"^## (.+?)\s*$")
POINTER_RE = re.compile(r"^- `([^`]+)` · (.+?) — (.*)$")
BOUNDARY_RE = re.compile(r"^- (.+?) — (.+?) — (.+?)\s*$")
MODPATH_RE = re.compile(r"^- 模块路径：`([^`]+)`\s*$")
PARENT_RE = re.compile(r"^- 父模块：`([^`]+)`\s*$")
EDGE_RE = re.compile(r"^(\S+) --> (\S+)$")
FORBIDDEN_IN_NAME = [" ", ".", "/", "\\", "-->"]


class Module:
    """一个文件夹模块及其合金文档的解析结果。"""

    def __init__(self, path, doc_path):
        self.path = path              # 项目根相对路径，以 "/" 结尾；根模块为 "project/"
        self.doc_path = doc_path      # ALLOY.md 的绝对路径
        self.name = None              # H1 命名行中的命名
        self.declared_path = None     # "模块简介"中声明的模块路径
        self.declared_parent = None   # "父模块指针"中声明的父模块路径
        self.children = []            # 子模块指针项：(路径, 命名, 说明)
        self.edges = []               # 内部关系依赖边：(X, Y)，X/Y 为子模块命名
        self.mermaid_block = None     # "内部关系"中的 mermaid 代码块原文
        self.boundary = []            # 边界关系项：(成员命名, 外部对象, 交互说明)
        self.contract = []            # "接口与行为约定"小节的内容行（已去除 HTML 注释与空行）
        self.errors = []              # 解析与格式错误


def default_root():
    """从脚本位置推导项目根：<项目根>/purplegold/scripts/align.py。"""
    return Path(__file__).resolve().parents[2]


def is_comment_or_blank(line):
    s = line.strip()
    return not s or (s.startswith("<!--") and s.endswith("-->"))


def split_sections(lines):
    """按 H2 标题切分，返回 {小节名: [行]}（不含标题行本身）。"""
    sections = {}
    current = None
    for line in lines:
        m = H2_RE.match(line)
        if m:
            current = m.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def parse_mermaid(section_lines, mod):
    """提取并解析内部关系小节中的 mermaid 代码块。"""
    text_lines = section_lines
    start = None
    for i, line in enumerate(text_lines):
        if line.strip() == "```mermaid":
            start = i
            break
    if start is None:
        mod.errors.append(f"{mod.path}：内部关系缺少 mermaid 代码块")
        return
    end = None
    for j in range(start + 1, len(text_lines)):
        if text_lines[j].strip() == "```":
            end = j
            break
    if end is None:
        mod.errors.append(f"{mod.path}：内部关系的 mermaid 代码块未闭合")
        return
    block_lines = text_lines[start:end + 1]
    mod.mermaid_block = "\n".join(block_lines)
    body = [l.strip() for l in block_lines[1:-1] if l.strip()]
    if not body or body[0] != "graph TD":
        mod.errors.append(f"{mod.path}：mermaid 图必须以 graph TD 开头")
        return
    for l in body[1:]:
        m = EDGE_RE.match(l)
        if not m:
            mod.errors.append(f"{mod.path}：mermaid 图含不符合严格子集的行：{l!r}")
        else:
            mod.edges.append((m.group(1), m.group(2)))


def parse_alloy(doc_path, module_path):
    """解析一份合金文档，返回 Module（错误记入 mod.errors）。"""
    mod = Module(module_path, doc_path)
    try:
        lines = doc_path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        mod.errors.append(f"{module_path}：无法读取 {doc_path}：{e}")
        return mod

    # H1 命名行与时间戳行
    if not lines:
        mod.errors.append(f"{module_path}：合金文档为空")
        return mod
    m = H1_RE.match(lines[0])
    if not m:
        mod.errors.append(f"{module_path}：H1 命名行格式不合规（应为 `# 合金文档 · <命名>`）")
    else:
        mod.name = m.group(1)
    if len(lines) < 2 or not TS_RE.match(lines[1]):
        mod.errors.append(f"{module_path}：时间戳行缺失或格式不合规（应为 `> 最后修改：YYYY-MM-DD HH:MM:SS`，位于 H1 下一行）")

    # 必备小节
    sections = split_sections(lines[2:] if len(lines) > 2 else [])
    for name in REQUIRED_SECTIONS:
        if name not in sections:
            mod.errors.append(f"{module_path}：缺少必备小节「{name}」")

    # 模块简介：模块路径声明
    for line in sections.get("模块简介", []):
        m = MODPATH_RE.match(line.strip())
        if m:
            mod.declared_path = m.group(1)
    if "模块简介" in sections and mod.declared_path is None:
        mod.errors.append(f"{module_path}：模块简介中缺少模块路径声明（应为 `- 模块路径：`路径``）")

    # 子模块指针：只检查列表项的格式，散文忽略（白名单制）
    for line in sections.get("子模块指针", []):
        s = line.strip()
        if is_comment_or_blank(s) or not s.startswith("- "):
            continue
        m = POINTER_RE.match(s)
        if not m:
            mod.errors.append(f"{module_path}：子模块指针含格式不合规的列表项：{s!r}")
        else:
            mod.children.append((m.group(1), m.group(2), m.group(3)))

    # 内部关系
    if "内部关系" in sections:
        parse_mermaid(sections["内部关系"], mod)

    # 边界关系：只检查列表项的格式（三段式），散文与"无"忽略（白名单制）
    for line in sections.get("边界关系", []):
        s = line.strip()
        if is_comment_or_blank(s) or not s.startswith("- "):
            continue
        m = BOUNDARY_RE.match(s)
        if not m:
            mod.errors.append(f"{module_path}：边界关系含格式不合规的列表项：{s!r}")
        else:
            mod.boundary.append((m.group(1), m.group(2), m.group(3)))

    # 父模块指针
    for line in sections.get("父模块指针", []):
        m = PARENT_RE.match(line.strip())
        if m:
            mod.declared_parent = m.group(1)

    # 接口与行为约定：内容不限格式，留存去除 HTML 注释与空行后的内容行
    if "接口与行为约定" in sections:
        text = re.sub(r"<!--.*?-->", "", "\n".join(sections["接口与行为约定"]), flags=re.S)
        mod.contract = [l.rstrip() for l in text.splitlines() if l.strip()]

    # 命名合规
    if mod.name:
        for bad in FORBIDDEN_IN_NAME:
            if bad in mod.name:
                mod.errors.append(f"{module_path}：命名 {mod.name!r} 含禁用字符 {bad!r}")
    for _, cname, _ in mod.children:
        for bad in FORBIDDEN_IN_NAME:
            if bad in cname:
                mod.errors.append(f"{module_path}：子模块命名 {cname!r} 含禁用字符 {bad!r}")

    return mod


def discover_modules(root):
    """扫描 project/，返回 ({模块路径: Module}, [错误])。只完成发现与解析，不做交叉校验。"""
    project_dir = root / "project"
    errors = []
    if not project_dir.is_dir():
        return {}, [f"工程根不存在：{project_dir}"]
    modules = {}
    for dirpath, dirnames, filenames in os.walk(project_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if "ALLOY.md" in filenames:
            rel = Path(dirpath).relative_to(root).as_posix() + "/"
            modules[rel] = parse_alloy(Path(dirpath) / "ALLOY.md", rel)
    if "project/" not in modules:
        errors.append("根模块合金文档缺失：project/ALLOY.md")
        return modules, errors
    # 模块的祖先必须全是模块（非模块文件夹的子树内不得出现 ALLOY.md）
    for path in modules:
        if path == "project/":
            continue
        parts = path.rstrip("/").split("/")
        for i in range(1, len(parts)):
            ancestor = "/".join(parts[:i]) + "/"
            if ancestor not in modules:
                errors.append(f"{path}：祖先文件夹 {ancestor} 不是模块，但其子树内出现了 ALLOY.md")
    return modules, errors


def generate_derived(modules):
    """根据各局部合金文档生成派生区文本（从标记线 --- 开始，以换行结尾）。"""
    out = ["---", "", MARKER, "", "## 全工程模块索引", ""]

    index = [(m.path, m.name or "（未命名）") for m in modules.values()]
    for m in modules.values():
        for cpath, cname, _ in m.children:
            if not cpath.endswith("/"):  # 单文件模块
                index.append((cpath, cname))
    for path, name in sorted(set(index), key=lambda x: x[0]):
        out.append(f"- `{path}` · {name}")

    out += ["", "## 内部关系总览", ""]
    any_graph = False
    for path in sorted(modules):
        m = modules[path]
        if m.mermaid_block is not None:
            any_graph = True
            out += [f"### `{path}`", "", m.mermaid_block, ""]
    if not any_graph:
        out.append("（各模块均无内部关系图。）")
        out.append("")

    out += ["## 全工程边界总览", ""]
    any_boundary = False
    for path in sorted(modules):
        m = modules[path]
        if m.boundary:
            any_boundary = True
            out += [f"### `{path}`", ""]
            for member, target, desc in m.boundary:
                out.append(f"- {member} — {target} — {desc}")
            out.append("")
    if not any_boundary:
        out.append("（各模块均无边界成员。）")
        out.append("")

    out += ["## 接口与行为约定总览", ""]
    any_contract = False
    for path in sorted(modules):
        m = modules[path]
        if any(l.strip() != "（无。）" for l in m.contract):
            any_contract = True
            out += [f"### `{path}`", ""]
            out += m.contract
            out.append("")
    if not any_contract:
        out.append("（各模块均无接口与行为约定内容。）")
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def split_at_derived(text):
    """把根模块合金文档切为（派生区之前的前缀, 派生区起始行号）。标记线缺失时返回 None。"""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == MARKER:
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0 and lines[j].strip() == "---":
                return "\n".join(lines[:j]).rstrip("\n") + "\n", j
            return None
    return None


def cmd_align(root):
    root_doc = root / "project" / "ALLOY.md"
    if not root_doc.is_file():
        print(f"错误：根模块合金文档不存在：{root_doc}")
        return 1
    text = root_doc.read_text(encoding="utf-8")
    cut = split_at_derived(text)
    if cut is None:
        print(f"错误：{root_doc} 中未找到派生区标记线（--- 加一行固定注释 {MARKER}）")
        return 1
    prefix, _ = cut
    modules, errors = discover_modules(root)
    parse_errors = [e for m in modules.values() for e in m.errors]
    if errors or parse_errors:
        print("警告：扫描中发现以下问题（派生区仍已按可解析的内容生成；请运行 validate.py 详查）：")
        for e in errors + parse_errors:
            print(f"  - {e}")
    derived = generate_derived(modules)
    root_doc.write_text(prefix + "\n" + derived, encoding="utf-8")
    n_mod = len(modules)
    n_single = sum(1 for m in modules.values() for c in m.children if not c[0].endswith("/"))
    print(f"派生区已对齐：{n_mod} 个文件夹模块、{n_single} 个单文件模块 → {root_doc}")
    return 0


def main(argv):
    root = Path(argv[1]).resolve() if len(argv) > 1 else default_root()
    return cmd_align(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
