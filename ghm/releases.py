from loguru import logger
from ratelimit import limits
import time


class Releases:
    """
    Releases
    """

    def __init__(self, config):
        """
        Constructor
        """
        self.migrate = config.get("migrate")

    @limits(calls=30, period=30)
    def get(self, client):
        """
        Get releases from repos
        """
        self.to_migrate = []
        if self.migrate:
            for repo in client.repositories:
                logger.info(f"Getting releases from {repo.name} on {client.base_url}")
                all_releases = []
                try:
                    all_releases = repo.get_releases()
                except:
                    logger.warning(f"Could not get all releases from {repo.name} on {client.base_url}")
                latest_release = None
                try:
                    latest_release = repo.get_latest_release()
                except:
                    logger.warning(f"Could not get latest release from {repo.name} on {client.base_url}")
                self.to_migrate.append(
                    {
                        "repo": repo.name,
                        "releases": all_releases,
                        "latest_release": latest_release,
                    }
                )
                logger.debug(
                    f"Obtained {len(self.to_migrate)} releases from {repo.name} on {client.base_url}"
                )

    @limits(calls=30, period=30)
    def copy(self, client):
        """
        Copy releases to destination
        """
        for artifact in self.to_migrate:
            repo = client.client.get_repo(f"{client.owner}/{artifact['repo']}")
            latest_release = artifact["latest_release"]
            # Copy all other releases first
            for release in artifact["releases"]:
                if release.title != latest_release.title:
                    logger.info(f"Copying releases to {artifact['repo']} on {client.base_url}")
                    try:
                        repo.create_git_release(
                            tag=release.tag_name,
                            name=release.title,
                            message=release.body,
                            draft=release.draft,
                            prerelease=release.prerelease,
                            target_commitish=release.target_commitish,
                        )
                        logger.debug(
                            f"Copied {release.title} to {repo.full_name} on {client.base_url}"
                        )
                        time.sleep(3)
                    except:
                        logger.warning(
                            f"{release.title} already exists on {repo.full_name} on {client.base_url} or has an invalid release tag associated with it"
                        )
                        pass
            # Copy latest release last
            if latest_release is not None:
                logger.info(
                    f"Copying latest release to {artifact['repo']} on {client.base_url}"
                )
                try:
                    repo.create_git_release(
                        tag=latest_release.tag_name,
                        name=latest_release.title,
                        message=latest_release.body,
                        draft=latest_release.draft,
                        prerelease=latest_release.prerelease,
                        target_commitish=latest_release.target_commitish,
                    )
                    logger.debug(
                        f"Copied latest release {latest_release.title} to {repo.full_name} on {client.base_url}"
                    )
                except:
                    logger.warning(
                        f"{latest_release.title} already exists on {repo.full_name} on {client.base_url} or has an invalid release tag associated with it"
                    )
                    pass
