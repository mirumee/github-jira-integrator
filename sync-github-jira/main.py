import os

import synchronizer
import utils


def lambda_handler(*_):
    github_project = os.environ.get("GITHUB_PROJECT")
    if not github_project:
        raise ValueError("Missing GITHUB_PROJECT environment")

    g = synchronizer.GitHubCredentials(
        github_project, **utils.get_secret(os.environ.get("GITHUB_CREDENTIALS_VAULT"))
    )
    j = synchronizer.JiraCredentials(
        **utils.get_secret(os.environ.get("JIRA_CREDENTIALS_VAULT"))
    )
    s = synchronizer.Synchronizer(g, j)
    s.synchronize()
