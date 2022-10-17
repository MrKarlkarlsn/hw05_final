from shutil import rmtree

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm


User = get_user_model()


class URLPathTemplatesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_in_post = User.objects.create(
            username='Lemon'
        )
        cls.user_no_post = User.objects.create(
            username='Pokemon'
        )
        cls.group_test = Group.objects.create(
            title='Группа созданная для тестов',
            slug='test-slug'
        )
        cls.test_post = Post.objects.create(
            author=cls.author_in_post,
            text='Тестовый текст для тестового поста'
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(
            self.author_in_post
        )

    def tearDown(self):
        rmtree('media/posts', ignore_errors=True)

    def test_right_temlate_use_with_url(self):
        """Проверка, что по запросу url используется верный шаблон."""
        self.slug = self.group_test.slug
        self.username = self.test_post.author
        self.post_id = self.test_post.id
        cache.clear()

        url_template_name = {
            reverse('posts:main'): 'posts/index.html',
            reverse('posts:group',
                    kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_id}):
            'posts/post_detail.html',
            reverse('posts:edit',
                    kwargs={'post_id': self.post_id}):
            'posts/create_post.html',
            reverse('posts:create'): 'posts/create_post.html'
        }

        for func_name, template_name in url_template_name.items():
            with self.subTest(func_name=func_name):
                resp = self.authorized_author.get(func_name)
                self.assertTemplateUsed(resp, template_name)


class ViewsContextTests(TestCase):
    """Проверка контекста, передаваемого из view в шаблоны."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user_test = User.objects.create(
            username='Lemon'
        )
        cls.group_test = Group.objects.create(
            title='Группа для тестов',
            description='Описание тестовой группы',
            slug='test-slug'
        )
        cls.test_post = Post.objects.create(
            author=cls.user_test,
            image=uploaded,
            text='test_post_text',
            group=cls.group_test,
        )

    def tearDown(self):
        rmtree('media/posts', ignore_errors=True)

    def page_queryset_post_test(self, context, find_object):
        cache.clear()
        post_in_db = self.test_post
        self.assertIn(find_object, context)
        if find_object == 'page_obj':
            page_list = context.get(find_object).object_list
            post_in_context = page_list[0]
        elif find_object == 'post':
            post_in_context = context['post']

        self.assertEqual(post_in_context, post_in_db)
        self.assertEqual(post_in_context.text, post_in_db.text)
        self.assertEqual(post_in_context.author, post_in_db.author)
        self.assertEqual(post_in_context.group, post_in_db.group)
        self.assertEqual(post_in_context.pub_date, post_in_db.pub_date)
        self.assertEqual(post_in_context.image, post_in_db.image)

    def test_index_put_in_render_right_context(self):
        """Проверка, что "main" выдаёт верный контекст в шаблон."""
        cache.clear()
        response = self.client.get(reverse('posts:main'))
        self.page_queryset_post_test(response.context, 'page_obj')
        title_page = 'Это главная страница проекта Yatube'
        response_title = response.context['title']
        self.assertEqual(response_title, title_page)

    def test_group_put_in_render_right_context(self):
        """Проверка, что "group" выдаёт верный контекст в шаблон."""
        response = self.client.get(
            reverse(
                'posts:group', args=(self.group_test.slug,)
            )
        )
        self.page_queryset_post_test(response.context, 'page_obj')
        group_in_db = self.group_test
        self.assertIn('group', response.context)
        group_in_context = response.context['group']
        self.assertEqual(group_in_context, group_in_db)
        self.assertEqual(group_in_context.title, group_in_db.title)
        self.assertEqual(group_in_context.description,
                         group_in_db.description)

    def test_profile_put_in_render_right_context(self):
        """Проверка, что "profile" выдаёт верный контекст в шаблон."""
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user_test.username}
            )
        )
        self.page_queryset_post_test(response.context, 'page_obj')

        user_in_db = ViewsContextTests.user_test
        self.assertIn('page_obj', response.context)
        user_in_context = response.context['author']
        self.assertEqual(user_in_context, user_in_db)
        count_post = response.context['post_count']
        self.assertEqual(count_post, self.test_post.id)

    def test_post_put_in_render_right_context(self):
        """Проверка, что "post" выдаёт верный контекст в шаблон."""
        response = self.client.get(reverse('posts:post_detail',
                                           args=(self.test_post.id,)))
        self.page_queryset_post_test(response.context, 'post')

        self.assertIn('post', response.context)
        user_in_db = self.user_test
        user_in_context = response.context['post']
        self.assertEqual(user_in_context.author.username, user_in_db.username)

    def test_new_post_put_in_render_right_context(self):
        """Проверка, что "new_post" выдаёт в шаблон верный контекст."""
        authorize_writer = Client()
        authorize_writer.force_login(self.user_test)
        response = authorize_writer.get(reverse('posts:create'))
        self.assertIn('form', response.context)
        self.assertIs(response.context['is_edit'], False)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_put_in_render_right_context(self):
        """Проверка, что "post_edit" выдаёт в шаблон верный контекст.."""
        authorize_writer = Client()
        authorize_writer.force_login(self.user_test)
        post_for_edit = self.test_post

        response = authorize_writer.get(
            reverse(
                'posts:edit',
                args=(post_for_edit.id,)
            )
        )
        self.assertIn('is_edit', response.context)
        self.assertIs(response.context['is_edit'], True)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)


class PaginatorWorkRight(TestCase):
    """Проверка пагинатора для главной страницы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test = User.objects.create(
            username='lemon'
        )
        cls.grop_test = Group.objects.create(
            title='Группа для тестов',
            slug='slug_test',
            description='Описание группы'
        )

        posts_14 = (Post(
            author=cls.user_test,
            group=cls.grop_test,
            text='Текст поста %s' % i
        ) for i in range(14))
        Post.objects.bulk_create(posts_14)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('posts:main'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        cache.clear()
        # Проверка: на второй странице должно быть 4 поста.
        response = self.client.get(reverse('posts:main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_paginator_in_group_1(self):
        response = self.client.get(reverse('posts:group',
                                           args=(self.grop_test.slug,)))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_in_group_2(self):
        # Проверка: на второй странице должно быть 4 поста.
        response = self.client.get(reverse('posts:group',
                                           args=(self.grop_test.slug,))
                                   + '?page=2')

        self.assertEqual(len(response.context['page_obj']), 4)

    def test_paginator_in_profile_1(self):
        response = self.client.get(reverse('posts:profile',
                                           args=(self.user_test,)))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_in_profile_2(self):
        # Проверка: на второй странице должно быть 4 поста.
        response = self.client.get(reverse('posts:profile',
                                           args=(self.user_test,)) + '?page=2')

        self.assertEqual(len(response.context['page_obj']), 4)


class PostRightInPage(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test = User.objects.create(
            username='Lemon'
        )
        cls.group_test = Group.objects.create(
            title='Заголовок тестовой группы',
            description='Описание тестовой группы',
            slug='test-slug'
        )
        cls.test_post = Post.objects.create(
            author=cls.user_test,
            text='Текст тестового поста',
            group=cls.group_test
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(
            self.test_post.author
        )
        cache.clear()

    def test_post_right_in_main(self):
        cache.clear()
        response = self.client.get(reverse('posts:main'))
        self.assertEqual(response.context['page_obj'][0], self.test_post)

    def test_post_right_in_group(self):
        response = self.client.get(reverse('posts:group',
                                           args=(self.group_test.slug,)))
        self.assertEqual(response.context['page_obj'][0], self.test_post)

    def test_post_right_in_profile(self):
        response = self.client.get(reverse('posts:profile',
                                           args=(self.user_test,)))
        self.assertEqual(response.context['page_obj'][0], self.test_post)

    def test_cache_main_page(self):
        """Проверка работы кеша."""
        cache_test_post = Post.objects.create(
            text='Пост тестирование кеша',
            author=self.test_post.author,
        )
        content_add = self.authorized_author.get(
            reverse('posts:main')).content
        cache_test_post.delete()
        content_delete = self.authorized_author.get(
            reverse('posts:main')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_author.get(
            reverse('posts:main')).content
        self.assertNotEqual(content_add, content_cache_clear)

    def test_delete_post(self):
        pass
