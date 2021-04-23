from django.test import TestCase

from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='группа',
            description='описание',
            slug='gruppa'
        )

    def test_label(self):
        """Поля модели Group содержат правильные названия"""
        field_verboses = {
            'title': 'имя группы',
            'description': 'описание',
            'slug': 'ключ адреса',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).verbose_name, expected)

    def test_object_name(self):
        """Обращение к объекту Group выводит его имя"""
        expected_object_name = self.group.title
        self.assertEquals(expected_object_name, str(self.group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='тестовая публикация',
            group=Group.objects.create(
                title='группа',
                description='описание',
                slug='gruppa'),
            author=User.objects.create(
                username='demo',
                password='demodemo'),
        )

    def test_label(self):
        """Поля модели Post содержат правильные названия"""
        field_verboses = {
            'text': 'текст публикации',
            'group': 'группа',
            'author': 'пользователь',
            'pub_date': 'дата публикации'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name, expected)

    def test_object_name(self):
        """Обращение к объекту Post выводит краткую информацию"""
        expected_object_name = (
            f'{self.post.author.username} '
            f'{self.post.pub_date.date()} '
            f'{self.post.group} '
            f'{self.post.text[:15]}...')
        self.assertEquals(expected_object_name, str(self.post))
