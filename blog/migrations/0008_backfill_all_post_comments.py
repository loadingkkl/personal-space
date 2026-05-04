from django.db import migrations


COMMENT_BODIES = [
    '这篇写得很清楚，尤其是中间那段例子很有帮助。',
    '收藏了，后面实践的时候再回来对照看一遍。',
    '结构很顺，读起来没有压力。',
    '这个角度之前没想到，算是补上了一块认知拼图。',
    '如果后面能再加一点踩坑记录就更完整了。',
    '内容很实用，适合快速建立整体印象。',
]


def backfill_all_post_comments(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Comment = apps.get_model('blog', 'Comment')

    names = ['林舟', '小夏', '青木', 'Echo', '北辰', '阿岚']
    posts = Post.objects.filter(is_published=True).order_by('pk')
    for post_index, post in enumerate(posts):
        existing_count = Comment.objects.filter(post=post).count()
        for offset in range(existing_count, 4):
            Comment.objects.get_or_create(
                post=post,
                name=names[(post_index + offset) % len(names)],
                email=f'backfill{post.pk}_{offset}@example.com',
                body=COMMENT_BODIES[(post_index + offset) % len(COMMENT_BODIES)],
            )


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_seed_media_and_comments'),
    ]

    operations = [
        migrations.RunPython(backfill_all_post_comments, migrations.RunPython.noop),
    ]
