#!/bin/bash
# 推送代码到 GitHub 的脚本
# 使用方法: 将 YOUR_GITHUB_REPO_URL 替换为你的 GitHub 仓库地址

GITHUB_REPO_URL="YOUR_GITHUB_REPO_URL"

if [ "$GITHUB_REPO_URL" == "YOUR_GITHUB_REPO_URL" ]; then
    echo "请先设置 GITHUB_REPO_URL 变量为你的 GitHub 仓库地址"
    echo "例如: https://github.com/yourusername/EasyPPID-ControlSystem.git"
    exit 1
fi

echo "添加远程仓库..."
git remote add origin $GITHUB_REPO_URL 2>/dev/null || git remote set-url origin $GITHUB_REPO_URL

echo "推送到 GitHub..."
git push -u origin main

echo "完成！代码已推送到 GitHub"

