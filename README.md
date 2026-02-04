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

## 本地安全检查（pre-commit）

本项目使用 pre-commit + gitleaks 在提交前自动检查是否存在密钥、Token、密码等敏感信息，避免误提交到远程仓库。

首次在本机使用本仓库时，建议执行：

```bash
pip install pre-commit
pre-commit install
```

之后每次在本仓库中运行 `git commit` 时，都会自动触发安全检查；如检测到疑似敏感信息，提交会被阻止并在终端给出提示。
