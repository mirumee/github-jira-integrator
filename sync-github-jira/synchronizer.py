import collections

import github
import jira
import utils


GitHubCredentials = collections.namedtuple(
    "GitHubCredentials", "repository_full_name access_token"
)
JiraCredentials = collections.namedtuple("JiraCredentials", "user api_token host")


class Synchronizer:
    def __init__(self, github_credentials, jira_credentials):
        options = {"server": jira_credentials.host}
        auth = (jira_credentials.user, jira_credentials.api_token)
        self.jira_connection = jira.JIRA(options, basic_auth=auth)

        self.github_connection = github.Github(github_credentials.access_token)
        self.repo = self.github_connection.get_repo(
            github_credentials.repository_full_name
        )
        self.repo_full_name = github_credentials.repository_full_name

    def get_issues(self):
        return filter(
            lambda issue: not issue.pull_request, self.repo.get_issues(state="open")
        )

    def synchronize(self):
        for issue in self.get_issues():
            self.check_issue_on_jira(issue)

    def check_issue_on_jira(self, issue):
        jira_issue = self.__find_jira_issue(issue.html_url)
        if jira_issue:
            self.__update_issue(jira_issue, issue)
        else:
            self.__create_issue(issue)

    def __create_issue(self, github_issue):
        print("Trying create: {}...".format(github_issue.title))
        issuetype = {"name": utils.get_issue_type(github_issue.labels)}
        github_link_field_name = self.__get_field_id("GitHub Link")
        github_author_field_name = self.__get_field_id("GitHub Author")
        github_link = github_issue.html_url
        labels = utils.get_jira_labels(github_issue.labels)
        project = utils.find_project(self.repo_full_name)
        fields = {
            "project": project,
            "summary": github_issue.title,
            "description": github_issue.body,
            "issuetype": issuetype,
            "labels": labels,
            github_link_field_name: github_link,
            github_author_field_name: github_issue.user.login,
        }
        self.jira_connection.create_issue(**fields)
        print("done")

    def __update_issue(self, jira_issue, github_issue):
        print("Trying update: {}...".format(github_issue.title))
        issuetype = {"name": utils.get_issue_type(github_issue.labels)}
        labels = utils.get_jira_labels(github_issue.labels)
        fields = {
            "summary": github_issue.title,
            "description": github_issue.body,
            "issuetype": issuetype,
            "labels": labels,
        }
        jira_issue.update(fields=fields)
        print("done")

    def __find_jira_issue(self, issue_url):
        query = '"GitHub Link" = "{github_link}"'.format(github_link=issue_url)
        issues = self.jira_connection.search_issues(query)
        return issues[0] if len(issues) else None

    def __get_field_id(self, field_name):
        fields = self.jira_connection.fields()
        selected_field = filter(
            lambda field: field["name"].lower() == field_name.lower(), fields
        )
        return next(selected_field)["key"]
