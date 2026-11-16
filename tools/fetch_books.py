"""下载 Project Gutenberg 公版书（中文 71 本 + 英文 48 本）到 assets/books。

网络说明：本机出网经 HTTP 代理，长响应会在约 128KB 处被截断，
故统一用 Range 分块请求 + 断点续传。
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.request

PROXY = "http://127.0.0.1:2327"
CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "assets", "books")
CHUNK = 100_000
MAX_RETRY = 5

# ---------------------------------------------------------------- 中文
ZH_BOOKS = [
    (23863, "水浒传", "Water Margin", "施耐庵"),
    (23950, "三国演义", "Romance of the Three Kingdoms", "罗贯中"),
    (23962, "西游记", "Journey to the West", "吴承恩"),
    (24264, "红楼梦", "Dream of the Red Chamber", "曹雪芹"),
    (24032, "儒林外史", "The Scholars", "吴敬梓"),
    (51828, "聊斋志异", "Strange Tales from a Chinese Studio", "蒲松龄"),
    (25124, "老残游记", "The Travels of Lao Can", "刘鹗"),
    (23818, "镜花缘", "Flowers in the Mirror", "李汝珍"),
    (25192, "浮生六记", "Six Records of a Floating Life", "沈复"),
    (24047, "世说新语", "A New Account of the Tales of the World", "刘义庆"),
    (24230, "今古奇观", "Marvellous Stories Now and Then", "抱瓮老人"),
    (25352, "长恨歌", "Song of Everlasting Sorrow", "白居易"),
    (24051, "李娃传", "The Tale of Li Wa", "白行简"),
    (24041, "洛神赋", "Rhapsody on the Luo River Goddess", "曹植"),
    (23915, "虬髯客传", "The Curly-Bearded Stranger", "杜光庭"),
    (25225, "古文观止", "A Selection of Classical Prose", "吴楚材"),
    (23906, "西厢记", "The West Chamber", "王实甫"),
    (23849, "牡丹亭", "The Peony Pavilion", "汤显祖"),
    (25246, "琵琶记", "The Story of a Pipa", "高明"),
    (24234, "桃花扇", "Peach Blossom Fan", "孔尚任"),
    (27166, "呐喊", "Call to Arms", "鲁迅"),
    (24042, "彷徨", "Wandering", "鲁迅"),
    (25271, "朝花夕拾", "Dawn Blossoms Plucked at Dusk", "鲁迅"),
    (25423, "狂人日记", "Diary of a Madman", "鲁迅"),
    (25242, "野草", "Wild Grass", "鲁迅"),
    (25332, "阿Q正传", "The True Story of Ah Q", "鲁迅"),
    (24138, "官场现形记", "The Bureaucracy Exposed", "李宝嘉"),
    (25327, "儿女英雄传", "A Tale of Heroic Children", "文康"),
    (25376, "三侠五义", "The Seven Heroes and Five Gallants", "石玉昆"),
    (24099, "二十年目睹之怪现状", "Strange Cases in Twenty Years", "吴趼人"),
    (26970, "彭公案", "The Cases of Magistrate Peng", "行素"),
    (27686, "狄公案", "Cases of Judge Dee", "作者不详"),
    (23835, "隋唐演义", "Stories of the Sui and Tang Dynasties", "褚人获"),
    (23910, "封神演义", "Investiture of the Gods", "许仲琳"),
    (23824, "说唐", "Stories of the Tang", "陈寿"),
    (24226, "史记", "Records of the Grand Historian", "司马迁"),
    (24049, "韩非子", "Han Feizi", "韩非"),
    (24039, "老子", "Laozi", "老子"),
    (7337, "道德经", "Tao Te Ching", "老子"),
    (23839, "论语", "Analects of Confucius", "孔子弟子"),
    (24178, "孟子", "Mencius", "孟子"),
    (25288, "山海经", "Classic of Mountains and Seas", "佚名"),
    (23873, "诗经", "The Book of Songs", "佚名"),
    (25501, "易经", "The Book of Changes", "佚名"),
    (12479, "三字经", "Three Character Classic", "王应麟"),
    (25196, "百家姓", "Hundred Family Surnames", "佚名"),
    (24050, "菜根谭", "Roots of Wisdom", "洪应明"),
    (24058, "穆天子传", "The Biography of King Mu", "佚名"),
    (52323, "唐诗三百首", "Three Hundred Tang Poems", "蘅塘退士 编"),
    (24169, "李太白集", "Poems of Li Bai", "李白"),
    (25247, "李义山诗集", "Poems of Li Shangyin", "李商隐"),
    (25367, "漱玉词", "Shuyu Ci", "李清照"),
    (25194, "饮水词集", "Yinshui Ci", "纳兰性德"),
    (25218, "六一词", "Liuyi Ci", "欧阳修"),
    (25397, "论衡", "Discourses on the Balance of Discourses", "王充"),
    (24112, "人间词话", "Remarks on Poetry", "王国维"),
    (25289, "沧浪诗话", "Canglang Shihua", "严羽"),
    (23822, "文心雕龙", "Wenxin Diaolong", "刘勰"),
    (25380, "闲情偶寄", "Idle Thoughts", "李渔"),
    (27122, "老学庵笔记", "Laoxue'an Biji", "陆游"),
    (27292, "梦溪笔谈", "Dream Pool Essays", "沈括"),
    (24052, "玉壶清话", "Yuhu Qinghua", "陶谷"),
    (25558, "呻吟语", "Shengyin Yu", "吕坤"),
    (25262, "日知录", "Rizhi Lu", "顾炎武"),
    (24048, "礼记", "The Book of Rites", "戴圣"),
    (25696, "抱朴子", "Baopuzi", "葛洪"),
    (25368, "西京杂记", "Miscellaneous Records of the Western Capital", "葛洪"),
    (25362, "搜神记", "In Search of the Supernatural", "干宝"),
    (7266, "搜神后记", "More Records of the Supernatural", "陶渊明"),
    (24004, "窦娥冤", "Injustice to Dou E", "关汉卿"),
]

# ---------------------------------------------------------------- 英文
EN_BOOKS = [
    (1342, "Pride and Prejudice", "Pride and Prejudice", "Jane Austen"),
    (11, "Alice's Adventures in Wonderland", "Alice in Wonderland", "Lewis Carroll"),
    (74, "The Adventures of Tom Sawyer", "Tom Sawyer", "Mark Twain"),
    (76, "Adventures of Huckleberry Finn", "Huckleberry Finn", "Mark Twain"),
    (1661, "The Adventures of Sherlock Holmes", "Sherlock Holmes", "Arthur Conan Doyle"),
    (244, "A Study in Scarlet", "A Study in Scarlet", "Arthur Conan Doyle"),
    (2852, "The Hound of the Baskervilles", "The Hound of the Baskervilles", "Arthur Conan Doyle"),
    (2097, "The Sign of the Four", "The Sign of the Four", "Arthur Conan Doyle"),
    (1260, "Jane Eyre", "Jane Eyre", "Charlotte Brontë"),
    (768, "Wuthering Heights", "Wuthering Heights", "Emily Brontë"),
    (2701, "Moby Dick", "Moby Dick", "Herman Melville"),
    (43, "Dr. Jekyll and Mr. Hyde", "Dr. Jekyll and Mr. Hyde", "R.L. Stevenson"),
    (120, "Treasure Island", "Treasure Island", "R.L. Stevenson"),
    (421, "Kidnapped", "Kidnapped", "R.L. Stevenson"),
    (98, "A Tale of Two Cities", "A Tale of Two Cities", "Charles Dickens"),
    (730, "Oliver Twist", "Oliver Twist", "Charles Dickens"),
    (1400, "Great Expectations", "Great Expectations", "Charles Dickens"),
    (1023, "Bleak House", "Bleak House", "Charles Dickens"),
    (766, "David Copperfield", "David Copperfield", "Charles Dickens"),
    (46, "A Christmas Carol", "A Christmas Carol", "Charles Dickens"),
    (55, "The Wonderful Wizard of Oz", "The Wonderful Wizard of Oz", "L. Frank Baum"),
    (1080, "A Modest Proposal", "A Modest Proposal", "Jonathan Swift"),
    (1200, "Gargantua and Pantagruel", "Gargantua and Pantagruel", "François Rabelais"),
    (1232, "The Prince", "The Prince", "Niccolò Machiavelli"),
    (996, "Don Quixote", "Don Quixote", "Miguel de Cervantes"),
    (10, "The King James Version of the Bible", "The Bible (King James Version)", "Various"),
    (1727, "The Odyssey", "The Odyssey", "Homer"),
    (1533, "Macbeth", "Macbeth", "William Shakespeare"),
    (203, "Uncle Tom's Cabin", "Uncle Tom's Cabin", "Harriet Beecher Stowe"),
    (45, "Anne of Green Gables", "Anne of Green Gables", "L.M. Montgomery"),
    (146, "A Little Princess", "A Little Princess", "Frances Hodgson Burnett"),
    (243, "The Secret Garden", "The Secret Garden", "Frances Hodgson Burnett"),
    (289, "The Wind in the Willows", "The Wind in the Willows", "Kenneth Grahame"),
    (215, "The Call of the Wild", "The Call of the Wild", "Jack London"),
    (910, "White Fang", "White Fang", "Jack London"),
    (219, "Heart of Darkness", "Heart of Darkness", "Joseph Conrad"),
    (2814, "Dubliners", "Dubliners", "James Joyce"),
    (174, "The Picture of Dorian Gray", "The Picture of Dorian Gray", "Oscar Wilde"),
    (5200, "Metamorphosis", "Metamorphosis", "Franz Kafka"),
    (84, "Frankenstein", "Frankenstein", "Mary Shelley"),
    (345, "Dracula", "Dracula", "Bram Stoker"),
    (1998, "Thus Spake Zarathustra", "Thus Spake Zarathustra", "Friedrich Nietzsche"),
    (4363, "Beyond Good and Evil", "Beyond Good and Evil", "Friedrich Nietzsche"),
    (2680, "Meditations", "Meditations", "Marcus Aurelius"),
    (155, "The Moonstone", "The Moonstone", "Wilkie Collins"),
    (514, "Little Women", "Little Women", "Louisa May Alcott"),
    (2600, "War and Peace", "War and Peace", "Leo Tolstoy"),
    (16328, "Beowulf", "Beowulf", "Anonymous"),
    (1322, "Leaves of Grass", "Leaves of Grass", "Walt Whitman"),
    (35, "The Time Machine", "The Time Machine", "H.G. Wells"),
    (36, "The War of the Worlds", "The War of the Worlds", "H.G. Wells"),
    (1257, "The Three Musketeers", "The Three Musketeers", "Alexandre Dumas"),
    (1184, "The Count of Monte Cristo", "The Count of Monte Cristo", "Alexandre Dumas"),
    (135, "Les Misérables", "Les Misérables", "Victor Hugo"),
    (2147, "The Works of Edgar Allan Poe", "The Works of Edgar Allan Poe", "Edgar Allan Poe"),
]


def make_opener():
    ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}),
        urllib.request.HTTPSHandler(context=ctx),
    )


def download(opener, url, dest):
    """Range 分块下载，支持断点续传。"""
    for attempt in range(MAX_RETRY):
        try:
            have = os.path.getsize(dest) if os.path.exists(dest) else 0
            total = 0
            try:
                head = opener.open(urllib.request.Request(url, method="HEAD"), timeout=40)
                total = int(head.headers.get("Content-Length", 0))
                head.close()
            except Exception:
                pass
            if total and have >= total:
                return have
            if not have:
                open(dest, "wb").close()

            pos = have
            while True:
                if total and pos >= total:
                    break
                end = pos + CHUNK - 1 if not total else min(pos + CHUNK - 1, total - 1)
                req = urllib.request.Request(url)
                req.add_header("Range", f"bytes={pos}-{end}")
                data = opener.open(req, timeout=60).read()
                if not data:
                    break
                with open(dest, "ab") as f:
                    f.write(data)
                pos += len(data)
            return os.path.getsize(dest)
        except Exception as e:
            sys.stderr.write(f"    retry{attempt+1} {type(e).__name__} {str(e)[:70]}\n")
            time.sleep(1.2 * (attempt + 1))
    return 0


def strip_gutenberg(text):
    """去掉 PG 头尾声明，只留正文。"""
    s = text.find("*** START OF TH")
    if s != -1:
        s = text.find("\n", s) + 1
    e = text.find("*** END OF TH")
    if e != -1:
        e = text.rfind("\n", 0, e)
    if s != -1 and e != -1 and e > s:
        text = text[s:e]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def slugify(title):
    keep = []
    for ch in title.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " -_":
            keep.append("_")
    return re.sub(r"_+", "_", "".join(keep)).strip("_")[:40]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    opener = make_opener()
    manifest = []
    jobs = ([(b, "zh") for b in ZH_BOOKS]) + ([(b, "en") for b in EN_BOOKS])
    for (bid, title, title_alt, author), lang in jobs:
        slug = f"{lang}_{bid}_{slugify(title)}"
        dest = os.path.join(OUT_DIR, slug + ".txt")
        raw_dest = dest + ".raw"
        if not (os.path.exists(dest) and os.path.getsize(dest) > 2000):
            if not (os.path.exists(raw_dest) and os.path.getsize(raw_dest) > 2000):
                url = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
                print(f"GET  {slug}", flush=True)
                size = download(opener, url, raw_dest)
                if size < 3000:
                    print(f"  !! FAIL {slug}")
                    if os.path.exists(raw_dest):
                        os.remove(raw_dest)
                    continue
            with open(raw_dest, "r", encoding="utf-8", errors="replace") as f:
                body = strip_gutenberg(f.read())
            if len(body) < 2000:
                print(f"  !! SHORT {slug} ({len(body)})")
                continue
            with open(dest, "w", encoding="utf-8") as f:
                f.write(body)
            os.remove(raw_dest)
            print(f"  -> {len(body)} chars")
        else:
            print(f"SKIP {slug}")
        with open(dest, "r", encoding="utf-8", errors="replace") as f:
            n = len(f.read())
        manifest.append({
            "id": bid, "lang": lang, "file": slug + ".txt",
            "title": title, "titleAlt": title_alt, "author": author, "chars": n,
        })
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    zh = sum(1 for m in manifest if m["lang"] == "zh")
    en = len(manifest) - zh
    print(f"\nDONE: {zh} zh + {en} en = {len(manifest)} books")


if __name__ == "__main__":
    main()
