from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q, Count
from django.utils.html import escape
from .models import Post, Category, Tag, Comment, Media, FriendLink
from .forms import CommentForm


def render_article_body(body):
    toc = []
    html_parts = []
    paragraph_lines = []
    list_items = []
    heading_index = 0

    def flush_paragraph():
        if not paragraph_lines:
            return
        text = '<br>'.join(escape(line) for line in paragraph_lines)
        html_parts.append(f'<p>{text}</p>')
        paragraph_lines.clear()

    def flush_list():
        if not list_items:
            return
        items_html = ''.join(f'<li>{escape(item)}</li>' for item in list_items)
        html_parts.append(f'<ul>{items_html}</ul>')
        list_items.clear()

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_list()
            continue

        level = None
        title = ''
        if line.startswith('### '):
            level = 3
            title = line[4:].strip()
        elif line.startswith('## '):
            level = 2
            title = line[3:].strip()

        if level and title:
            flush_paragraph()
            flush_list()
            heading_index += 1
            anchor = f'section-{heading_index}'
            toc.append({'id': anchor, 'title': title, 'level': level})
            html_parts.append(
                f'<h{level} id="{anchor}" class="article-heading article-heading-{level}">'
                f'{escape(title)}</h{level}>'
            )
        elif line.startswith('- ') and line[2:].strip():
            flush_paragraph()
            list_items.append(line[2:].strip())
        else:
            flush_list()
            paragraph_lines.append(raw_line)

    flush_paragraph()
    flush_list()
    return ''.join(html_parts), toc


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = (
            Post.objects.filter(is_published=True, is_featured=True, cover__isnull=False)
            .exclude(cover='')
            .select_related('category', 'author')[:5]
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comment_list'] = self.object.comments.all()
        body_html, toc_items = render_article_body(self.object.body)
        context['body_html'] = body_html
        context['toc_items'] = toc_items
        prev_post = Post.objects.filter(
            created_time__gt=self.object.created_time, is_published=True
        ).order_by('created_time').first()
        next_post = Post.objects.filter(
            created_time__lt=self.object.created_time, is_published=True
        ).order_by('-created_time').first()
        context['prev_post'] = prev_post
        context['next_post'] = next_post
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return Post.objects.filter(category=self.category, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'分类: {self.category.name}'
        return context


class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return Post.objects.filter(tags=self.tag, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'标签: {self.tag.name}'
        return context


class SearchView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        self.q = self.request.GET.get('q', '').strip()
        if not self.q:
            return Post.objects.none()
        return Post.objects.filter(
            Q(title__icontains=self.q) | Q(body__icontains=self.q),
            is_published=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'搜索: {self.q}' if self.q else '搜索'
        context['q'] = self.q
        return context


class ArchiveView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return Post.objects.filter(
            created_time__year=year, created_time__month=month, is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'{self.kwargs["year"]}年{self.kwargs["month"]}月 归档'
        return context


SORT_OPTIONS = {
    'latest': ('-modified_time', '最近更新'),
    'views': ('-views', '最多阅读'),
    'comments': ('-comment_count', '最多评论'),
}


class ArticleListView(ListView):
    model = Post
    template_name = 'blog/articles.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        qs = (
            Post.objects.filter(is_published=True)
            .annotate(comment_count=Count('comments'))
            .select_related('category', 'author')
            .prefetch_related('tags')
        )

        self.current_category = self.request.GET.get('cat', '')
        self.current_tag = self.request.GET.get('tag', '')
        self.current_sort = self.request.GET.get('sort', 'latest')

        if self.current_category:
            qs = qs.filter(category__pk=self.current_category)
        if self.current_tag:
            qs = qs.filter(tags__pk=self.current_tag)

        order_field = SORT_OPTIONS.get(self.current_sort, SORT_OPTIONS['latest'])[0]
        return qs.order_by(order_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
        context['all_tags'] = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
        context['sort_options'] = SORT_OPTIONS
        context['current_category'] = self.current_category
        context['current_tag'] = self.current_tag
        context['current_sort'] = self.current_sort
        context['total_count'] = self.get_queryset().count()
        return context


MEDIA_TYPE_ICONS = {
    'movie': '\U0001F3AC',
    'book': '\U0001F4DA',
    'game': '\U0001F3AE',
}


class MediaListView(ListView):
    model = Media
    template_name = 'blog/media.html'
    context_object_name = 'media_list'
    paginate_by = 24

    def get_queryset(self):
        qs = Media.objects.all()
        self.current_type = self.request.GET.get('type', '')
        if self.current_type:
            qs = qs.filter(media_type=self.current_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_types'] = Media.MEDIA_TYPES
        context['media_type_icons'] = MEDIA_TYPE_ICONS
        context['current_type'] = self.current_type
        type_counts = {}
        for key, label in Media.MEDIA_TYPES:
            type_counts[key] = Media.objects.filter(media_type=key).count()
        context['type_counts'] = type_counts
        context['total_count'] = Media.objects.count()
        return context


def links_view(request):
    links = FriendLink.objects.all()
    return render(request, 'blog/links.html', {'links': links, 'link_count': links.count()})


def about_view(request):
    return render(request, 'blog/about.html')


def comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, '评论发表成功！')
            return redirect(post.get_absolute_url() + '#comments')
    return redirect(post.get_absolute_url())
