import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_user_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def func_redirect_and_tests_post_correct_created_form_fields(
            self, response, form_data, redirect
    ):
        """
        Функция для тестов, что пост создан с корректным контекстом.
        Тест редиректа.
        """
        self.assertRedirects(response, redirect)
        post_last = Post.objects.latest('id')
        self.assertEqual(post_last.text, form_data['text'])
        self.assertEqual(post_last.author, self.user)
        self.assertEqual(post_last.group_id, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        if 'Отредактированный текст' in form_data.values():
            self.assertEqual(post_last.image, 'posts/small1.gif')
        else:
            self.assertEqual(post_last.image, 'posts/small.gif')

    def test_create_post_form_valid_by_authorized_user(self):
        """
        Тест: валидная форма create_post, авторизованный пользователь создает
        запись в базе данных.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.id,
            'image': self.uploaded_image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )
        redirect = reverse(
            'posts:profile', kwargs={'username': self.user.username})
        self.func_redirect_and_tests_post_correct_created_form_fields(
            response, form_data, redirect)

    def test_post_edit_form_valid_by_authorized_user(self):
        """
        Тест: валидная форма edite_post, авторизованный пользователь меняет
        запись в базе данных.
        """
        posts_count = Post.objects.count()
        uploaded_image = SimpleUploadedFile(
            name='small1.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
            'image': uploaded_image
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        redirect = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        self.func_redirect_and_tests_post_correct_created_form_fields(
            response, form_data, redirect)

    def test_post_create_redirect_with_none_authorized(self):
        """
        Тест post_create для неавторизованного: Валидная форма перенаправляет
        на страницу авторизации.
        """
        posts_count = Post.objects.count()
        response = self.guest_user_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count)
        redirect = '/auth/login/?next=/create/'
        self.assertRedirects(response, redirect)

    def test_comments_form_after_valid_create_comment(self):
        """
        Тест: комментарий появляется на странице post_detail, данные переданы
        верные после успешной валидации
        """
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Новый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.last()
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=form_data['text']).exists())
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

        response_post = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        obj_comment = response_post.context.get('comments')[0].text
        self.assertEqual(obj_comment, form_data['text'])

    def test_create_comments_not_allowed_for_guest_user(self):
        """
        Тест: неавторизованный пользователь со страницы комментария
        перенаправляется на страницу авторизации
        """
        response = self.guest_user_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),

        )
        redirect = f'/auth/login/?next=/posts/{self.post.id}/comment/'
        self.assertRedirects(response, redirect)
