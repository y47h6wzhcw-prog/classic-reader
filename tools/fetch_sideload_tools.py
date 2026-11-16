"""下载 WiFi 侧载所需组件（走系统代理）。

1. SideloadlySetup64.exe —— 侧载工具本体
2. iTunes64.exe           —— Apple 官方网页版安装包，内含 Bonjour（WiFi 侧载必需）

注意：本机的 curl 不走代理且不带 CA bundle，必须用 urllib + 环境变量代理。
"""
import os
import ssl
import sys
import urllib.request

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"
OUT_DIR = r"C:\Users\Administrator\WorkBuddy\2026-10-23-15-44-23\reader_app\dist\tools"

ITEMS = [
    ("https://sideloadly.io/SideloadlySetup64.exe", "SideloadlySetup64.exe"),
    ("https://www.apple.com/itunes/download/win64", "iTunes64.exe"),
]


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


def download(url, dest):
    op = make_opener()
    req = urllib.request.Request(url)
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    print(f"下载 {url}", flush=True)
    r = op.open(req, timeout=120)
    total = 0
    with open(dest, "wb") as f:
        while True:
            chunk = r.read(512 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            if total % (10 * 1024 * 1024) < 512 * 1024:
                print(f"  {total/1048576:.1f} MB", flush=True)
    r.close()
    print(f"  -> {dest} ({total} 字节)", flush=True)
    return total


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for url, name in ITEMS:
        dest = os.path.join(OUT_DIR, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 100000:
            print(f"跳过（已存在）: {name}", flush=True)
            continue
        try:
            download(url, dest)
        except Exception as e:
            print(f"  失败: {type(e).__name__} {str(e)[:120]}", flush=True)
    print("完成", flush=True)


if __name__ == "__main__":
    main()
