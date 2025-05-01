from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Tralalela Tralala')
        cls.reader = User.objects.create(username='Bombordiro Crocodillo')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='title',
            author=cls.author
            )


    def test_pages_availabitily(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.notes.slug)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
