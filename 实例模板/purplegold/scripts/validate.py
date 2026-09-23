#!/usr/bin/env python3
"""校验脚本：检查实例中外骨骼体系的健康度，以及实例骨架就位情况。

用法：python3 purplegold/scripts/validate.py [项目根路径]
校验项见 purplegold/RULES.md 第 2.5 节（以彼为权威）；退出码 0 = 全部通过，1 = 存在问题。
"""

import sys
from pathlib import Path

from align import (MARKER, Module, default_root, discover_modules,
                   generate_derived, split_at_derived)


def check_names_unique(modules):
    errors = []
    for m in modules.values():
        seen = {}
        for cpath, cname, _ in m.children:
            if cname in seen:
                errors.append(f"{m.path}：子模块重名 {cname!r}（{seen[cname]} 与 {cpath}）")
            else:
                seen[cname] = cpath
    return errors


def check_pointers(root, modules):
    """子模块指针、父模块指针与实际目录树一致。"""
    errors = []
    for m in modules.values():
        child_names = {cname: cpath for cpath, cname, _ in m.children}
        for cpath, cname, _ in m.children:
            # 必须为直接子路径
            if not cpath.startswith(m.path):
                errors.append(f"{m.path}：子模块路径 {cpath} 不在本模块路径之下")
                continue
            rest = cpath[len(m.path):]
            is_folder = cpath.endswith("/")
            core = rest[:-1] if is_folder else rest
            if not core or "/" in core:
                errors.append(f"{m.path}：子模块路径 {cpath} 不是直接子路径")
                continue
            if is_folder:
                target = modules.get(cpath)
                if target is None:
                    if (root / cpath).is_dir():
                        errors.append(f"{m.path}：子模块 {cpath} 缺少 ALLOY.md")
                    else:
                        errors.append(f"{m.path}：子模块指针指向不存在的文件夹 {cpath}")
                elif target.name and target.name != cname:
                    errors.append(f"{m.path}：子模块指针中的命名 {cname!r} 与 {cpath} 的 H1 命名 {target.name!r} 不一致")
            else:
                if not (root / cpath).is_file():
                    errors.append(f"{m.path}：单文件子模块指向不存在的文件 {cpath}")
        # 反向：磁盘上的子文件夹模块必须已登记
        for opath in modules:
            if opath == "project/" or opath == m.path:
                continue
            parent = opath.rstrip("/").rsplit("/", 1)[0] + "/"
            if parent == m.path and opath not in {c[0] for c in m.children}:
                errors.append(f"{m.path}：文件夹模块 {opath} 未在子模块指针中登记")
    # 父模块指针
    for m in modules.values():
        if m.path == "project/":
            if m.declared_parent is not None:
                errors.append("project/：根模块不应声明父模块")
            continue
        actual_parent = m.path.rstrip("/").rsplit("/", 1)[0] + "/"
        if m.declared_parent is None:
            errors.append(f"{m.path}：缺少父模块指针（应为 `- 父模块：`路径``）")
        elif m.declared_parent != actual_parent:
            errors.append(f"{m.path}：父模块指针声明为 {m.declared_parent}，实际应为 {actual_parent}")
    return errors


def check_declared_paths(modules):
    errors = []
    for m in modules.values():
        if m.declared_path is not None and m.declared_path != m.path:
            errors.append(f"{m.path}：模块简介中声明的路径为 {m.declared_path}，与实际位置不一致")
    return errors


def check_graphs(modules):
    """依赖边引用已登记子模块、图无环；边界成员为已登记子模块。"""
    errors = []
    for m in modules.values():
        names = {cname for _, cname, _ in m.children}
        for x, y in m.edges:
            for node in (x, y):
                if node not in names:
                    errors.append(f"{m.path}：内部关系图中的 {node!r} 不是已登记的子模块")
        # 无环检查（三色标记 DFS）
        color = {}
        adj = {}
        for x, y in m.edges:
            adj.setdefault(x, []).append(y)

        def visit(u, stack):
            color[u] = 1
            for v in adj.get(u, []):
                if color.get(v) == 1:
                    errors.append(f"{m.path}：依赖关系有环：{' --> '.join(stack + [v])}")
                    return
                if color.get(v) is None:
                    visit(v, stack + [v])
            color[u] = 2

        for x, _ in m.edges:
            if color.get(x) is None:
                visit(x, [x])
        # 边界成员
        for member, _, _ in m.boundary:
            if member not in names:
                errors.append(f"{m.path}：边界关系中的成员 {member!r} 不是已登记的子模块")
    return errors


def check_derived_aligned(root, modules):
    errors = []
    root_doc = root / "project" / "ALLOY.md"
    if not root_doc.is_file():
        return []  # 缺失问题已由 discover_modules 报告
    text = root_doc.read_text(encoding="utf-8")
    cut = split_at_derived(text)
    if cut is None:
        return [f"project/ALLOY.md：未找到派生区标记线（--- 加一行固定注释 {MARKER}）"]
    marker_pos = text.find(MARKER)
    current = text[marker_pos:].rstrip("\n")
    expected_full = generate_derived(modules)
    expected = expected_full[expected_full.find(MARKER):].rstrip("\n")
    if current != expected:
        errors.append("project/ALLOY.md：派生区与各局部合金文档不对齐，请运行 align.py")
    return errors


def check_instance_skeleton(root):
    errors = []
    ab03 = root / "紫金产物" / "肋骨产物" / "AB03-项目最新状态"
    for name in ("脊椎流程进展.md", "肋骨规范进展.md", "外骨骼实现情况.md"):
        if not (ab03 / name).is_file():
            errors.append(f"实例骨架：紫金产物/肋骨产物/AB03-项目最新状态/{name} 未就位")
    if not (root / "紫金产物" / "紫金规范反馈.md").is_file():
        errors.append("实例骨架：紫金产物/紫金规范反馈.md 未就位")
    if not (root / "purplegold" / "VERSION").is_file():
        errors.append("实例骨架：purplegold/VERSION 未就位")
    return errors


def cmd_validate(root):
    modules, errors = discover_modules(root)
    for m in modules.values():
        errors.extend(m.errors)
    if "project/" in modules:
        errors += check_names_unique(modules)
        errors += check_pointers(root, modules)
        errors += check_declared_paths(modules)
        errors += check_graphs(modules)
        errors += check_derived_aligned(root, modules)
    errors += check_instance_skeleton(root)

    if errors:
        print(f"校验未通过，共 {len(errors)} 个问题：")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"校验通过：{len(modules)} 个文件夹模块；AB03 三份状态文档、紫金规范反馈.md 与 VERSION 就位。")
    return 0


def main(argv):
    root = Path(argv[1]).resolve() if len(argv) > 1 else default_root()
    return cmd_validate(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
