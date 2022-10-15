from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

from http import HTTPStatus

from django.conf import settings

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_in_post = User.objects.create(
            username='Lemon'
        )

        cls.authorized_user = User.objects.create(
            username='Pokemon'
        )

        cls.group_in_post = Group.objects.create(
            title='Группа для тестового поста',
            slug='group_test',
            description='Описание для тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.author_in_post,
            group=cls.group_in_post
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)
        self.authorized_client_author_in_post = Client()
        self.authorized_client_author_in_post.force_login(self.author_in_post)

    def test_page_404(self):
        """Проверяем несуществующую страницу."""
        no_page = self.guest_client.get('no_page')
        self.assertEqual(no_page.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(no_page, 'core/404.html')


    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны страниц."""
        slug_group = self.group_in_post.slug
        user = self.author_in_post.username
        post_id = self.post.id
        template_page_edit = 'posts/create_post.html'

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{slug_group}/',
            'posts/profile.html': f'/profile/{user}/',
            'posts/post_detail.html': f'/posts/{post_id}/',
            template_page_edit: f'/posts/{post_id}/edit/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author_in_post.get(address)
                self.assertTemplateUsed(response, template)

    def test_task_list_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит
        авторизованного пользователя который не является автором поста на
        страницу деталей поста."""
        post_id = self.post.id

        response = self.authorized_client.get(
            f'/posts/{post_id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/posts/{post_id}/'
        )

    def test_edit_post_in_author_post(self):
        """Проверка редактирования поста автором этого поста."""
        post_id = self.post.id
        response = self.authorized_client_author_in_post.get(
            f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_access_page(self):
        """Проверка что гостю доступны все страницы кроме.

        /create/ и /edit/
        """
        page_create = '/create/'
        page_edit = f'/posts/{self.post.id}/edit/'
        login_url = settings.LOGIN_URL
        redirect_create = f'{login_url}?next={page_create}'
        redirect_edit = f'{login_url}?next={page_edit}'
        go_to_page = {
            '/': HTTPStatus.OK,
            f'/group/{self.group_in_post.slug}/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
        }
        for page, status_code in go_to_page.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, status_code)

        respons_in_create = self.guest_client.get(page_create)
        respons_in_edit = self.guest_client.get(page_edit)
        self.assertRedirects(respons_in_create, redirect_create)
        self.assertRedirects(respons_in_edit, redirect_edit)
