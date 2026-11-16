"""探测 Gutenberg 候选 ID 的真实标题/作者/语种，避免下载到错书。"""
import re
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from fetch_books import make_opener  # noqa: E402

CANDIDATES = [
    # 中文候选
    23962, 23950, 23957, 25328, 25438, 27228, 25330, 25851, 24018, 24196,
    25237, 25234, 25524, 25437, 24880, 24160, 24195, 24197, 24198, 24199,
    24200, 24201, 24202, 24203, 25238, 25239, 25240, 25241, 25438, 25439,
    25440, 25441, 25442, 25329, 25331, 25332, 25333, 25525, 25526, 24881,
    24882, 24161, 24162, 24163, 24164, 24165, 24166, 27229, 27230, 27231,
    27232, 27233, 25852, 25853, 24019, 24020, 24021, 25242, 25243, 25244,
    # 英文候选
    1342, 11, 74, 76, 1661, 2097, 1250, 2701, 43, 421, 98, 730, 1400, 46,
    1232, 1230, 19033, 164, 37106, 1998, 10, 1322, 155, 244, 2852, 1564,
    146, 289, 215, 910, 1080, 514, 45, 203, 1533, 1267, 103, 863, 233,
    1260, 861, 1727, 1727, 219, 1023, 1460, 996, 2600, 120, 1023, 766,
    16328, 2814, 4363, 199, 2264, 345, 174, 5200, 1200, 219, 2680, 2814,
]


def probe(op, bid):
    url = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
    try:
        r = op.open(url, timeout=30)
        d = r.read(4000).decode("utf-8", "replace")
        r.close()
    except Exception as e:
        return None, type(e).__name__

    first = d.split("\n", 1)[0]
    m = re.match(r"The Project Gutenberg eBook of (.+?)\r?$", first)
    title = m.group(1).strip() if m else first.strip()[:60]

    def field(name):
        mm = re.search(rf"^{name}:\s*(.+?)\r?$", d, re.M)
        return mm.group(1).strip() if mm else ""

    lang = field("Language") or field("Language: ")
    author = field("Author")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", d))
    return {
        "id": bid,
        "title": title,
        "author": author[:40],
        "lang": lang,
        "cjk": cjk,
    }, None


def main():
    op = make_opener()
    zh, en = [], []
    for bid in sorted(set(CANDIDATES)):
        info, err = probe(op, bid)
        if err:
            print(f"{bid}\tERR {err}")
            continue
        tag = "ZH" if info["cjk"] > 50 else "EN"
        print(f"{bid}\t{tag}\t{info['lang'][:12]:12s}\t{info['title'][:52]:52s}\t{info['author'][:28]}")
        (zh if tag == "ZH" else en).append(info)

    print(f"\n# 中文候选 {len(zh)} 本：")
    print("ZH_IDS = [" + ", ".join(str(b["id"]) for b in zh) + "]")
    print(f"\n# 英文候选 {len(en)} 本")
    print("EN_IDS = [" + ", ".join(str(b["id"]) for b in en) + "]")


if __name__ == "__main__":
    main()
