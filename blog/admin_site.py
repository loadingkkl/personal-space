from django.contrib.admin import AdminSite
from django.db.models import Sum
from django.utils import timezone


class BlogAdminSite(AdminSite):
    site_header = '星语博客'
    site_title = '星语管理后台'
    index_title = '管理中心'

    def index(self, request, extra_context=None):
        from .models import Post, Comment, Media, Category, Tag, FriendLink

        extra_context = extra_context or {}
        extra_context['stats'] = {
            'post_count': Post.objects.count(),
            'published_count': Post.objects.filter(is_published=True).count(),
            'comment_count': Comment.objects.count(),
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
