"""把书稿文件名改为纯 ASCII，避免跨平台（尤其 macOS/Linux runner）的中文文件名问题。

manifest.json 里的 file 字段同步更新，保证引用一致。
"""
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(os.path.dirname(HERE), "assets", "books")
MANIFEST = os.path.join(BOOKS_DIR, "manifest.json")

# 常见中文名 → 英文/拼音简写，避免过度依赖转写库
TITLE_MAP = {
    "水浒传": "shuihu_zhuan", "三国演义": "sanguo_yanyi", "西游记": "xiyou_ji",
    "红楼梦": "hongloumeng", "儒林外史": "rulin_waishi", "聊斋志异": "liaozhai_zhiyi",
    "老残游记": "laocan_youji", "镜花缘": "jinghuayuan", "浮生六记": "fusheng_liuji",
    "世说新语": "shishuo_xinyu", "今古奇观": "jingu_qiguan", "长恨歌": "changhenge",
    "李娃传": "liwa_zhuan", "洛神赋": "luoshenfu", "虬髯客传": "qiuranke_zhuan",
    "古文观止": "guwen_guanzhi", "西厢记": "xixiangji", "牡丹亭": "mudanting",
    "琵琶记": "pipaji", "桃花扇": "taohuashan", "呐喊": "nahan", "彷徨": "panghuang",
    "朝花夕拾": "chaohua_xishi", "狂人日记": "kuangren_riji", "野草": "yecao",
    "阿q正传": "ahq_zhengzhuan", "官场现形记": "guanchang_xianxingji",
    "儿女英雄传": "ernv_yingxiongzhuan", "三侠五义": "sanxia_wuyi",
    "二十年目睹之怪现状": "ershinianmu_guai_xianzhuang", "彭公案": "penggongan",
    "狄公案": "digongan", "隋唐演义": "suitang_yanyi", "封神演义": "fengshen_yanyi",
    "说唐": "shuotang", "史记": "shiji", "韩非子": "hanfeizi", "老子": "laozi",
    "道德经": "daodejing", "论语": "lunyu", "孟子": "mengzi", "山海经": "shanhaijing",
    "诗经": "shijing", "易经": "yijing", "三字经": "sanzijing", "百家姓": "baijiaxing",
    "菜根谭": "caigentan", "穆天子传": "mutianzi_zhuan", "唐诗三百首": "tangshi_sanbaishou",
    "李太白集": "litaibai_ji", "李义山诗集": "liyishan_shiji", "漱玉词": "shuyu_ci",
    "饮水词集": "yinshui_ci", "六一词": "liuyi_ci", "论衡": "lunheng",
    "人间词话": "renjian_cihua", "沧浪诗话": "canglang_shihua", "文心雕龙": "wenxin_diaolong",
    "闲情偶寄": "xianqing_ouji", "老学庵笔记": "laoxuean_biji", "梦溪笔谈": "mengxi_bitan",
    "玉壶清话": "yuhu_qinghua", "呻吟语": "shenyin_yu", "日知录": "rizhi_lu",
    "礼记": "liji", "抱朴子": "baopuzi", "西京杂记": "xijing_zaoji", "搜神记": "soushenji",
    "搜神后记": "soushen_houji", "窦娥冤": "doueyuan",
}


def ascii_slug(title: str) -> str:
    """中文书名走映射表；英文名走通用 slug 化。"""
    if title in TITLE_MAP:
        return TITLE_MAP[title]
    # 英文标题：小写、非字母数字转下划线
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return slug[:40] or "book"


def main():
    m = json.load(open(MANIFEST, encoding="utf-8"))
    renamed = 0
    for b in m:
        old = b["file"]
        # 只处理文件名里含非 ASCII 的
        if all(ord(c) < 128 for c in old):
            continue
        base = old[:-4]  # 去掉 .txt
        prefix = f"{b['lang']}_{b['id']}_"
        assert base.startswith(prefix), f"unexpected name: {old}"
        tail = base[len(prefix):]
        # 英文书尾��本身已是 ASCII，只有中文名需要映射
        new_tail = ascii_slug(tail)
        new = f"{prefix}{new_tail}.txt"
        src = os.path.join(BOOKS_DIR, old)
        dst = os.path.join(BOOKS_DIR, new)
        if os.path.exists(src):
            if os.path.exists(dst):
                os.remove(src)
            else:
                os.rename(src, dst)
            b["file"] = new
            renamed += 1

    json.dump(m, open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"renamed {renamed} files")

    # 校验
    bad = [b["file"] for b in m if not os.path.exists(os.path.join(BOOKS_DIR, b["file"]))]
    nonascii = [b["file"] for b in m if not all(ord(c) < 128 for c in b["file"])]
    print("missing:", bad or "none")
    print("still non-ascii:", nonascii or "none")


if __name__ == "__main__":
    main()
