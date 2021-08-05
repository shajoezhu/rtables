from loguru import logger
from ratelimit import limits
import time

class Labels:
    """
    Labels
    """

    def __init__(self, config):
        """
        Constructor
        """
        self.migrate = config.get("migrate")

    @limits(calls=30, period=30)
    def get(self, client):
        """
        Get issues and comments
        """
        self.to_migrate = []
        if self.migrate:
            for repo in client.repositories:
                logger.info(f"Getting labels from {repo.name} on {client.base_url}")
                self.to_migrate.append(
                    {
                        "repo": repo.name,
                        "labels": repo.get_labels(),
                    }
                )
                try:
                    repo.create_label(
                        "migrated", "#FF7F50", description="Issue has been migrated"
                    )
                    logger.info(
                        f"Created the 'migrated' label on {repo.name} on {client.base_url}"
                    )
                    time.sleep(1)
                except:
                    logger.warning(
                        f"The 'migrated' label already exists on {repo.name} on {client.base_url}"
                    )
                    pass
                logger.debug(
                    f"Obtained {len(self.to_migrate)} labels from {repo.name} on {client.base_url}"
                )

    @limits(calls=30, period=30)
    def copy(self, client):
        """
        Copy labels to destination
        """
        for artifact in self.to_migrate:
            logger.info(f"Copying labels to {artifact['repo']} on {client.base_url}")
            repo = client.client.get_repo(f"{client.owner}/{artifact['repo']}")
            time.sleep(1)
            for label in artifact["labels"]:
                repo.create_label(
                    name=label.name, color=label.color, description=label.description
                )
                logger.debug(
                    f"Copied {label.name} to {repo.full_name} on {client.base_url}"
                )
                time.sleep(1)
