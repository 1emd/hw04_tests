from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User
from .constants import (
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    POST_CREATE_URL_NAME,
    INDEX_URL_TEMPLATE,
    GROUP_LIST_URL_TEMPLATE,
    PROFILE_URL_TEMPLATE,
    POST_DETAIL_URL_TEMPLATE,
    POST_EDIT_URL_TEMPLATE,
    POST_CREATE_URL_TEMPLATE
)

TEST_OF_POST: int = 13
POST_LIMIT = 10
MIN_POST_LIMIT = 3


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
                INDEX_URL_NAME): INDEX_URL_TEMPLATE,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): GROUP_LIST_URL_TEMPLATE,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author}): PROFILE_URL_TEMPLATE,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_DETAIL_URL_TEMPLATE,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_EDIT_URL_TEMPLATE,
            reverse(
                POST_CREATE_URL_NAME): POST_CREATE_URL_TEMPLATE,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(INDEX_URL_NAME))
        self.assertEqual(
            response.context['page_obj'][0].text, self.post.text
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username, self.user.username
        )
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title
        )

    def test_groups_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(
            response.context['group'].description, self.group.description
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.post.author})
        )
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.post.author.username
        )
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.post.group.title
        )
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['post'].text, self.post.text
        )
        self.assertEqual(
            response.context['post'].author.username, self.post.author.username
        )
        self.assertEqual(
            response.context['post'].group.title, self.post.group.title
        )

    def test_forms_correct(self):
        """Шаблоны post_edit и create_post сформированы
        с правильным контекстом"""
        urls_names = {
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}),
            reverse(POST_CREATE_URL_NAME)
        }
        for url in urls_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)

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
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertContains(response, self.post.text)

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

    def test_first_and_second_page_contains_ten_and_three_records(self):
        """Проверка: количество постов на
        index, group_list, profile равно 10 и 3."""
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
                response_two = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), POST_LIMIT)
                self.assertEqual(
                    len(response_two.context['page_obj']), MIN_POST_LIMIT
                )
