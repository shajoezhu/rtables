import re
from loguru import logger
from ratelimit import limits


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
        self.labels = config.get("labels")

        self.sensitive_info = config.get("sensitive_info")

        self.authors = config.get("authors")
        self.close_on_migrate = config.get("close_on_migrate")

    @limits(calls=50, period=30)
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
                    f"Issue ID {issue.id} in {repo.name} on {client.base_url} has {comments.totalCount} comments"
                )
                self.issues.append(
                    {
                        "repo": repo.name,
                        "issue": issue,
                        "comments": comments,
                    }
                )

    def transform(self):
        """
        Filter issues based on authors
        Filter issues based on labels
        Add provenance information
        Redact sensitive content from issue body and comments
        """
        self.to_migrate = []
        for issue in self.issues:
            repo = issue["repo"]
            i = issue["issue"]
            body = i.body
            author = i.user.login
            labels = [l.name for l in i.labels]
            logger.info(f"Processing issue body data for {i.title} on {repo}")
            # Filter based on authors and labels
            if author in self.authors and any(l in self.labels for l in labels):
                # Redact sensitive content from issue body
                if self.sensitive_info["redact"] and self.sensitive_info["regexes"]:
                    for r in self.sensitive_info["regexes"]:
                        body = re.sub(r, "<redacted>", body)
                # Add provenance message to issue body
                if self.add_provenance:
                    body = (
                        body
                        + "\n\nProvenance: \n```\n"
                        + f"Origin: {i.html_url}\n"
                        + f"Creator: {i.user.name}\n"
                        + "```"
                    )
                updated_comments = []
                logger.debug(f"Processing comment data for {i.title} on {repo}")
                for comment in issue["comments"]:
                    comment_body = comment.body
                    # Redact sensitive content from comment body
                    if self.sensitive_info["redact"] and self.sensitive_info["regexes"]:
                        for r in self.sensitive_info["regexes"]:
                            comment_body = re.sub(r, "<redacted>", comment_body)
                    updated_comments.append(comment_body)
                self.to_migrate.append(
                    {
                        "repo": repo,
                        "title": i.title,
                        "body": body,
                        "comments": updated_comments,
                        "milestone": i.milestone,
                        "labels": i.labels,
                    }
                )

    def copy(self, client):
        """
        Copy issue body and comments to repo
        """
        for i in self.to_migrate:
            # Create the issues
            logger.info(f"Copying issues to {i['repo']} on {client.base_url}")
            repo = client.client.get_repo(f"{client.owner}/{i['repo']}")
            issue = repo.create_issue(
                title=i["title"],
                body=i["body"],
                # milestone=i["milestone"], # TODO: Convert this to a milestone object
                labels=i["labels"],
            )
            logger.debug(
                f"Copied {i['title']} to {repo.full_name} on {client.base_url}"
            )
            for comment in i["comments"]:
                issue.create_comment(comment)
                logger.debug(
                    f"Added comment to {i['title']} on {repo.full_name} on {client.base_url}"
                )
