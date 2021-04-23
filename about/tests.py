from django.test import Client, TestCase


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """Для всех пользователей доступны страницы About"""
        templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
