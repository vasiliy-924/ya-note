# notes/tests/test_routes.py
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
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )

    def test_pages_availability(self):
        """
        Проверка доступности страниц для анонимного пользователя:
        - notes:home       -> 200 OK
        - notes:detail     -> 302 Redirect (LoginRequired)
        - users:login      -> 200 OK
        - users:logout     -> 405 Method Not Allowed (GET)
        - users:signup     -> 200 OK
        """
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args) if args else reverse(name)
                response = self.client.get(url)
                if name == 'notes:detail':
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                elif name == 'users:logout':
                    self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        Редирект анонимного пользователя на логин для edit и delete заметки
        """
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                expected = f'{login_url}?next={url}'
                self.assertRedirects(self.client.get(url), expected)
