"""生成书单文档（BOOKLIST.md）。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(os.path.dirname(HERE), "assets", "books")
OUT = os.path.join(os.path.dirname(HERE), "BOOKLIST.md")

m = json.load(open(os.path.join(BOOKS_DIR, "manifest.json"), encoding="utf-8"))
zh = [b for b in m if b["lang"] == "zh"]
en = [b for b in m if b["lang"] == "en"]

lines = []
lines.append("# 完整书单\n")
lines.append(f"共 **{len(m)} 本**，{sum(b['chars'] for b in m):,} 字符（约 {sum(b['chars'] for b in m)/10000:.0f} 万字）。\n")
lines.append("全部来自 [Project Gutenberg](https://www.gutenberg.org) 公有领域作品。")
lines.append("外国名著一律使用英文原文，不做翻译。\n")

lines.append(f"## 中文典籍（{len(zh)} 本）\n")
lines.append("| 书名 | 作者 | 字数 |")
lines.append("|---|---|---|")
for b in zh:
    lines.append(f"| {b['title']} | {b['author']} | {b['chars']:,} |")

lines.append("")
lines.append(f"## 英文原著（{len(en)} 本）\n")
lines.append("| Title | Author | Chars |")
lines.append("|---|---|---|")
for b in en:
    lines.append(f"| {b['title']} | {b['author']} | {b['chars']:,} |")

lines.append("")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"wrote {OUT}: {len(zh)} zh + {len(en)} en")
