from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True, publish_time__lte=timezone.now()).order_by('-modified_time')

    def lastmod(self, obj):
        return obj.modified_time
