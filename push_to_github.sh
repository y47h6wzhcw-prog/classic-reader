#!/usr/bin/env bash
# 一键推送脚本：注册完 GitHub 后，把项目推到你的仓库并触发云端编译。
#
# 用法：
#   bash push_to_github.sh <你的GitHub用户名> [仓库名]
#
# 例：
#   bash push_to_github.sh zhangsan classic-reader
#
# 仓库名默认 classic-reader。

set -e

cd "$(dirname "$0")"

USERNAME="$1"
REPO="${2:-classic-reader}"

if [ -z "$USERNAME" ]; then
  echo "用法: bash push_to_github.sh <你的GitHub用户名> [仓库名]"
  echo "例:  bash push_to_github.sh zhangsan classic-reader"
  exit 1
fi

echo "======================================"
echo " 推送目标: https://github.com/${USERNAME}/${REPO}.git"
echo "======================================"
echo

# 1. 身份检查
if [ -z "$(git config user.name)" ]; then
  echo "[!] 还没设置 git 身份，请先运行："
  echo "    git config --global user.name \"你的名字\""
  echo "    git config --global user.email \"你的GitHub邮箱\""
  exit 1
fi

# 2. 首次提交
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "[1/4] 已有提交，跳过"
else
  echo "[1/4] 创建首次提交..."
  git commit -m "feat: 经典书房 - 离线公版名著阅读器

内置 125 本中英文公版名著（中文 70 + 英文 55，约 5874 万字）
纯本地阅读，无网络请求；GitHub Actions 云端编译出 unsigned IPA"
fi

# 3. 关联远程仓库
echo "[2/4] 配置远程仓库..."
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/${USERNAME}/${REPO}.git"
else
  git remote add origin "https://github.com/${USERNAME}/${REPO}.git"
fi
git remote -v

# 4. 推送
echo "[3/4] 推送到 GitHub..."
echo "      (首次推送会要求输入 GitHub 用户名 + Personal Access Token)"
echo "      Token 生成地址: https://github.com/settings/tokens"
echo "      勾选 'public_repo' 权限即可"
echo
git push -u origin main

# 5. 提示
echo "[4/4] 完成！"
echo
echo "接下来："
echo "  1. 打开 https://github.com/${USERNAME}/${REPO}/actions"
echo "  2. 等待 'Build unsigned iOS IPA' 跑完（约 5-10 分钟）"
echo "  3. 在页面底部 Artifacts 区域下载 reader-unsigned-ipa"
echo "  4. 解压得到 reader-1.0.0-unsigned.ipa"
echo "  5. 用 Sideloadly 拖入 IPA + 填 Apple ID → Start"
echo
echo "详细步骤见 SIDELOAD.md"
