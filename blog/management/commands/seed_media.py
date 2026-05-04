import random
import re
import time
import urllib.request
from datetime import date, timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from blog.models import Media


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

PALETTES = {
    'movie': [(220, 38, 38), (248, 113, 113)],
    'book': [(79, 70, 229), (129, 140, 248)],
    'game': [(16, 185, 129), (52, 211, 153)],
}


def make_fallback_cover(title, media_type, width=300, height=450):
    c1, c2 = PALETTES.get(media_type, [(100, 100, 100), (180, 180, 180)])
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(c1[0] + (c2[0] - c1[0]) * y / height)
        g = int(c1[1] + (c2[1] - c1[1]) * y / height)
        b = int(c1[2] + (c2[2] - c1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    for _ in range(4):
        cx, cy = random.randint(0, width), random.randint(0, height)
        cr = random.randint(30, 120)
        ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255, 20))
        img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("msyh.ttc", 26)
    except (OSError, IOError):
        font = ImageFont.load_default()

    lines, line = [], ''
    for ch in title:
        test = line + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > width - 40:
            lines.append(line)
            line = ch
        else:
            line = test
    if line:
        lines.append(line)

    total_h = len(lines) * 36
    y_start = (height - total_h) // 2
    for i, ln in enumerate(lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        tw = bbox[2] - bbox[0]
        tx = (width - tw) // 2
        ty = y_start + i * 36
        draw.text((tx + 1, ty + 1), ln, font=font, fill=(0, 0, 0, 60))
        draw.text((tx, ty), ln, font=font, fill=(255, 255, 255))

    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()


def fetch_url(url, timeout=10):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_douban_cover(douban_url):
    """Try to extract and download the cover image from a Douban page."""
    try:
        html = fetch_url(douban_url).decode('utf-8', errors='ignore')
        patterns = [
            r'<img[^>]+src="(https://img\d+\.doubanio\.com/view/subject/[^"]+)"',
            r'"image"\s*:\s*"(https://img\d+\.doubanio\.com/view/subject/[^"]+)"',
            r'data-src="(https://img\d+\.doubanio\.com/view/subject/[^"]+)"',
        ]
        for pat in patterns:
            m = re.search(pat, html)
            if m:
                img_url = m.group(1)
                img_url = re.sub(r'/s_ratio_poster/', '/l_ratio_poster/', img_url)
                img_url = re.sub(r'/view/subject/s/', '/view/subject/l/', img_url)
                return fetch_url(img_url)
    except Exception:
        pass
    return None


def fetch_cover_from_bing(keyword):
    """Search Bing Images (cn.bing.com) for a matching cover image."""
    try:
        search_url = (
            f'https://cn.bing.com/images/search?q={urllib.request.quote(keyword + " 海报")}'
            f'&first=1&count=5&qft=+filterui:aspect-tall'
        )
        html = fetch_url(search_url, timeout=10).decode('utf-8', errors='ignore')
        pattern = r'murl&quot;:&quot;(https?://[^&]+?\.(?:jpg|jpeg|png))'
        matches = re.findall(pattern, html, re.IGNORECASE)
        for img_url in matches[:3]:
            try:
                data = fetch_url(img_url, timeout=10)
                if len(data) > 5000:
                    return data
            except Exception:
                continue
    except Exception:
        pass
    return None


def fetch_cover_fallback(title):
    """Fallback: get a seeded image from picsum."""
    try:
        search_url = f'https://picsum.photos/seed/{urllib.request.quote(title)}/300/450'
        return fetch_url(search_url, timeout=12)
    except Exception:
        pass
    return None


MEDIA_DATA = [
    # ===== 影视 =====
    {
        'title': '星际穿越',
        'media_type': 'movie',
        'creator': '克里斯托弗·诺兰',
        'rating': 9,
        'summary': '穿越虫洞的科幻史诗，关于爱与时间的终极探索。',
        'douban_url': 'https://movie.douban.com/subject/1889243/',
        'status': 'done', 'days_ago': 10,
    },
    {
        'title': '千与千寻',
        'media_type': 'movie',
        'creator': '宫崎骏',
        'rating': 10,
        'summary': '最好的动画电影之一，奇幻世界里的成长故事。',
        'douban_url': 'https://movie.douban.com/subject/1291561/',
        'status': 'done', 'days_ago': 30,
    },
    {
        'title': '肖申克的救赎',
        'media_type': 'movie',
        'creator': '弗兰克·德拉邦特',
        'rating': 10,
        'summary': '希望是个好东西。经典中的经典，百看不厌。',
        'douban_url': 'https://movie.douban.com/subject/1292052/',
        'status': 'done', 'days_ago': 60,
    },
    {
        'title': '沙丘2',
        'media_type': 'movie',
        'creator': '丹尼斯·维伦纽瓦',
        'rating': 8,
        'summary': '视觉盛宴，史诗级的科幻巨制。',
        'douban_url': 'https://movie.douban.com/subject/35575567/',
        'status': 'done', 'days_ago': 45,
    },
    {
        'title': '奥本海默',
        'media_type': 'movie',
        'creator': '克里斯托弗·诺兰',
        'rating': 9,
        'summary': '原子弹之父的传记，诺兰叙事依旧精彩。',
        'douban_url': 'https://movie.douban.com/subject/35593344/',
        'status': 'done', 'days_ago': 90,
    },
    {
        'title': '你的名字',
        'media_type': 'movie',
        'creator': '新海诚',
        'rating': 8,
        'summary': '美到窒息的画面，跨越时空的爱情。',
        'douban_url': 'https://movie.douban.com/subject/26683290/',
        'status': 'done', 'days_ago': 120,
    },
    {
        'title': '漫长的季节',
        'media_type': 'movie',
        'creator': '辛爽',
        'rating': 9,
        'summary': '往前看，别回头。东北背景下的悬疑佳作。',
        'douban_url': 'https://movie.douban.com/subject/35588177/',
        'status': 'done', 'days_ago': 25,
    },
    {
        'title': '绝命毒师',
        'media_type': 'movie',
        'creator': '文斯·吉里根',
        'rating': 10,
        'summary': '电视剧的天花板。沃尔特的堕落之路。',
        'douban_url': 'https://movie.douban.com/subject/2373195/',
        'status': 'done', 'days_ago': 130,
    },

    # ===== 书籍 =====
    {
        'title': '三体',
        'media_type': 'book',
        'creator': '刘慈欣',
        'rating': 10,
        'summary': '中国科幻的巅峰之作。黑暗森林法则让人细思极恐。',
        'douban_url': 'https://book.douban.com/subject/2567698/',
        'status': 'done', 'days_ago': 15,
    },
    {
        'title': '百年孤独',
        'media_type': 'book',
        'creator': '加西亚·马尔克斯',
        'rating': 9,
        'summary': '魔幻现实主义的巅峰，孤独是永恒的主题。',
        'douban_url': 'https://book.douban.com/subject/6082808/',
        'status': 'done', 'days_ago': 50,
    },
    {
        'title': '小王子',
        'media_type': 'book',
        'creator': '圣埃克苏佩里',
        'rating': 9,
        'summary': '写给大人的童话，重要的东西肉眼看不见。',
        'douban_url': 'https://book.douban.com/subject/1084336/',
        'status': 'done', 'days_ago': 80,
    },
    {
        'title': '人类简史',
        'media_type': 'book',
        'creator': '尤瓦尔·赫拉利',
        'rating': 8,
        'summary': '重新理解人类文明的演进，视角独特。',
        'douban_url': 'https://book.douban.com/subject/25985021/',
        'status': 'done', 'days_ago': 100,
    },
    {
        'title': '被讨厌的勇气',
        'media_type': 'book',
        'creator': '岸见一郎 / 古贺史健',
        'rating': 8,
        'summary': '阿德勒心理学的通俗解读，一切烦恼都来自人际关系。',
        'douban_url': 'https://book.douban.com/subject/26369699/',
        'status': 'doing', 'days_ago': 3,
    },
    {
        'title': '活着',
        'media_type': 'book',
        'creator': '余华',
        'rating': 9,
        'summary': '人是为了活着本身而活着，而不是为了活着之外的任何事物。',
        'douban_url': 'https://book.douban.com/subject/4913064/',
        'status': 'done', 'days_ago': 70,
    },

    # ===== 游戏 =====
    {
        'title': '塞尔达传说：王国之泪',
        'media_type': 'game',
        'creator': '任天堂',
        'rating': 10,
        'summary': '开放世界的天花板，物理引擎和创造力的完美结合。',
        'douban_url': 'https://www.douban.com/game/35494erta/',
        'status': 'done', 'days_ago': 20,
    },
    {
        'title': '艾尔登法环',
        'media_type': 'game',
        'creator': 'FromSoftware',
        'rating': 9,
        'summary': '魂系开放世界，宫崎英高的奇幻史诗。难但上瘾。',
        'douban_url': 'https://www.douban.com/game/35044erta/',
        'status': 'done', 'days_ago': 70,
    },
    {
        'title': '博德之门3',
        'media_type': 'game',
        'creator': '拉瑞安工作室',
        'rating': 10,
        'summary': 'CRPG 新标杆，选择自由度令人叹为观止。',
        'douban_url': 'https://www.douban.com/game/30208erta/',
        'status': 'done', 'days_ago': 40,
    },
    {
        'title': '黑神话：悟空',
        'media_type': 'game',
        'creator': '游戏科学',
        'rating': 9,
        'summary': '国产3A大作，西游题材的重新演绎。',
        'douban_url': 'https://www.douban.com/game/35230954/',
        'status': 'done', 'days_ago': 5,
    },
    {
        'title': '空洞骑士',
        'media_type': 'game',
        'creator': 'Team Cherry',
        'rating': 9,
        'summary': '银河恶魔城类的巅峰之作，手绘风格令人沉醉。',
        'douban_url': 'https://www.douban.com/game/27100419/',
        'status': 'done', 'days_ago': 90,
    },
]


class Command(BaseCommand):
    help = '生成示例书影游数据（含豆瓣链接和封面图）'

    def handle(self, *args, **options):
        Media.objects.all().delete()
        today = date.today()

        self.stdout.write('正在创建书影游记录并抓取封面...\n')
        for i, data in enumerate(MEDIA_DATA):
            finished = None
            if data['status'] in ('done', 'doing'):
                finished = today - timedelta(days=data['days_ago'])

            item = Media.objects.create(
                title=data['title'],
                media_type=data['media_type'],
                creator=data.get('creator', ''),
                rating=data['rating'],
                summary=data.get('summary', ''),
                status=data['status'],
                finished_date=finished,
                douban_url=data.get('douban_url', ''),
            )

            img_data = None
            source = ''
            self.stdout.write(f'  [{i+1:2d}/{len(MEDIA_DATA)}] {data["title"]} ... ', ending='')

            # 1) Try Douban cover
            if data.get('douban_url'):
                img_data = fetch_douban_cover(data['douban_url'])
                if img_data:
                    source = 'douban'
                time.sleep(0.3)

            # 2) Try Bing Images wallpaper search
            if not img_data:
                img_data = fetch_cover_from_bing(data['title'])
                if img_data:
                    source = 'bing'
                time.sleep(0.3)

            # 3) Fallback: picsum with title seed
            if not img_data:
                img_data = fetch_cover_fallback(data['title'])
                if img_data:
                    source = 'picsum'

            # 4) Generate with Pillow
            if not img_data:
                img_data = make_fallback_cover(data['title'], data['media_type'])
                source = 'generated'

            filename = f'media_{i+1:02d}.jpg'
            item.cover.save(filename, ContentFile(img_data), save=True)
            self.stdout.write(self.style.SUCCESS(f'OK ({source})'))

        counts = {}
        for key, label in Media.MEDIA_TYPES:
            counts[label] = Media.objects.filter(media_type=key).count()
        total = Media.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n完成！共 {total} 条记录'))
        for label, cnt in counts.items():
            self.stdout.write(f'  {label}: {cnt}')
