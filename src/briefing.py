# src/briefing.py
from src.aggregation import ActionItem
from datetime import date

def render_briefing(items: list[ActionItem]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"📋 **Daily Briefing — {today}**", ""]
    if not items:
        lines.append("✅ 没有待办项，太棒了！")
        return "\n".join(lines)

    # 按来源分组
    from itertools import groupby
    items_sorted = sorted(items, key=lambda x: x.source)
    for source, group in groupby(items_sorted, key=lambda x: x.source):
        lines.append(f"### {source.upper()}")
        for item in list(group):
            priority_mark = {"High": "🔴", "Medium": "🟡", "Low": "⚪"}.get(item.priority, "")
            line = f"- {priority_mark} [{item.title}]({item.url}) _{item.detail}_"
            lines.append(line)
        lines.append("")

    lines.append("---")
    lines.append("自动生成，请勿回复。")
    return "\n".join(lines)
# src/briefing.py 追加部分

from rich.console import Console
from rich.table import Table
from rich import box
import webbrowser
import os
from datetime import date

def render_briefing_html(items: list[ActionItem]) -> str:
    """生成适合浏览器查看的 HTML 简报"""
    today = date.today().isoformat()
    rows = []
    if not items:
        rows.append('<tr><td colspan="4" style="text-align:center; color:green;">✅ 没有待办项，太棒了！</td></tr>')
    else:
        for item in items:
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "⚪"}.get(item.priority, "")
            rows.append(f"""<tr>
                <td>{item.source.upper()}</td>
                <td>{priority_emoji} {item.priority}</td>
                <td><a href="{item.url}" target="_blank">{item.title}</a></td>
                <td>{item.detail}</td>
            </tr>""")
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Daily Briefing {today}</title>
<style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 30px; background: #f5f7fa; }}
    .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
    h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th {{ background: #3498db; color: white; padding: 12px; text-align: left; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid #ecf0f1; }}
    tr:hover {{ background: #f8f9fa; }}
    a {{ color: #2980b9; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .footer {{ margin-top: 30px; font-size: 0.8em; color: #95a5a6; text-align: center; }}
</style>
</head>
<body>
<div class="container">
    <h2>📋 Daily Briefing — {today}</h2>
    <table>
        <thead><tr><th>来源</th><th>优先级</th><th>标题</th><th>详情</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="footer">自动生成 · 请勿回复</div>
</div>
</body>
</html>"""

def print_rich_table(items: list[ActionItem]):
    """在终端用 Rich 打印彩色表格"""
    console = Console()
    table = Table(title=f"📋 Daily Briefing — {date.today().isoformat()}", box=box.SIMPLE_HEAVY)
    table.add_column("来源", style="cyan", no_wrap=True)
    table.add_column("优先级", style="magenta")
    table.add_column("标题", style="white", ratio=2)
    table.add_column("详情", style="dim", ratio=2)

    if not items:
        table.add_row("", "", "✅ 没有待办项", "")
    else:
        priority_colors = {"High": "red", "Medium": "yellow", "Low": "green"}
        for item in items:
            p_style = priority_colors.get(item.priority, "white")
            table.add_row(
                item.source.upper(),
                f"[{p_style}]{item.priority}[/]",
                item.title,
                item.detail
            )
    console.print(table)

def save_and_open_html(html_content: str, folder: str = "output"):
    """将 HTML 保存到 output 文件夹并自动用浏览器打开"""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"briefing_{date.today().isoformat()}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    # webbrowser.open("file://" + os.path.abspath(filepath)) #不自动打开html页面