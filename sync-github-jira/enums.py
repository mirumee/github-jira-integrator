import enum


@enum.unique
class JiraIssueType(str, enum.Enum):
    Task = "Task"
    Bug = "Bug"
