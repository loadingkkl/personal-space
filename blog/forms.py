from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
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
