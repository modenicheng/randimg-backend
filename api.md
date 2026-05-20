# randimg-backend API 文档

Base URL（本地默认）：`http://127.0.0.1:8000`

鉴权方式：

- 登录接口获取 `access_token`
- 受保护接口使用请求头：`Authorization: Bearer <token>`

---

## 1. 认证

### 1.1 `POST /token`

管理员登录，返回 JWT。

请求类型：`application/x-www-form-urlencoded`

参数：

- `username` (string, required)
- `password` (string, required)

响应示例：

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

## 2. 图片查询

### 2.1 `GET /`

随机返回一张图片。

查询参数：

- `format` (string, default: `json`)：`json` 或 `image`
- `local` (bool, default: `false`)：`true` 时尝试返回本地文件
- `ratio_floor` (float, default: `0`)
- `ratio_ceil` (float, default: `10`)
- `tags` (string, optional)：逗号分隔标签

说明：

- `format=json` 返回图片信息 JSON
- `format=image` 返回 307 跳转到图片地址（或本地文件）

### 2.2 `GET /image/{image_id}`

按 ID 获取图片。

路径参数：

- `image_id` (int, required)

查询参数：

- `format` (string, default: `json`)：`json` 或 `image`
- `local` (bool, default: `false`)

请求头（可选）：

- `Authorization: Bearer <token>`（携带后按管理员身份读取）

返回：

- 200：图片信息 / 图片重定向 / 本地文件
- 404：未找到图片

### 2.3 `GET /list`

分页查询图片列表。

查询参数：

- `offset` (int, default: `0`)
- `limit` (int, default: `30`，服务端会限制最大值)
- `desc` (bool|string, default: `true`)
- `ratio_floor` (float, default: `0`)
- `ratio_ceil` (float, default: `10`)
- `author` (string|int, optional)：作者名模糊匹配或作者 ID
- `accessable` (`true`/`false`/`all`, default: `all`)
- `tags` (string, optional)：逗号分隔标签（中英文）

请求头（可选）：

- `Authorization: Bearer <token>`

说明：

- 未携带有效 token 时，仅返回 `accessable=True` 的图片
- 携带有效 token 时，可按 `accessable` 参数返回更多范围数据

### 2.4 `GET /tags`

获取所有标签。

返回字段包含：

- `id`
- `name`
- `translated_name`
- `search_string`

### 2.5 `GET /statistic`

获取统计信息。

返回示例：

```json
{
  "illust_count": 123,
  "tag_count": 456,
  "author_count": 78
}
```

---

## 3. 图片管理（需鉴权）

### 3.1 `PATCH /image/{image_id}`

更新图片信息（实际更新依赖请求体中的 `id` 字段）。

路径参数：

- `image_id` (int, required)

请求体：`ImageManagementSchema`（可选字段更新），常见字段：

- `id` (int)
- `title` (string)
- `source_url` (string)
- `source_id` (int)
- `colors` (object)
- `width` / `height` / `aspect_ratio`
- `accessable` / `uploaded` / `processed` / `processing`

请求头：

- `Authorization: Bearer <token>`（必需）

### 3.2 `DELETE /image/{image_id}`

当前代码中为占位接口，未实现。

---

## 4. 爬虫任务与处理队列

### 4.1 `GET /crawler`

当前代码中为占位接口，未实现。

### 4.2 `POST /crawler`

创建爬虫任务。

请求体：`CreateCrawlerSchema`

- `task_name` (string)
- `crawl_type` (`RANKING`/`USER`/`SEARCH`)
- `target_user_id` (string, 当 `crawl_type=USER` 时必填)
- `target_start_date` / `target_end_date` (datetime, 当 `crawl_type=RANKING` 时必填)
- `target_search_prompt` (string)

### 4.3 `GET /crawler/image`

图片处理队列读取接口（需鉴权）。

查询参数：

- `init` (bool, default: `false`)

行为：

- `init=true`：重新初始化待处理队列，返回数量
- `init=false`：弹出一个待处理图片并将其标记为 `processing=True`

### 4.4 `POST /crawler/image`

图片处理异常回传（需鉴权），会把图片放回队列头，并更新图片状态。

请求体：JSON，至少应包含 `id`，并可附带状态字段（如 `processing`、`processed` 等）。

### 4.5 `GET /adjust-accessible`

可访问性校验队列读取接口（需鉴权）。

查询参数：

- `init` (bool, default: `false`)

行为：

- `init=true`：扫描 `downloaded=True 且 accessable is None` 的图片并初始化队列
- `init=false`：弹出一个待处理项

### 4.6 `POST /adjust-aaccessible`

向可访问性校验队列回填数据。  
注意：路由名称实际为 `/adjust-aaccessible`（双 `a`），请按实际路径调用。

---

## 5. 错误码概览

- `400`：参数校验失败（如创建爬虫缺必要字段）
- `401`：未授权或 token 无效/过期
- `404`：资源不存在（如图片未找到或队列为空）
- `500`：服务内部错误

---

## 6. 建议

- 本文档以当前代码实现为准，接口真实 schema 以 `/docs` 为最终参考。
