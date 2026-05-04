from django.db import migrations


def delete_self_cultivation_post(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Post.objects.filter(
        title='程序员的自我修养',
        category__name='生活随笔',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_friendlink'),
    ]

    operations = [
        migrations.RunPython(delete_self_cultivation_post, migrations.RunPython.noop),
    ]
