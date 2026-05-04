from django.db.models import Count
from .models import Post, Category, Tag, Comment


def blog_sidebar(request):
    recent_posts = Post.objects.filter(is_published=True)[:5]
    categories = Category.objects.annotate(
        num_posts=Count('post')
    ).filter(num_posts__gt=0)
    tags = Tag.objects.annotate(
        num_posts=Count('post')
    ).filter(num_posts__gt=0)
    archive_dates = Post.objects.filter(is_published=True).dates('created_time', 'month', order='DESC')

    stats = {
        'post_count': Post.objects.filter(is_published=True).count(),
        'category_count': Category.objects.count(),
        'comment_count': Comment.objects.count(),
        'tag_count': Tag.objects.count(),
    }

    return {
        'recent_posts': recent_posts,
        'categories': categories,
        'tags': tags,
        'archive_dates': archive_dates,
        'stats': stats,
    }
