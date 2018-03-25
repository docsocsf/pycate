import pytest

from pycate.models import Exercise, AssessedStatus, SubmissionStatus


class TestExercise:
    @classmethod
    def setup_class(cls):
        cls.test_exercise = Exercise(
            '100', 'Computers', '1:CW', 'TestExercise', '2018-01-01',
            '2018-01-05', AssessedStatus.UNASSESSED_SUBMISSION_REQUIRED,
            SubmissionStatus.NOT_SUBMITTED, {}, '2017:3:000:c1:SPECS:user')

    def test_creation(self):
        assert self.test_exercise.module_number == '100'
        assert self.test_exercise.submission_status is \
            SubmissionStatus.NOT_SUBMITTED

    # noinspection PyPropertyAccess
    def test_properties_are_read_only(self):
        with pytest.raises(AttributeError):
            self.test_exercise.module_number = 100

