from ghm.client import Client
from ghm.config import Config
from ghm.users import Users
from ghm.issues import Issues
from ghm.projects import Projects
from ghm.labels import Labels
from ghm.milestones import Milestones


def main(config_file):
    # Load config
    config = Config(config_file)

    # Init clients
    source_client = Client(config.source)
    dest_client = Client(config.destination)

    # Get users
    source_users = Users(config.users, filter="source", client=source_client)
    dest_users = Users(config.users, filter="destination", client=dest_client)

    # Get issues from source
    issues = Issues(config.issues)
    issues.get(source_client)

    # Get projects from source
    projects = Projects(config.projects)
    projects.get(source_client)

    # Get milestones from source
    milestones = Milestones(config.milestones)
    milestones.get(source_client)

    # Get labels from source
    labels = Labels(config.labels)
    labels.get(source_client)

    # Copy projects to destination
    projects.transform()
    projects.copy(dest_client)

    # Copy milestones to destination
    milestones.copy(dest_client)

    # Copy issues to destination
    issues.transform()
    issues.copy(dest_client)
