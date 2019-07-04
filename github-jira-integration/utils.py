import base64
import json

import boto3

import enums


def find_project(repository):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("github-jira")
    dynamodb_key = {"ProjectName": repository["full_name"]}

    response = table.get_item(Key=dynamodb_key)

    return response["Item"]["JIRATag"]


def get_issue_type(labels):
    is_bug = any(filter(lambda x: x["name"].lower() == "bug", labels))
    return enums.JiraIssueType.BUG.value if is_bug else enums.JiraIssueType.TASK.value


def to_camel_case(text):
    title = text.title()
    title_without_spaces = [c for c in title if not c.isspace()]
    return "".join(title_without_spaces)


def find_github_link(project, number):
    return f"https://github.com/{project}/issues/{number}"


def get_jira_labels(labels):
    labels_without_bug = filter(lambda label: label["name"].lower() != "bug", labels)
    labels_camel_case = map(
        lambda label: to_camel_case(label["name"]), labels_without_bug
    )
    return list(labels_camel_case)


def get_secret(secret_name):
    """
    :raise: Exception when secret is not found
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret = response["SecretString"]
    else:
        secret = base64.b64decode(response["SecretBinary"])
    return json.loads(secret)
