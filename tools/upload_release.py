"""把 IPA 上传为 GitHub Release 资产。

好处：iPhone 用 Safari 直接访问 Release 页面即可下载安装包，
不需要数据线、不需要网盘、不需要微信传文件。

用法：
    python upload_release.py <token> <ipa路径> [tag]
"""
import json
import os
import ssl
import sys
import urllib.request

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
REPO = "y47h6wzhcw-prog/classic-reader"


def make_opener():
    ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    proxy = os.environ.get("https_proxy")
    ph = {"http": proxy, "https": proxy} if proxy else {}
    return urllib.request.build_opener(
        urllib.request.ProxyHandler(ph),
        urllib.request.HTTPSHandler(context=ctx),
    )


def api(opener, token, method, url, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "classic-reader-setup")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        r = opener.open(req, timeout=60)
        d = r.read()
        r.close()
        return r.status, (json.loads(d) if d else None)
    except urllib.error.HTTPError as e:
        d = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(d)
        except Exception:
            return e.code, d[:400]


def main():
    token = sys.argv[1]
    ipa_path = sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else "v1.0.0"
    opener = make_opener()
    base = f"https://api.github.com/repos/{REPO}"

    name = os.path.basename(ipa_path)
    size = os.path.getsize(ipa_path)
    print(f"准备上传 {name} ({size/1048576:.1f} MB)")

    # 1. 确保 tag 存在
    st, ref = api(opener, token, "GET", f"{base}/git/ref/tags/{tag}")
    if st != 200:
        st, d = api(opener, token, "POST", f"{base}/git/refs",
                    {"ref": f"refs/tags/{tag}",
                     "sha": api(opener, token, "GET",
                                f"{base}/git/ref/heads/main")[1]["object"]["sha"]})
        print(f"创建 tag {tag}: HTTP {st}")

    # 2. 创建 release
    st, rel = api(opener, token, "POST", f"{base}/releases", {
        "tag_name": tag,
        "name": "经典书房 v1.0.0（离线公版名著阅读器）",
        "body": (
            "## 经典书房 · Classic Reader\n\n"
            "内置 **125 本公版名著**（中文 70 + 英文 55，约 5874 万字）的离线阅读器。\n"
            "纯本地运行，零网络请求，不含任何 SDK 或埋点。\n\n"
            "### 安装\n\n"
            "1. 在 iPhone 上用 **Safari** 打开本页\n"
            "2. 点击下方 `reader-1-unsigned.ipa` 下载\n"
            "3. 用支持 IPA 安装的工具签名安装（见仓库 README 的「侧载」章节）\n\n"
            "> 文件为 unsigned IPA，需自行签名后安装。\n"
        ),
        "draft": False,
        "prerelease": False,
    })
    if st not in (200, 201):
        print(f"创建 release 失败 HTTP {st}: {rel}")
        sys.exit(1)
    print(f"release 已创建: {rel['html_url']}")
    upload_url = rel["upload_url"].split("{")[0]
    asset_name = "reader-1-unsigned.ipa"

    # 3. 上传资产
    print("上传资产中（58MB，请稍候）...", flush=True)
    url = f"{upload_url}?name={asset_name}"
    req = urllib.request.Request(url, data=open(ipa_path, "rb").read(), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/octet-stream")
    req.add_header("User-Agent", "classic-reader-setup")
    try:
        r = opener.open(req, timeout=600)
        d = json.loads(r.read())
        r.close()
        print(f"上传成功: {d['browser_download_url']}")
        print(f"大小: {d['size']/1048576:.1f} MB")
    except urllib.error.HTTPError as e:
        print(f"上传失败 HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
