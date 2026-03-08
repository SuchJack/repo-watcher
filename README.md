# 仓库变更监控工具

**定时轮询 GitHub / Gitee 仓库，发现新提交后通过飞书或邮件通知，配置全部在 Web 界面完成。**

**📚 文档** · [English](README_EN.md)

---

## 📖 项目背景

在跟进多个开源项目、依赖库或团队仓库时，我们往往需要**第一时间知道「谁在什么时候提交了什么」**。GitHub/Gitee 自带的 Watch、Star 或邮件提醒要么过于嘈杂、要么不够及时，且无法按自己的节奏统一管理多个仓库；手动刷新页面又费时费力。若能把「仓库有更新」这件事收敛到**自己可控的轮询间隔**，并推送到**日常使用的协作工具**（如飞书群、邮箱），就能在不打扰的前提下不错过重要变更。

本工具正是在这一需求下诞生的：在一个 Web 界面里配置要监控的仓库列表与通知方式，由后端定时轮询并在发现新 commit 时通过飞书或邮件通知，**所有配置都在页面上完成，无需改配置文件或写脚本**。

---

## ✨ 项目简介

本工具用于监控指定仓库的 **新提交**：按可配置的间隔轮询 GitHub/Gitee API，发现 commit 变化后，通过 **飞书 Webhook** 或 **邮箱（SMTP）** 发送通知。所有配置（仓库列表、轮询间隔、通知渠道）均在网页前端完成，无需手改配置文件。

### 适用场景

- 关注多个开源仓库的更新，希望第一时间收到提醒
- 团队仓库有提交时，通过飞书群或邮件同步
- 需要按自定义间隔检查仓库，而不是依赖平台自带的 Watch/Star 通知

---

## 🎯 功能介绍

| 功能 | 说明 |
|------|------|
| **仓库监控** | 支持 GitHub、Gitee；可配置 owner/repo/分支，列表增删改 |
| **轮询间隔** | 可设置 60～86400 秒，保存后立即生效 |
| **仪表盘** | 展示各仓库最新 commit、最后检查时间、是否有更新、累计更新次数 |
| **通知渠道** | 飞书 Webhook（可选签名）、邮箱 SMTP（自配置服务器与账号） |
| **手动检查** | 支持「立即检查」与「清空更新次数」 |
| **配置持久化** | 数据存于本地 JSON，Docker 部署时可挂载目录持久化 |

---

## 🛠️ 技术架构

### 前端

- **框架**：Vue 3 + Vue Router
- **构建**：Vite 6
- **UI**：Element Plus
- **请求**：Axios

### 后端

- **框架**：FastAPI
- **运行**：Uvicorn
- **定时**：APScheduler
- **存储**：JSON 文件（config / repos / state），无需数据库

---

## 📦 使用方法

### 使用 Docker Compose（推荐）

通过 Docker Compose 一键启动前后端，前端 Nginx 托管静态并反向代理 `/api` 到后端。

1. **克隆项目**

```bash
git clone <你的仓库地址>
cd demo9-监控项目
```

2. **启动服务**

```bash
docker compose up -d
```

3. **访问应用**

- **前端**：<http://localhost:3000>
- **后端 API**：<http://localhost:8000>（可选，调试用）

4. **查看日志**

```bash
# 后端日志
docker logs -f repo-monitor-backend

# 前端（Nginx）日志
docker logs -f repo-monitor-frontend
```

5. **停止服务**

```bash
docker compose down
```

6. **更新后重新构建**

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**数据持久化**：配置与状态保存在项目根目录下的 `./data`（挂载到容器的 `/app/backend/data`），重启或重建容器不会丢失。

---

### 从源码运行

#### 环境要求

- Python 3.10+
- Node.js 16+、npm

#### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

需在项目**根目录**执行上述命令（或设置 `PYTHONPATH` 包含根目录），以便 `backend` 包可被正确导入。

#### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器默认运行在 <http://localhost:3001>，Vite 已将 `/api` 代理到 `http://127.0.0.1:8000`。

---

## 📁 项目结构

```
├── backend/                 # Python 后端
│   ├── main.py               # FastAPI 入口、路由、静态托管
│   ├── config.py             # 配置与存储（config/repos/state）
│   ├── scheduler.py          # 定时轮询调度
│   ├── checker/              # 仓库检查（GitHub/Gitee）
│   ├── notifier/             # 通知（飞书、邮件）
│   ├── data/                 # 运行时数据（可挂载）
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Vue 前端
│   ├── src/
│   │   ├── views/            # 仪表盘、仓库管理、设置
│   │   ├── api/              # 请求封装
│   │   └── router/
│   ├── nginx.conf            # 生产环境 Nginx（/api 反向代理）
│   ├── package.json
│   └── Dockerfile
├── data/                     # Docker 挂载目录（持久化）
├── docker-compose.yml
└── README.md
```

---

## 🔧 常见问题

1. **Docker 启动后前端无法访问后端 / 接口 404**  
   确认 `docker-compose` 中 frontend 与 backend 在同一网络；Nginx 中 `proxy_pass http://backend:8000` 的服务名与 compose 中 backend 服务名一致。

2. **轮询间隔改了不生效**  
   保存配置后调度器会 reschedule；若仍不生效，可重启后端容器或再次保存一次配置。

3. **飞书/邮件收不到通知**  
   检查「通知设置」中对应渠道已启用且 URL/ SMTP 配置正确；可先点「立即检查」触发一次，再查看后端日志是否有发送错误。

4. **端口 3000 或 8000 被占用**  
   修改 `docker-compose.yml` 中 `ports`，例如将 `"3000:80"` 改为 `"3080:80"`，访问时使用新端口即可。

---

## 📄 许可证与参考

- 详细设计与 API 说明见 **仓库变更监控工具-概要设计.md**。
- 若本项目对你有帮助，欢迎 Star。
