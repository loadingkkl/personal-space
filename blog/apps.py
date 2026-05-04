from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = '博客管理'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = '星语管理后台'
        admin.site.site_title = '星语管理后台'
        admin.site.index_title = '仪表盘'
