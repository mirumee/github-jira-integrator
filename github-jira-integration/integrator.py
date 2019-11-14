import logging

from jira import JIRA

import enums
import utils

COMPONENT_ID_DASHBOARD = "10001"
COMPONENT_ID_DOCS = "10008"


class JiraIntegrator:
    def __init__(self, user, api_token, host):
        options = {"server": host}
        self.jira_connection = JIRA(options, basic_auth=(user, api_token))
        self.event_handlers = {
            enums.GitHubAction.OPENED.value: self.create_new_jira_issue,
            enums.GitHubAction.CREATED.value: self.create_new_jira_issue,
            enums.GitHubAction.EDITED.value: self.update_jira_issue,
            enums.GitHubAction.LABELED.value: self.update_jira_label,
            enums.GitHubAction.UNLABELED.value: self.update_jira_label,
            enums.GitHubAction.CLOSED.value: self.close_jira_issue,
            enums.GitHubAction.REOPENED.value: self.reopen_jira_issue,
        }

    def handle(self, event):
        status_code = 500
        try:
            handler = self.event_handlers[event["action"]]
            handler(event["issue"], event["repository"])
            status_code = 200
        except (KeyError, ValueError) as err:
            status_code = 404
            logging.exception(f"Can not find: {repr(err)}")
        except Exception as err:
            logging.exception(f"Error occurs: {repr(err)}")

        return {
            "statusCode": status_code,
            "headers": {"Access-Control-Allow-Origin": "*"},
        }

    def create_new_jira_issue(self, issue, repository):
        issuetype = {"name": utils.get_issue_type(issue["labels"])}
        github_link_field_name = self._get_field_id("GitHub Link")
        github_author_field_name = self._get_field_id("GitHub Author")
        github_link = utils.find_github_link(repository["full_name"], issue["number"])
        labels = utils.get_jira_labels(issue["labels"])
        project = utils.find_project(repository)
        fields = {
            "project": project,
            "summary": issue["title"],
            "description": issue["body"],
            "issuetype": issuetype,
            "labels": labels,
            github_link_field_name: github_link,
            github_author_field_name: issue.get("user", {}).get("login"),
        }

        component = None
        try:
            if "mirumee/saleor-dashboard" in github_link:
                component = self.jira_connection.component(COMPONENT_ID_DASHBOARD)
            if "mirumee/saleor-docs" in github_link:
                component = self.jira_connection.component(COMPONENT_ID_DOCS)
            if component:
                fields["components"] = [{"name": component.name}]
        except Exception as err:
            logging.exception(f"Failed to assign component: {repr(err)}")

        self.jira_connection.create_issue(**fields)

    def update_jira_issue(self, issue, repository):
        jira_issue = self._find_jira_issue(repository["full_name"], issue["number"])
        fields = {"summary": issue["title"], "description": issue["body"]}

        jira_issue.update(fields=fields)

    def update_jira_label(self, issue, repository):
        jira_issue = self._find_jira_issue(repository["full_name"], issue["number"])
        issuetype = {"name": utils.get_issue_type(issue["labels"])}
        labels = utils.get_jira_labels(issue["labels"])
        fields = {"issuetype": issuetype, "labels": labels}

        jira_issue.update(fields=fields)

    def close_jira_issue(self, issue, repository):
        jira_issue = self._find_jira_issue(repository["full_name"], issue["number"])
        ready_to_test_transition = self._get_ready_to_test_transition(jira_issue)

        self.jira_connection.transition_issue(
            jira_issue, ready_to_test_transition["id"]
        )

    def reopen_jira_issue(self, issue, repository):
        jira_issue = self._find_jira_issue(repository["full_name"], issue["number"])
        to_do_transition = self._get_to_do_transition(jira_issue)

        self.jira_connection.transition_issue(jira_issue, to_do_transition["id"])

    def _get_field_id(self, field_name):
        fields = self.jira_connection.fields()
        selected_field = filter(
            lambda field: field["name"].lower() == field_name.lower(), fields
        )
        return next(selected_field)["key"]

    def _find_jira_issue(self, github_project, issue_number):
        query = '"GitHub Link" = "{github_link}"'.format(
            github_link=utils.find_github_link(github_project, issue_number)
        )
        issues = self.jira_connection.search_issues(query)
        if not issues:
            raise ValueError(f"Can not find jira issue with number {issue_number}")

        return issues[0]

    def _get_to_do_transition(self, issue):
        return self._get_transition_by_name(issue, enums.JiraTransition.TO_DO.value)

    def _get_ready_to_test_transition(self, issue):
        return self._get_transition_by_name(
            issue, enums.JiraTransition.READY_TO_TEST.value
        )

    def _get_transition_by_name(self, issue, transition):
        transitions = self.jira_connection.transitions(issue)
        ready_to_test_transition = next(
            filter(lambda tr: tr["name"].lower() == transition, transitions)
        )
        return ready_to_test_transition
