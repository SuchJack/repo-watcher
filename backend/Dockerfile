# 后端镜像：Python + FastAPI
FROM python:3.12-slim

WORKDIR /app

# 复制后端代码（构建上下文为 backend/）
COPY . /app/backend/

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 从项目根运行，使 backend 包可被导入
WORKDIR /app
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
