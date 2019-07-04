def test_return_404_when_action_is_not_recognized(dummy_event, jira_integrator):
    response_obj = jira_integrator.handle(dummy_event)

    assert response_obj["statusCode"] == 404


def test_return_500_when_exception_occures(github_create_issue_event, jira_integrator):
    jira_integrator.jira_connection.create_issue.side_effect = Exception("Test error")

    response_obj = jira_integrator.handle(github_create_issue_event)

    assert response_obj["statusCode"] == 500


def test_return_200_when_action_is_opened(
    mocker, github_create_issue_event, jira_integrator, fields_mock
):
    mocker.patch("utils.find_project", return_value="TEST", autospec=True)
    response_obj = jira_integrator.handle(github_create_issue_event)

    expected_args = {
        "project": "TEST",
        "summary": "Test issue title",
        "description": "Test issue body",
        "issuetype": {"name": "Bug"},
        "labels": ["Duplicated"],
        "customfield_10000": "https://github.com/Test repository/issues/12",
    }
    assert response_obj["statusCode"] == 200
    jira_integrator.jira_connection.create_issue.assert_called_once_with(
        **expected_args
    )


def test_return_200_when_update_jira_issue(
    github_edit_issue_event, jira_integrator, issue_mock
):
    response_obj = jira_integrator.handle(github_edit_issue_event)

    expected_args = {"summary": "Test issue title", "description": "Test issue body"}
    issue_mock.update.assert_called_with(fields=expected_args)
    assert response_obj["statusCode"] == 200


def test_return_200_when_label_was_add(
    github_add_label_event, jira_integrator, issue_mock
):
    response_obj = jira_integrator.handle(github_add_label_event)

    expected_args = {"issuetype": {"name": "Bug"}, "labels": ["Duplicated"]}
    issue_mock.update.assert_called_with(fields=expected_args)
    assert response_obj["statusCode"] == 200


def test_return_200_when_label_was_remove(
    github_remove_label_event, jira_integrator, issue_mock
):
    response_obj = jira_integrator.handle(github_remove_label_event)

    expected_args = {"issuetype": {"name": "Bug"}, "labels": ["Duplicated"]}
    issue_mock.update.assert_called_with(fields=expected_args)
    assert response_obj["statusCode"] == 200


def test_return_200_when_issue_was_close(
    github_close_issue_event, jira_integrator, issue_mock, transitions_mock
):
    response_obj = jira_integrator.handle(github_close_issue_event)

    expected_args = [issue_mock, 3]
    jira_integrator.jira_connection.transition_issue.assert_called_with(*expected_args)
    assert response_obj["statusCode"] == 200


def test_return_200_when_issue_was_reopen(
    github_reopen_issue_event, jira_integrator, issue_mock, transitions_mock
):
    response_obj = jira_integrator.handle(github_reopen_issue_event)

    expected_args = [issue_mock, 1]
    jira_integrator.jira_connection.transition_issue.assert_called_with(*expected_args)
    assert response_obj["statusCode"] == 200
