from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Проверка доступности главной страницы всем пользователям."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_auth = User.objects.create_user(username='NameAuth')
        cls.user = User.objects.create_user(username='NameTest')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста',
            group=cls.group
        )

        cls.template_url_names = [
            ("/", False, "posts/index.html"),
            (f"/group/{cls.group.slug}/", False, "posts/group_list.html"),
            (f"/profile/{cls.user}/", False, "posts/profile.html"),
            (f"/posts/{cls.post.id}/", False, "posts/post_detail.html"),
            ("/create/", True, "posts/create_post.html"),
            (f"/posts/{cls.post.id}/edit/", True, "posts/create_post.html")
        ]
        cls.template_url = [
            "/",
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.id}/",
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_user_not_author = Client()
        self.authorized_user_not_author.force_login(self.user_auth)
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_unexisting_page_uses_custom_template_return_notfound(self):
        """
        Тест возврата 404 и использование кастомного шаблона с несуществующей
        страницы.
        """
        response = self.guest_client.get('/unexisting_page/')
        template = 'core/404.html'
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, template)

    def test_posts_url_status_templates_authorised_and_not_authorized(self):
        """
        Проверка доступности страниц и шаблонов авторизованному и неавторизов..
        пользователю.
        """
        for address, auth_status, template in self.template_url_names:
            with self.subTest(address=address):
                if auth_status:
                    self.guest_client.force_login(self.user)
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_posts_url_redirect_for_non_authorized_users(self):
        """
        Проверка для анонимного пользователя
        редиректа на страницу логина со страниц post_edit, post_create.
        """
        template_url_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for address, urls in template_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, urls)

    def test_posts_url_redirect_for_authorized_users_auth(self):
        """
        Проверка для авторизованного пользователя
        не автора поста редиректа с post_edit на сам пост.
        """
        address = f'/posts/{self.post.id}/edit/'
        template = f'/posts/{self.post.id}/'
        response = self.authorized_user_not_author.get(address, follow=True)
        self.assertRedirects(response, template)

    def test_urls_equal_path_name(self):
        """
        Тест - соответствие адресов страниц их именам.
        """
        url_names = [
            (reverse('posts:index'), '/'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             f'/group/{self.group.slug}/'),
            (reverse('posts:profile', kwargs={'username': self.user}),
             f'/profile/{self.user}/'),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             f'/posts/{self.post.id}/'),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             f'/posts/{self.post.id}/edit/'),
            (reverse('posts:post_create'), f'/create/')
        ]
        for reverse_address, path_name in url_names:
            with self.subTest(reverse_address=reverse_address):
                self.assertEqual(reverse_address, path_name)
