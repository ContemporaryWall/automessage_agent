from github import Github, GithubException
from langchain.tools import tool
from src.config import settings
import structlog

logger = structlog.get_logger()
gh = Github(settings.GITHUB_TOKEN)

@tool
def fetch_github_assigned_issues() -> str:
    """Fetch open issues assigned to the current user."""
    try:
        query = f"assignee:{settings.GITHUB_USERNAME} is:open"
        issues = gh.search_issues(query, sort="updated")
        # 安全地取第一页前15条
        first_page = issues.get_page(0)  # 返回list，最多30条
        results = []
        for issue in first_page[:15]:
            results.append({
                "repo": issue.repository.full_name,
                "title": issue.title,
                "url": issue.html_url,
                "updated_at": str(issue.updated_at)
            })
        logger.info("GitHub issues fetched", count=len(results))
        return str(results)
    except GithubException as e:
        logger.error("GitHub error", error=str(e))
        return f"Error: {e}"

@tool
def fetch_github_review_requests() -> str:
    """Fetch open pull requests where review is requested from the user."""
    try:
        query = f"is:pr is:open review-requested:{settings.GITHUB_USERNAME}"
        prs = gh.search_issues(query, sort="updated")
        first_page = prs.get_page(0)
        results = []
        for pr in first_page[:15]:
            results.append({
                "repo": pr.repository.full_name,
                "title": pr.title,
                "url": pr.html_url,
                "updated_at": str(pr.updated_at)
            })
        logger.info("GitHub review requests fetched", count=len(results))
        return str(results)
    except GithubException as e:
        logger.error("GitHub error", error=str(e))
        return f"Error: {e}"