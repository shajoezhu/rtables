import yaml
import yamale
from loguru import logger
import os
from ratelimit import limits


class Config:
    """
    Configuration
    """

    def __init__(self, file):
        """
        Constructor
        """
        # Config file
        self.file = file
        # Validate
        conf = self.validate()
        # Source
        self.source = conf["source"]
        # Destination
        self.destination = conf["destination"]
        # Issues
        self.issues = conf["issues"]
        # Projects
        self.projects = conf["projects"]
        # Users
        self.users = conf["users"]
        # Labels
        self.labels = conf["labels"]
        # Milestones
        self.milestones = conf["milestones"]

    def load(self):
        """
        Load config from file
        """
        try:
            logger.info(f"Loading config from {self.file}")
            with open(self.file, "r") as f:
                return yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            logger.critical(e)

    def validate(self):
        """
        Validate config
        """
        pkg_root = os.path.abspath(os.path.dirname(__file__))
        schema_file = os.path.join(pkg_root, "conf", "schema.yaml")
        logger.info("Validating config...")
        schema = yamale.make_schema(schema_file)
        data = yamale.make_data(self.file)
        try:
            yamale.validate(schema, data)
            logger.info("Config validated")
            return self.load()
        except yamale.YamaleError as e:
            logger.critical("Config validation failed!\n")
            logger.critical(e.message)
