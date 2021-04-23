from django.urls import reverse

from django.test import TestCase

from posts.models import Post, User


USER_NAME = 'demo'
GROUP_SLUG = 'gruppa'
URL_HOME_PAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
URL_PROFILE = reverse('profile', args=[USER_NAME])
URL_GROUP_POSTS = reverse('group_posts', args=[GROUP_SLUG])


class RoutesTest(TestCase):
    def test_routes(self):
        user = User.objects.create_user(username=USER_NAME)
        post = Post.objects.create(
            text='тестовая публикация',
            author=user,
        )
        URL_VIEW_POST = reverse('post', args=[USER_NAME, post.id])
        URL_POST_EDIT = reverse('post_edit', args=[USER_NAME, post.id])
        url_names = [
            [URL_HOME_PAGE, '/'],
            [URL_NEW_POST, '/new/'],
            [URL_GROUP_POSTS, f'/group/{GROUP_SLUG}/'],
            [URL_PROFILE, f'/{USER_NAME}/'],
            [URL_VIEW_POST, f'/{USER_NAME}/{post.id}/'],
            [URL_POST_EDIT, f'/{USER_NAME}/{post.id}/edit/']
        ]
        for reverse_name, url, in url_names:
            self.assertEqual(reverse_name, url)
