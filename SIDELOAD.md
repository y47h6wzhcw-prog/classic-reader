# 经典书房 · 从零装到你自己的 iPhone

本指南带你走完**方案 A：完全免费**的完整流程。全程不需要 Mac、
不需要付费开发者账号、不需要 App Store 审核、不需要任何备案。

```
写代码（Windows）→ 推到 GitHub → 云端 macOS 编译出 IPA
→ 下载 IPA → Sideloadly 侧载 → 装到 iPhone 上
```

---

## 零、前置条件清单

| 项 | 要求 | 说明 |
|---|---|---|
| 电脑 | Windows / macOS / Linux 均可 | 你这台 Windows 就够 |
| iPhone | iOS 16 及以上 | iOS 16+ 必须开启「开发者模式」 |
| 数据线 | 一根 | 首次安装必须 USB 连接 |
| Apple ID | **免费**普通账号 | 就是你 iPhone 上登录的那个，无需注册开发者 |
| GitHub 账号 | 免费 | 用来触发云端编译，注册约 2 分钟 |
| 邮箱 | 能收验证码 | QQ / 163 / Gmail 均可，用于注册 GitHub |
| Personal Access Token | 免费生成 | 推送代码用，见 1.0 节 |
| Sideloadly | 免费 | Windows 版在官网下载 |

**全程花费：0 元。**

---

## 一、把项目推上 GitHub（触发云端编译）

### 1.0 首次使用：注册 GitHub 账号

如果你还没有 GitHub 账号，先注册一个（免费，约 2 分钟）：

1. 打开 <https://github.com/signup>
2. **填用户名**（Username）——全局唯一，注册后不能改。建议用
   `姓名拼音` 或 `姓名拼音 + 数字` 的形式，例如 `zhangsan`、
   `lihua2026`。避免用中文和下划线。
3. **填邮箱**——用你能长期接收验证码的（QQ 邮箱、163、Gmail 都行）。
   GitHub 会往这个邮箱发 6 位验证码。
4. **设密码**——至少 8 位，含字母和数字。建议用密码管理器生成。
5. 点 **Continue** → 输入邮箱收到的验证码 → 完成。

**注册后建议立刻做两件事：**

#### 启用两步验证（强烈建议）

<https://github.com/settings/tokens> 旁边就是
<https://github.com/settings/security>，找到 **Two-factor authentication**，
用手机装个 **Microsoft Authenticator** 或 **Google Authenticator** 扫码绑定。

> 为什么建议做：不开两步验证时，GitHub 会要求用密码推送代码；
> 开了之后可以用 **Personal Access Token** 代替密码推送，
> 既安全又不会因为密码策略被拒。

#### 生成 Personal Access Token（推送代码时用）

<https://github.com/settings/tokens> → **Generate new token (classic)**：

- **Note**：随便写，比如 `classic-reader`
- **Expiration**：选 90 days 或 1 year
- **Scopes**：只勾 **`public_repo`** 就够了（我们推的是公开仓库）

生成后那串 `ghp_xxxxxxxx` **只显示一次**，立刻复制保存。

### 1.1 设置 git 身份

在项目目录执行（把引号里的换成你的信息，邮箱要和 GitHub 注册的一致）：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的GitHub邮箱"
```

### 1.2 创建仓库

打开 <https://github.com/new>：

- **Repository name**：`classic-reader`
- **Public / Private**：选 **Public**
  > 公开仓库在 GitHub Actions 上有免费额度（macOS runner 不按 10 倍扣），
  > 私有仓库的 macOS 分钟会被 10 倍计费，免费额度只够约 25 次构建。
- **不要**勾选 "Add a README file"（本地已有）
- 点 **Create repository**

### 1.3 一键推送

项目里已备好推送脚本，填上你的用户名即可：

```bash
cd reader_app
bash push_to_github.sh <你的GitHub用户名>
```

或者手动执行：

```bash
cd reader_app
git add -A
git commit -m "feat: 经典书房 - 离线公版名著阅读器"
git remote add origin https://github.com/<你的用户名>/classic-reader.git
git branch -M main
git push -u origin main
```

推送时会提示输入：
- **Username**：你的 GitHub 用户名
- **Password**：粘贴前面生成的 **Personal Access Token**（不是登录密码）

### 1.4 触发构建

推送完成后，GitHub 会自动开始跑 `Build unsigned iOS IPA`。

也可以手动触发：仓库页面 → **Actions** → 左侧 **Build unsigned iOS IPA**
→ 右侧 **Run workflow**。

### 1.5 下载 IPA

构建成功后（约 5–10 分钟）：

1. 进入 Actions 页面，点开那次运行记录
2. 页面底部 **Artifacts** 区域
3. 下载 `reader-unsigned-ipa`
4. GitHub 会把 artifact 打包成 zip，解压后得到 `reader-1.0.0-unsigned.ipa`

---

## 二、装到 iPhone 上（Sideloadly 侧载）

### 2.1 准备 Sideloadly

1. 访问 <https://sideloadly.io>，下载 Windows 版
2. 安装
3. **重要**：Windows 上需先安装 Apple 官方的
   [iTunes 网页版](https://www.apple.com/itunes/) 和
   [iCloud 网页版](https://www.icloud.com/)。
   如果你装的是 Microsoft Store 版，Sideloadly 无法使用，需先卸载。

### 2.2 手机端设置

在 iPhone 上依次操作：

1. **设置 → 隐私与安全性 → 开发者模式** → 打开
   （此选项仅在 iOS 16+ 且已侧载过应用后才显示）
   - 打开后手机会重启，重启后确认一次
2. 用数据线连接电脑，手机弹出「信任此电脑」→ 信任

### 2.3 侧载

1. 打开 Sideloadly
2. 把 `reader-1.0.0-unsigned.ipa` **拖进窗口**
3. 输入你的 Apple ID 和密码（**只用于本机签名**，不会上传给第三方；
   建议用一个备用 Apple ID）
   - 开启两步验证的账号需要输入验证码
4. 点 **Start**
5. 等待安装完成

### 2.4 首次打开

1. 桌面出现「经典书房」图标
2. **可能无法直接打开**，提示「不受信任的开发者」。处理：
   **设置 → 通用 → VPN 与设备管理** → 点你的 Apple ID →
   点「信任」→ 确认
3. 再回到桌面打开 App

---

## 三、关于 7 天有效期

免费 Apple ID 签名的应用 **7 天后会失效**：图标还在桌面，但点开会闪退。

### 自动续签（推荐）

Sideloadly 自带后台守护程序，会在过期前自动重签：

1. Sideloadly → **Settings** → 勾选 **Automatic App Refreshing**
2. 设置刷新间隔（建议 3 天）
3. 保持 Sideloadly 常驻运行，或加入开机启动

只要电脑开着且 Sideloadly 在后台运行，App 会一直可用。

### 手动续签

若已失效：连接手机，打开 Sideloadly，点 **Start** 重新安装即可。
**你的阅读进度不会丢失**，因为进度存在手机本地的 SharedPreferences 里。

---

## 四、限制说明

免费 Apple ID 侧载有以下硬性限制，务必了解：

| 限制 | 具体表现 |
|---|---|
| 有效期 | 7 天（靠自动重签维持） |
| 同时安装数量 | 最多 3 个侧载 App（含 Sideloadly/AltStore 本身也占一个） |
| App ID 数量 | 7 天内最多注册 10 个 App ID |
| 功能缺失 | 无推送通知、无 iCloud 同步、无内购、无 Game Center |
| 设备数量 | 免费账号最多 3 台设备 |

**这些限制都不影响本 App**：它是纯本地阅读器，不需要推送、不需要内购、
不需要云同步。书稿全部随包分发，阅读进度存在沙盒内。

---

## 五、如果想更省心：升级到付费方案

如果你不想再管签名，可以花 **688 元/年**（中国大陆 Apple Developer Program
个人账号）换到：

- 签名有效期 **1 年**，不用重签
- Ad Hoc 分发最多 **100 台设备**，不用 SideStore 刷新
- 可用 TestFlight 自分发
- 推送、内购、iCloud 全部解锁

### 升级步骤

1. 在 iPhone 上安装 **Developer** App（App Store 搜 "Developer"）
2. 用你的 Apple ID 登录，选择「个人」，完成身份证与人脸验证
3. 付款 688 元/年
4. 拿到证书后，在 GitHub Actions 的 workflow 中加入签名步骤：
   - 把 `p12` 证书和 `mobileprovision` 描述文件存为 GitHub Secrets
   - 改用 `xcodebuild archive` 产出已签名 IPA
   - 用 Sideloadly 导入该 IPA 即可，一年不用再签

**注意**：如果未来想上架 App Store 中国区，还需要额外处理
**App 备案（ICP 备案号）**。本 App 是纯单机、无任何网络请求，
可以走「离线 App 豁免」路径——下载苹果官方豁免声明模板，
签字盖章后上传 App Store Connect 客服，约 3 个工作日。

---

## 六、常见问题

**Q：App 打开闪退？**
A：99% 是 7 天签名过期，重新用 Sideloadly 装一次即可。
若刚装上就闪退，检查「设置 → 通用 → VPN 与设备管理」里是否已信任证书。

**Q：书能正常显示吗？**
A：可以。内置 **125 本公版名著（中文 70 + 英文 55，约 5874 万字）**，
书稿已随包分发为 asset，完全离线，不依赖网络。完整书单见
[BOOKLIST.md](BOOKLIST.md)。

**Q：怎么加书？**
A：编辑 `assets/books/` 下的 txt 文件与 `manifest.json`，
再重新推送触发构建。`tools/fetch_books.py` 里有完整书单，
`tools/fetch_parallel.py` 负责下载（已下载的自动跳过），
`tools/probe_zh.py` / `probe_ids.py` 可用于校验新书的 ID 与标题，
`tools/gen_booklist.py` 可重新生成书单文档。

**Q：GitHub Actions 报错？**
A：打开失败的那次运行记录看具体日志。最常见的问题是
`flutter pub get` 失败或 Xcode 版本选择。workflow 里已做 Xcode 多版本回退，
若仍失败，把 Actions 日志贴给我，我帮你改。

**Q：能不能不用 GitHub？**
A：可以，用 Codemagic（每月 500 免费 macOS 分钟）或 Expo EAS Build
（每月 15 次免费 iOS 构建）。但 GitHub 公开仓库最简单，优先用它。
