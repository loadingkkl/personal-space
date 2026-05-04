from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html

from .admin_site import blog_admin_site
from .models import Category, Comment, FriendLink, Media, OperationLog, Post, Tag

blog_admin_site.register(User, UserAdmin)
blog_admin_site.register(Group, GroupAdmin)


class PostAdminForm(forms.ModelForm):
    body = forms.CharField(
        label='正文',
        help_text='支持 Markdown 小标题：## 二级标题、### 三级标题会自动生成文章目录；空行会分段，- 开头会渲染为列表。',
        widget=forms.Textarea(attrs={
            'class': 'markdown-editor',
            'data-markdown-editor': 'true',
            'rows': 18,
            'placeholder': '用 ## 写章节标题，用 ### 写小节标题；正文空行分段，- 开头写列表。',
        }),
    )

    class Meta:
        model = Post
        fields = '__all__'


class OperationLogMixin:
    def _write_operation_log(self, request, action, obj, detail=''):
        OperationLog.objects.create(
            actor=request.user if request.user.is_authenticated else None,
            action=action,
            object_type=obj._meta.verbose_name,
            object_id=str(obj.pk or ''),
            object_repr=str(obj),
            detail=detail,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self._write_operation_log(
            request,
            OperationLog.ACTION_UPDATE if change else OperationLog.ACTION_CREATE,
            obj,
        )

    def delete_model(self, request, obj):
        self._write_operation_log(request, OperationLog.ACTION_DELETE, obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self._write_operation_log(request, OperationLog.ACTION_DELETE, obj, detail='后台批量删除')
        super().delete_queryset(request, queryset)


@admin.register(Category, site=blog_admin_site)
class CategoryAdmin(OperationLogMixin, admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        return format_html('<span class="admin-count">{}</span>', obj.post_set.count())
    post_count.short_description = '文章数'


@admin.register(Tag, site=blog_admin_site)
class TagAdmin(OperationLogMixin, admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        return format_html('<span class="admin-count">{}</span>', obj.post_set.count())
    post_count.short_description = '文章数'


@admin.register(Post, site=blog_admin_site)
class PostAdmin(OperationLogMixin, admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'slug', 'category_display', 'author', 'created_time', 'views_display', 'is_published', 'is_featured')
    list_filter = ('category', 'author', 'created_time', 'is_published', 'is_featured')
    search_fields = ('title', 'slug', 'body')
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'created_time'
    filter_horizontal = ('tags',)
    list_per_page = 20
    list_display_links = ('title',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'category', 'tags', 'cover'),
        }),
        ('文章内容', {
            'fields': ('excerpt', 'body'),
        }),
        ('发布设置', {
            'fields': ('is_published', 'is_featured', 'created_time'),
            'classes': ('collapse',),
        }),
    )

    def category_display(self, obj):
        return format_html(
            '<span class="admin-badge admin-badge--indigo">{}</span>',
            obj.category.name,
        )
    category_display.short_description = '分类'
    category_display.admin_order_field = 'category'

    def views_display(self, obj):
        return format_html('<span class="admin-count">{}</span>', obj.views)
    views_display.short_description = '阅读量'
    views_display.admin_order_field = 'views'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    class Media:
        js = ('js/admin_markdown_preview.js',)


@admin.register(Media, site=blog_admin_site)
class MediaAdmin(OperationLogMixin, admin.ModelAdmin):
    list_display = ('cover_preview', 'title', 'type_display', 'rating_display', 'status_display', 'creator', 'finished_date')
    list_filter = ('media_type', 'status', 'rating')
    search_fields = ('title', 'creator', 'summary')
    list_editable = ('finished_date',)
    list_per_page = 20
    readonly_fields = ('cover_preview',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'media_type', 'cover', 'cover_preview', 'rating', 'status'),
        }),
        ('详情', {
            'fields': ('creator', 'summary', 'finished_date', 'douban_url'),
        }),
    )

    def cover_preview(self, obj):
        if obj and obj.cover:
            return format_html(
                '<img src="{}" alt="{}" style="width:48px;height:72px;object-fit:cover;border-radius:6px;">',
                obj.cover.url,
                obj.title,
            )
        return format_html('<span class="admin-preview">暂无封面</span>')
    cover_preview.short_description = '封面'

    def type_display(self, obj):
        colors = {'movie': 'violet', 'book': 'emerald', 'game': 'sky'}
        return format_html(
            '<span class="admin-badge admin-badge--{}">{}</span>',
            colors.get(obj.media_type, 'slate'),
            obj.get_media_type_display(),
        )
    type_display.short_description = '类型'
    type_display.admin_order_field = 'media_type'

    def rating_display(self, obj):
        return format_html('<span class="admin-count">{}/10</span>', obj.rating)
    rating_display.short_description = '评分'
    rating_display.admin_order_field = 'rating'

    def status_display(self, obj):
        status_map = {
            'done': 'emerald',
            'doing': 'sky',
            'wish': 'amber',
        }
        return format_html(
            '<span class="admin-badge admin-badge--{}">{}</span>',
            status_map.get(obj.status, 'slate'),
            obj.get_status_display(),
        )
    status_display.short_description = '状态'
    status_display.admin_order_field = 'status'


@admin.register(FriendLink, site=blog_admin_site)
class FriendLinkAdmin(OperationLogMixin, admin.ModelAdmin):
    list_display = ('avatar_preview', 'name', 'url_display', 'description', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('name', 'url')
    list_per_page = 20
    readonly_fields = ('avatar_preview',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'url', 'avatar', 'avatar_preview', 'description', 'sort_order'),
        }),
    )

    def avatar_preview(self, obj):
        if obj and obj.avatar:
            return format_html(
                '<img src="{}" alt="{}" style="width:36px;height:36px;object-fit:contain;border-radius:8px;background:#fff;">',
                obj.avatar,
                obj.name,
            )
        return format_html('<span class="admin-preview">暂无头像</span>')
    avatar_preview.short_description = '头像'

    def url_display(self, obj):
        return format_html('<a href="{}" target="_blank" class="admin-link">{}</a>', obj.url, obj.url)
    url_display.short_description = '链接'


@admin.register(Comment, site=blog_admin_site)
class CommentAdmin(OperationLogMixin, admin.ModelAdmin):
    list_display = ('name', 'post', 'status_display', 'body_preview', 'created_time')
    list_filter = ('status', 'created_time')
    search_fields = ('name', 'body')
    list_per_page = 20
    readonly_fields = ('name', 'email', 'body', 'post', 'created_time')
    actions = ('approve_comments', 'hide_comments')

    def status_display(self, obj):
        color = {
            Comment.STATUS_PENDING: 'amber',
            Comment.STATUS_APPROVED: 'emerald',
            Comment.STATUS_HIDDEN: 'slate',
        }.get(obj.status, 'slate')
        return format_html('<span class="admin-badge admin-badge--{}">{}</span>', color, obj.get_status_display())
    status_display.short_description = '审核状态'
    status_display.admin_order_field = 'status'

    def body_preview(self, obj):
        text = obj.body[:60] + '...' if len(obj.body) > 60 else obj.body
        return format_html('<span class="admin-preview">{}</span>', text)
    body_preview.short_description = '内容预览'

    def approve_comments(self, request, queryset):
        count = queryset.update(status=Comment.STATUS_APPROVED)
        OperationLog.objects.create(
            actor=request.user,
            action=OperationLog.ACTION_REVIEW,
            object_type='评论',
            object_repr=f'批量通过 {count} 条评论',
            detail='后台批量操作',
        )
    approve_comments.short_description = '通过选中的评论'

    def hide_comments(self, request, queryset):
        count = queryset.update(status=Comment.STATUS_HIDDEN)
        OperationLog.objects.create(
            actor=request.user,
            action=OperationLog.ACTION_REVIEW,
            object_type='评论',
            object_repr=f'批量隐藏 {count} 条评论',
            detail='后台批量操作',
        )
    hide_comments.short_description = '隐藏选中的评论'


@admin.register(OperationLog, site=blog_admin_site)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('created_time', 'actor', 'action', 'object_type', 'object_repr')
    list_filter = ('action', 'object_type', 'created_time')
    search_fields = ('object_repr', 'detail', 'actor__username')
    readonly_fields = ('actor', 'action', 'object_type', 'object_id', 'object_repr', 'detail', 'created_time')
    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
