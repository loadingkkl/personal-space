# 个人博客 - Django

基于 Django 构建的现代个人博客网站。

## 功能特性

- 文章发布与管理（支持分类、标签、封面图）
- 文章搜索
- 按分类 / 标签 / 月份归档浏览
- 评论系统
- 阅读量统计
- 响应式设计，适配手机与桌面
- Django Admin 后台管理

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python manage.py migrate

# 3. 创建管理员账号
python manage.py createsuperuser

# 4. （可选）加载示例数据
python manage.py seed

# 5. 启动开发服务器
python manage.py runserver
```

打开浏览器访问 http://127.0.0.1:8000 即可查看博客。

管理后台：http://127.0.0.1:8000/admin/

## 项目结构

```
blog1/
├── blog/                # 博客应用
│   ├── models.py        # 数据模型（文章、分类、标签、评论）
│   ├── views.py         # 视图
│   ├── urls.py          # URL 路由
│   ├── forms.py         # 表单
│   ├── admin.py         # 后台管理
│   └── context_processors.py  # 侧边栏上下文
├── blogproject/         # 项目配置
├── templates/           # HTML 模板
├── static/css/          # 样式文件
├── media/               # 上传文件
└── manage.py
```
