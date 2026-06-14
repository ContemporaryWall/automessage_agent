# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Slack
    SLACK_BOT_TOKEN: str
    SLACK_USER_TOKEN: str   # 用于获取用户相关消息
    SLACK_USER_ID: str      # 当前用户 UID

    # GitHub
    GITHUB_TOKEN: str
    GITHUB_USERNAME: str

    # Jira
    JIRA_URL: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_JQL: str = "assignee = currentUser() AND status not in (Closed, Done)"

    # Email
    SMTP_HOST: str = "smtp.office365.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_RECIPIENTS: list[str]

    # LangChain
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-4o-mini"

    # Scheduler
    SCHEDULE_HOUR: int = 8
    SCHEDULE_MINUTE: int = 0

    class Config:
        env_file = r"C:\Users\asus\PycharmProjects\automessage_agent\.env"

settings = Settings()