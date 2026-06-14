from slack_sdk import WebClient
from src.config import settings
import structlog

logger = structlog.get_logger()

def send_slack_briefing(channel: str, text: str):
    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(channel=channel, text=text, mrkdwn=True)
        logger.info("Slack briefing sent", channel=channel, ts=response["ts"])
    except Exception as e:
        logger.error("Slack send failed", error=str(e))
        raise