from jira import JIRA
from langchain.tools import tool
from src.config import settings
import structlog

logger = structlog.get_logger()

def _get_jira_client():
    return JIRA(server=settings.JIRA_URL, basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN))

@tool
def fetch_jira_tickets() -> str:
    """Fetch open Jira tickets assigned to the current user."""
    try:
        jira = _get_jira_client()
        issues = jira.search_issues(settings.JIRA_JQL, maxResults=20)
        results = []
        for issue in issues:
            results.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "type": issue.fields.issuetype.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "url": f"{settings.JIRA_URL}/browse/{issue.key}"
            })
        logger.info("Jira tickets fetched", count=len(results))
        return str(results)
    except Exception as e:
        logger.error("Jira error", error=str(e))
        return f"Error: {e}"