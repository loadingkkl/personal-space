from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.html import escape
import markdown
from .models import (
    Comment,
    FriendLink,
    Media,
    Post,
    get_category_items,
    get_tag_items,
    normalize_taxonomy_name,
    tag_filter_q,
)
from .forms import CommentForm


COMMENT_RATE_LIMIT_SECONDS = 60


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def is_comment_rate_limited(request, post_id):
    ip_address = get_client_ip(request) or 'unknown'
    cache_key = f'comment-rate:{post_id}:{ip_address}'
    if cache.get(cache_key):
        return True
    cache.set(cache_key, True, COMMENT_RATE_LIMIT_SECONDS)
    return False


def get_spam_reason(comment):
    body = comment.body.lower()
    suspicious_phrases = ('viagra', 'casino', 'loan', 'crypto', '博彩', '贷款', '代开', '发票')
    if any(phrase in body for phrase in suspicious_phrases):
        return '命中垃圾评论关键词'
    if body.count('\n') > 12:
        return '评论换行过多'
    if len(comment.body) > 1200:
        return '评论内容过长'
    return ''

def live_posts():
    return Post.objects.filter(is_published=True, publish_time__lte=timezone.now())


def flatten_toc(tokens):
    items = []
    for token in tokens:
        items.append({
            'id': token['id'],
            'title': token['name'],
            'level': token['level'],
        })
        items.extend(flatten_toc(token.get('children', [])))
    return items


def render_article_body(body):
    md = markdown.Markdown(
        extensions=['extra', 'toc', 'codehilite', 'sane_lists'],
        extension_configs={
            'toc': {
                'anchorlink': False,
                'permalink': False,
                'toc_depth': '2-3',
            },
            'codehilite': {
                'guess_lang': False,
                'linenums': False,
            },
        },
        output_format='html5',
    )
    html = md.convert(escape(body))
    return html, flatten_toc(md.toc_tokens)

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        return live_posts().select_related('author').order_by('-is_pinned', '-publish_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = (
            live_posts().filter(is_featured=True, cover__isnull=False)
            .exclude(cover='')
            .select_related('author')
            .order_by('-is_pinned', '-publish_time')[:5]
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return live_posts()

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comment_list'] = self.object.comments.filter(status=Comment.STATUS_APPROVED)
        body_html, toc_items = render_article_body(self.object.body)
        context['body_html'] = body_html
        context['toc_items'] = toc_items
        prev_post = live_posts().filter(
            publish_time__gt=self.object.publish_time
        ).order_by('publish_time').first()
        next_post = live_posts().filter(
            publish_time__lt=self.object.publish_time
        ).order_by('-publish_time').first()
        context['prev_post'] = prev_post
        context['next_post'] = next_post
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        self.category_name = normalize_taxonomy_name(self.kwargs.get('name'))
        return live_posts().filter(category_name__iexact=self.category_name).order_by('-is_pinned', '-publish_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'分类: {self.category_name}'
        return context


class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 6

    def get_queryset(self):
        self.tag_name = normalize_taxonomy_name(self.kwargs.get('name'), fallback='')
        return live_posts().filter(tag_filter_q(self.tag_name)).order_by('-is_pinned', '-publish_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'标签: {self.tag_name}'
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
        return live_posts().filter(
            Q(title__icontains=self.q) | Q(body__icontains=self.q),
        ).order_by('-is_pinned', '-publish_time')

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
        return live_posts().filter(publish_time__year=year, publish_time__month=month).order_by('-is_pinned', '-publish_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'{self.kwargs["year"]}年{self.kwargs["month"]}月 归档'
        return context


SORT_OPTIONS = {
    'latest': ('-publish_time', '最近发布'),
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
            live_posts()
            .annotate(comment_count=Count('comments', filter=Q(comments__status=Comment.STATUS_APPROVED)))
            .select_related('author')
        )

        self.current_category = self.request.GET.get('cat', '').strip()
        self.current_tag = self.request.GET.get('tag', '').strip()
        self.current_sort = self.request.GET.get('sort', 'latest')

        if self.current_category:
            qs = qs.filter(category_name__iexact=self.current_category)
        if self.current_tag:
            qs = qs.filter(tag_filter_q(self.current_tag))

        if self.current_sort == 'latest':
            return qs.order_by('-is_pinned', '-publish_time')
        order_field = SORT_OPTIONS.get(self.current_sort, SORT_OPTIONS['latest'])[0]
        return qs.order_by(order_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = get_category_items(live_posts())
        context['all_tags'] = get_tag_items(live_posts())
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
    post = get_object_or_404(live_posts(), pk=pk)
    if request.method == 'POST':
        if is_comment_rate_limited(request, post.pk):
            messages.error(request, '提交太频繁了，请稍后再试。')
            return redirect(post.get_absolute_url() + '#comments')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = get_client_ip(request)
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            spam_reason = get_spam_reason(comment)
            if spam_reason:
                comment.status = Comment.STATUS_SPAM
                comment.moderation_reason = spam_reason
            else:
                comment.status = Comment.STATUS_PENDING
            comment.save()
            if comment.status == Comment.STATUS_SPAM:
                messages.warning(request, '评论已收到，系统会进一步审核。')
            else:
                messages.success(request, '评论已提交，审核通过后会显示。')
            return redirect(post.get_absolute_url() + '#comments')
        messages.error(request, '评论提交失败，请检查内容后重试。')
    return redirect(post.get_absolute_url())


