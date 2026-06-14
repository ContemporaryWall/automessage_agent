# src/agent.py
import os
from src.tools.slack_tools import fetch_slack_mentions, fetch_slack_starred
from src.tools.github_tools import fetch_github_assigned_issues, fetch_github_review_requests
from src.tools.jira_tools import fetch_jira_tickets
from src.aggregation import aggregate
from src.briefing import (
    render_briefing,
    print_rich_table,
    render_briefing_html,
    save_and_open_html,
)
from src.notifiers.email_notifier import send_email_briefing
from src.notifiers.slack_notifier import send_slack_briefing
from src.git_publisher import push_to_github
from datetime import date
import structlog

logger = structlog.get_logger()

def run_daily_briefing():
    logger.info("Starting daily briefing aggregation")
    # 1. 采集数据
    mentions = fetch_slack_mentions.run("")
    stars = fetch_slack_starred.run("")
    gh_issues = fetch_github_assigned_issues.run("")
    gh_reviews = fetch_github_review_requests.run("")
    jira_tickets = fetch_jira_tickets.run("")

    # 2. 聚合
    items = aggregate(mentions, stars, gh_issues, gh_reviews, jira_tickets)
    logger.info("Aggregation complete", item_count=len(items))

    # 3. 生成简报
    briefing_md = render_briefing(items)

    # 4. 终端美化输出
    print_rich_table(items)

    # 5. 生成 HTML 并保存到本地 / 自动打开
    html = render_briefing_html(items)
    save_and_open_html(html)  # 可选，如果不想自动打开浏览器可注释掉

    # 6. 推送到 GitHub Pages（免费网站）
    # 获取项目根目录绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #不这么做会导致找不到git地址
    success = push_to_github(html, repo_path=project_root)
    if success:
        site_url = "https://你的用户名.github.io/automessage_agent/"
        logger.info(f"✅ 在线看板已更新：{site_url}")
    else:
        logger.error("❌ GitHub Pages 发布失败，请检查 Git 配置")

    # 7. 推送邮件和 Slack
    subject = f"Daily Briefing - {date.today().isoformat()}"
    try:
        send_email_briefing(subject, briefing_md)
    except Exception as e:
        logger.error("Email delivery failed, fallback to Slack", error=str(e))
    try:
        send_slack_briefing(channel="U0BAEP8NXGC", text=briefing_md)
    except Exception as e:
        logger.error("Slack delivery failed", error=str(e))
    logger.info("Daily briefing completed")