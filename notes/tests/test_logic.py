from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'test-slug'
        }

    def test_user_cant_use_dublicate_slug(self):
        Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=self.user
        )
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            f'test-slug{WARNING}'
        )


class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-note',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

