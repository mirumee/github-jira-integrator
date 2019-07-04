import pytest
import unittest.mock

import integrator


def create_event(
    action, labels, issue_number, issue_body, issue_title, repository_full_name
):
    return {
        "action": action,
        "issue": {
            "labels": list(map(lambda label: {"name": label}, labels)),
            "number": issue_number,
            "body": issue_body,
            "title": issue_title,
        },
        "repository": {"full_name": repository_full_name},
    }


@pytest.fixture
def jira_instance_mock():
    return unittest.mock.MagicMock()


@pytest.fixture
def issue_mock(jira_instance_mock):
    issue = unittest.mock.MagicMock()
    jira_instance_mock.search_issues.return_value = [issue]
    return issue


@pytest.fixture
def fields_mock(jira_instance_mock):
    jira_instance_mock.fields.return_value = [
        {"name": "GitHub Link", "key": "customfield_10000"}
    ]


@pytest.fixture
def transitions_mock(jira_instance_mock):
    jira_instance_mock.transitions.return_value = [
        {"name": "To Do", "id": 1},
        {"name": "In progress", "id": 2},
        {"name": "Ready to test", "id": 3},
        {"name": "Done", "id": 4},
    ]


@pytest.fixture
def jira_integrator(mocker, jira_instance_mock):
    mocker.patch("integrator.JIRA", return_value=jira_instance_mock, autospec=True)
    return integrator.JiraIntegrator("DummyUser", "DummyToken", "example.com")


@pytest.fixture
def dummy_event():
    return {"action": "dummy_action"}


@pytest.fixture
def github_create_issue_event():
    return create_event(
        action="opened",
        labels=["bug", "duplicated"],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )


@pytest.fixture
def github_edit_issue_event():
    return create_event(
        action="edited",
        labels=["bug", "duplicated"],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )


@pytest.fixture
def github_add_label_event():
    return create_event(
        action="labeled",
        labels=["bug", "duplicated"],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )


@pytest.fixture
def github_remove_label_event():
    return create_event(
        action="unlabeled",
        labels=["bug", "duplicated"],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )


@pytest.fixture
def github_close_issue_event():
    return create_event(
        action="closed",
        labels=[],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )


@pytest.fixture
def github_reopen_issue_event():
    return create_event(
        action="reopened",
        labels=[],
        issue_number=12,
        issue_body="Test issue body",
        issue_title="Test issue title",
        repository_full_name="Test repository",
    )
