from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/id/<int:pk>/', views.PostDetailView.as_view(), name='detail_by_pk'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='detail_legacy'),
    path('post/<str:slug>/', views.PostDetailView.as_view(), name='detail'),
    path('category/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('tag/<int:pk>/', views.TagView.as_view(), name='tag'),
    path('archive/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('media/', views.MediaListView.as_view(), name='media'),
    path('links/', views.links_view, name='links'),
    path('about/', views.about_view, name='about'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('post/id/<int:pk>/comment/', views.comment_view, name='comment_by_pk'),
    path('post/<int:pk>/comment/', views.comment_view, name='comment_legacy'),
    path('post/<str:slug>/comment/', views.comment_view, name='comment'),
]
