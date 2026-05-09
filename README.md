# 星语博客 - Django 个人内容空间

一个基于 Django 5 构建的个人博客与内容管理系统。项目面向个人技术写作、生活记录、书影音收藏和友链展示，包含前台浏览体验、自定义 Django Admin 后台、评论审核、RSS/Sitemap、静态资源收集、Cloudinary 媒体存储和 Vercel 部署支持。

## 项目亮点

- 文章系统：支持 Markdown 正文、摘要、封面图、分类、标签、置顶、推荐轮播、定时发布和阅读量统计。
- 列表检索：支持首页分页、文章库筛选、分类页、标签页、月份归档和全文搜索。
- 文章详情：自动渲染 Markdown、生成二级/三级标题目录、展示上一篇/下一篇和审核通过的评论。
- 评论管理：前台评论提交、蜜罐字段、频率限制、链接数量限制、屏蔽词检查、垃圾评论识别和后台审核流转。
- 书影音页面：支持电影、书籍、游戏三类收藏，包含封面、评分、状态、创作者、简评和完成日期。
- 友链页面：维护站点名称、链接、头像和描述，支持后台排序。
- 自定义后台：独立 AdminSite，提供仪表盘统计、文章/媒体/友链/评论管理、操作日志、数据备份恢复、SEO 入口和部署健康检查。
- SEO 与订阅：内置 `robots.txt`、`sitemap.xml`、`rss.xml` 和订阅说明页。
- 部署适配：本地默认 SQLite；生产可通过 `DATABASE_URL` 使用 PostgreSQL，通过 `CLOUDINARY_URL` 使用 Cloudinary 存储媒体文件。

## 技术栈

- Python 3
- Django 5.2
- SQLite / PostgreSQL
- Markdown + Pygments
- Pillow
- WhiteNoise
- Cloudinary / django-cloudinary-storage
- Vercel Python Runtime

## 目录结构

```text
blog1/
├── api/
│   └── index.py                  # Vercel 入口，暴露 WSGI application
├── blog/
│   ├── admin.py                  # 自定义后台模型管理、审核动作、操作日志
│   ├── admin_site.py             # 后台首页、健康检查、备份恢复、SEO 页面
│   ├── context_processors.py     # 侧边栏文章、分类、标签、归档、统计数据
│   ├── feeds.py                  # RSS Feed
│   ├── forms.py                  # 评论表单与反垃圾校验
│   ├── models.py                 # 文章、评论、书影音、友链、操作日志模型
│   ├── ops.py                    # 部署健康检查逻辑
│   ├── sitemaps.py               # Sitemap 配置
│   ├── urls.py                   # 博客前台路由
│   ├── views.py                  # 首页、详情、筛选、搜索、评论等视图
│   └── management/commands/      # 示例数据、超管创建、部署检查等命令
├── blogproject/
│   ├── settings.py               # Django 配置、数据库、静态资源、存储后端
│   ├── urls.py                   # 项目总路由
│   └── wsgi.py / asgi.py
├── static/
│   ├── css/                      # 前台与后台样式
│   ├── js/                       # 后台 Markdown 预览、图片压缩、轮播脚本
│   ├── avatar.png
│   └── favicon.ico
├── templates/
│   ├── base.html
│   ├── blog/                     # 前台页面模板
│   └── admin/                    # 自定义后台模板
├── media/                        # 本地上传文件目录
├── build.py                      # Vercel 构建脚本：迁移、建超管、收集静态文件
├── manage.py
├── requirements.txt
└── vercel.json
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/loadingkkl/personal-space.git
cd personal-space
```

### 2. 创建虚拟环境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python manage.py migrate
```

### 5. 创建管理员

交互式创建：

```bash
python manage.py createsuperuser
```

或通过环境变量创建/更新：

```bash
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=your-password
set ADMIN_EMAIL=admin@example.com
python manage.py ensure_superuser
```

PowerShell 可使用：

```powershell
$env:ADMIN_USERNAME="admin"
$env:ADMIN_PASSWORD="your-password"
$env:ADMIN_EMAIL="admin@example.com"
python manage.py ensure_superuser
```

### 6. 可选：生成演示数据

```bash
python manage.py seed
python manage.py seed_media
python manage.py seed_links
```

`seed` 会生成示例文章和封面图；`seed_media` 会生成书影音记录；`seed_links` 会生成友链记录。部分命令会尝试联网抓取图片，网络不可用时会使用降级方案。

### 7. 启动开发服务器

```bash
python manage.py runserver
```

常用地址：

- 前台首页：http://127.0.0.1:8000/
- 管理后台：http://127.0.0.1:8000/admin/
- 文章库：http://127.0.0.1:8000/articles/
- 书影音：http://127.0.0.1:8000/media/
- 友链：http://127.0.0.1:8000/links/
- RSS：http://127.0.0.1:8000/rss.xml
- Sitemap：http://127.0.0.1:8000/sitemap.xml

## 主要页面与路由

| 路由 | 名称 | 说明 |
| --- | --- | --- |
| `/` | 首页 | 最新文章列表与推荐轮播 |
| `/post/id/<pk>/` | 文章详情 | Markdown 渲染、目录、评论、上一篇/下一篇 |
| `/articles/` | 文章库 | 分类、标签、排序筛选 |
| `/category/<name>/` | 分类页 | 按分类查看文章 |
| `/tag/<name>/` | 标签页 | 按标签查看文章 |
| `/archive/<year>/<month>/` | 归档页 | 按月份查看文章 |
| `/search/?q=keyword` | 搜索 | 按标题和正文搜索 |
| `/media/` | 书影音 | 电影、书籍、游戏收藏 |
| `/links/` | 友链 | 友情链接展示 |
| `/about/` | 关于 | 个人介绍页面 |
| `/feeds/` | 订阅页 | RSS、Sitemap、Robots 入口 |
| `/admin/` | 后台 | 内容管理和运维入口 |

## 数据模型概览

### Post

文章模型，包含标题、正文、摘要、封面、创建时间、修改时间、发布时间、分类、标签、作者、阅读量、发布状态、轮播推荐和置顶状态。

发布侧规则：

- 只有 `is_published=True` 且 `publish_time <= 当前时间` 的文章会在前台展示。
- 分类和标签使用轻量字符串字段保存，便于后台直接编辑。
- 标签支持中文逗号和英文逗号输入，保存时会统一去重和格式化。

### Comment

评论模型，包含昵称、邮箱、正文、审核状态、IP、User Agent、审核备注和通过时间。

审核状态：

- `pending`：待审核
- `approved`：已通过
- `hidden`：已隐藏
- `spam`：垃圾评论

### Media

书影音模型，支持 `movie`、`book`、`game` 三种类型，并记录封面、评分、创作者、简评、状态、完成日期和豆瓣链接。

### FriendLink

友链模型，维护站点名称、URL、头像、描述和排序值。

### OperationLog

后台操作日志模型，用于记录新增、修改、删除、审核、备份和恢复等管理动作。

## 后台能力

项目没有直接使用默认 `admin.site`，而是通过 `BlogAdminSite` 定制后台：

- 后台首页展示文章数、已发布文章数、评论数、待审核评论数、书影音数量、阅读量、分类数、标签数和友链数。
- 文章后台支持 Markdown 编辑提示、封面上传大小限制、发布状态标识、置顶和轮播推荐。
- 评论后台支持批量通过、隐藏、标记垃圾评论、移回待审核。
- 媒体后台支持封面预览、类型标识、评分展示和状态筛选。
- 友链后台支持头像预览和排序编辑。
- 操作日志后台只读，避免审计记录被随意修改。
- `/admin/health/` 可查看部署健康检查。
- `/admin/backup/` 支持 JSON 备份导出和恢复。
- `/admin/seo/` 汇总 RSS、Sitemap、Robots 和订阅页地址。

## Markdown 写作支持

文章正文通过 `markdown` 渲染，启用以下扩展：

- `extra`：表格、脚注等扩展语法
- `toc`：标题目录生成
- `codehilite`：代码高亮
- `sane_lists`：更稳定的列表解析

详情页会提取二级和三级标题生成文章目录。后台编辑器还提供 Markdown 预览脚本，正文中不允许直接粘贴 base64 图片，建议上传到 Cloudinary 后使用图片 URL。

## 评论安全策略

评论提交包含多层基础防护：

- 隐藏 `website` 蜜罐字段，用于拦截机器人提交。
- 同一 IP 对同一文章 60 秒内只能提交一次评论。
- 评论正文至少 3 个字符。
- 通过 `COMMENT_MAX_LINKS` 限制正文中的链接数量。
- 通过 `COMMENT_BLOCKED_WORDS` 配置屏蔽词。
- 自动识别常见垃圾关键词、过多换行和过长评论。
- 非垃圾评论默认进入待审核，后台通过后才展示。

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | 生产必填 | 开发用 insecure key | Django 密钥，线上必须单独配置 |
| `DEBUG` | 否 | `True` | 是否开启调试；Vercel 环境未显式设置时自动关闭 |
| `DATABASE_URL` | 生产推荐 | 无 | PostgreSQL 等数据库连接，存在时覆盖 SQLite |
| `CLOUDINARY_URL` | 生产推荐 | 无 | Cloudinary 连接串，存在时媒体文件走 Cloudinary |
| `COMMENT_MAX_LINKS` | 否 | `2` | 单条评论允许的最大链接数 |
| `COMMENT_BLOCKED_WORDS` | 否 | 空 | 评论屏蔽词，多个词用英文逗号分隔 |
| `ADMIN_USERNAME` | 部署可选 | 无 | 构建时创建/更新后台管理员 |
| `ADMIN_PASSWORD` | 部署可选 | 无 | 构建时创建/更新后台管理员 |
| `ADMIN_EMAIL` | 否 | 空 | 管理员邮箱 |
| `VERCEL` | 平台注入 | 无 | 用于识别 Vercel 生产环境 |

## 部署说明

### Vercel 部署流程

项目已包含 `vercel.json`：

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "python build.py",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index"
    }
  ]
}
```

构建时会执行 `build.py`：

1. `python manage.py migrate --run-syncdb`
2. 如果配置了 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`，执行 `python manage.py ensure_superuser`
3. `python manage.py collectstatic --noinput`

部署到 Vercel 时建议配置：

- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `CLOUDINARY_URL`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_EMAIL`

### 数据库建议

本地开发默认使用项目根目录下的 `db.sqlite3`。Vercel 的文件系统不适合持久化 SQLite 数据，线上应配置外部 PostgreSQL，并通过 `DATABASE_URL` 注入。

### 媒体文件建议

本地未配置 `CLOUDINARY_URL` 时，上传文件保存在 `media/`。线上建议配置 Cloudinary，否则用户上传的媒体文件无法可靠持久保存。

## 运维命令

检查 Django 配置：

```bash
python manage.py check
```

执行迁移：

```bash
python manage.py migrate
```

收集静态资源：

```bash
python manage.py collectstatic --noinput
```

创建或更新环境变量指定的管理员：

```bash
python manage.py ensure_superuser
```

查看部署健康检查：

```bash
python manage.py deployment_health
python manage.py deployment_health --json
```

同步本地媒体到 Cloudinary：

```bash
python manage.py sync_media_to_cloudinary
```

## 开发注意事项

- 文章前台查询统一使用“已发布且发布时间不晚于当前时间”的 live posts 逻辑。
- 文章详情每次访问会增加阅读量。
- 评论默认不会立即公开展示，需要后台审核通过。
- 后台图片上传限制为 3MB，并配合前端脚本进行图片压缩。
- 生产环境不要使用仓库中的开发密钥，必须配置 `DJANGO_SECRET_KEY`。
- 线上部署必须谨慎配置 `DATABASE_URL` 和 `CLOUDINARY_URL`，否则数据和上传文件可能无法持久保存。

## 许可证

当前仓库未声明开源许可证。如需公开复用或二次分发，请先补充 LICENSE 文件并明确授权范围。
