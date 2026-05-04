from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.admin_site import blog_admin_site

urlpatterns = [
    path('admin/', blog_admin_site.urls),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
