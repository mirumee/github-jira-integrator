import enums
import utils as tested_utils


def test_get_issue_type_when_labels_contains_bug():
    labels = [{"name": "bug"}, {"name": "duplicated"}]

    result = tested_utils.get_issue_type(labels)

    assert result == enums.JiraIssueType.BUG.value


def test_get_issue_type_when_labels_not_contains_bug():
    labels = [{"name": "invalid"}, {"name": "duplicated"}]

    result = tested_utils.get_issue_type(labels)

    assert result == enums.JiraIssueType.TASK.value


def test_to_camel_case():
    text = "A simple text With SoMe WeIrD cHaracteR"

    result = tested_utils.to_camel_case(text)

    assert result == "ASimpleTextWithSomeWeirdCharacter"


def test_get_jira_labels_without_bug():
    labels = [{"name": "invalid"}, {"name": "duplicated"}, {"name": "Two words"}]

    result = tested_utils.get_jira_labels(labels)

    assert result == ["Invalid", "Duplicated", "TwoWords"]
