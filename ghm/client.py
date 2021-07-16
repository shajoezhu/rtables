from github import Github
import os
from loguru import logger
from ratelimit import limits


class Client:
    """
    Github client
    """

    def __init__(self, config):
        """
        Constructor
        """
        self.base_url = config["base_url"]
        self.owner = config["owner"]
        self.token = os.environ.get(config["token_env_var"])
        self.repo_names = config.get("repositories", [])

        logger.info(f"Initializing client for {self.base_url}")
        self.client = Github(
            base_url=self.base_url, login_or_token=self.token, per_page=100
        )

        self.org = self.client.get_organization(self.owner)
        self.get_repos()
        logger.info(f"Client initialization complete for {self.base_url}")

    @limits(calls=30, period=30)
    def get_repos(self):
        """
        Get repos
        """
        self.repositories = []
        logger.debug(f"Getting repository info from {self.base_url}")
        for repo in self.repo_names:
            self.repositories.append(self.client.get_repo(f"{self.owner}/{repo}"))
        logger.debug(f"Obtained {len(self.repositories)} repos from {self.base_url}")

    @limits(calls=30, period=30)
    def get_user(self, username):
        """
        Get user object
        """
        try:
            logger.debug(f"Getting user info for {username} from {self.base_url}")
            return self.client.get_user(username)
        except:
            logger.critical(f"Error getting {username} from {self.base_url}")
            raise
