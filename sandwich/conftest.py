import os

import pytest

from sandwich.users.models import User
from sandwich.users.tests.factories import UserFactory

# For playwright tests, it uses async internally.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()
