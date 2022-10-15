from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from shutil import rmtree

from ..models import Post, Group


User = get_user_model()

Test_folder = '/media/test-folder'

class FormsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif_one = (
            b'\x51\x52\x53\x54\x55\x56\x57\x58'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_one_img = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif_one,
            content_type=Test_folder,
        )
        small_gif_two = (
            b'\x45\x46\x47\x48\x49\x59\x60\x61'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_two_img = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif_two,
            content_type=Test_folder
        )
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
            text='Тестовый текст для тестового поста',
            image=cls.uploaded_one_img

        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def tearDown(self):
        rmtree(Test_folder, ignore_errors=True)

    def test_new_post(self):
        count_posts = Post.objects.count()
        redirect_user = self.test_user.username
        form_data = {
            'text': 'Просто текст',
            'group': self.group_test.id,
            'image': self.uploaded_one_img
        }

        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.first()
        self.assertRedirects(response, reverse('posts:profile',
                                               args=(redirect_user,)))
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, self.group_test.id)
        self.assertEqual(new_post.image, form_data['image'])

    def test_edit_post(self):
        count_posts = Post.objects.count()
        post_id = self.test_post.id
        form_data = {
            'text': 'Обновленный пост',
            'group': self.group_test2.id,
            'image': self.uploaded_two_img
        }
        response = self.authorized_client.post(
            reverse('posts:edit', args=(post_id,)),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(id=post_id)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=(post_id,)))
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.author, self.test_user)
        self.assertTrue(edit_post.group.slug, self.group_test2.slug)
        self.assertEqual(edit_post.image, form_data['image'])
