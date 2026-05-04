from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Category, Comment, Post
from .views import render_article_body


class CommentModerationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.author = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Django')
        self.post = Post.objects.create(
            title='Moderation test',
            body='Body',
            excerpt='Excerpt',
            category=self.category,
            author=self.author,
        )

    def test_new_comment_is_pending_and_hidden_until_approved(self):
        response = self.client.post(
            reverse('blog:comment_by_pk', args=[self.post.pk]),
            {
                'name': 'Reader',
                'email': 'reader@example.com',
                'body': 'A thoughtful comment.',
                'website': '',
            },
            REMOTE_ADDR='203.0.113.10',
            HTTP_USER_AGENT='Django test client',
        )

        self.assertRedirects(response, self.post.get_absolute_url() + '#comments')
        comment = Comment.objects.get()
        self.assertEqual(comment.status, Comment.STATUS_PENDING)
        self.assertEqual(comment.ip_address, '203.0.113.10')
        self.assertEqual(comment.user_agent, 'Django test client')

        detail = self.client.get(self.post.get_absolute_url())
        self.assertNotContains(detail, 'A thoughtful comment.')

        comment.status = Comment.STATUS_APPROVED
        comment.save(update_fields=['status'])
        detail = self.client.get(self.post.get_absolute_url())
        self.assertContains(detail, 'A thoughtful comment.')

    def test_post_absolute_url_uses_stable_id_route(self):
        self.assertEqual(self.post.get_absolute_url(), f'/post/id/{self.post.pk}/')
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_future_post_is_not_public_until_publish_time(self):
        future_post = Post.objects.create(
            title='Future post',
            body='Hidden for now',
            excerpt='Hidden',
            category=self.category,
            author=self.author,
            is_published=True,
            publish_time=timezone.now() + timedelta(days=1),
        )

        response = self.client.get(future_post.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_markdown_renderer_supports_toc_code_and_images(self):
        html, toc = render_article_body(
            '## Section\n\n![Alt](/media/a.png)\n\n```python\nprint(\"hi\")\n```'
        )

        self.assertIn('<h2', html)
        self.assertIn('<img', html)
        self.assertIn('codehilite', html)
        self.assertEqual(toc[0]['title'], 'Section')

    def test_honeypot_rejects_bot_submission(self):
        response = self.client.post(
            reverse('blog:comment_by_pk', args=[self.post.pk]),
            {
                'name': 'Bot',
                'email': 'bot@example.com',
                'body': 'Looks normal enough.',
                'website': 'https://spam.example',
            },
        )

        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertEqual(Comment.objects.count(), 0)

    def test_rate_limit_blocks_repeated_submissions(self):
        url = reverse('blog:comment_by_pk', args=[self.post.pk])
        payload = {
            'name': 'Reader',
            'email': 'reader@example.com',
            'body': 'First comment.',
            'website': '',
        }

        self.client.post(url, payload, REMOTE_ADDR='203.0.113.11')
        second = self.client.post(
            url,
            {**payload, 'body': 'Second comment.'},
            REMOTE_ADDR='203.0.113.11',
        )

        self.assertRedirects(second, self.post.get_absolute_url() + '#comments')
        self.assertEqual(Comment.objects.count(), 1)

    @override_settings(COMMENT_MAX_LINKS=0)
    def test_link_limit_rejects_comment(self):
        response = self.client.post(
            reverse('blog:comment_by_pk', args=[self.post.pk]),
            {
                'name': 'Reader',
                'email': 'reader@example.com',
                'body': 'Read this https://example.com',
                'website': '',
            },
            REMOTE_ADDR='203.0.113.12',
        )

        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertEqual(Comment.objects.count(), 0)
