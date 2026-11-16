"""从 Windows 系统证书库导出根 CA 为 PEM，供 git 的 http.sslCAInfo 使用。

背景：
- git 默认用 schannel，报 SEC_E_UNTRUSTED_ROOT
- 改用 openssl + WorkBuddy 自带 bundle，报 "unable to get local issuer certificate"
  （该 bundle 里缺 GitHub 证书链的根：Sectigo / USER Trust Root）

做法：Python 的 SSLContext.load_default_certs() 在 Windows 上会从系统
Root 存储枚举全部根证书，取其 DER 后转 PEM 写出。
"""
import os
import ssl
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "windows-roots.pem")


def flatten_name(name):
    """把 subject/issuer 的嵌套元组展平成字符串列表。"""
    out = []
    for rdn in name:
        for attr in rdn:
            if isinstance(attr, (tuple, list)) and len(attr) == 2:
                out.append(str(attr[1]))
            elif isinstance(attr, (tuple, list)) and len(attr) == 1:
                out.append(str(attr[0]))
            else:
                out.append(str(attr))
    return out


def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_default_certs()
    certs = ctx.get_ca_certs()
    print(f"系统根证书数: {len(certs)}")

    blocks = []
    subjects = []
    for c in certs:
        der = c.get("der")
        if not der:
            continue
        pem = ssl.DER_cert_to_PEM_cert(der)
        blocks.append(pem)
        subjects.append(", ".join(flatten_name(c.get("subject", ()))))

    if not blocks:
        print("未取到任何证书")
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))

    key = ("Sectigo", "USER Trust", "Baltimore", "DigiCert", "GlobalSign",
           "ISRG", "GTS Root", "Amazon", "Microsoft")
    hits = sorted({s for s in subjects if any(k in s for k in key)})
    print(f"导出 {len(blocks)} 张 -> {OUT} ({os.path.getsize(OUT)} 字节)")
    print("关键 CA:")
    for h in hits[:14]:
        print("  -", h)


if __name__ == "__main__":
    main()
