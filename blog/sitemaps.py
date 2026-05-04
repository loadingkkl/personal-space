from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-modified_time')

    def lastmod(self, obj):
        return obj.modified_time
