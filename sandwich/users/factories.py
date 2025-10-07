from collections.abc import Sequence
from typing import Any

from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory

from sandwich.users.models import User


class UserFactory(DjangoModelFactory[User]):
    email = Faker("email")
    name = Faker("name")

    def __init__(self):
        self.password = None

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.password = password

    class Meta:
        model = User
        django_get_or_create = ["email"]
        skip_postgeneration_save = False
