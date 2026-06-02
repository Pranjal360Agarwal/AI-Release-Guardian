import re
from dataclasses import dataclass

import httpx

from app.config import settings
from app.models import PullRequestInfo


PR_URL_RE = re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)")


@dataclass
class PullRequestPayload:
    info: PullRequestInfo
    diff: str


class GitHubService:
    def __init__(self) -> None:
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    def parse_pr_url(self, pr_url: str) -> tuple[str, str, int]:
        match = PR_URL_RE.search(pr_url)
        if not match:
            raise ValueError("Invalid GitHub PR URL. Use https://github.com/owner/repo/pull/123")
        return match.group("owner"), match.group("repo"), int(match.group("number"))

    async def fetch_pull_request(self, pr_url: str) -> PullRequestPayload:
        owner, repo, number = self.parse_pr_url(pr_url)
        async with httpx.AsyncClient(timeout=30) as client:
            pr_res = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}",
                headers=self.headers,
            )
            pr_res.raise_for_status()
            files_res = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}/files",
                headers=self.headers,
            )
            files_res.raise_for_status()

        pr = pr_res.json()
        files = files_res.json()
        diff_parts: list[str] = []
        additions = 0
        deletions = 0
        for file in files:
            additions += file.get("additions", 0)
            deletions += file.get("deletions", 0)
            patch = file.get("patch", "")
            diff_parts.append(
                f"FILE: {file.get('filename')}\n"
                f"STATUS: {file.get('status')}\n"
                f"ADDITIONS: {file.get('additions')} DELETIONS: {file.get('deletions')}\n"
                f"{patch}\n"
            )

        info = PullRequestInfo(
            owner=owner,
            repo=repo,
            number=number,
            title=pr.get("title", ""),
            author=pr.get("user", {}).get("login", "unknown"),
            branch=pr.get("head", {}).get("ref", ""),
            base_branch=pr.get("base", {}).get("ref", ""),
            url=pr_url,
            files_changed=len(files),
            additions=additions,
            deletions=deletions,
        )
        return PullRequestPayload(info=info, diff="\n\n".join(diff_parts))

    async def post_pr_comment(self, report_markdown: str, owner: str, repo: str, number: int) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{number}/comments",
                headers=self.headers,
                json={"body": report_markdown},
            )
            response.raise_for_status()
