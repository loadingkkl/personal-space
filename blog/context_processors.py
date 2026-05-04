from django.db.models import Count, Q
from django.utils import timezone
from .models import Post, Category, Tag, Comment


def blog_sidebar(request):
    live_posts = Post.objects.filter(is_published=True, publish_time__lte=timezone.now())
    recent_posts = live_posts.order_by('-is_pinned', '-publish_time')[:5]
    live_filter = Q(post__is_published=True, post__publish_time__lte=timezone.now())
    categories = Category.objects.annotate(
        num_posts=Count('post', filter=live_filter)
    ).filter(num_posts__gt=0)
    tags = Tag.objects.annotate(
        num_posts=Count('post', filter=live_filter)
    ).filter(num_posts__gt=0)
    archive_dates = live_posts.dates('publish_time', 'month', order='DESC')

    stats = {
        'post_count': live_posts.count(),
        'category_count': Category.objects.count(),
        'comment_count': Comment.objects.filter(status=Comment.STATUS_APPROVED).count(),
        'tag_count': Tag.objects.count(),
    }

    return {
        'recent_posts': recent_posts,
        'categories': categories,
        'tags': tags,
        'archive_dates': archive_dates,
        'stats': stats,
    }
