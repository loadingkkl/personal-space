import urllib.request
import re
from django.core.management.base import BaseCommand
from blog.models import FriendLink

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

LINKS = [
    {'name': '阮一峰的网络日志', 'url': 'https://www.ruanyifeng.com/blog/', 'description': '科技爱好者周刊，分享技术与人文'},
    {'name': '张鑫旭博客', 'url': 'https://www.zhangxinxu.com/wordpress/', 'description': 'CSS 大神，前端技术深度好文'},
    {'name': '廖雪峰的官方网站', 'url': 'https://www.liaoxuefeng.com/', 'description': 'Python / Git / JavaScript 教程'},
    {'name': 'TendCode', 'url': 'https://tendcode.com/', 'description': 'Django 自建博客，热爱 Python'},
    {'name': '酷壳', 'url': 'https://coolshell.cn/', 'description': '陈皓的技术博客，享受编程与技术'},
    {'name': 'DIYgod', 'url': 'https://diygod.cc/', 'description': 'RSSHub 作者，开源爱好者'},
    {'name': '少数派', 'url': 'https://sspai.com/', 'description': '高效工作，品质生活'},
    {'name': '空山灵雨', 'url': 'https://www.dearom.com/', 'description': '写下思考，等待时间回答'},
]


def fetch_favicon(site_url):
    """Try to fetch the favicon URL from a website."""
    domain = site_url.rstrip('/')
    if '://' in domain:
        scheme_domain = domain.split('/', 3)
        base = scheme_domain[0] + '//' + scheme_domain[2]
    else:
        base = 'https://' + domain

    # 1) Try Google favicon service (accessible in China)
    google_url = f'https://www.google.com/s2/favicons?domain={base}&sz=64'

    # 2) Try direct /favicon.ico
    direct_url = f'{base}/favicon.ico'

    # 3) Try parsing HTML for <link rel="icon">
    try:
        req = urllib.request.Request(base, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read(50000).decode('utf-8', errors='ignore')
        patterns = [
            r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'](?:shortcut )?icon["\']',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                href = m.group(1)
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = base + href
                elif not href.startswith('http'):
                    href = base + '/' + href
                return href
    except Exception:
        pass

    # Fallback to direct favicon.ico
    try:
        req = urllib.request.Request(direct_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return direct_url
    except Exception:
        pass

    return ''


class Command(BaseCommand):
    help = '生成示例友链数据（含 favicon 抓取）'

    def handle(self, *args, **options):
        FriendLink.objects.all().delete()
        self.stdout.write('正在创建友链并抓取 favicon...\n')

        for i, data in enumerate(LINKS):
            self.stdout.write(f'  [{i+1}/{len(LINKS)}] {data["name"]} ... ', ending='')
            avatar = fetch_favicon(data['url'])
            FriendLink.objects.create(
                name=data['name'],
                url=data['url'],
                description=data['description'],
                avatar=avatar,
                sort_order=i,
            )
            src = 'found' if avatar else 'none'
            self.stdout.write(self.style.SUCCESS(f'OK (favicon: {src})'))

        self.stdout.write(self.style.SUCCESS(f'\n完成！共 {FriendLink.objects.count()} 条友链'))
