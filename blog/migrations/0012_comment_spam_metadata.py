from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_comment_status_post_slug_operationlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='approved_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='通过时间'),
        ),
        migrations.AddField(
            model_name='comment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP 地址'),
        ),
        migrations.AddField(
            model_name='comment',
            name='moderation_reason',
            field=models.CharField(blank=True, max_length=255, verbose_name='审核备注'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user_agent',
            field=models.CharField(blank=True, max_length=255, verbose_name='User agent'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', '待审核'),
                    ('approved', '已通过'),
                    ('hidden', '已隐藏'),
                    ('spam', '垃圾评论'),
                ],
                db_index=True,
                default='pending',
                max_length=20,
                verbose_name='审核状态',
            ),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['status', '-created_time'], name='blog_commen_status_859d2c_idx'),
        ),
    ]
