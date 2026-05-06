from django.db import migrations, models


def copy_taxonomy_to_post(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.select_related('category').prefetch_related('tags'):
        category_name = post.category.name if post.category_id else '未分类'
        tag_names = ', '.join(tag.name for tag in post.tags.all().order_by('name'))
        post.category_name = category_name
        post.tag_names = tag_names
        post.save(update_fields=['category_name', 'tag_names'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_alter_post_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='category_name',
            field=models.CharField(db_index=True, default='未分类', max_length=100, verbose_name='分类'),
        ),
        migrations.AddField(
            model_name='post',
            name='tag_names',
            field=models.CharField(blank=True, help_text='多个标签请用逗号分隔', max_length=255, verbose_name='标签'),
        ),
        migrations.RunPython(copy_taxonomy_to_post, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='post',
            name='category',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
