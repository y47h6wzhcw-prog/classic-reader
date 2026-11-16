# Xcode 自动生成说明

`ios/` 目录由 `flutter create` 自动生成，包含 Xcode 工程、Runner target、
Info.plist、图标等。本仓库未提交该目录，原因有二：

1. **体积**：Flutter 生成的 `ios/` 目录约 3–5 MB，全是模板文件，
   放 Git 里对阅读器本身没有价值。
2. **可维护性**：Flutter SDK 版本升级时 `flutter create .` 会自动
   用匹配当前 SDK 的模板覆盖生成，避免模板与 SDK 不匹配导致构建失败。

## 首次构建前的初始化步骤

在项目根目录执行：

```bash
flutter create --platforms=ios --org com.example .
```

这条命令会：

- 生成 `ios/` 目录与 `Runner.xcworkspace`
- 创建 `ios/Runner/Assets.xcassets`（App 图标与启动图占位）
- 保留你已有的 `lib/`、`assets/`、`pubspec.yaml`（不会覆盖同名文件）

随后：

```bash
flutter pub get
cd ios && pod install && cd ..
```

## iOS target 配置核对

`flutter create` 生成的默认配置已满足本项目的需求，无需额外修改：

| 项 | 值 | 说明 |
|---|---|---|
| Bundle Identifier | `com.example.classicReader` | 可自行改成唯一值 |
| Deployment Target | iOS 12.0+ | 满足 Flutter 3.24 最低要求 |
| Supported Orientations | Portrait | 竖屏阅读 |
| `UIFileSharingEnabled` | 否 | 不开放文档目录 |
| 网络权限 | 无 | App 完全不发起网络请求 |

**关于无网络声明**：本 App 不含任何网络代码，也不引入网络类 SDK。
所有书稿以 `assets` 形式随包分发，阅读进度存于
`SharedPreferences`（沙盒内）。这一点同时也是将来若要上架
App Store 中国区、申请 ICP 备案豁免的必要条件。

## 签名说明

本项目走 **方案 A：未签名 IPA + Sideloadly 侧载**，因此：

- 不需要在 Xcode 中配置任何证书或描述文件
- `flutter build ios --release --no-codesign` 产出的是无签名 `.app`
- 签名由 Sideloadly 在你本机用你的 Apple ID 完成

若将来改走付费开发者账号路线，只需在 `ios/` 的 Signing & Capabilities
里选择你的 Team，再执行普通 `flutter build ipa` 即可。
