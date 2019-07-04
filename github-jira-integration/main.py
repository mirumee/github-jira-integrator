import os

import integrator
import utils


def lambda_handler(event, _):
    secrets = utils.get_secret(os.environ["SECRET_MANAGER_VAULT"])
    jira_integrator = integrator.JiraIntegrator(**secrets)

    return jira_integrator.handle(event)
