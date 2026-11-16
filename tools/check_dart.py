"""对 Dart 源码做静态一致性检查（无 Flutter SDK 时的替代方案）。"""
import glob
import os
import re
import sys

errors = []
ROOT = os.getcwd()


def dart_files():
    return sorted(glob.glob("lib/**/*.dart", recursive=True)) + sorted(glob.glob("test/*.dart"))


# 1. 括号平衡
for f in dart_files():
    src = open(f, encoding="utf-8").read()
    for o, c in [("(", ")"), ("[", "]"), ("{", "}")]:
        if src.count(o) != src.count(c):
            errors.append(f"{f}: {o}{c} 不平衡 ({src.count(o)}/{src.count(c)})")

# 2. 相对 import 路径存在性
for f in dart_files():
    src = open(f, encoding="utf-8").read()
    base = os.path.dirname(f)
    for line in src.splitlines():
        m = re.match(r"\s*import\s+'([^']+)'", line)
        if not m:
            continue
        path = m.group(1)
        if path.startswith("package:") or path.startswith("dart:"):
            continue
        target = os.path.normpath(os.path.join(base, path))
        if not os.path.exists(target):
            errors.append(f"{f}: import 路径不存在 -> {path}")

# 3. 构造器调用完整性（跨括号配平提取参数）
def extract_calls(src, name):
    out = []
    for m in re.finditer(rf"\b{name}\(", src):
        i = m.end()
        depth = 1
        while i < len(src) and depth > 0:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        out.append(src[m.end():i - 1])
    return out


for f in dart_files():
    src = open(f, encoding="utf-8").read()
    for cls in ("ReaderPage", "ShelfPage"):
        for body in extract_calls(src, cls):
            if "onPrefsChanged" not in body:
                errors.append(f"{f}: {cls}(...) 未传 onPrefsChanged")

# 4. 已废弃 API 残留
for f in dart_files():
    src = open(f, encoding="utf-8").read()
    for bad in ("_estimateOffset", ".withValues(", "surfaceContainerHighest"):
        if bad in src:
            errors.append(f"{f}: 残留不兼容/废弃 API -> {bad}")

# 5. TabBar / TabController 配对
for f in dart_files():
    src = open(f, encoding="utf-8").read()
    if "TabBar(" in src:
        for body in extract_calls(src, "TabBar"):
            if "controller:" not in body:
                errors.append(f"{f}: TabBar 未指定 controller")
            if "onTap:" in body:
                errors.append(f"{f}: TabBar 同时用了 onTap 与 controller")
    if "_tabController" in src and "TabController(" not in src:
        errors.append(f"{f}: 使用 _tabController 但未创建")

# 6. dispose 中释放 controller
for f in dart_files():
    src = open(f, encoding="utf-8").read()
    if "_tabController" in src and "_tabController.dispose()" not in src:
        errors.append(f"{f}: _tabController 未 dispose")

if errors:
    print("发现问题：")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("静态检查通过，无问题")
