# notes/tests/test_content.py
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNotesList(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug='test-note',
            author=cls.author
        )

    def test_notes_list_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        self.assertContains(response, self.note.title)
        # Автор не видит кнопку редактирования на списке
        self.assertNotContains(response, 'Редактировать')


class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug='test-note',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_author_sees_buttons(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Редактировать')
        self.assertContains(response, 'Удалить')

    def test_other_user_doesnt_see_buttons(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.detail_url)
        # Чужая заметка даёт 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.add_url = reverse('notes:add')

    def test_auto_slug_creation(self):
        self.client.force_login(self.user)
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': ''
        }
        response = self.client.post(self.add_url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))

    def test_duplicate_slug_validation(self):
        self.client.force_login(self.user)
        Note.objects.create(
            title='Уникальная заметка',
            text='Текст',
            slug='unique-slug',
            author=self.user
        )
        form_data = {
            'title': 'Повторный заголовок',
            'text': 'Текст',
            'slug': 'unique-slug'
        }
        response = self.client.post(self.add_url, data=form_data)
        self.assertContains(
            response,
            'unique-slug - такой slug уже существует, придумайте уникальное значение!',
            status_code=200
        )


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            slug='test-note',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args) if args else reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Detail редиректит анонимного пользователя
        detail_url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Logout: GET и POST возвращают страницу logout (200)
        logout_url = reverse('users:logout')
        response_get = self.client.get(logout_url)
        self.assertEqual(response_get.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        response_post = self.client.post(logout_url)
        self.assertEqual(response_post.status_code, HTTPStatus.FOUND)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                expected = f'{login_url}?next={url}'
                self.assertRedirects(self.client.get(url), expected)
