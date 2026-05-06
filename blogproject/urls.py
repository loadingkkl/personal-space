from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from blog.admin_site import blog_admin_site
from blog.feeds import LatestPostsFeed
from blog.sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap,
}


def robots_txt(request):
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


urlpatterns = [
    path('admin/', blog_admin_site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('rss.xml', LatestPostsFeed(), name='rss'),
    path('robots.txt', robots_txt, name='robots'),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
