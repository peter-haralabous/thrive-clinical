import pytest
from django.utils import timezone
from freezegun import freeze_time

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.submission import SubmissionFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.submission import Submission
from sandwich.core.models.submission import SubmissionStatus


@pytest.mark.django_db
def test_submission_creation(encounter: Encounter):
    """
    Test that a new FormSubmission is created with the correct values.
    """
    task = TaskFactory.create(encounter=encounter)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task, data={"q1": "answer"})
    assert submission.pk is not None
    assert submission.form == form
    assert submission.patient == task.patient
    assert submission.task == task
    assert submission.status == SubmissionStatus.DRAFT
    assert submission.data == {"q1": "answer"}
    assert submission.metadata == {}
    assert submission.submitted_at is None
    assert submission.form_version is None


@pytest.mark.django_db
def test_submit(encounter: Encounter):
    """
    Test the submit() method transitions the status and sets the submitted_at timestamp.
    """

    task = TaskFactory.create(encounter=encounter)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task)
    assert submission.status == SubmissionStatus.DRAFT
    assert submission.submitted_at is None

    # Freeze time to make the timestamp predictable
    frozen_time = timezone.now()
    with freeze_time(frozen_time):
        submission.submit()

    # Re-fetch from DB to confirm save
    submission.refresh_from_db()

    assert submission.status == SubmissionStatus.COMPLETED
    assert submission.submitted_at == frozen_time


@pytest.mark.django_db
def test_submit_on_completed_submission(encounter: Encounter):
    """
    Test that calling submit() on an already completed submission does nothing.
    """

    task = TaskFactory.create(encounter=encounter)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task)
    submission.submit()
    first_submit_time = submission.submitted_at
    assert submission.status == SubmissionStatus.COMPLETED

    submission.submit()
    submission.refresh_from_db()

    assert submission.status == SubmissionStatus.COMPLETED
    assert submission.submitted_at == first_submit_time


@pytest.mark.django_db
def test_on_delete_patient_cascades(encounter: Encounter):
    """
    Test that deleting the Patient also deletes the FormSubmission (CASCADE).
    """
    patient = PatientFactory.create()
    task = TaskFactory.create(encounter=encounter, patient=patient)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task)
    submission_id = submission.id
    assert Submission.objects.filter(id=submission_id).exists()
    patient.delete()
    with pytest.raises(Submission.DoesNotExist):
        Submission.objects.get(id=submission_id)


@pytest.mark.django_db
def test_on_delete_form_sets_null(encounter: Encounter):
    """
    Test that deleting the Form sets the submission's form field to None (SET_NULL).
    """

    task = TaskFactory.create(encounter=encounter)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task)
    assert submission.form == form
    form.delete()
    submission.refresh_from_db()
    assert submission.form is None


@pytest.mark.django_db
def test_on_delete_task_sets_null(encounter: Encounter):
    """
    Test that deleting the Task sets the submission's task field to None (SET_NULL).
    """
    task = TaskFactory.create(encounter=encounter)
    form = FormFactory.create()
    submission = SubmissionFactory.create(form=form, task=task)
    assert submission.form == form
    task.delete()
    submission.refresh_from_db()
    assert submission.task is None
