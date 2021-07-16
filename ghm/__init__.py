"""
CLI and main
"""

import argparse
import pkg_resources

from ghm.main import main


def cli():
    """
    Command line interface
    """
    parser = argparse.ArgumentParser(description="Github Migrator")
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file containing migration settings",
        dest="config",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Display current version",
        action="version",
        version=pkg_resources.require("ghm")[0].version,
    )
    args = parser.parse_args()
    main(args.config)
