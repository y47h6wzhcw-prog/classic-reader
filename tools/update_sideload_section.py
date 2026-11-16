"""把 SIDELOAD.md 的第二节替换为 AirSign 主方案 + SideInstaller 备选。

用字符串定位而非行号，避免行号漂移。
"""
import io
import os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "SIDELOAD.md")

NEW = """## 二、iOS 27+：手机端全无线安装（免数据线）

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

"""

src = io.open(P, encoding="utf-8").read()
start = src.index("## 二、iOS 27+：手机端全无线安装（免数据线）")
end = src.index("## 三、装到 iPhone 上（Sideloadly 侧载，iOS 26 及以下）")
out = src[:start] + NEW + src[end:]
io.open(P, "w", encoding="utf-8").write(out)
print("第二节已替换")
print("新长度:", len(out))
