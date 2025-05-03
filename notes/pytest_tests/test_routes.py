import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

# Проверка доступных страниц для анонимного пользователя
@pytest.mark.parametrize(
    'name, expected_status',
    [
        ('notes:home', HTTPStatus.OK),
        ('users:login', HTTPStatus.OK),
        ('users:logout', HTTPStatus.METHOD_NOT_ALLOWED),  # logout по GET возвращает 405
        ('users:signup', HTTPStatus.OK),
    ]
)
def test_pages_availability_for_anonymous_user(client, name, expected_status):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == expected_status

# Проверка страниц, доступных авторизованному пользователю (не автору конкретной заметки)
@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_logged_in_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK

# Проверка доступа к детальному просмотру/редактированию/удалению заметки для разных пользователей
@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK),
    ]
)
@pytest.mark.parametrize(
    'view_name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
        client_fixture, view_name, note, expected_status
):
    url = reverse(view_name, args=(note.slug,))
    response = client_fixture.get(url)
    assert response.status_code == expected_status

# Проверка редиректа на страницу логина для анонимного пользователя
@pytest.mark.parametrize(
    'view_name, args',
    [
        ('notes:detail', lazy_fixture('slug_for_args')),
        ('notes:edit', lazy_fixture('slug_for_args')),
        ('notes:delete', lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ]
)
def test_redirects_for_anonymous_user(client, view_name, args):
    login_url = reverse('users:login')
    url = reverse(view_name, args=args)
    expected = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected)