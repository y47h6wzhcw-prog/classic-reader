# 经典书房 · Classic Reader

一个**完全离线**的 iOS 读书 App，内置 **70 本中文典籍 + 55 本英文原著**，
从代码到装上自己的 iPhone，**零元、零注册、零审核**。

---

## 特性

- **内置 125 本公版名著，共 5873 万字**
  - 中文 70 本：四大名著（《红楼梦》《三国演义》《西游记》《水浒传》）、
    《聊斋志异》《儒林外史》《浮生六记》《西厢记》《牡丹亭》《桃花扇》、
    《史记》《论语》《道德经》《山海经》《诗经》《易经》、
    《唐诗三百首》《李太白集》《漱玉词》《人间词话》《文心雕龙》……
  - 英文 55 本：《Pride and Prejudice》《Alice's Adventures in Wonderland》
    《The Adventures of Sherlock Holmes》《Jane Eyre》《Wuthering Heights》
    《Moby Dick》《Dracula》《Frankenstein》《War and Peace》
    《Les Misérables》《The Count of Monte Cristo》《Don Quixote》
    《The Odyssey》《Macbeth》《Beowulf》《Meditations》……
  - **外国名著全部保留英文原文**，不做翻译
- **纯离线**：全部书稿作为 `assets` 随包分发，**不发起任何网络请求**，
  不含任何网络 SDK 或埋点
- **阅读体验**：章节目录（自动识别「第X回 / CHAPTER X」）、阅读进度记忆、
  字号/行距/边距调节、日间夜间主题、衬线/等宽字体切换
- **中英分区**：中文书架与英文书架独立，支持书名/作者搜索、最近阅读
- **书架**：三种视图（中文 / English / 最近阅读），带阅读进度条

---

## 目录结构

```
reader_app/
├── lib/
│   ├── main.dart                    # 应用入口 + 主题
│   ├── data/
│   │   ├── book_repository.dart     # 书库加载（manifest + 正文缓存）
│   │   └── prefs_store.dart         # 外观设置与阅读进度持久化
│   └── pages/
│       ├── shelf_page.dart          # 书架（分类 / 搜索 / 最近）
│       └── reader_page.dart         # 阅读器（正文 / 目录 / 设置面板）
├── assets/books/                    # 125 本书正文（83 MB）+ manifest.json
├── tools/                           # 书稿下载与校验脚本
├── test/book_test.dart              # 单元测试
├── .github/workflows/ios_build.yml  # 云端编译出 unsigned IPA
├── SIDELOAD.md                      # 装到 iPhone 的完整图文步骤
└── ios/README.md                    # ios/ 目录生成说明
```

---

## 本地运行（需要 Flutter SDK）

```bash
flutter create --platforms=ios --org com.example .   # 首次：生成 ios/ 目录
flutter pub get
flutter run           # 连接 iPhone 或启动模拟器
flutter test          # 跑单元测试
```

---

## 出包并装到 iPhone（不需要 Mac）

完整步骤见 **[SIDELOAD.md](SIDELOAD.md)**，简要版：

```bash
# 1. 推代码，触发 GitHub Actions 云端 macOS 编译
bash push_to_github.sh <你的GitHub用户名>
#    提示 Username 时填 GitHub 用户名
#    提示 Password 时粘贴 Personal Access Token（不是登录密码）

# 2. Actions → Build unsigned iOS IPA → 下载 artifact
#    得到 reader-1.0.0-unsigned.ipa

# 3. Windows 上用 Sideloadly 拖入 IPA + 填 Apple ID → Start
```

> 没有 GitHub 账号？注册只要 2 分钟，详见 SIDELOAD.md 的「1.0 首次使用：注册 GitHub 账号」。
>
> 免费 Apple ID 签名有效期 7 天。Sideloadly 自带后台自动重签，
> 开启后电脑开机状态下无需手动干预。

---

## 书单扩充

书稿来自 [Project Gutenberg](https://www.gutenberg.org)（全部为公版作品）。
新增书目：

1. 在 `tools/probe_zh.py` / `probe_ids.py` 中校验候选 ID 的真实标题与语种
2. 把条目追加到 `tools/fetch_books.py` 的 `ZH_BOOKS` / `EN_BOOKS`
3. 运行 `python tools/fetch_parallel.py` 重新拉取并生成 `manifest.json`
   （已下载的会自动跳过，支持断点续跑）
4. 推送后重新构建

### 下载脚本说明

`tools/fetch_parallel.py` 是针对当前网络环境调优过的版本，实测要点：

| 问题 | 应对 |
|---|---|
| 代理截断单次响应（128KB~528KB 不等） | 全部请求用 Range 分块，块大小 32KB |
| 单连接限速约 16 KB/s | 16 线程并发，提速至约 140 KB/s |
| 嵌套线程池互相等待导致卡死 | 改为「全局块池 + 书籍任务共用」的扁平结构 |
| 代理端口会轮换 | 从环境变量读取，失效时自动探测重连 |
| 代理会拒绝 http.client 的 CONNECT 隧道 | 改用 urllib 的 ProxyHandler |

### GitHub 相关脚本

| 脚本 | 用途 |
|---|---|
| `tools/create_repo.py` | 通过 API 创建公开仓库（网页端被拦时的替代方案） |
| `tools/upload_workflow.py` | 通过 Contents API 上传 workflow 文件 |
| `tools/api_commit.py` | **git 协议不通时**，用 Git Data API 提交文件改动 |
| `tools/download_artifact.py` | 下载 Actions 产出的 IPA（自动处理 S3 重定向） |

> **artifact 下载坑**：GitHub 的 artifact 下载会 302 重定向到 S3，
> S3 不接受 GitHub 的 `Bearer` 头。必须自定义 `HTTPRedirectHandler`
> 在重定向时剥掉 `Authorization`，否则会一直 401。

---

## 版权说明

所有书稿均为 **Project Gutenberg 收录的公有领域作品**（作者逝世逾 50 年
或原始作品本身已过期），Gutenberg License 允许自由使用与再分发。
中文古籍（四大名著、先秦诸子、唐宋诗词等）本身即为公版。

本项目不含任何付费墙内容、不抓取任何在线书源、不绕过任何 DRM。
