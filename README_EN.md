# Repo Change Monitor

**Poll GitHub / Gitee repos on a schedule; get notified via Feishu or email when new commits appear. All configuration is done in the web UI.**

**📚 Docs** · [中文](README.md)

---

## 📖 Background

When you follow many open-source projects, dependencies, or team repos, you often need to know **as soon as possible who committed what and when**. Built-in GitHub/Gitee Watch, Star, or email alerts are either too noisy or not timely enough, and you can’t manage multiple repos on your own schedule; manually refreshing pages is tedious. This tool lets you control the **polling interval** and send updates to tools you already use (e.g. Feishu, email), so you don’t miss important changes without being overwhelmed.

The app provides a single web interface: configure the repos to watch and how to notify; the backend polls on a schedule and sends Feishu or email notifications when it detects new commits. **Everything is configured in the UI—no config files or scripts.**

---

## 😤 Problems It Solves

| Pain point | What this tool does |
|------------|----------------------|
| **Too many repos, platform notifications are messy** | One dashboard shows the latest commit, last check time, and update status for all monitored repos. |
| **Don’t want to rely on platform Watch/email** | Uses its own polling with a configurable interval (60s–24h); changes take effect immediately. |
| **Want notifications in Feishu or work email** | Feishu Webhook and custom SMTP; updates go straight to your workflow. |
| **Config means editing YAML/scripts** | Repo list, poll interval, Feishu URL, SMTP—all set in the web form; zero config files. |
| **Just need “has there been a new commit?”** | Focused on commit detection and notification only; simple logic and one-command Docker deployment with persistent data. |

---

## ✨ Overview

The tool monitors **new commits** in selected repos: it polls GitHub/Gitee APIs at a configurable interval and sends notifications via **Feishu Webhook** or **email (SMTP)** when commits change. All settings (repo list, poll interval, notification channels) are managed in the web UI—no manual config editing.

### Use cases

- Track multiple open-source repos and get notified quickly
- Sync team repo activity to a Feishu group or email
- Use a custom poll interval instead of platform Watch/Star notifications

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Login** | Backend requires login; default **admin** / **admin**. Change password after first login under **Settings → Change password**. |
| **Repo monitoring** | GitHub and Gitee; configure owner/repo/branch; add, edit, remove from list |
| **Poll interval** | 60–86400 seconds; takes effect immediately after save |
| **Dashboard** | Latest commit, last check time, update status, and update count per repo |
| **Notifications** | Feishu Webhook (optional signature), SMTP (your server and account) |
| **Manual actions** | “Check now” and “Clear update count” |
| **Persistence** | Data stored in local JSON; use a volume in Docker to persist |

---

## 🛠️ Tech Stack

### Frontend

- **Framework**: Vue 3 + Vue Router  
- **Build**: Vite 6  
- **UI**: Element Plus  
- **HTTP**: Axios  

### Backend

- **Framework**: FastAPI  
- **Server**: Uvicorn  
- **Scheduler**: APScheduler  
- **Auth**: JWT + bcrypt (single user admin; password configurable or default)  
- **Storage**: JSON files (config / repos / state); no database  

---

## 📦 Usage

### Docker Compose (recommended)

One command starts both frontend and backend; Nginx serves the frontend and proxies `/api` to the backend.

1. **Clone**

```bash
git clone https://github.com/SuchJack/repo-watcher
cd repo-watcher
```

2. **Start**

```bash
docker compose up -d
```

3. **Open**

- **Frontend**: <http://localhost:3000>  
- **Backend API**: <http://localhost:8000> (optional, for debugging)

You’ll see the login page first. With no admin password configured, use username **admin** and password **admin**; **change the password after first login under Settings → Change password**. To set a custom initial password, use the `ADMIN_PASSWORD` env var or write an `admin_password` bcrypt hash into `backend/data/config.json` .

4. **Logs**

```bash
docker logs -f repo-monitor-backend
docker logs -f repo-monitor-frontend
```

5. **Stop**

```bash
docker compose down
```

6. **Rebuild after update**

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Data**: Config and state live under `./data` (mounted to `/app/backend/data` in the container); they survive restarts and rebuilds.

---

### Run from source

**Requirements**: Python 3.10+, Node.js 16+, npm

**Backend** (run from project root):

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

(If you are already in `backend`, run `cd ..` first.)

**Frontend**:

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server runs at <http://localhost:3000>; Vite proxies `/api` to `http://127.0.0.1:8000`. First visit shows the login page; default credentials are **admin** / **admin**; change the password under **Settings → Change password** after logging in.

---

## 📁 Project structure

```
├── backend/                 # Python backend
│   ├── main.py               # FastAPI app, routes, static serve
│   ├── config.py             # Config & storage (config/repos/state)
│   ├── auth.py               # Login (JWT, default password, change password)
│   ├── scheduler.py          # Poll scheduler
│   ├── checker/              # GitHub/Gitee checkers
│   ├── notifier/             # Feishu, email
│   ├── data/                 # Runtime data (mountable)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Vue frontend
│   ├── src/
│   │   ├── views/            # Dashboard, repos, settings, login
│   │   ├── api/
│   │   └── router/
│   ├── nginx.conf            # Nginx: static + /api proxy
│   ├── package.json
│   └── Dockerfile
├── data/                     # Docker volume (persistence)
├── docker-compose.yml
├── 仓库变更监控工具-概要设计.md   # Design doc (Chinese)
├── README.md
└── README_EN.md
```

---

## 🔧 FAQ

1. **Default login**  
   Use **admin** / **admin** when no admin password is configured. Change it after first login under **Settings → Change password**. For a custom password, set the `ADMIN_PASSWORD` env var or add `admin_password` (bcrypt hash) to `backend/data/config.json`.

2. **Frontend can’t reach backend / API 404**  
   Ensure frontend and backend are on the same Docker network and Nginx `proxy_pass` uses the service name `backend:8000`.

3. **Poll interval change doesn’t apply**  
   Config save triggers a reschedule. If it still doesn’t, restart the backend container or save config again.

4. **No Feishu/email notifications**  
   Check that the channel is enabled and URL/SMTP are correct in Settings. Trigger “Check now” and check backend logs for send errors.

5. **Port 3000 or 8000 in use**  
   Change `ports` in `docker-compose.yml` (e.g. `"3080:80"`) and use the new port.

---

## 📄 License & reference

- If this project helps you, a Star is appreciated.
