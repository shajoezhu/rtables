from ratelimit import limits
from loguru import logger
import re

"""
Projects
"""


class Projects:
    """
    Constructor
    """

    def __init__(self, config):
        self.migrate = config.get("migrate")
        self.add_provenance = config.get("add_provenance")
        self.sensitive_info = config.get("sensitive_info")
        self.close_on_migrate = config.get("close_on_migrate")
        self.state = config.get("state")
        self.names = config.get("names")

    """
    Get projects
    """

    @limits(calls=30, period=30)
    def get(self, client):
        self.projects = []
        if self.migrate:
            logger.info(f"Getting projects from {client.org.name}")
            self.projects = client.org.get_projects(state=self.state)
            logger.debug(
                f"Obtained {self.projects.totalCount} projects from {client.org.name}"
            )

    def transform(self):
        """
        Prep objects for loading to destination
        Redact sensitive content
        Add provenance info
        """
        self.to_migrate = []
        for project in self.projects:
            if project.name in self.names:
                logger.info(f"Processing data for {project.name}")
                new_body = project.body
                columns = project.get_columns()
                logger.debug(
                    f"Obtained {columns.totalCount} columns from {project.name}"
                )
                # Redact sensitive content
                if self.sensitive_info["redact"] and self.sensitive_info["regexes"]:
                    for r in self.sensitive_info["regexes"]:
                        new_body = re.sub(r, "<redacted>", new_body)
                # Add provenance message
                if self.add_provenance:
                    new_body = (
                        new_body
                        + "\n\nProvenance: \n```\n"
                        + f"Origin: {project.html_url}\n"
                        + f"Creator: {project.creator.name}\n"
                        + f"Created at: {project.created_at}\n"
                        + "```"
                    )
                # Create migration artifact
                self.to_migrate.append(
                    {"name": project.name, "body": new_body, "columns": columns}
                )

    @limits(calls=30, period=30)
    def copy(self, client):
        """
        Copy projects and columns
        """
        for artifact in self.to_migrate:
            logger.info(f"Copying project {artifact['name']} to {client.owner}")
            project = client.org.create_project(
                name=artifact["name"], body=artifact["body"]
            )
            for column in artifact["columns"]:
                logger.info(
                    f"Copying column {column.name} to {artifact['name']} on {client.owner}"
                )
                project.create_column(name=column.name)
