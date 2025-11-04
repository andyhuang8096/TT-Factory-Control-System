# 推送代码到 GitHub 的 PowerShell 脚本
# 使用方法: 将 $GITHUB_REPO_URL 替换为你的 GitHub 仓库地址

$GITHUB_REPO_URL = "YOUR_GITHUB_REPO_URL"

if ($GITHUB_REPO_URL -eq "YOUR_GITHUB_REPO_URL") {
    Write-Host "请先设置 `$GITHUB_REPO_URL 变量为你的 GitHub 仓库地址" -ForegroundColor Red
    Write-Host "例如: https://github.com/yourusername/TT_PPID_CS.git" -ForegroundColor Yellow
    exit 1
}

Write-Host "检查远程仓库..." -ForegroundColor Cyan
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "添加远程仓库..." -ForegroundColor Cyan
    git remote add origin $GITHUB_REPO_URL
} else {
    Write-Host "更新远程仓库地址..." -ForegroundColor Cyan
    git remote set-url origin $GITHUB_REPO_URL
}

Write-Host "推送到 GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n完成！代码已推送到 GitHub" -ForegroundColor Green
    Write-Host "你可以在 GitHub 上创建 Pull Request 了" -ForegroundColor Green
} else {
    Write-Host "`n推送失败，请检查网络连接和仓库权限" -ForegroundColor Red
}

