from datetime import date, timedelta
from io import BytesIO
import random
import re
import urllib.parse
import urllib.request

from django.core.files.base import ContentFile
from django.db import migrations


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


MEDIA_ITEMS = [
    ('book', '三体', '刘慈欣', 10, 'done', '宏大的宇宙尺度和黑暗森林法则，让科幻感和现实感一起压过来。', 'https://book.douban.com/subject/27077612/', 'https://img3.doubanio.com/view/subject/l/public/s29512502.jpg'),
    ('book', '活着', '余华', 9, 'done', '朴素到锋利的苦难叙事，读完会长久记得福贵这个人。', 'https://book.douban.com/subject/27064488/', 'https://img1.doubanio.com/view/subject/l/public/s29652928.jpg'),
    ('book', '围城', '钱锺书', 9, 'done', '语言机锋密集，婚姻、学术和人情世故都写得又冷又准。', 'https://book.douban.com/subject/1007305/', 'https://img1.doubanio.com/view/subject/l/public/s1070959.jpg'),
    ('book', '明朝那些事儿', '当年明月', 8, 'doing', '把厚重历史讲得有节奏、有温度，适合一口气读下去。', 'https://book.douban.com/subject/26912767/', 'https://img1.doubanio.com/view/subject/l/public/s29195878.jpg'),
    ('book', '人类简史', '尤瓦尔·赫拉利', 8, 'done', '用大跨度重新理解人类文明，很多观点适合作为讨论起点。', 'https://book.douban.com/subject/25862578/', 'https://img2.doubanio.com/view/subject/l/public/s27264181.jpg'),
    ('book', '追风筝的人', '卡勒德·胡赛尼', 8, 'wish', '关于亲情、亏欠和救赎的故事，情绪很浓。', 'https://book.douban.com/subject/1770782/', 'https://img1.doubanio.com/view/subject/l/public/s1727290.jpg'),
    ('movie', '流浪地球2', '郭帆', 9, 'done', '工业完成度和宏大叙事都很扎实，国产科幻的重要一步。', 'https://movie.douban.com/subject/35267208/', ''),
    ('movie', '长安三万里', '谢君伟 / 邹靖', 8, 'done', '唐诗、历史和动画表达结合得很有气韵。', 'https://movie.douban.com/subject/36035676/', ''),
    ('movie', '宇宙探索编辑部', '孔大山', 8, 'done', '荒诞外壳下是非常真诚的孤独和执念。', 'https://movie.douban.com/subject/34941536/', ''),
    ('movie', '隐入尘烟', '李睿珺', 9, 'done', '缓慢、克制，却有非常沉重的生活质地。', 'https://movie.douban.com/subject/35131346/', ''),
    ('movie', '哪吒之魔童降世', '饺子', 8, 'done', '节奏爽利，人物弧光清楚，是很有记忆点的国产动画。', 'https://movie.douban.com/subject/26752088/', ''),
    ('movie', '肖申克的救赎', '弗兰克·德拉邦特', 10, 'done', '希望是个好东西，也许是最好的东西。', 'https://movie.douban.com/subject/1292052/', 'https://img2.doubanio.com/view/photo/l_ratio_poster/public/p480747492.jpg'),
    ('game', '黑神话：悟空', '游戏科学', 9, 'done', '美术、动作和东方神话气质很突出，国产 3A 的重要作品。', 'https://www.douban.com/game/35184766/', 'https://img3.doubanio.com/view/photo/albumicon/public/p2617819017.jpg'),
    ('game', '原神', '米哈游', 8, 'doing', '开放世界、角色收集和持续更新结合得很成熟。', 'https://www.douban.com/game/35184766/', ''),
    ('game', '崩坏：星穹铁道', '米哈游', 8, 'done', '回合制包装很现代，角色塑造和演出都在线。', 'https://www.douban.com/game/35184766/', ''),
    ('game', '戴森球计划', '柚子猫游戏', 9, 'done', '自动化建造的正反馈非常强，越铺越停不下来。', 'https://www.douban.com/game/35184766/', ''),
    ('game', '江南百景图', '椰岛游戏', 7, 'wish', '题材和美术辨识度高，适合轻量经营。', 'https://www.douban.com/game/35184766/', ''),
    ('game', '中国式家长', '墨鱼玩游戏', 8, 'done', '用轻松机制包住了很有共鸣的成长压力。', 'https://www.douban.com/game/35184766/', ''),
]


COMMENT_BODIES = [
    '这篇写得很清楚，尤其是中间那段例子很有帮助。',
    '收藏了，后面实践的时候再回来对照看一遍。',
    '结构很顺，读起来没有压力。',
    '这个角度之前没想到，算是补上了一块认知拼图。',
    '如果后面能再加一点踩坑记录就更完整了。',
    '内容很实用，适合快速建立整体印象。',
    '配图和小标题都挺舒服，阅读体验不错。',
    '这类主题很适合继续写成一个系列。',
    '看完之后想自己动手试一下。',
    '解释得比官方文档更接近日常使用场景。',
]


def fetch_url(url, referer=None, timeout=12):
    headers = dict(HEADERS)
    if referer:
        headers['Referer'] = referer
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_bing_cover(title, media_type):
    suffix = '书籍封面' if media_type == 'book' else '电影海报' if media_type == 'movie' else '游戏封面'
    query = urllib.parse.quote(f'{title} {suffix}')
    search_url = f'https://cn.bing.com/images/search?q={query}&first=1&count=8&qft=+filterui:aspect-tall'
    html = fetch_url(search_url).decode('utf-8', errors='ignore')
    urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+?\.(?:jpg|jpeg|png|webp))', html, re.I)
    for image_url in urls[:5]:
        try:
            data = fetch_url(image_url)
            if len(data) > 5000:
                return data
        except Exception:
            continue
    return None


def normalize_image(data):
    try:
        from PIL import Image

        image = Image.open(BytesIO(data)).convert('RGB')
        image.thumbnail((720, 1080))
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=88)
        return buffer.getvalue()
    except Exception:
        return data


def seed_media_and_comments(apps, schema_editor):
    Media = apps.get_model('blog', 'Media')
    Post = apps.get_model('blog', 'Post')
    Comment = apps.get_model('blog', 'Comment')

    Media.objects.all().delete()
    today = date.today()

    for index, (media_type, title, creator, rating, status, summary, douban_url, cover_url) in enumerate(MEDIA_ITEMS, start=1):
        item = Media.objects.create(
            title=title,
            media_type=media_type,
            creator=creator,
            rating=rating,
            status=status,
            summary=summary,
            douban_url=douban_url,
            finished_date=today - timedelta(days=index * 6) if status in ('done', 'doing') else None,
        )

        image_data = None
        try:
            if cover_url:
                image_data = fetch_url(cover_url, referer=douban_url)
            else:
                image_data = fetch_bing_cover(title, media_type)
        except Exception:
            image_data = None

        if image_data:
            filename = f'media_seed_{index:02d}.jpg'
            item.cover.save(filename, ContentFile(normalize_image(image_data)), save=True)

    posts = list(Post.objects.filter(is_published=True).order_by('pk'))
    if not posts:
        return

    names = ['林舟', '小夏', '青木', 'Echo', '北辰', '阿岚', 'Ming', '拾光']
    for index, post in enumerate(posts[:15]):
        for offset in range(4):
            body = COMMENT_BODIES[(index + offset) % len(COMMENT_BODIES)]
            name = names[(index + offset) % len(names)]
            Comment.objects.get_or_create(
                post=post,
                name=name,
                email=f'user{index}_{offset}@example.com',
                body=body,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_delete_self_cultivation_post'),
    ]

    operations = [
        migrations.RunPython(seed_media_and_comments, migrations.RunPython.noop),
    ]
