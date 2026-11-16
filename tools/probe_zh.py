"""从官方中文书目中筛出文学经典，验证标题与体量后生成最终书单。"""
import re
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from fetch_books import make_opener  # noqa: E402

# 依据 gutenberg.org/browse/languages/zh 官方中文书目筛选：
# 选文学/史传/诗词类经典，避开纯科技、数学、方言教材
CANDIDATES = [
    # ---- 中国古典四大名著 ----
    (23863, "水浒传", "Water Margin"),
    (23950, "三国演义", "Romance of the Three Kingdoms"),
    (23962, "西游记", "Journey to the West"),
    (24264, "红楼梦", "Dream of the Red Chamber"),
    # ---- 其他古典小说 ----
    (24032, "儒林外史", "The Scholars"),
    (51828, "聊斋志异", "Strange Tales from a Chinese Studio"),
    (25124, "老残游记", "Lao Can You Ji"),
    (23818, "镜花缘", "Flowers of Mirror"),
    (25192, "浮生六记", "Six Records of a Floating Life"),
    (24047, "世说新语", "A New Account of the Tales of the World"),
    (24230, "今古奇观", "Strange Stories"),
    (25352, "长恨歌", "Song of Everlasting Sorrow"),
    (24051, "李娃传", "The Tale of Li Wa"),
    (24041, "洛神赋", "Rhapsody on the Luo River Goddess"),
    (23915, "虬髯客传", "Story of the Curly-Bearded Stranger"),
    (25225, "古文观止", "A Selection of Classical Prose"),
    (23906, "西厢记", "The West Chamber"),
    (23849, "牡丹亭", "The Peony Pavilion"),
    (25246, "琵琶记", "The Story of a Pipa"),
    (24234, "桃花扇", "Peach Blossom Fan"),
    (23906, "西厢记", "The West Chamber"),
    (27166, "呐喊", "Call to Arms"),
    (24042, "彷徨", "Wandering"),
    (25271, "朝花夕拾", "Dawn Blossoms Plucked at Dusk"),
    (25423, "狂人日记", "Diary of a Madman"),
    (25242, "野草", "Wild Grass"),
    (25332, "阿Q正传", "The True Story of Ah Q"),
    (24138, "官场现形记", "The Bureaucracy Exposed"),
    (25327, "儿女英雄传", "A Tale of Heroic Children"),
    (25376, "三侠五义", "The Seven Heroes and Five Gallants"),
    (24099, "二十年目睹之怪现状", "Strange Cases in Twenty Years"),
    (26970, "彭公案", "The Cases of Magistrate Peng"),
    (27686, "狄公案", "Cases of Di Renjie"),
    (23835, "隋唐演义", "Stories of Sui and Tang"),
    (23910, "封神演义", "Investiture of the Gods"),
    (23824, "说唐", "Stories of the Tang"),
    (25376, "三侠五义", "The Seven Heroes and Five Gallants"),
    (24226, "史记", "Records of the Grand Historian"),
    (24049, "韩非子", "Han Feizi"),
    (24039, "老子", "Laozi"),
    (7337, "道德经", "Tao Te Ching"),
    (23839, "论语", "Analects of Confucius"),
    (24178, "孟子", "Mencius"),
    (24049, "韩非子", "Han Feizi"),
    (25288, "山海经", "Classic of Mountains and Seas"),
    (23873, "诗经", "Book of Songs"),
    (25501, "易经", "Book of Changes"),
    (12479, "三字经", "Three Character Classic"),
    (25196, "百家姓", "Hundred Family Surnames"),
    (24050, "菜根谭", "Roots of Wisdom"),
    (24058, "穆天子传", "Biography of King Mu"),
    # ---- 诗词文集 ----
    (52323, "唐诗三百首", "Three Hundred Tang Poems"),
    (24169, "李太白集", "Poems of Li Bai"),
    (25247, "李义山诗集", "Poems of Li Shangyin"),
    (25367, "漱玉词", "Shuyu Ci"),
    (25194, "饮水词集", "Yinshui Ci"),
    (25218, "六一词", "Liuyi Ci"),
    (25397, "论衡", "Lunheng"),
    (24112, "人间词话", "Remarks on Poetry"),
    (25289, "沧浪诗话", "Canglang Shihua"),
    (23822, "文心雕龙", "Wenxin Diaolong"),
    (25380, "闲情偶寄", "Idle Thoughts"),
    (25471, "闲情偶寄", "Idle Thoughts"),
    (27122, "老学庵笔记", "Laoxue'an Biji"),
    (27292, "梦溪笔谈", "Dream Pool Essays"),
    (24052, "玉壶清话", "Yuhu Qinghua"),
    (25558, "呻吟语", "Shengyin Yu"),
    (25262, "日知录", "Rizhi Lu"),
    (24048, "礼记", "Book of Rites"),
    (25696, "抱朴子", "Baopuzi"),
    (25368, "西京杂记", "Miscellaneous Records of the Capital"),
    (25362, "搜神记", "In Search of the Supernatural"),
    (7266, "搜神后记", "More Records of the Supernatural"),
    (24004, "窦娥冤", "Injustice to Dou E"),
    (7415, "牡丹亭", "Peony Pavilion"),
]


def probe(op, bid):
    url = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
    try:
        r = op.open(url, timeout=30)
        d = r.read(4000).decode("utf-8", "replace")
        r.close()
    except Exception as e:
        return None
    first = d.split("\n", 1)[0]
    m = re.match(r"The Project Gutenberg eBook of (.+?)\r?$", first)
    title = m.group(1).strip() if m else first.strip()[:70]
    mm = re.search(r"^Language:\s*(.+?)\r?$", d, re.M)
    lang = mm.group(1).strip() if mm else ""
    cjk = len(re.findall(r"[\u4e00-\u9fff]", d))
    return {"id": bid, "title": title, "lang": lang, "cjk": cjk}


def main():
    op = make_opener()
    ok, bad = [], []
    for bid, zh, en in CANDIDATES:
        if any(b["id"] == bid for b in ok):
            continue
        info = probe(op, bid)
        if not info:
            bad.append(bid)
            continue
        if info["cjk"] < 50:
            bad.append(bid)
            print(f"MISMATCH {bid}: cjk={info['cjk']} title={info['title'][:40]}")
            continue
        info["zh"] = zh
        info["en"] = en
        ok.append(info)
        print(f"{bid}\t{info['title'][:40]:40s}\t{info['lang'][:8]:8s}\t=> {zh}")
    print(f"\n# VALID {len(ok)} / BAD {len(bad)}: {bad}")
    print("ZH_BOOKS = " + repr([(b["id"], b["zh"], b["en"]) for b in ok]))


if __name__ == "__main__":
    main()
