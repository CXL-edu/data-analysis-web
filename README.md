# 数据分析Agent

详情请访问官网：http://ai-messages.cn/


<br>
<br>
<br>



## 技术栈

本项目基于以下框架：
- 前端框架 [Next.js](https://nextjs.org)
- 样式库 [Tailwindcss](https://tailwindcss.com/)
- 文档框架 [Fumadocs](https://fumadocs.vercel.app)


## 启动命令
```bash
nohup npx next start -p `端口号` &  # 设置nginx映射的端口
disown %1   # 移除第一个作业，使得不会因为端口ssh连接导致后台进程失效
jobs  # 查看作业列表
```

## 本地安全检查（commit / push 前）

本项目通过 **仓库内 Git 钩子**（`.githooks`）统一做提交与推送前检查：

- **pre-commit**：pre-commit 框架（YAML、尾随空格、合并冲突等）
- **pre-push**：gitleaks 全仓库扫描，避免密钥、Token、密码等敏感信息被推送

**克隆或拉取本仓库后，只需在本机执行一次：**

```bash
./scripts/setup-git-hooks.sh
```

（或手动执行：`git config core.hooksPath .githooks`）

建议再安装 pre-commit 与 gitleaks，以便检查生效：

```bash
pip install pre-commit
pre-commit install-hooks
# gitleaks 请按官方文档安装：https://github.com/gitleaks/gitleaks
```

之后每次 `git commit` / `git push` 都会自动跑上述检查；未安装时对应钩子会跳过并提示。
