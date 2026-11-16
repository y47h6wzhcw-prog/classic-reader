"""用 GitHub Git Data API 提交本地改动（git 协议不可用时的备用方案）。

背景：本机 github.com 的 git smart-http 端点经常被代理拦截/重置，
但 api.github.com 始终可用。因此改用 API 直接构造 blob → tree → commit → ref。

用法：
    python api_commit.py <token> <文件路径> [<文件路径> ...]

说明：
  - 以远端 main 的当前 tree 为基准，把指定文件写入（新增或覆盖）
  - 未指定的文件保持不变
  - 若某文件在远端已存在，会先删除旧条目再写入新内容
"""
import base64
import json
import os
import ssl
import sys
import urllib.request

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
REPO = "y47h6wzhcw-prog/classic-reader"
BRANCH = "main"


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
        r = opener.open(req, timeout=45)
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
    if len(sys.argv) < 3:
        print("用法: python api_commit.py <token> <文件路径> [...]")
        sys.exit(1)
    token = sys.argv[1]
    files = sys.argv[2:]
    opener = make_opener()
    base = f"https://api.github.com/repos/{REPO}"

    st, ref = api(opener, token, "GET", f"{base}/git/ref/heads/{BRANCH}")
    if st != 200:
        print(f"取 ref 失败 HTTP {st}: {ref}")
        sys.exit(1)
    head_sha = ref["object"]["sha"]

    st, commit = api(opener, token, "GET", f"{base}/git/commits/{head_sha}")
    base_tree = commit["tree"]["sha"]

    # 构造 tree 条目
    entries = []
    for f in files:
        if not os.path.exists(f):
            print(f"跳过（不存在）: {f}")
            continue
        content = open(f, "rb").read()
        st, blob = api(opener, token, "POST", f"{base}/git/blobs",
                       {"content": base64.b64encode(content).decode(),
                        "encoding": "base64"})
        if st != 201:
            print(f"创建 blob 失败 HTTP {st}: {blob}")
            sys.exit(1)
        entries.append({
            "path": f.replace("\\", "/"),
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print(f"  blob: {f} -> {blob['sha'][:8]}")

    if not entries:
        print("没有可提交的文件")
        sys.exit(1)

    st, tree = api(opener, token, "POST", f"{base}/git/trees",
                   {"base_tree": base_tree, "tree": entries})
    if st != 201:
        print(f"创建 tree 失败 HTTP {st}: {tree}")
        sys.exit(1)
    print(f"  tree: {tree['sha'][:8]}")

    msg = os.environ.get("COMMIT_MSG", "chore: 通过 API 提交修复")
    st, new_commit = api(opener, token, "POST", f"{base}/git/commits",
                          {"message": msg, "tree": tree["sha"],
                           "parents": [head_sha]})
    if st != 201:
        print(f"创建 commit 失败 HTTP {st}: {new_commit}")
        sys.exit(1)
    print(f"  commit: {new_commit['sha'][:8]}")

    st, d = api(opener, token, "PATCH", f"{base}/git/refs/heads/{BRANCH}",
                {"sha": new_commit["sha"], "force": False})
    if st != 200:
        print(f"更新 ref 失败 HTTP {st}: {d}")
        sys.exit(1)
    print(f"\n提交成功: {new_commit['sha'][:8]}")
    print(f"https://github.com/{REPO}/commit/{new_commit['sha']}")


if __name__ == "__main__":
    main()
