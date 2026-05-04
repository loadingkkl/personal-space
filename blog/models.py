from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('分类名称', max_length=100)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('标签名称', max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True, allow_unicode=True)
    body = models.TextField('正文')
    excerpt = models.CharField('摘要', max_length=300, blank=True)
    cover = models.ImageField('封面图', upload_to='covers/%Y/%m/', blank=True, null=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('修改时间', auto_now=True)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    views = models.PositiveIntegerField('阅读量', default=0)
    is_published = models.BooleanField('已发布', default=True)
    is_featured = models.BooleanField('轮播推荐', default=False)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug:
            return reverse('blog:detail', kwargs={'slug': self.slug})
        return reverse('blog:detail_by_pk', kwargs={'pk': self.pk})

    def _build_unique_slug(self):
        base_slug = slugify(self.title, allow_unicode=True)[:90] or f'post-{timezone.now():%Y%m%d%H%M%S}'
        slug = base_slug
        suffix = 2
        qs = Post.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            suffix_text = f'-{suffix}'
            slug = f'{base_slug[:120 - len(suffix_text)]}{suffix_text}'
            qs = Post.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            suffix += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Media(models.Model):
    MEDIA_TYPES = [
        ('movie', '影视'),
        ('book', '书籍'),
        ('game', '游戏'),
    ]
    STATUS_CHOICES = [
        ('done', '已看/已读/已玩'),
        ('doing', '在看/在读/在玩'),
        ('wish', '想看/想读/想玩'),
    ]

    title = models.CharField('标题', max_length=200)
    media_type = models.CharField('类型', max_length=10, choices=MEDIA_TYPES)
    cover = models.ImageField('封面', upload_to='media_covers/%Y/%m/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField('评分', default=0, help_text='0-10 分，对应 0-5 星')
    creator = models.CharField('创作者', max_length=200, blank=True, help_text='导演/作者/开发商等')
    summary = models.TextField('简评', blank=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='done')
    finished_date = models.DateField('完成日期', blank=True, null=True)
    douban_url = models.URLField('豆瓣链接', blank=True)
    created_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '书影音'
        verbose_name_plural = verbose_name
        ordering = ['-finished_date', '-created_time']

    def __str__(self):
        return f'[{self.get_media_type_display()}] {self.title}'

    @property
    def stars(self):
        return self.rating / 2

    @property
    def full_stars(self):
        return int(self.stars)

    @property
    def half_star(self):
        return (self.stars - self.full_stars) >= 0.5

    @property
    def empty_stars(self):
        return 5 - self.full_stars - (1 if self.half_star else 0)


class FriendLink(models.Model):
    name = models.CharField('站点名称', max_length=100)
    url = models.URLField('链接')
    avatar = models.URLField('头像链接', blank=True)
    description = models.CharField('描述', max_length=200, blank=True)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '友链'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-pk']

    def __str__(self):
        return self.name

    @property
    def initial(self):
        return self.name[0] if self.name else '?'


class Comment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_HIDDEN = 'hidden'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_HIDDEN, '已隐藏'),
    ]

    post = models.ForeignKey(Post, verbose_name='文章', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField('昵称', max_length=100)
    email = models.EmailField('邮箱')
    body = models.TextField('内容')
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.name}: {self.body[:20]}'


class OperationLog(models.Model):
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_REVIEW = 'review'
    ACTION_BACKUP = 'backup'
    ACTION_RESTORE = 'restore'
    ACTION_CHOICES = [
        (ACTION_CREATE, '新增'),
        (ACTION_UPDATE, '修改'),
        (ACTION_DELETE, '删除'),
        (ACTION_REVIEW, '审核'),
        (ACTION_BACKUP, '备份'),
        (ACTION_RESTORE, '恢复'),
    ]

    actor = models.ForeignKey(User, verbose_name='操作人', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField('对象类型', max_length=100)
    object_id = models.CharField('对象 ID', max_length=64, blank=True)
    object_repr = models.CharField('对象名称', max_length=255)
    detail = models.TextField('详情', blank=True)
    created_time = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return f'{self.get_action_display()} {self.object_repr}'
