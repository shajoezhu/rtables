from loguru import logger
from ratelimit import limits


class Milestones:
    """
    Milestones
    """

    def __init__(self, config):
        """
        Constructor
        """
        self.migrate = config.get("migrate")
        self.state = config.get("state")

    @limits(calls=30, period=30)
    def get(self, client):
        """
        Get milestones from repos
        """
        self.to_migrate = []
        if self.migrate:
            for repo in client.repositories:
                logger.info(f"Getting milestones from {repo.name} on {client.base_url}")
                self.to_migrate.append(
                    {
                        "repo": repo.name,
                        "milestones": repo.get_milestones(state=self.state),
                    }
                )
                logger.debug(
                    f"Obtained {len(self.to_migrate)} milestones from {repo.name} on {client.base_url}"
                )

    @limits(calls=30, period=30)
    def copy(self, client):
        """
        Copy milestones to destination
        """
        for artifact in self.to_migrate:
            repo = client.client.get_repo(f"{client.owner}/{artifact['repo']}")
            logger.info(
                f"Copying milestones to {artifact['repo']} on {client.base_url}"
            )
            for milestone in artifact["milestones"]:
                try:
                    repo.create_milestone(
                        title=milestone.title,
                        state=milestone.state,
                        description=milestone.description,
                    )
                    logger.debug(
                        f"Copied {milestone.title} to {repo.full_name} on {client.base_url}"
                    )
                except:
                    logger.warning(
                        f"{milestone.title} already exists on {repo.full_name} on {client.base_url}"
                    )
                    pass
