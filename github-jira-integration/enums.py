import enum


@enum.unique
class JiraIssueType(enum.Enum):
    TASK = "Task"
    BUG = "Bug"


@enum.unique
class GitHubAction(enum.Enum):
    OPENED = "opened"
    EDITED = "edited"
    LABELED = "labeled"
    UNLABELED = "unlabeled"
    CLOSED = "closed"
    REOPENED = "reopened"


@enum.unique
class JiraTransition(enum.Enum):
    TO_DO = "to do"
    READY_TO_TEST = "ready to test"
