# 提交到 GitHub 的步骤

## 方法 1: 如果已有 GitHub 仓库

1. 添加远程仓库：
```bash
git remote add origin https://github.com/你的用户名/仓库名.git
```

2. 推送代码：
```bash
git push -u origin main
```

3. 在 GitHub 上创建 Pull Request

## 方法 2: 创建新的 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库（不要初始化 README）
3. 复制仓库地址后运行：
```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

## 方法 3: 使用 GitHub CLI

如果已安装 GitHub CLI：
```bash
gh repo create EasyPPID-ControlSystem --public --source=. --remote=origin --push
```

