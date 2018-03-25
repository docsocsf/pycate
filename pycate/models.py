from enum import Enum
from typing import Dict


class AssessedStatus(Enum):
    UNKNOWN = 'UNKNOWN'

    UNASSESSED = 'UA'
    UNASSESSED_SUBMISSION_REQUIRED = 'UA-SR'

    ASSESSED_INDIVIDUAL = 'A-I'
    ASSESSED_GROUP = 'A-G'


class SubmissionStatus(Enum):
    UNKNOWN = 'UNKNOWN'

    OK = 'OK'

    NOT_SUBMITTED = 'N-S'
    NOT_SUBMITTED_DUE_SOON = 'N-S-DS'

    INCOMPLETE_SUBMISSION = 'I-S'
    INCOMPLETE_SUBMISSION_DUE_SOON = 'I-S-DS'


class Exercise:
    def __init__(
            self, module_number: str, module_name: str, code: str, name: str,
            start: str, end: str, assessed_status: AssessedStatus,
            submission_status: SubmissionStatus, links: Dict[str, str],
            spec_key: str):
        self.__module_number = module_number
        self.__module_name = module_name
        self.__code = code
        self.__name = name
        self.__start = start
        self.__end = end
        self.__assessed_status = assessed_status
        self.__submission_status = submission_status
        self.__links = links
        self.__spec_key = spec_key

    def __str__(self):
        return 'Exercise{{Module={} {};Code={};Name={}}}'.format(
            self.module_number,
            self.module_name,
            self.code,
            self.name
        )

    @property
    def module_number(self) -> str:
        return self.__module_number

    @property
    def module_name(self) -> str:
        return self.__module_name

    @property
    def code(self) -> str:
        return self.__code

    @property
    def name(self) -> str:
        return self.__name

    @property
    def start(self) -> str:
        return self.__start

    @property
    def end(self) -> str:
        return self.__end

    @property
    def assessed_status(self) -> AssessedStatus:
        return self.__assessed_status

    @property
    def submission_status(self) -> SubmissionStatus:
        return self.__submission_status

    @property
    def links(self) -> Dict[str, str]:
        return self.__links

    @property
    def spec_key(self) -> str:
        return self.__spec_key
