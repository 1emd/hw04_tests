from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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

User = get_user_model()


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

    def setUp(self):
        self.guest = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_guest_user_urls_status_code(self):
        """Проверка доступности адресов для неавторизованного пользователя."""
        templates_url_names = {
            reverse(
                INDEX_URL_NAME): HTTPStatus.OK,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                POST_CREATE_URL_NAME): HTTPStatus.FOUND,
        }
        for url, response_code in templates_url_names.items():
            with self.subTest(url=url):
                status_code = self.guest.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_author_user_urls_status_code(self):
        """Проверка доступности адресов для автора."""
        templates_url_names = {
            reverse(
                INDEX_URL_NAME): HTTPStatus.OK,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                POST_CREATE_URL_NAME): HTTPStatus.OK,
        }
        for url, response_code in templates_url_names.items():
            with self.subTest(url=url):
                status_code = self.post_author.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls_status_code(self):
        """Проверка доступности адресов для авторизованного пользователя."""
        templates_url_names = {
            reverse(
                INDEX_URL_NAME): HTTPStatus.OK,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                POST_CREATE_URL_NAME): HTTPStatus.OK,
        }
        for url, response_code in templates_url_names.items():
            with self.subTest(url=url):
                status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_unexisting_page_return_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response1 = self.guest.get('/unexisting_page/')
        response2 = self.authorized_user.get('/unexisting_page/')
        response3 = self.post_author.get('/unexisting_page/')
        self.assertEqual(response1.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response2.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response3.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                INDEX_URL_NAME): INDEX_URL_ADDRESS,
            reverse(
                GROUP_LIST_URL_NAME,
                kwargs={'slug': self.group.slug}): GROUP_LIST_URL_ADDRESS,
            reverse(
                PROFILE_URL_NAME,
                kwargs={'username': self.user}): PROFILE_URL_ADDRESS,
            reverse(
                POST_DETAIL_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_DETAIL_URL_ADDRESS,
            reverse(
                POST_EDIT_URL_NAME,
                kwargs={'post_id': self.post.id}): POST_EDIT_URL_ADDRESS,
            reverse(
                POST_CREATE_URL_NAME): POST_CREATE_URL_ADDRESS,
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.post_author.get(adress)
                self.assertTemplateUsed(response, template)
