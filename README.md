# randimg-backend

随机图片后端服务，基于 FastAPI + SQLAlchemy，提供：

- 随机图片与图片列表查询
- 图片标签、统计信息查询
- 管理员登录与图片元数据更新
- 爬虫任务创建与图片处理队列接口

项目入口文件：`/home/runner/work/randimg-backend/randimg-backend/main.py`  
API 文档：`/home/runner/work/randimg-backend/randimg-backend/api.md`

## 1. 环境要求

- Python 3.8+
- PostgreSQL（Alembic 默认示例为 PostgreSQL）

## 2. 安装依赖

```bash
cd /home/runner/work/randimg-backend/randimg-backend
pip install -r requirements.txt
```

## 3. 配置

仓库中有多个配置文件采用本地私有配置方式（未提交到 Git）：

### 3.1 根目录 `configs.py`

请在 `/home/runner/work/randimg-backend/randimg-backend/configs.py` 创建至少以下字段：

- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CDN_BASE_URL`
- `IMAGE_DIR`

### 3.2 数据库配置 `db/configs.py`

请在 `/home/runner/work/randimg-backend/randimg-backend/db/configs.py` 创建：

- `DATABASE_URL`（SQLAlchemy 连接串）

### 3.3 爬虫配置 `crawlers/configs.py`

参考模板：

`/home/runner/work/randimg-backend/randimg-backend/crawlers/configs_template.py`

## 4. 数据库迁移

```bash
cd /home/runner/work/randimg-backend/randimg-backend
alembic upgrade head
```

## 5. 启动服务

```bash
cd /home/runner/work/randimg-backend/randimg-backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

服务启动后可访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 6. 创建管理员账号

```bash
cd /home/runner/work/randimg-backend/randimg-backend
python create_admin.py
```

## 7. 代码质量检查（现有）

仓库当前提供的工作流为 Pylint：

```bash
cd /home/runner/work/randimg-backend/randimg-backend
pylint $(git ls-files '*.py')
```

## 8. API 说明

详细接口文档见：

- `/home/runner/work/randimg-backend/randimg-backend/api.md`
