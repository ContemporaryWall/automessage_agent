# src/aggregation.py
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timezone
import json

class ActionItem(BaseModel):
    source: Literal["slack", "github", "jira"]
    title: str
    detail: str          # 简短描述
    url: str
    priority: str        # High/Medium/Low
    due_date: str | None = None
    timestamp: str       # ISO格式

def aggregate(raw_slack_mentions: str, raw_slack_stars: str,
              raw_github_issues: str, raw_github_reviews: str,
              raw_jira_tickets: str) -> list[ActionItem]:
    items: list[ActionItem] = []

    # 处理 Slack mentions
    try:
        mentions = json.loads(raw_slack_mentions.replace("'", "\"")) if "Error" not in raw_slack_mentions else []
        for m in mentions:
            items.append(ActionItem(
                source="slack", title=f"Slack mention in #{m['channel']}",
                detail=m['text'][:100], url=m.get('permalink', ''),
                priority="Medium", timestamp=m.get('ts', datetime.now(timezone.utc).isoformat())
            ))
    except Exception:
        pass

    # 处理 Slack starred
    try:
        stars = json.loads(raw_slack_stars.replace("'", "\"")) if "Error" not in raw_slack_stars else []
        for s in stars:
            items.append(ActionItem(
                source="slack", title="Starred message",
                detail=s['text'][:100], url=s.get('permalink', ''),
                priority="Low", timestamp=datetime.now(timezone.utc).isoformat()
            ))
    except Exception:
        pass

    # 处理 GitHub issues
    try:
        issues = json.loads(raw_github_issues.replace("'", "\"")) if "Error" not in raw_github_issues else []
        for i in issues:
            items.append(ActionItem(
                source="github", title=f"Issue: {i['title']}", detail=f"Repo: {i['repo']}",
                url=i['url'], priority="High",
                timestamp=i['updated_at']
            ))
    except Exception:
        pass

    # 处理 GitHub reviews
    try:
        reviews = json.loads(raw_github_reviews.replace("'", "\"")) if "Error" not in raw_github_reviews else []
        for r in reviews:
            items.append(ActionItem(
                source="github", title=f"PR Review: {r['title']}", detail=f"Repo: {r['repo']}",
                url=r['url'], priority="High",
                timestamp=r['updated_at']
            ))
    except Exception:
        pass

    # 处理 Jira tickets
    try:
        tickets = json.loads(raw_jira_tickets.replace("'", "\"")) if "Error" not in raw_jira_tickets else []
        for t in tickets:
            priority = t.get('priority', 'Medium')
            if priority == "Highest": priority = "High"
            items.append(ActionItem(
                source="jira", title=f"{t['key']}: {t['summary']}",
                detail=f"Type: {t['type']}, Status: {t['status']}",
                url=t['url'], priority=priority,
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
    except Exception:
        pass

    # 按优先级与时间排序
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    items.sort(key=lambda x: (priority_order.get(x.priority, 2), x.timestamp), reverse=False)
    return items