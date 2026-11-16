# 经典书房 · 从零装到你自己的 iPhone

本指南带你走完**方案 A：完全免费**的完整流程。全程不需要 Mac、
不需要付费开发者账号、不需要 App Store 审核、不需要任何备案。

```
写代码（Windows）→ 推到 GitHub → 云端 macOS 编译出 IPA
→ iPhone 上安装
```

---

## 选哪条路装？

| 你的 iOS 版本 | 推荐路径 | 需要数据线？ | 国区可用？ |
|---|---|---|---|
| **iOS 27+** | **方案 A：AirSign**（TestFlight 分发） | ❌ 不需要 | ✅ 可以 |
| iOS 27+ 且有美区/港区 ID | 方案 B：SideInstaller（开源） | ❌ 不需要 | ❌ 需切区 |
| iOS 17.4 ~ 26.x | 第三节：Sideloadly Wi-Fi 侧载 | 首次需要一次 | ✅ 可以 |
| iOS 17 以下 | 第三节：Sideloadly USB 侧载 | 需要 | ✅ 可以 |

> 关键分水岭：**iOS 27 起支持「设备自配对」**，iPhone 可以自己完成配对，
> 因此整个安装流程不再需要电脑和数据线。
>
> **国区用户请直接看方案 A（AirSign）**：它只依赖 TestFlight，
> 国区 App Store 能直接下载；方案 B 依赖的 `rootshell` 和 `LocalDevVPN`
> 国区上架不了。

---

## 零、前置条件清单

| 项 | 要求 | 说明 |
|---|---|---|
| 电脑 | Windows / macOS / Linux 均可 | 这台 Windows 就够（仅云端编译时用） |
| iPhone | iOS 16 及以上 | iOS 16+ 必须开启「开发者模式」 |
| 数据线 | 一根 | **iOS 27 可完全免**，见第二节 |
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
- **Scopes**：勾选 **`public_repo`** 和 **`workflow`**

> ⚠️ **`workflow` 权限必须一起勾。**
>
> 本项目包含 `.github/workflows/ios_build.yml`（云端编译用的 workflow）。
> GitHub 规定：修改 workflow 文件需要 Token 具备 `workflow` scope，
> 否则 `git push` 会被直接拒绝：
>
> ```
> ! [remote rejected] main -> main
>   (refusing to allow a Personal Access Token to create or update
>    workflow `.github/workflows/ios_build.yml` without `workflow` scope)
> ```
>
> 这个限制**无法绕过**——Contents API 和 Git Tree API 同样会返回 404。
> 只能回去给 Token 补权限：
>
> <https://github.com/settings/tokens> → 找到该 Token → **Edit** →
> 在 Select permissions 搜索 `workflow` → 勾选 → **Update token**
>
> 补完权限后 Token 字符串不变，无需重新复制。

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

## 二、iOS 27+：手机端全无线安装（免数据线）

> iOS 27 起支持「设备自配对」，iPhone 能自己完成配对与签名，
> **全程不需要电脑、不需要数据线**。

### 2.1 方案 A：AirSign（推荐，国区可用）

[AirSign](https://tarplay.com/airsign/) 是运行在 iPhone 上的独立 IPA 签名安装器，
由 TarPlay 团队开发，走 **TestFlight 官方分发**（不是随时可能跑路的证书签名），
且**自带 `10.7.0.1` 本地回环**，不需要额外装 LocalDevVPN 之类的工具。

> **为什么优先选它**：SideInstaller 依赖 `rootshell` 和 `LocalDevVPN`
> 两个 App，实测**国区 App Store 没有**（只有美区/港区有）。
> AirSign 只依赖 TestFlight，**国区 App Store 可以直接下载**。

#### 第 1 步 · 装 AirSign

用 iPhone 的 **Safari** 打开 TestFlight 邀请链接：

<https://testflight.apple.com/join/uvCeQG8t>

- 没装 TestFlight 会自动跳转到 App Store 安装（国区有）
- 点 **Accept / Install** 接受邀请，等下载完成

官方文档：<https://tarplay.com/airsign/guide/>
（Safari 打开后可用菜单「翻译成简体中文」）

#### 第 2 步 · 开启开发者模式

**设置 › 隐私与安全性 › 开发者模式** → 打开 → 手机重启 →
重启后回到该页面点「启用」确认。

#### 第 3 步 · 在 AirSign 里配置

1. **检测 UDID**（一次性）
   首页 UDID 旁点「Detect / 检测」→ 选「Auto-Detect via Safari Profile」→
   Safari 里点「允许」→ 回到**设置**，点「已下载描述文件」→ 安装。
   这个临时描述文件会自动移除。

2. **登录 Apple ID**
   「2. APPLE ACCOUNT」区 → 点「Sign In with Apple ID」→ 填邮箱、密码、6 位验证码。
   > 收不到短信验证码时，输入框里有「Send Code via SMS」和
   > 「Call Me with Code」按钮，语音电话通常更可靠（尤其境外号码）。

3. **无线配对（iOS 27+ 免电脑的关键一步）**
   在「APPLE ACCOUNT」区点 **Wireless Pair (No PC)** →
   AirSign 显示一个 6 位配对码 →
   打开 **设置 › 隐私与安全性 › 开发者模式**，滚到底部点 **Pair with AirSign** →
   输入锁屏密码和那 6 位码。

   > 若找不到「Pair with AirSign」：
   > 确认系统是 iOS 27.0+，且**设置 › 隐私与安全性 › 本地网络**里 AirSign 已打开。

#### 第 4 步 · 签名并安装

在 AirSign 首页「1. SIGN & INSTALL .IPA」区，点
**🌐 Sign & Install from URL**，粘贴：

```
https://github.com/y47h6wzhcw-prog/classic-reader/releases/download/v1.0.0/reader-1-unsigned.ipa
```

点「签名」→ 等进度条走完 → 弹出「tarplay.com 想要安装…」时点**安装** →
回到桌面，「经典书房」图标就出来了。

> 也可以先用 Safari 下载 IPA 到「文件」App，再点
> **📦 Pick & Sign .ipa from Files** 选中它。

#### 第 5 步 · 首次打开

- 若提示**不受信任的开发者** →
  **设置 › 通用 › VPN 与设备管理** → 点你的 Apple ID → 信任
- 若提示需要开发者模式 → **设置 › 隐私与安全性 › 开发者模式** → 开 → 重启

#### 第 6 步 · 7 天到期怎么办

免费 Apple ID 签名的 App 有效期 7 天。到期前打开 AirSign，保持同一 Apple ID 登录，
在 **INSTALLED APPS** 列表里找到「经典书房」点 **Re-sign**
（或重新选同一个 IPA 签名）——iOS 会**原地覆盖升级**，阅读进度、书签都保留。

建议每 5～6 天刷一次。免费账号最多同时装 3 个侧载 App，只装这一个不受影响。

#### 隐私与安全

- AirSign 的 Apple ID 登录是**手机直连 gsa.apple.com**（Apple 官方服务器），
  私钥和证书全程留在本机，不经过 AirSign 的服务器。
  它只在两处联系自己的域名：UDID 一次性登记、以及你主动点「Send Diagnostics」时。
- AirSign 目前是 v1.0 早期阶段，稳定性仍在完善。
  **建议先用一个小 IPA 试完整流程**，确认没问题再装正式应用。
- **不要用主力 Apple ID**，用小号。

---

### 2.2 方案 B：SideInstaller（需美区/港区 Apple ID，开源可审计）

如果你想要 SideStore 生态（可后台自动续签），另一条路是
[SideInstaller](https://github.com/FrizzleM/SideInstaller)（开源，代码可审计）。
它依赖三个 App，其中**两个国区没有**：

| App | 作用 | 国区 | 美区/港区 |
|---|---|---|---|
| rootshell | 本地终端 | ✗ | ✓ |
| Open Minis | 运行安装脚本 | ✓ | ✓ |
| LocalDevVPN | 本地回环隧道 | ✗ | ✓ |

> 上表为实测结果（Apple iTunes Lookup API，country=cn/us/hk）。
> 用国区账号的可以先试方案 A。

**步骤 1 · 装三个 App**（都来自 App Store，免费）

- <https://apps.apple.com/app/id6755794662> — rootshell
- <https://apps.apple.com/app/id6759188481> — Open Minis
- <https://apps.apple.com/app/id6755608044> — LocalDevVPN

**步骤 2 · 用 siboot 装 SideInstaller**

打开 <https://sideinstaller.net/>，按页面 1→2→3 步：

打开 rootshell → 右上角 **Open** → **Local Shell**，逐行执行：

```bash
curl -fsSLO https://raw.githubusercontent.com/FrizzleM/siboot/main/rootshell/bin/siboot-pair.wasm
ifconfig en0 > ifconfig.txt
./siboot-pair.wasm
```

rootshell 会显示一个**配对码**。接着打开
**设置 › 隐私与安全性 › 开发者模式**，滚到底部点 **Pair with siboot**，
输入锁屏密码和那个配对码。**保持 rootshell 运行。**

连接 LocalDevVPN → 打开 Open Minis → 右上角控制台图标 →
**Shell Terminal**，执行：

```bash
wget -qO- https://raw.githubusercontent.com/FrizzleM/siboot/main/minis/install.sh | sh
```

输入 rootshell 显示的传输码（仅首次），再输入你的
**Apple ID 邮箱、密码和验证码**。Minis 保持打开直到提示完成。

首次完成后去 **设置 › 通用 › VPN 与设备管理** 信任你的 Apple 账号。

**步骤 3 · 装 SideStore**

保持 LocalDevVPN 已连接 → 打开 SideInstaller → 登录 Apple ID →
点 **Install SideStore**（或 **SideStore + LiveContainer**）。

**步骤 4 · 一键安装经典书房**

Safari 打开：

<https://sideinstaller.net/open.html?url=https%3A%2F%2Fgithub.com%2Fy47h6wzhcw-prog%2Fclassic-reader%2Freleases%2Fdownload%2Fv1.0.0%2Freader-1-unsigned.ipa>

也可以把 IPA 从 Release 页面下载到「文件」App，放进
**文件 › 我的 iPhone › SideInstaller** 并命名为 `SideStore.ipa`，
SideInstaller 会自动识别并安装。

> ⚠️ **安全提醒**：只从 **<https://sideinstaller.net/>** 和
> **<https://github.com/FrizzleM/SideInstaller>** 获取 SideInstaller。
> `sideinstaller.com` 是**假站点**，可能携带木马。
> 这类工具开放源码，任何人都能伪造同样的图标和名字分发恶意版本。

---

## 三、装到 iPhone 上（Sideloadly 侧载，iOS 26 及以下）

### 3.1 准备 Sideloadly

1. 访问 <https://sideloadly.io>，下载 Windows 版
2. 安装
3. **重要**：Windows 上需先安装 Apple 官方的
   [iTunes 网页版](https://www.apple.com/itunes/) 和
   [iCloud 网页版](https://www.icloud.com/)。
   如果你装的是 Microsoft Store 版，Sideloadly 无法使用，需先卸载。
   > iTunes 网页版安装包会一并装上 **Bonjour** 服务，
   > 它是 Wi-Fi 侧载的必需组件。

### 3.2 手机端设置

在 iPhone 上依次操作：

1. **设置 → 隐私与安全性 → 开发者模式** → 打开
   （此选项仅在 iOS 16+ 且已侧载过应用后才显示）
   - 打开后手机会重启，重启后确认一次
2. 用数据线连接电脑，手机弹出「信任此电脑」→ 信任
3. **开启 Wi-Fi 同步**（这一步决定了以后能不能脱离数据线）：
   - Windows：打开 iTunes → 点左上角设备图标 → 设备摘要页 →
     勾选 **「通过 Wi-Fi 与此 iPhone 同步」** → 同步
   - macOS：Finder → 选中设备 → 通用 → 勾选
     **「使用 Wi-Fi 时显示此 iPhone」** → 同步

> 配对完成后，Sideloadly 就能在局域网内发现手机，
> 之后**安装和续签都可以走 Wi-Fi**，不再需要插线。
> 若 Sideloadly 里看不到设备，多半是 Bonjour 没装上——
> 重新运行 iTunes 网页版安装包补装即可。

### 3.3 侧载

1. 打开 Sideloadly
2. 把 `reader-1.0.0-unsigned.ipa` **拖进窗口**
3. 输入你的 Apple ID 和密码（**只用于本机签名**，不会上传给第三方；
   建议用一个备用 Apple ID）
   - 开启两步验证的账号需要输入验证码
4. 点 **Start**
5. 等待安装完成

### 3.4 首次打开

1. 桌面出现「经典书房」图标
2. **可能无法直接打开**，提示「不受信任的开发者」。处理：
   **设置 → 通用 → VPN 与设备管理** → 点你的 Apple ID →
   点「信任」→ 确认
3. 再回到桌面打开 App

---

## 四、关于 7 天有效期

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

## 五、限制说明

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

## 六、如果想更省心：升级到付费方案

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

## 七、常见问题

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
