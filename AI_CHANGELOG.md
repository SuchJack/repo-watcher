# AI 变更日志

## 2026-04-09

### 变更摘要
- 为 GitHub、Gitee 和飞书的 HTTP 请求增加了可选的 Worker 中转支持。
- 未配置中转地址时，默认仍然保持直连。
- 在设置页中增加了按平台配置中转地址的输入项。

### 涉及文件
- `backend/http_relay.py`
- `backend/config.py`
- `backend/scheduler.py`
- `backend/checker/github.py`
- `backend/checker/gitee.py`
- `backend/notifier/feishu.py`
- `frontend/src/views/Settings.vue`

### 说明
- 中转模式通过 Worker 发送 `url`、`method`、`headers` 以及可选的 `body` 来完成请求转发。
- 直连请求统一通过共享请求层执行，并使用 `trust_env=False`，避免受到进程级代理环境变量的干扰。
- 中转地址在配置接口返回时会按敏感字段处理。

### 验证情况
- 已通过：`python -m compileall /www/data/repo-watcher/backend`
- 未成功执行：`npm -C /www/data/repo-watcher/frontend run build`，原因是当前环境缺少本地 `vite` 依赖，`node_modules` 不存在。

## 2026-04-10

### 变更摘要
- 将 Cloudflare Worker 中转地址接入运行配置，用于 GitHub、Gitee 和飞书。
- 验证了该 Worker 可以完成项目当前使用的仓库检查请求和飞书机器人通知请求。

### 运行配置
- `github_relay_url` 设置为 `https://jolly-morning-4b9b.lkun42844.workers.dev/`
- `gitee_relay_url` 设置为 `https://jolly-morning-4b9b.lkun42844.workers.dev/`
- `feishu_relay_url` 设置为 `https://jolly-morning-4b9b.lkun42844.workers.dev/`

### 涉及文件
- `data/config.json`

### 验证情况
- Worker 根地址可访问；直接 `GET` 返回 `HTTP 400`，符合该中转接口要求通过 JSON 提交请求参数的预期。
- GitHub 中转已验证，通过带认证信息的请求成功访问 `spring-ai-alibaba/DataAgent`。
- Gitee 中转已验证，成功访问 `yudaocode/yudao-ui-admin-vue3`。
- 飞书中转已验证，测试机器人消息返回 `code: 0`。

### 说明
- 2026-04-09 已完成代码层对 Worker 中转模式的支持，本次主要是运行配置接入和联通性验证。
- 当前工作区中的 `data/config.json` 仍然是未纳入 Git 跟踪的文件。
