"""下载 GitHub Actions artifact（IPA）到本地。

要点：GitHub 的 artifact 下载会 302 重定向到 S3，
S3 不接受 GitHub 的 Bearer 头 —— 必须自定义 redirect handler 剥掉它。
"""
import os
import ssl
import sys
import urllib.request

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
PROXY = os.environ.get("https_proxy")
PH = {"http": PROXY, "https": PROXY} if PROXY else {}


class StripAuthRedirect(urllib.request.HTTPRedirectHandler):
    """重定向到对象存储时剥掉 Authorization / X-GitHub-* 头。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None:
            for h in ("Authorization", "X-GitHub-Api-Version", "Accept"):
                if h in new.headers:
                    del new.headers[h]
        return new


def make_opener():
    ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(
        urllib.request.ProxyHandler(PH),
        urllib.request.HTTPSHandler(context=ctx),
        StripAuthRedirect(),
    )


def main():
    token, artifact_id, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    op = make_opener()
    url = (f"https://api.github.com/repos/y47h6wzhcw-prog/classic-reader"
           f"/actions/artifacts/{artifact_id}/zip")
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "classic-reader-setup")

    print(f"下载 artifact {artifact_id} ...", flush=True)
    r = op.open(req, timeout=300)
    total = 0
    with open(out_path, "wb") as f:
        while True:
            chunk = r.read(512 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            if total % (10 * 1024 * 1024) < 512 * 1024:
                print(f"  {total/1048576:.1f} MB", flush=True)
    r.close()
    print(f"完成: {out_path} ({total} 字节)", flush=True)


if __name__ == "__main__":
    main()
