import factory
from factory.django import DjangoModelFactory

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.submission import Submission
from sandwich.core.models.submission import SubmissionStatus


class SubmissionFactory(DjangoModelFactory[Submission]):
    class Meta:
        model = Submission

    form = factory.SubFactory(FormFactory)
    task = factory.SubFactory(TaskFactory)
    patient = factory.SelfAttribute("task.patient")
    status = SubmissionStatus.DRAFT
    data = factory.LazyFunction(dict)
    metadata = factory.LazyFunction(dict)
