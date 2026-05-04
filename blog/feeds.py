from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Post


class LatestPostsFeed(Feed):
    title = '星语博客'
    description = '星语博客最新文章'

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-created_time')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.body[:180]

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_time

    def item_updateddate(self, item):
        return item.modified_time

    def link(self):
        return reverse('blog:index')
