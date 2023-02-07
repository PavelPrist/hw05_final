import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

NUMBER_POSTS = 13
NUMBER_POSTS_FIRST_PAGE = 10
NUMBER_POSTS_SECOND_PAGE = 3


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='NameTest')
        cls.author_new = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста',
            group=cls.group,
            image=cls.uploaded_image,
            is_published=True
        )
        cls.template_urls = [
            (
                reverse('posts:index'),
                'posts/index.html'
            ),
            (
                reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
                'posts/group_list.html'
            ),
            (
                reverse('posts:profile', kwargs={'username': cls.user}),
                'posts/profile.html'
            ),
            (
                reverse('posts:post_detail', kwargs={'post_id': cls.post.id}),
                'posts/post_detail.html'
            ),
            (
                reverse('posts:post_create'),
                'posts/create_post.html'
            ),
            (
                reverse('posts:post_edit', kwargs={'post_id': cls.post.id}),
                'posts/create_post.html'
            )
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author_new = Client()
        self.authorized_client_author_new.force_login(self.author_new)
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_pages_uses_correct_templates_authorised_user(self):
        """
        Тесты namespace, проверяющие, что во view-функциях используются
        правильные html-шаблоны.
        """
        for reverse_name, template in self.template_urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def func_test_type_fields_in_context(self, response):
        """Функция для тестов типы полей контекст словаря."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post тест типы полей в словаре context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.func_test_type_fields_in_context(response)

    def test_create_post_form_is_post_form_class(self):
        """Тест, что форма в create_post это PostForm."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit тест типы полей в словаре context."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.func_test_type_fields_in_context(response)

    def func_for_test_context(self, objects):
        """Функция для тестов верного контекста у шаблонов."""
        post_id = objects.id
        post_author = objects.author
        post_group = objects.group
        post_text = objects.text
        post_image = objects.image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_id, self.post.pk)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_image, self.post.image)

    def test_pages_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с верным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        objects = response.context.get('post')
        self.func_for_test_context(objects)

    def test_post_on_pages_show_correct_context(self):
        """
        Тест: пост, выводится корректно на страницы, проверка контекста.
        """
        reverse_objects = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for reverse_name in reverse_objects:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                objects = response.context['page_obj'][0]
                resp_obj = response.context.get('page_obj').object_list
                self.func_for_test_context(objects)
                self.assertIn(self.post, resp_obj)

    def test_post_not_in_over_group(self):
        """Тест НЕ_нахождения поста в чужой группе."""
        reverse_name_group2 = reverse(
            'posts:group_list',
            kwargs={'slug': self.group2.slug}
        )
        response = self.authorized_client.get(reverse_name_group2)
        self.assertNotContains(response, self.post)

    def test_index_cache_content(self):
        """Тестируем работу кэширования главной страницы index."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.get(pk=self.post.id).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_cache = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_2.content, response_cache.content)

    def test_authorized_user_follow_unfollow_author(self):
        """
        Тест подписки и отписки авторизованного пользователь от автора
        постов.
        """
        count_follower = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author_new}))
        path_redirect = reverse(
            'posts:profile', kwargs={'username': self.author_new})
        following_is = Follow.objects.filter(
            user=self.user, author=self.author_new)
        self.assertRedirects(response, path_redirect)
        self.assertEqual(Follow.objects.count(), count_follower + 1)
        self.assertTrue(following_is)

        # тест отписки авторизованного пользователя от автора
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author_new}))
        following_not_is = Follow.objects.filter(
            user=self.user, author=self.author_new)
        self.assertFalse(following_not_is)
        self.assertEqual(Follow.objects.count(), count_follower)

    def test_there_is_post_in_feed_of_follower(self):
        """
        Тест добавленный пост есть в ленте у подписчика.
        """
        self.authorized_client_author_new.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}))
        response = self.authorized_client_author_new.get(
            reverse('posts:follow_index'))
        objects = response.context['page_obj'][0]
        self.func_for_test_context(objects)
        self.assertContains(response, self.post)

    def test_there_is_no_post_in_feed_of_not_follower(self):
        """
        Тест добавленный пост отсутствует в ленте у не подписчика.
        """
        response = self.authorized_client_author_new.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NameTest')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовые посты номер {n}',
                    author=cls.user,
                    group=cls.group
                )
                for n in range(NUMBER_POSTS)
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def tearDown(self):
        cache.clear()

    def pagination_test_setup(self, url_params, expected_count):
        """Функция для тестирования шаблонов с пагинацией."""
        reverse_pages_names = [
            reverse('posts:index') + url_params,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}) + url_params,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}) + url_params,
        ]
        for reverse_name in reverse_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), expected_count
                )

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        self.pagination_test_setup('', NUMBER_POSTS_FIRST_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        self.pagination_test_setup('?page=2', NUMBER_POSTS_SECOND_PAGE)
