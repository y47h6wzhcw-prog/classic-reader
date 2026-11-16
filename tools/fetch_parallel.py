"""最终版下载器（2026-10-23 实测调优）。

网络环境实测结论：
  - 出网经 HTTP 代理 127.0.0.1:2327
  - 代理会截断单次响应（128KB~528KB 不等）→ 必须 Range 分块
  - 单连接限速约 16 KB/s；并发 16 线程可达约 140 KB/s（提升 8.7 倍）
  - 并发超过 16 后收益递减且错误率上升
  - http.client 的 CONNECT 隧道被代理拒绝 → 必须用 urllib ProxyHandler
  - 每线程独立 opener（共享 opener 在并发下互相阻塞）

分块 32KB，可完整避开截断阈值。
"""
import json
import os
import ssl
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_books import EN_BOOKS, OUT_DIR, ZH_BOOKS, slugify, strip_gutenberg  # noqa: E402

BLOCK = 32 * 1024
BLOCK_RETRIES = 4
BOOK_WORKERS = 16
BLOCK_WORKERS = 16
READ_TIMEOUT = 15

CA_BUNDLE = r"C:\Users\Administrator\.workbuddy\system-ca-bundle.pem"


def _proxy_from_env():
    """代理端口会轮换，优先用环境变量；读不到再退回默认端口并探测。"""
    for key in ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY"):
        val = os.environ.get(key)
        if val:
            hostport = val.replace("http://", "").replace("https://", "").strip("/")
            if ":" in hostport:
                return {"http": f"http://{hostport}", "https": f"http://{hostport}"}
    # 环境变量缺失时，探测本机常见代理端口
    import socket
    for port in (2327, 54254, 7890, 10809, 8080):
        s = socket.socket()
        s.settimeout(0.6)
        try:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return {"http": f"http://127.0.0.1:{port}",
                        "https": f"http://127.0.0.1:{port}"}
        finally:
            s.close()
    return {"http": "http://127.0.0.1:2327", "https": "http://127.0.0.1:2327"}


PROXY = _proxy_from_env()
HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "download.log")
PROGRESS_PATH = os.path.join(HERE, "progress.txt")

_lock = threading.Lock()
_tls = threading.local()
_stats = {"books": 0, "blocks": 0}
_log_fh = None
_block_pool = None


def _log_fh():
    global _log_fh
    if _log_fh is None:
        _log_fh = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
    return _log_fh


def log(msg):
    """无锁写日志：只用内置文件对象的线程安全写，避免与 _lock 互相等待。"""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
    except Exception:
        pass


def get_opener():
    op = getattr(_tls, "opener", None)
    if op is None:
        ctx = ssl.create_default_context(cafile=CA_BUNDLE)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        op = urllib.request.build_opener(
            urllib.request.ProxyHandler(PROXY),
            urllib.request.HTTPSHandler(context=ctx),
        )
        _tls.opener = op
    return op


def refresh_proxy():
    """代理进程挂掉后，刷新端口并让当前线程重建 opener。"""
    global PROXY
    new = _proxy_from_env()
    if new != PROXY:
        log(f"  !! proxy changed {PROXY.get('https')} -> {new.get('https')}")
        PROXY = new
    _tls.opener = None


def get_block(url, start, end):
    """返回 (数据, content_range)。失败抛异常。"""
    last = None
    for attempt in range(BLOCK_RETRIES):
        try:
            req = urllib.request.Request(url)
            req.add_header("Range", f"bytes={start}-{end}")
            r = get_opener().open(req, timeout=READ_TIMEOUT)
            data = r.read()
            cr = r.headers.get("Content-Range")
            r.close()
            return data, cr
        except Exception as e:
            last = e
            # 连接被拒 = 代理挂了，刷新端口后重试
            reason = str(getattr(e, "reason", e))
            if "10061" in reason or " refused" in reason or "timed out" in reason:
                time.sleep(1.5)
                refresh_proxy()
            else:
                time.sleep(0.25 * (attempt + 1))
    raise last if last else RuntimeError("block failed")


def _grab(url, start, end):
    try:
        d, _ = get_block(url, start, end)
        return d
    except Exception:
        return None


def fetch_book(bid, title, title_alt, author, lang):
    url = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
    slug = f"{lang}_{bid}_{slugify(title)}"
    dest = os.path.join(OUT_DIR, slug + ".txt")
    log(f">>> start {slug}")

    # 断点跳过：已完整下载的书直接复用
    if os.path.exists(dest):
        try:
            with open(dest, "r", encoding="utf-8", errors="replace") as f:
                cached = f.read()
            if len(cached) >= 500:
                with _lock:
                    _stats["books"] += 1
                    _stats["skipped"] = _stats.get("skipped", 0) + 1
                log(f"    = cached {slug} {len(cached)} chars")
                return {
                    "id": bid, "lang": lang, "file": slug + ".txt",
                    "title": title, "titleAlt": title_alt, "author": author,
                    "chars": len(cached),
                }
        except OSError:
            pass

    try:
        first, cr = get_block(url, 0, BLOCK - 1)
    except Exception as e:
        log(f"  !! FAIL {slug} {type(e).__name__}")
        return None
    if not first:
        log(f"  !! EMPTY {slug}")
        return None

    parts = [first]
    if cr and "/" in cr:
        total = int(cr.split("/")[-1])
        nblocks = (total + BLOCK - 1) // BLOCK
        results = {}
        # 扁平化：块级任务直接提交到全局池，避免嵌套线程池的调度死锁
        if _block_pool is None:
            raise RuntimeError("pool not ready")
        futs = {}
        for i in range(1, nblocks):
            s = i * BLOCK
            e = min(s + BLOCK, total) - 1
            futs[_block_pool.submit(_grab, url, s, e)] = i
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                results[i] = fut.result()
            except Exception:
                results[i] = None
            with _lock:
                _stats["blocks"] += 1
                if _stats["blocks"] % 40 == 0:
                    log(f"    .. {_stats['blocks']} blocks / {_stats['books']} books")
        bad = [i for i in range(1, nblocks) if results.get(i) is None]
        if bad:
            log(f"  !! PARTIAL {slug} missing={len(bad)}")
            return None
        parts.extend(results[i] for i in range(1, nblocks))
    else:
        pos = len(first)
        while pos < 12 * 1024 * 1024:
            try:
                d, _ = get_block(url, pos, pos + BLOCK - 1)
            except Exception:
                break
            if not d:
                break
            parts.append(d)
            pos += len(d)

    raw = b"".join(parts).decode("utf-8", errors="replace")
    body = strip_gutenberg(raw)
    # 短文本合法（三字经、百家姓等本就千字以内），阈值放宽到 500
    if len(body) < 500:
        log(f"  !! SHORT {slug} ({len(body)})")
        return None
    with open(dest, "w", encoding="utf-8") as f:
        f.write(body)
    with _lock:
        _stats["books"] += 1
        log(f"[{_stats['books']:3d}] ok {slug} {len(body)} chars")
        try:
            with open(PROGRESS_PATH, "w", encoding="utf-8") as pf:
                pf.write(f"books={_stats['books']} blocks={_stats['blocks']}\n")
        except Exception:
            pass
    return {
        "id": bid, "lang": lang, "file": slug + ".txt",
        "title": title, "titleAlt": title_alt, "author": author, "chars": len(body),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    open(LOG_PATH, "w", encoding="utf-8").close()
    jobs = [(b, "zh") for b in ZH_BOOKS] + [(b, "en") for b in EN_BOOKS]
    results = []
    t0 = time.time()
    log(f"=== start {len(jobs)} books ===")

    # 单一全局块池 + 书籍级任务共享它，避免嵌套池互相等待
    global _block_pool
    with ThreadPoolExecutor(max_workers=BOOK_WORKERS + BLOCK_WORKERS) as book_pool:
        _block_pool = ThreadPoolExecutor(max_workers=BLOCK_WORKERS)
        futs = {book_pool.submit(fetch_book, *b, lang): b for b, lang in jobs}
        for fut in as_completed(futs):
            try:
                r = fut.result()
                if r:
                    results.append(r)
            except Exception as e:
                log(f"  !! TASK {type(e).__name__} {str(e)[:90]}")
        _block_pool.shutdown(wait=True)

    order = {b[0]: i for i, b in enumerate(ZH_BOOKS + EN_BOOKS)}
    results.sort(key=lambda m: order.get(m["id"], 9999))
    # 按 ID 去重（同一本书可能在书单中出现多次）
    deduped = []
    seen_ids = set()
    for m in results:
        if m["id"] in seen_ids:
            continue
        seen_ids.add(m["id"])
        deduped.append(m)
    results = deduped
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    zh = sum(1 for m in results if m["lang"] == "zh")
    log(f"=== DONE in {time.time()-t0:.0f}s: {zh} zh + {len(results)-zh} en = {len(results)} books ===")
    got = {m["id"] for m in results}
    missing = [b[0] for b in ZH_BOOKS + EN_BOOKS if b[0] not in got]
    if missing:
        log(f"MISSING IDS: {missing}")


if __name__ == "__main__":
    main()
