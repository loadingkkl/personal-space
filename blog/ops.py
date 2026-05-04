import os
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.storage import default_storage
from django.db import connection


def _status(ok=True, level='ok'):
    if ok:
        return 'ok'
    return level


def _configured(name):
    value = os.environ.get(name)
    return bool(value and value.strip())


def _database_label():
    config = settings.DATABASES.get('default', {})
    engine = config.get('ENGINE', '')
    if 'postgresql' in engine:
        return 'PostgreSQL'
    if 'sqlite' in engine:
        return 'SQLite'
    return engine.rsplit('.', 1)[-1] or 'Unknown'


def get_deployment_health():
    checks = []
    is_vercel = bool(os.environ.get('VERCEL'))

    checks.append({
        'name': '运行环境',
        'status': 'ok',
        'label': 'Vercel 线上' if is_vercel else '本地开发',
        'detail': '根据 VERCEL 环境变量识别。',
    })

    checks.append({
        'name': 'DEBUG',
        'status': _status(not (is_vercel and settings.DEBUG), 'warning'),
        'label': '已开启' if settings.DEBUG else '已关闭',
        'detail': '线上环境建议关闭 DEBUG。',
    })

    checks.append({
        'name': 'DJANGO_SECRET_KEY',
        'status': _status(_configured('DJANGO_SECRET_KEY'), 'warning'),
        'label': '已配置' if _configured('DJANGO_SECRET_KEY') else '未配置',
        'detail': '线上建议在 Vercel 环境变量中设置独立密钥。',
    })

    database_status = 'ok'
    database_detail = '连接正常。'
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception as exc:  # pragma: no cover - depends on deployment environment
        database_status = 'error'
        database_detail = str(exc)

    checks.append({
        'name': '数据库连接',
        'status': database_status,
        'label': _database_label(),
        'detail': database_detail,
    })

    checks.append({
        'name': 'DATABASE_URL',
        'status': _status(_configured('DATABASE_URL') or not is_vercel, 'error'),
        'label': '已配置' if _configured('DATABASE_URL') else '未配置',
        'detail': '线上缺失时会退回 SQLite，不适合 Vercel 持久化数据。',
    })

    cloudinary_url = os.environ.get('CLOUDINARY_URL', '')
    parsed_cloudinary = urlparse(cloudinary_url) if cloudinary_url else None
    cloudinary_valid = bool(parsed_cloudinary and parsed_cloudinary.scheme == 'cloudinary')
    checks.append({
        'name': 'Cloudinary',
        'status': _status(cloudinary_valid, 'error' if is_vercel else 'warning'),
        'label': '格式正确' if cloudinary_valid else ('未配置' if not cloudinary_url else '格式异常'),
        'detail': 'CLOUDINARY_URL 必须以 cloudinary:// 开头。',
    })

    storage_backend = default_storage.__class__.__module__ + '.' + default_storage.__class__.__name__
    checks.append({
        'name': '媒体存储',
        'status': _status(('cloudinary' in storage_backend.lower()) == bool(cloudinary_url), 'warning'),
        'label': storage_backend.rsplit('.', 1)[-1],
        'detail': storage_backend,
    })

    static_assets = [
        'css/style.css',
        'css/admin_custom.css',
        'js/admin_markdown_preview.js',
    ]
    missing_assets = [asset for asset in static_assets if not finders.find(asset)]
    checks.append({
        'name': '静态资源',
        'status': _status(not missing_assets, 'error'),
        'label': '可找到' if not missing_assets else '缺失',
        'detail': '关键文件正常。' if not missing_assets else '缺失：' + '、'.join(missing_assets),
    })

    for name in ('ADMIN_USERNAME', 'ADMIN_PASSWORD'):
        checks.append({
            'name': name,
            'status': _status(_configured(name), 'warning'),
            'label': '已配置' if _configured(name) else '未配置',
            'detail': '用于 Vercel 构建时创建或更新后台管理员。',
        })

    counts = {
        'ok': sum(1 for item in checks if item['status'] == 'ok'),
        'warning': sum(1 for item in checks if item['status'] == 'warning'),
        'error': sum(1 for item in checks if item['status'] == 'error'),
    }
    overall = 'error' if counts['error'] else ('warning' if counts['warning'] else 'ok')

    return {
        'overall': overall,
        'counts': counts,
        'checks': checks,
        'environment': 'Vercel 线上' if is_vercel else '本地开发',
        'database': _database_label(),
    }
