from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post
from .constants import (
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    POST_CREATE_URL_NAME,
    INDEX_URL_ADDRESS,
    GROUP_LIST_URL_ADDRESS,
    PROFILE_URL_ADDRESS,
    POST_DETAIL_URL_ADDRESS,
    POST_EDIT_URL_ADDRESS,
    POST_CREATE_URL_ADDRESS
)

TEST_OF_POST: int = 13
POST_LIMIT = 10
MIN_POST_LIMIT = 3

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='kir')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.fail_group = Group.objects.create(
            title='fail-group',
            slug='fail-group',
            description='Тестовое описание пустой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                INDEX_URL_NAME): INDEX_URL_ADDRESS,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): GROUP_LIST_URL_ADDRESS,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author}): PROFILE_URL_ADDRESS,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_DETAIL_URL_ADDRESS,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_EDIT_URL_ADDRESS,
            reverse(
                POST_CREATE_URL_NAME): POST_CREATE_URL_ADDRESS,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(INDEX_URL_NAME))
        response_object = response.context['page_obj'][0]
        post_text = response_object.text
        post_author = response_object.author.username
        group_post = response_object.group.title
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.user.username)
        self.assertEqual(group_post, self.group.title)

    def test_groups_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug})
        )
        response_object = response.context['group']
        group_title = response_object.title
        group_description = response_object.description
        group_slug = response_object.slug
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_description, self.group.description)
        self.assertEqual(group_slug, self.group.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author})
        )
        response_object = response.context['page_obj'][0]
        post_text = response_object.text
        post_author = response_object.author.username
        group_post = response_object.group.title
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author.username)
        self.assertEqual(group_post, self.post.group.title)
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id})
        )
        response_object = response.context['post']
        post_text = response_object.text
        post_author = response_object.author.username
        group_post = response_object.group.title
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author.username)
        self.assertEqual(group_post, self.post.group.title)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                POST_CREATE_URL_NAME)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_new_post_with_group_checking(self):
        """Созданный пост отобразился на: на главной странице сайта,
        на странице выбранной группы,
        в профайле пользователя.
        """
        urls_names = (
            reverse(INDEX_URL_NAME),
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}),
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author})
        )
        for url in urls_names:
            response = self.authorized_client.get(url)
            self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_with_group_not_in_new_group(self):
        """Созданный пост не попал в группу, для которой не был предназначен"""
        response = self.authorized_client.get(
            reverse(GROUP_LIST_URL_NAME, kwargs={'slug': self.fail_group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='kir')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.posts: list = []
        for i in range(TEST_OF_POST):
            cls.posts.append(Post(text=f'Тестовый текст {i}',
                                  group=cls.group,
                                  author=cls.user))
        Post.objects.bulk_create(cls.posts)

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на
        index, group_list, profile равно 10."""
        urls_names = (
            reverse(INDEX_URL_NAME),
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}),
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user.username})
        )
        for url in urls_names:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']), POST_LIMIT)

    def test_second_page_contains_three_records(self):
        """Проверка: на страницах index, group_list, profile
        должно быть три поста."""
        urls_names = (
            (reverse(INDEX_URL_NAME) + '?page=2'),
            (reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}) + '?page=2'),
            (reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user.username}) + '?page=2')
        )
        for url in urls_names:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), MIN_POST_LIMIT
                )
