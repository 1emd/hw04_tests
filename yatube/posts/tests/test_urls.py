from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

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


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы',
        )

        cls.user = User.objects.create_user(
            username='user_kir')
        cls.another_user = User.objects.create_user(
            username='another_user')

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        # status
        cls.status_ok = HTTPStatus.OK
        cls.status_found = HTTPStatus.FOUND
        cls.status_not_found = HTTPStatus.NOT_FOUND
        # index
        cls.index_urls = reverse(INDEX_URL_NAME)
        cls.index_template = INDEX_URL_TEMPLATE
        # group_list
        cls.group_list_url = reverse(
            GROUP_LIST_URL_NAME,
            kwargs={'slug': cls.group.slug}
        )
        cls.group_list_template = GROUP_LIST_URL_TEMPLATE
        # profile
        cls.profile_url = reverse(
            PROFILE_URL_NAME,
            kwargs={'username': cls.user}
        )
        cls.profile_template = PROFILE_URL_TEMPLATE
        # post_detail
        cls.post_detail_url = reverse(
            POST_DETAIL_URL_NAME,
            kwargs={'post_id': cls.post.id}
        )
        cls.post_detail_template = POST_DETAIL_URL_TEMPLATE
        # post_edit
        cls.post_edit_url = reverse(
            POST_EDIT_URL_NAME,
            kwargs={'post_id': cls.post.id}
        )
        cls.post_edit_template = POST_EDIT_URL_TEMPLATE
        # post_create
        cls.post_create_url = reverse(POST_CREATE_URL_NAME)
        cls.post_create_template = POST_CREATE_URL_TEMPLATE
        # unexisting_page
        cls.unexisting_page_url = '/unexisting_page/'
        cls.fake_template = ''
        # tuples
        cls.public_urls = {
            (cls.index_urls, cls.index_template, cls.status_ok),
            (cls.group_list_url, cls.group_list_template, cls.status_ok),
            (cls.profile_url, cls.profile_template, cls.status_ok),
            (cls.post_detail_url, cls.post_detail_template, cls.status_ok),
            (cls.post_edit_url, cls.post_edit_template, cls.status_found),
            (cls.post_create_url, cls.post_create_template, cls.status_found),
        }
        cls.unex_page = {
            (cls.unexisting_page_url, cls.fake_template, cls.status_not_found)
        }
        cls.author_urls = {
            (cls.post_edit_url, cls.post_edit_template, cls.status_ok),
            (cls.post_create_url, cls.post_create_template, cls.status_ok),
        }
        cls.auth_urls = {
            (cls.post_edit_url, cls.post_edit_template, cls.status_found),
            (cls.post_create_url, cls.post_create_template, cls.status_ok),
        }

    def setUp(self):
        self.guest = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_guest_user_urls_status_code(self):
        """Проверка доступности адресов для неавторизованного пользователя."""
        for url, _, response_code in self.public_urls and self.unex_page:
            with self.subTest(url=url):
                status_code = self.guest.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_author_user_urls_status_code(self):
        """Проверка доступности адресов для автора."""
        for url, _, response_code in self.author_urls:
            with self.subTest(url=url):
                status_code = self.post_author.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls_status_code(self):
        """Проверка доступности адресов для авторизованного пользователя."""
        for url, _, response_code in self.auth_urls:
            with self.subTest(url=url):
                status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template, _ in self.public_urls:
            with self.subTest(adress=adress):
                response = self.post_author.get(adress)
                self.assertTemplateUsed(response, template)
