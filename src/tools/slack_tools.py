from langchain.tools import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.config import settings
import structlog
import warnings

warnings.filterwarnings("ignore", message="stars.list is deprecated")
logger = structlog.get_logger()

def _get_slack_client():
    return WebClient(token=settings.SLACK_USER_TOKEN)

@tool
def fetch_slack_mentions() -> str:
    """Fetch unread messages where the current user is mentioned."""
    client = _get_slack_client()
    try:
        # 读取最近7天的提及（简化示例）
        response = client.search_messages(query=f"<@{settings.SLACK_USER_ID}>", count=10)
        mentions = response["messages"]["matches"]
        results = []
        for msg in mentions:
            results.append({
                "channel": msg["channel"]["name"],
                "text": msg["text"],
                "ts": msg["ts"],
                "permalink": msg.get("permalink")
            })
        logger.info("Slack mentions fetched", count=len(results))
        return str(results)
    except SlackApiError as e:
        logger.error("Slack API error", error=str(e))
        return f"Error: {e}"

@tool
def fetch_slack_starred() -> str:
    """Fetch starred items of the current user."""
    client = _get_slack_client()
    try:
        response = client.stars_list(limit=20)
        items = response.get("items", [])
        results = []
        for item in items:
            if item["type"] == "message":
                msg = item["message"]
                results.append({
                    "text": msg["text"],
                    "permalink": item.get("permalink")
                })
        logger.info("Slack starred items fetched", count=len(results))
        return str(results)
    except SlackApiError as e:
        logger.error("Slack API error", error=str(e))
        return f"Error: {e}"