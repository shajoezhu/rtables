import re
from loguru import logger
from ratelimit import limits
import time
import github


class Issues:
    """
    Issues
    """

    def __init__(self, config):
        """
        Constructor
        """
        self.migrate = config.get("migrate")
        self.state = config.get("state")
        self.add_provenance = config.get("add_provenance")

        self.sensitive_info = config.get("sensitive_info")

        self.authors = config.get("authors")

        self.lock_on_migrate = config.get("lock_on_migrate")

        self.add_migrated_label = config.get("add_migrated_label")

    @limits(calls=30, period=30)
    def get(self, client):
        """
        Get issues and comments
        """
        self.issues = []
        # Get all issues and comments from all repos
        for repo in client.repositories:
            logger.info(f"Getting issues from {repo.name} on {client.base_url}")
            issues = repo.get_issues(state=self.state)
            logger.debug(f"Obtained {issues.totalCount} issues from {client.base_url}")
            for issue in issues:
                comments = issue.get_comments()
                logger.debug(
                    f"#{issue.id} in {repo.name} on {client.base_url} has {comments.totalCount} comments"
                )
                self.issues.append(
                    {
                        "repo": repo.name,
                        "issue": issue,
                        "comments": comments,
                    }
                )

    def transform(self, users):
        """
        Filter issues based on authors
        Add provenance information
        Redact sensitive content from issue body and comments
        Add the migrated label to the source issue
        """
        self.to_migrate = []
        for issue in self.issues:
            repo = issue["repo"]
            i = issue["issue"]
            body = i.body
            author = i.user.login
            logger.info(f"Processing issue body data for {i.title} on {repo}")
            # Filter based on authors, and do not migrate migrated issues
            if author in self.authors and "migrated" not in [x.name for x in i.labels]:
                # Redact sensitive content from issue body
                if self.sensitive_info["redact"] and self.sensitive_info["regexes"]:
                    for r in self.sensitive_info["regexes"]:
                        body = re.sub(r, "<REDACTED>", body)
                # Add provenance message to issue body
                if self.add_provenance:
                    body = (
                        body
                        + "\n\nProvenance: \n```\n"
                        + f"Creator: {i.user.login}\n"
                        + "```"
                    )
                # Replace author mentions
                for user in users:
                    body = re.sub(user["source"], user["destination"], body)
                updated_comments = []
                logger.debug(f"Processing comment data for {i.title} on {repo}")
                for comment in issue["comments"]:
                    comment_body = comment.body
                    # Redact sensitive content from comment body
                    if self.sensitive_info["redact"] and self.sensitive_info["regexes"]:
                        for r in self.sensitive_info["regexes"]:
                            comment_body = re.sub(r, "<REDACTED>", comment_body)
                    # Add provenance message to issue comments
                    if self.add_provenance:
                        comment_body = (
                            comment_body
                            + "\n\nProvenance: \n```\n"
                            + f"Creator: {comment.user.login}\n"
                            + "```"
                        )
                    # Replace author mentions
                    for user in users:
                        comment_body = re.sub(
                            user["source"], user["destination"], comment_body
                        )
                    updated_comments.append(comment_body)
                self.to_migrate.append(
                    {
                        "number": i.number,
                        "repo": repo,
                        "title": i.title,
                        "body": body,
                        "comments": updated_comments,
                        "milestone": i.milestone,
                        "labels": i.labels,
                    }
                )

    @limits(calls=10, period=30)
    def copy(self, client):
        """
        Copy issue body and comments to repo
        """
        for i in self.to_migrate:
            # Create the issues
            logger.info(
                f"Copying issue {i['title']} to {i['repo']} on {client.base_url}"
            )
            repo = client.client.get_repo(f"{client.owner}/{i['repo']}")
            milestone = i["milestone"]
            if not isinstance(milestone, github.Milestone.Milestone):
                milestone = github.GithubObject.NotSet
            issue = repo.create_issue(
                title=i["title"],
                body=i["body"],
                # milestone=milestone, ## TODO: Figure out milestones
                labels=i["labels"],
            )
            logger.debug(
                f"Copied {i['title']} to {repo.full_name} on {client.base_url}"
            )
            time.sleep(2)
            for comment in i["comments"]:
                issue.create_comment(comment)
                logger.debug(
                    f"Added comment to {i['title']} on {repo.full_name} on {client.base_url}"
                )
                time.sleep(3)

    @limits(calls=50, period=30)
    def cleanup(self, client):
        """
        Post migration cleanup
        """
        for i in self.to_migrate:
            repo = client.client.get_repo(f"{client.owner}/{i['repo']}")
            issue = repo.get_issue(i["number"])
            if self.add_migrated_label:
                logger.info(
                    f"Adding 'migrated' label to issue #{i['number']} on {i['repo']} on {client.base_url}"
                )
                issue.add_to_labels("migrated")
            if self.lock_on_migrate:
                logger.info(
                    f"Locking issue #{i['number']} on {i['repo']} on {client.base_url}"
                )
                issue.create_comment(
                    "## This issue is now locked as it has been migrated."
                )
                issue.lock("resolved")
