#!/usr/bin/env bash
# 一键完成：建公开仓库 + 推送代码 + 触发云端编译
#
# 用法：
#   bash push_to_github.sh <你的GitHub用户名> <PersonalAccessToken> [仓库名]
#
# 例：
#   bash push_to_github.sh y47h6wzhcw-prog ghp_xxxxxxxxxxxx classic-reader
#
# Token 生成：https://github.com/settings/tokens
#   → Generate new token (classic) → 勾选 public_repo → Generate
#   （生成后只显示一次，请立刻复制）
#
# 说明：
#   本机网络下 github.com 网页端会被代理拦截，但 api.github.com 直连可用，
#   所以建仓走 API（tools/create_repo.py），推送走 git 原生协议。

set -e
cd "$(dirname "$0")"

USERNAME="$1"
TOKEN="$2"
REPO="${3:-classic-reader}"

if [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
  echo "用法: bash push_to_github.sh <GitHub用户名> <PersonalAccessToken> [仓库名]"
  echo ""
  echo "Token 获取: https://github.com/settings/tokens"
  echo "  → Generate new token (classic) → 勾选 public_repo → Generate"
  exit 1
fi

PY="C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe"
[ -x "$PY" ] || PY="python"

echo "======================================"
echo " 目标仓库: https://github.com/${USERNAME}/${REPO}"
echo "======================================"
echo

# 1. git 身份
if [ -z "$(git config user.name)" ]; then
  git config user.name "$USERNAME"
  git config user.email "${USERNAME}@users.noreply.github.com"
  echo "[1/4] 已设置 git 身份: $USERNAME"
else
  echo "[1/4] git 身份已配置: $(git config user.name)"
fi

# 2. 提交
if git diff --quiet && git diff --cached --quiet; then
  echo "[2/4] 无待提交更改"
else
  echo "[2/4] 提交更改..."
  git add -A
  git commit -m "chore: 更新项目"
fi

# 3. 建仓（已存在则跳过）
echo "[3/4] 创建/检查仓库..."
"$PY" tools/create_repo.py "$USERNAME" "$TOKEN"

# 4. 推送
echo "[4/4] 推送到 GitHub..."
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/${USERNAME}/${REPO}.git"
else
  git remote add origin "https://github.com/${USERNAME}/${REPO}.git"
fi

# 把 Token 交给凭据助手缓存，避免重复输入
printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' "$USERNAME" "$TOKEN" \
  | git credential approve 2>/dev/null || true

git push -u origin main

echo ""
echo "======================================"
echo " 完成！"
echo "======================================"
echo ""
echo "  1. 打开 https://github.com/${USERNAME}/${REPO}/actions"
echo "  2. 等待 'Build unsigned iOS IPA' 跑完（约 5-10 分钟）"
echo "  3. 页面底部 Artifacts 下载 reader-unsigned-ipa"
echo "  4. 解压得到 reader-1.0.0-unsigned.ipa"
echo "  5. Sideloadly 拖入 IPA + 填 Apple ID → Start"
echo ""
echo " 详细步骤见 SIDELOAD.md"
