from django import forms
from django.conf import settings
from .models import Comment


class CommentForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '你的昵称',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': '你的邮箱',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': '写下你的评论...',
                'rows': 4,
            }),
        }

    def clean_website(self):
        value = self.cleaned_data.get('website', '').strip()
        if value:
            raise forms.ValidationError('评论提交异常，请重试。')
        return value

    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        if len(body) < 3:
            raise forms.ValidationError('评论内容至少需要 3 个字。')

        max_links = getattr(settings, 'COMMENT_MAX_LINKS', 2)
        link_count = body.lower().count('http://') + body.lower().count('https://')
        if link_count > max_links:
            raise forms.ValidationError('评论中的链接过多，请减少链接后再提交。')

        blocked_words = getattr(settings, 'COMMENT_BLOCKED_WORDS', ())
        lowered_body = body.lower()
        if any(word.lower() in lowered_body for word in blocked_words):
            raise forms.ValidationError('评论包含暂不允许发布的内容。')

        return body
