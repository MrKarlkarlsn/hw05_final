from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from shutil import rmtree

from ..models import Post, Group


User = get_user_model()


class FormsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            username='Lemon'
        )
        cls.group_test = Group.objects.create(
            title='Группа созданная для тестов',
            slug='test-slug'
        )

        cls.group_test2 = Group.objects.create(
            title='Вторая группа созданная для тестов',
            slug='test-slug_2'

        )
        cls.test_post = Post.objects.create(
            author=cls.test_user,
            text='Тестовый текст для тестового поста'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)
        small_gif_one = (
            b'\x51\x52\x53\x54\x55\x56\x57\x58'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded_one_img = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif_one,
            content_type='image/gif',
        )
        cache.clear()

    def tearDown(self):
        rmtree('media/posts', ignore_errors=True)

    def test_new_post(self):
        """Проверка создания нового поста."""
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Просто текст',
            'group': self.group_test.id,
            'image': self.uploaded_one_img
        }

        self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        db_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertEqual(db_post.text, form_data['text'])
        self.assertEqual(db_post.group.id, form_data['group'])
        self.assertFalse(db_post.image, None)

    def test_edit_post(self):
        """Проверка редактирования поста."""
        text = 'Просто текс'
        form_data = {
            'text': text,
            'group': self.group_test.id
        }

        self.authorized_client.post(
            reverse('posts:edit', args=(self.test_post.id,)),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.test_post.id,
                group=self.group_test.id,
                text=text,
            ).exists(),
        )
