from django.utils import timezone
from .models import Comment, Post, get_category_items, get_tag_items


def blog_sidebar(request):
    live_posts = Post.objects.filter(is_published=True, publish_time__lte=timezone.now())
    recent_posts = live_posts.order_by('-is_pinned', '-publish_time')[:5]
    categories = get_category_items(live_posts)
    tags = get_tag_items(live_posts)
    archive_dates = live_posts.dates('publish_time', 'month', order='DESC')

    stats = {
        'post_count': live_posts.count(),
        'category_count': len(categories),
        'comment_count': Comment.objects.filter(status=Comment.STATUS_APPROVED).count(),
        'tag_count': len(tags),
    }

    return {
        'recent_posts': recent_posts,
        'categories': categories,
        'tags': tags,
        'archive_dates': archive_dates,
        'stats': stats,
    }
