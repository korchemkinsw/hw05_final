import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase, override_settings

from posts.models import Group, Post, User


URL_HOME_PAGE = reverse('index')
URL_NEW_POST = reverse('new_post')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='demo')
        cls.group = Group.objects.create(
            title='группа',
            description='описание',
            slug='gruppa')
        cls.other_group = Group.objects.create(
            title='другая группа',
            description='',
            slug='drugaya_gruppa')
        cls.post = Post.objects.create(
            text='тестовая публикация',
            group=cls.group,
            author=cls.user,)

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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'group': self.group.id,
            'text': 'новая публикация',
            'image': uploaded
        }
        response = self.authorized_client.post(
            URL_NEW_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, URL_HOME_PAGE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.count(), 2)
        posts = Post.objects.all().exclude(id=self.post.id)
        self.assertEqual(
            posts[0].group.id,
            form_data['group'])
        self.assertEqual(
            posts[0].text,
            form_data['text'])
        self.assertEqual(
            posts[0].author.username,
            self.user.username)
        self.assertEqual(
            posts[0].image.name,
            'posts/small.gif')

    def test_edit_post(self):
        """Форма редактирования изменяет запись не добавляя новой"""

        posts_count = Post.objects.count()
        form_data = {
            'group': self.other_group.id,
            'text': 'измененная публикация',
        }
        response = self.authorized_client.post(
            self.URL_POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.URL_VIEW_POST)
        self.assertEqual(Post.objects.count(), posts_count)
        post = response.context['post']
        self.assertEqual(
            post.group.id,
            form_data['group'])
        self.assertEqual(
            post.text,
            form_data['text'])
        self.assertEqual(
            post.author.username,
            self.post.author.username)
