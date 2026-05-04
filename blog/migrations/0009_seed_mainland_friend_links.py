from django.db import migrations


LINKS = [
    {
        'name': '掘金',
        'url': 'https://juejin.cn/',
        'avatar': 'https://juejin.cn/favicon.ico',
        'description': '面向开发者的技术社区，前端、后端、AI 与工程实践内容活跃。',
    },
    {
        'name': '开源中国',
        'url': 'https://www.oschina.net/',
        'avatar': 'https://www.oschina.net/favicon.ico',
        'description': '国内开源技术社区，关注开源项目、软件资讯和开发者动态。',
    },
    {
        'name': '知乎',
        'url': 'https://www.zhihu.com/',
        'avatar': 'https://www.zhihu.com/favicon.ico',
        'description': '中文问答社区，适合发现技术、阅读、生活方式相关讨论。',
    },
    {
        'name': '哔哩哔哩',
        'url': 'https://www.bilibili.com/',
        'avatar': 'https://www.bilibili.com/favicon.ico',
        'description': '国内视频社区，技术分享、公开课、游戏与影视内容都很丰富。',
    },
    {
        'name': '博客园',
        'url': 'https://www.cnblogs.com/',
        'avatar': 'https://www.cnblogs.com/favicon.ico',
        'description': '老牌中文技术博客社区，积累了大量开发经验和教程文章。',
    },
    {
        'name': 'Gitee',
        'url': 'https://gitee.com/',
        'avatar': 'https://gitee.com/favicon.ico',
        'description': '国内代码托管平台，适合开源项目托管与协作。',
    },
    {
        'name': '阿里云开发者社区',
        'url': 'https://developer.aliyun.com/',
        'avatar': 'https://developer.aliyun.com/favicon.ico',
        'description': '云计算、数据库、AI 和工程架构相关技术文章与实践案例。',
    },
    {
        'name': '腾讯云开发者',
        'url': 'https://cloud.tencent.com/developer',
        'avatar': 'https://cloud.tencent.com/favicon.ico',
        'description': '腾讯云开发者内容平台，覆盖云原生、后端和行业方案。',
    },
    {
        'name': 'IT之家',
        'url': 'https://www.ithome.com/',
        'avatar': 'https://www.ithome.com/favicon.ico',
        'description': '科技资讯站点，关注硬件、软件、互联网和数码产品动态。',
    },
    {
        'name': '小米',
        'url': 'https://www.mi.com/',
        'avatar': 'https://www.mi.com/favicon.ico',
        'description': '国内科技品牌官网，适合作为产品与设计参考站点。',
    },
]


def seed_mainland_friend_links(apps, schema_editor):
    FriendLink = apps.get_model('blog', 'FriendLink')
    FriendLink.objects.all().delete()
    for index, data in enumerate(LINKS, start=1):
        FriendLink.objects.create(sort_order=index, **data)


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_backfill_all_post_comments'),
    ]

    operations = [
        migrations.RunPython(seed_mainland_friend_links, migrations.RunPython.noop),
    ]
