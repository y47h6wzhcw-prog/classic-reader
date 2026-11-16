"""用 GitHub API 创建公开仓库（classic-reader）。

用法：
    python create_repo.py <github用户名> <token>

Token 生成：https://github.com/settings/tokens → Generate new token (classic)
→ 勾选 public_repo 权限。

说明：
- api.github.com 直连可用（实测），无需浏览器
- github.com 网页端在本机网络下会被代理拦截，所以走 API 建仓库
"""
import json
import os
import ssl
import sys
import urllib.request

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
REPO_NAME = "classic-reader"
DESCRIPTION = "经典书房 - 离线公版名著阅读器（中文 70 本 + 英文 55 本）"


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


def api(opener, method, url, token, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "classic-reader-setup")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        r = opener.open(req, timeout=30)
        d = r.read()
        r.close()
        return r.status, json.loads(d) if d else None
    except urllib.error.HTTPError as e:
        d = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(d)
        except Exception:
            return e.code, d[:400]


def main():
    if len(sys.argv) < 3:
        print("用法: python create_repo.py <github用户名> <token>")
        sys.exit(1)
    user, token = sys.argv[1], sys.argv[2].strip()
    opener = make_opener()

    # 1. 验证 token
    st, data = api(opener, "GET", "https://api.github.com/user", token)
    if st != 200:
        print(f"Token 验证失败 HTTP {st}: {data}")
        sys.exit(1)
    print(f"Token 有效，身份: {data['login']}")

    # 2. 检查仓库是否已存在
    st, data = api(opener, "GET", f"https://api.github.com/repos/{user}/{REPO_NAME}", token)
    if st == 200:
        print(f"仓库已存在: {data['full_name']} (private={data['private']})")
        if data["private"]:
            print("提示：当前是私有仓库，Actions 免费额度会按 10 倍扣 macOS 分钟。")
        print(f"\n推送命令：")
        print(f"  cd reader_app && git push -u origin main")
        return
    if st != 404:
        print(f"查询仓库失败 HTTP {st}: {data}")
        sys.exit(1)

    # 3. 创建公开仓库
    st, data = api(opener, "POST", "https://api.github.com/user/repos", token, {
        "name": REPO_NAME,
        "description": DESCRIPTION,
        "private": False,
        "auto_init": False,
        "has_issues": True,
        "has_wiki": False,
    })
    if st not in (200, 201):
        print(f"创建失败 HTTP {st}: {data}")
        sys.exit(1)

    print(f"创建成功: {data['full_name']}")
    print(f"  地址: {data['html_url']}")
    print(f"  可见性: {'private' if data['private'] else 'public'}")
    print(f"\n下一步:")
    print(f"  cd reader_app")
    print(f"  git remote set-url origin https://github.com/{user}/{REPO_NAME}.git")
    print(f"  git push -u origin main")


if __name__ == "__main__":
    main()
