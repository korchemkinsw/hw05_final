from django.urls import reverse
from django.test import Client, TestCase

from posts.models import Follow, Group, Post, User
from yatube.settings import PER_PAGE


USER_NAME = 'demo'
GROUP_SLUG = 'gruppa'
OTHER_GROUP_SLUG = 'drugaya_gruppa'
URL_HOME_PAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
URL_PROFILE = reverse('profile', args=[USER_NAME])
URL_GROUP_POSTS = reverse('group_posts', args=[GROUP_SLUG])
URL_OTHER_GROUP_POST = reverse('group_posts', args=[OTHER_GROUP_SLUG])
URL_FOLLOW_INDEX = reverse('follow_index')
URL_FOLLOW = reverse('profile_follow', args=[USER_NAME])
URL_UNFOLLOW = reverse('profile_unfollow', args=[USER_NAME])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.other_user = User.objects.create_user(username='demon')
        cls.third_user = User.objects.create_user(username='dimon')
        cls.group = Group.objects.create(
            title='группа',
            description='описание',
            slug=GROUP_SLUG)
        cls.other_group = Group.objects.create(
            title='другая группа',
            description='',
            slug=OTHER_GROUP_SLUG)
        cls.post = Post.objects.create(
            text='тестовая публикация',
            group=cls.group,
            author=cls.user,
        )

        cls.URL_OTHER_GROUP_POSTS = reverse(
            'group_posts',
            args=[OTHER_GROUP_SLUG])
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
        cls.URL_COMMENT = reverse(
            'add_comment',
            args=[
                cls.post.author.username,
                cls.post.id
            ]
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_postspages_context(self):
        """Шаблоны публикаций сформированы с правильным контекстом."""
        url_names = (
            URL_HOME_PAGE,
            URL_GROUP_POSTS,
            URL_PROFILE,
            self.URL_VIEW_POST
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                if url_name == self.URL_VIEW_POST:
                    post = response.context['post']
                else:
                    self.assertEqual(
                        len(response.context['page']), 1,
                        'объект не единственный'
                    )
                    post = response.context['page'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(
                    post.author,
                    self.post.author)

    def test_author_pages(self):
        """Страницы profile и post содержат публикации автора"""
        url_names = (
            URL_PROFILE,
            self.URL_VIEW_POST
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertEqual(response.context['user'], self.post.author)

    def test_group_post_pages(self):
        """
        Пост не отображается на странице группы
        для которой не предназначен
        """
        response = self.authorized_client.get(URL_OTHER_GROUP_POST)
        self.assertIsNot(response.context['group'], self.post.group)

    def test_paginator(self):
        """Паджинатор выводит нужное количество постов на страницу"""
        for counter in range(1, PER_PAGE + 2):
            Post.objects.create(
                text=str(counter),
                author=self.user,
            )
        response = self.authorized_client.get(URL_HOME_PAGE)
        self.assertEqual(len(response.context['page']), PER_PAGE)

    def test_autorized_user_follow(self):
        """
        авторизованный пользователь может
        подписываться на других авторов и удалять их из подписок
        """
        follower_client = Client()
        follower_client.force_login(self.other_user)
        follower_client.get(URL_FOLLOW)
        self.assertTrue(Follow.objects.all())
        follower_client.get(URL_UNFOLLOW)
        self.assertFalse(Follow.objects.all())

    def test_user_comment(self):
        """Только авторизованный пользователь может комментировать"""
        guest_client = Client()
        response = guest_client.get(self.URL_COMMENT)
        self.assertEqual(response.status_code, 302)
        response = self.authorized_client.get(self.URL_COMMENT)
        self.assertEqual(response.status_code, 200)

    def test_new_post_follower(self):
        """
        новая запись появляется в ленте подписчиков
        и не отображается у тех, кто не подписан
        """
        follower_client = Client()
        follower_client.force_login(self.other_user)
        follower_client.get(URL_FOLLOW)
        unfollower_client = Client()
        unfollower_client.force_login(self.third_user)
        response = follower_client.get(URL_FOLLOW_INDEX)
        self.assertTrue(response.context['post'])
        response = unfollower_client.get(URL_FOLLOW_INDEX)
        self.assertEqual(len(response.context['page']), 0)
