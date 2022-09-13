from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

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

    def test_new_post(self):
        count_posts = Post.objects.count()
        redirect_user = self.test_user.username
        form_data = {
            'text': 'Просто текст',
            'group': self.group_test.id
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

    def test_edit_post(self):
        count_posts = Post.objects.count()
        post_id = self.test_post.id
        form_data = {
            'text': 'Обновленный пост',
            'group': self.group_test2.id
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
