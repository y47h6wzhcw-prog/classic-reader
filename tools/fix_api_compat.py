"""把 Dart 代码里较新的 Flutter API 替换为 Flutter 3.24 兼容写法。

- Color.withValues(alpha: X)      -> Color.withOpacity(X)   （withValues 需 3.27+）
- colorScheme.surfaceContainerHighest -> colorScheme.surfaceVariant（需 3.22+）
"""
import glob
import re

changed = 0
for f in glob.glob("lib/**/*.dart", recursive=True):
    src = open(f, encoding="utf-8").read()
    out = src
    out = re.sub(r"\.withValues\(alpha:\s*([^)]+)\)", r".withOpacity(\1)", out)
    out = out.replace("surfaceContainerHighest", "surfaceVariant")
    if out != src:
        open(f, "w", encoding="utf-8").write(out)
        changed += 1
        print("updated", f)
print(f"done, {changed} files changed")
