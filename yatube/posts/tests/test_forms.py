from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User
from .constants import (
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    POST_CREATE_URL_NAME
)

PAGE_COUNT = 1


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='kir')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый новый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE_URL_NAME,
            kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), posts_count + PAGE_COUNT)
        new_post = Post.objects.latest('id')
        self.assertEqual(form_data['text'], new_post.text)
        self.assertEqual(form_data['group'], new_post.group.id)

    def test_post_edit(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение поста"""
        form_data = {
            'text': 'Изменить текст.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id})
        )
        new_post = Post.objects.latest('id')
        self.assertEqual(form_data['text'], new_post.text)
        self.assertEqual(form_data['group'], new_post.group.id)
