from django.urls import reverse
from django.test import Client, TestCase

from posts.models import Group, Post, User
from yatube.settings import LOGIN_URL


USER_NAME = 'demo'
GROUP_SLUG = 'gruppa'
URL_HOME_PAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
URL_NOT_PAGE = '/not_page/'
URL_PROFILE = reverse('profile', args=[USER_NAME])
URL_GROUP_POSTS = reverse('group_posts', args=[GROUP_SLUG])


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username=USER_NAME)
        cls.user_b = User.objects.create_user(username='demon')
        cls.group = Group.objects.create(
            title='группа',
            description='описание',
            slug=GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text='тестовая публикация',
            group=cls.group,
            author=cls.user_a,
        )
        cls.URL_VIEW_POST = reverse(
            'post',
            args=[
                cls.post.author.username,
                cls.post.id
            ]
        )
        cls.URL_POST_EDIT = reverse(
            'post_edit',
            args=[
                cls.post.author.username,
                cls.post.id
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user_a)
        self.user_client = Client()
        self.user_client.force_login(self.user_b)

    def test_urls_return_codes(self):
        """"Возвращаемые коды верны"""
        templates_url_names = [
            [self.author_client.get(URL_HOME_PAGE), 200],
            [self.author_client.get(URL_NEW_POST), 200],
            [self.author_client.get(URL_GROUP_POSTS), 200],
            [self.author_client.get(URL_PROFILE), 200],
            [self.author_client.get(self.URL_VIEW_POST), 200],
            [self.author_client.get(self.URL_POST_EDIT), 200],
            [self.user_client.get(self.URL_POST_EDIT), 302],
            [self.guest_client.get(URL_NEW_POST), 302],
            [
                self.author_client.post(
                    self.URL_POST_EDIT,
                    {'group': self.group.id, 'text': self.post.text},
                ),
                302
            ],
            [self.user_client.get(URL_NOT_PAGE), 404]
        ]
        for response, code in templates_url_names:
            with self.subTest(response=response):
                self.assertEqual(
                    response.status_code,
                    code
                )

    def test_urls_uses_correct_template(self):
        """Для авторизованного пользователя доступны все страницы"""
        templates_url_names = [
            [URL_HOME_PAGE, 'index.html'],
            [URL_NEW_POST, 'new.html'],
            [URL_GROUP_POSTS, 'group.html'],
            [URL_PROFILE, 'profile.html'],
            [self.URL_VIEW_POST, 'post.html'],
            [self.URL_POST_EDIT, 'new.html']
        ]
        for reverse_name, template, in templates_url_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.author_client.get(reverse_name),
                    template,
                )

    def test_redirects(self):
        """
        Тест редиректов для страниц
        создание нового поста анонимным пользователем
        редактирование поста не его автором
        """
        templates_url_names = [
            [self.user_client.get(self.URL_POST_EDIT), self.URL_VIEW_POST],
            [
                self.guest_client.get(URL_NEW_POST),
                LOGIN_URL + '?next=' + URL_NEW_POST
            ],
            [
                self.author_client.post(
                    self.URL_POST_EDIT,
                    {'group': self.group.id, 'text': self.post.text},
                    follow=True
                ),
                self.URL_VIEW_POST
            ]
        ]
        for response, url_redirect in templates_url_names:
            with self.subTest(url_redirect=url_redirect):
                self.assertRedirects(
                    response,
                    url_redirect
                )
