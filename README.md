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