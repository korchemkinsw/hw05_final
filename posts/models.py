from django.contrib.auth import get_user_model

from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="имя группы",
        help_text="имя группы",
        max_length=200, null=False)
    description = models.TextField(
        verbose_name="описание",
        help_text="описание",
        max_length=200)
    slug = models.SlugField(
        verbose_name="ключ адреса",
        help_text="ключ адреса",
        max_length=70, unique=True)

    class Meta:
        verbose_name = "группа"
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="текст публикации",
        help_text="текст публикации")
    pub_date = models.DateTimeField(
        verbose_name="дата публикации",
        help_text="дата публикации",
        auto_now_add=True)
    author = models.ForeignKey(
        User, verbose_name="пользователь", help_text="пользователь",
        on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(
        Group, verbose_name="группа",
        help_text="группа", on_delete=models.SET_NULL,
        related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            f'{self.author.username} '
            f'{self.pub_date.date()} '
            f'{self.group} '
            f'{self.text[:15]}...')


class Comment(models.Model):
    post = models.ForeignKey(
        Post, verbose_name="публикация", help_text="публикация",
        on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, verbose_name="пользователь", help_text="пользователь",
        on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(
        verbose_name="текст комментария",
        help_text="текст комментария")
    created = models.DateTimeField(
        verbose_name="дата комментария",
        help_text="дата комментария",
        auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ('-created',)

    def __str__(self):
        return (
            f'{self.author.username} '
            f'{self.created.date()} '
            f'{self.post.text[:15]}... '
            f'{self.text[:15]}...')


class Follow(models.Model):
    user = models.ForeignKey(
        User, verbose_name="подписчик", help_text="подписчик",
        on_delete=models.SET_NULL, null=True, related_name="follower")
    author = models.ForeignKey(
        User, verbose_name="интересный автор", help_text="интересный автор",
        on_delete=models.SET_NULL, null=True, related_name="following")

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return (
            f'{self.user.username} subscribed to '
            f'{self.author.username}')
