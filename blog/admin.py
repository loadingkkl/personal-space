from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.html import format_html
from .models import Category, Tag, Post, Comment, Media, FriendLink
from .admin_site import blog_admin_site

blog_admin_site.register(User, UserAdmin)
blog_admin_site.register(Group, GroupAdmin)


@admin.register(Category, site=blog_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        count = obj.post_set.count()
        return format_html('<span class="admin-count">{}</span>', count)
    post_count.short_description = '文章数'


@admin.register(Tag, site=blog_admin_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        count = obj.post_set.count()
        return format_html('<span class="admin-count">{}</span>', count)
    post_count.short_description = '文章数'


@admin.register(Post, site=blog_admin_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_display', 'author', 'created_time', 'views_display', 'is_published', 'is_featured')
    list_filter = ('category', 'author', 'created_time', 'is_published', 'is_featured')
    search_fields = ('title', 'body')
    list_editable = ('is_published', 'is_featured')
    date_hierarchy = 'created_time'
    filter_horizontal = ('tags',)
    list_per_page = 20
    list_display_links = ('title',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'category', 'tags', 'cover')
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
            obj.category.name
        )
    category_display.short_description = '分类'
    category_display.admin_order_field = 'category'

    def views_display(self, obj):
        return format_html(
            '<span class="admin-count">{}</span>',
            obj.views
        )
    views_display.short_description = '阅读量'
    views_display.admin_order_field = 'views'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Media, site=blog_admin_site)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('cover_preview', 'title', 'type_display', 'rating_display', 'status_display', 'creator', 'finished_date')
    list_filter = ('media_type', 'status', 'rating')
    search_fields = ('title', 'creator', 'summary')
    list_editable = ('finished_date',)
    list_per_page = 20
    readonly_fields = ('cover_preview',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'media_type', 'cover', 'cover_preview', 'rating', 'status')
        }),
        ('详情', {
            'fields': ('creator', 'summary', 'finished_date', 'douban_url')
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
        icons = {'movie': '🎬', 'book': '📖', 'game': '🎮'}
        icon = icons.get(obj.media_type, '')
        colors = {'movie': 'violet', 'book': 'emerald', 'game': 'sky'}
        color = colors.get(obj.media_type, 'slate')
        return format_html(
            '<span class="admin-badge admin-badge--{}">{} {}</span>',
            color, icon, obj.get_media_type_display()
        )
    type_display.short_description = '类型'
    type_display.admin_order_field = 'media_type'

    def rating_display(self, obj):
        full = obj.full_stars
        half = 1 if obj.half_star else 0
        empty = obj.empty_stars
        stars_html = '<span class="admin-stars">'
        stars_html += '<span class="admin-stars--filled">' + '★' * full
        if half:
            stars_html += '⯨'
        stars_html += '</span>'
        stars_html += '<span class="admin-stars--empty">' + '★' * empty + '</span>'
        stars_html += '</span>'
        return format_html(stars_html)
    rating_display.short_description = '评分'
    rating_display.admin_order_field = 'rating'

    def status_display(self, obj):
        status_map = {
            'done': ('emerald', '✓'),
            'doing': ('sky', '▶'),
            'wish': ('amber', '☆'),
        }
        color, icon = status_map.get(obj.status, ('slate', ''))
        return format_html(
            '<span class="admin-badge admin-badge--{}">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_display.short_description = '状态'
    status_display.admin_order_field = 'status'


@admin.register(FriendLink, site=blog_admin_site)
class FriendLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_display', 'description', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('name', 'url')
    list_per_page = 20

    def url_display(self, obj):
        return format_html(
            '<a href="{}" target="_blank" class="admin-link">🔗 {}</a>',
            obj.url, obj.url
        )
    url_display.short_description = '链接'


@admin.register(Comment, site=blog_admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'body_preview', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('name', 'body')
    list_per_page = 20
    readonly_fields = ('name', 'email', 'body', 'post', 'created_time')

    def body_preview(self, obj):
        text = obj.body[:60] + '…' if len(obj.body) > 60 else obj.body
        return format_html('<span class="admin-preview">{}</span>', text)
    body_preview.short_description = '内容预览'
