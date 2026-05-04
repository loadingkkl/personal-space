import os

from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib import messages
from django.core import serializers
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone


class BlogAdminSite(AdminSite):
    site_header = '星语博客'
    site_title = '星语管理后台'
    index_title = '管理中心'

    def each_context(self, request):
        context = super().each_context(request)
        is_vercel = bool(os.environ.get('VERCEL'))
        has_database_url = bool(os.environ.get('DATABASE_URL'))
        context.update({
            'admin_environment': 'Vercel 线上' if is_vercel else '本地开发',
            'admin_environment_class': 'production' if is_vercel else 'local',
            'admin_database_label': 'PostgreSQL / DATABASE_URL' if has_database_url else 'SQLite 本地数据库',
            'admin_debug_enabled': settings.DEBUG,
        })
        return context

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('health/', self.admin_view(self.health_view), name='health'),
            path('backup/', self.admin_view(self.backup_view), name='backup'),
        ]
        return custom_urls + urls

    def health_view(self, request):
        from .ops import get_deployment_health

        context = {
            **self.each_context(request),
            'title': '线上运维健康检查',
            'health': get_deployment_health(),
        }
        return TemplateResponse(request, 'admin/health.html', context)

    def backup_view(self, request):
        from .models import Category, Comment, FriendLink, Media, OperationLog, Post, Tag

        models = [Category, Tag, Post, Comment, Media, FriendLink]
        if request.GET.get('download') == '1':
            objects = []
            for model in models:
                objects.extend(model.objects.all())
            payload = serializers.serialize('json', objects, indent=2, use_natural_foreign_keys=False)
            OperationLog.objects.create(
                actor=request.user,
                action=OperationLog.ACTION_BACKUP,
                object_type='站点数据',
                object_repr='导出备份',
                detail=f'导出 {len(objects)} 条记录',
            )
            response = HttpResponse(payload, content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="blog-backup-{timezone.now():%Y%m%d%H%M%S}.json"'
            return response

        restored_count = 0
        if request.method == 'POST' and request.FILES.get('backup_file'):
            content = request.FILES['backup_file'].read().decode('utf-8')
            for item in serializers.deserialize('json', content):
                item.save()
                restored_count += 1
            OperationLog.objects.create(
                actor=request.user,
                action=OperationLog.ACTION_RESTORE,
                object_type='站点数据',
                object_repr='导入备份',
                detail=f'导入 {restored_count} 条记录',
            )
            messages.success(request, f'备份恢复完成，共导入 {restored_count} 条记录。')
            return redirect('admin:backup')

        context = {
            **self.each_context(request),
            'title': '备份与恢复',
            'backup_models': [model._meta.verbose_name for model in models],
        }
        return TemplateResponse(request, 'admin/backup.html', context)

    def index(self, request, extra_context=None):
        from .models import Post, Comment, Media, Category, Tag, FriendLink

        extra_context = extra_context or {}
        extra_context['stats'] = {
            'post_count': Post.objects.count(),
            'published_count': Post.objects.filter(is_published=True).count(),
            'comment_count': Comment.objects.filter(status=Comment.STATUS_APPROVED).count(),
            'pending_comment_count': Comment.objects.filter(status=Comment.STATUS_PENDING).count(),
            'media_count': Media.objects.count(),
            'media_done_count': Media.objects.filter(status='done').count(),
            'total_views': Post.objects.aggregate(s=Sum('views'))['s'] or 0,
            'category_count': Category.objects.count(),
            'tag_count': Tag.objects.count(),
            'link_count': FriendLink.objects.count(),
        }
        extra_context['today'] = timezone.localdate().strftime('%Y年%m月%d日')
        return super().index(request, extra_context=extra_context)


blog_admin_site = BlogAdminSite(name='admin')
