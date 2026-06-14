# src/git_publisher.py
import subprocess
import os
import shutil
import structlog
from datetime import date

logger = structlog.get_logger()

def push_to_github(html_content: str, repo_path: str = ".", branch: str = "gh-pages"):
    """
    将 HTML 内容发布到 GitHub Pages 的指定分支，且绝不泄露 .env 文件
    """
    env_backup = None
    current_branch = None
    stashed = False

    try:
        # 0. 准备输出目录
        output_folder = os.path.join(repo_path, "output")
        os.makedirs(output_folder, exist_ok=True)
        filepath = os.path.join(output_folder, "index.html")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 1. 确保在 git 仓库中
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            logger.error("当前目录不是一个 Git 仓库")
            return False

        # 2. 备份 .env 文件内容（如果存在）
        env_path = os.path.join(repo_path, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                env_backup = f.read()
            logger.info("已备份 .env 文件")

        # 3. 记录当前分支
        current_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path, stderr=subprocess.PIPE
        ).decode().strip()
        logger.info(f"当前分支：{current_branch}")

        # 4. 暂存未提交的更改（包括 .env，因为 .env 未被跟踪，git stash 默认不处理未跟踪文件）
        # 我们使用 git stash --include-untracked 来暂存所有内容，包括 .env
        has_changes = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo_path
        ).decode().strip()
        if has_changes:
            logger.info("工作区有未提交更改，暂存所有内容（含未跟踪文件）...")
            subprocess.run(
                ["git", "stash", "push", "--include-untracked", "-m", "briefing-auto-stash"],
                cwd=repo_path, check=True
            )
            stashed = True

        # 5. 切换到目标分支（不存在则创建孤儿分支）
        try:
            subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
            logger.info(f"已切换到分支 {branch}")
        except subprocess.CalledProcessError:
            logger.info(f"分支 {branch} 不存在，创建孤儿分支...")
            subprocess.run(["git", "checkout", "--orphan", branch], cwd=repo_path, check=True)

        # 6. 清理索引中的所有旧文件（但工作目录的文件仍存在）
        subprocess.run(["git", "rm", "-rf", "--ignore-unmatch", "."], cwd=repo_path, check=False)

        # 7. 删除工作目录中多余的 gitignore（因为我们要重建一个，确保 .env 被忽略）
        #    注意：不再删除 .env ！我们依赖 .gitignore 来阻止它被提交
        gitignore_path = os.path.join(repo_path, ".gitignore")
        if os.path.exists(gitignore_path):
            os.remove(gitignore_path)
            logger.info("已删除旧 .gitignore（将新建）")

        # 8. 将 output 文件夹内的内容复制到仓库根目录
        for f in os.listdir(output_folder):
            src = os.path.join(output_folder, f)
            dst = os.path.join(repo_path, f)
            shutil.copy(src, dst)

        # 9. 删除 output 目录自身
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        # 10. 创建新的 .gitignore 文件，确保 .env 永远不会被提交
        gitignore_content = ".env\noutput/\nsrc/\n.venv/\n.idea/\n*.pyc\n"
        with open(os.path.join(repo_path, ".gitignore"), "w") as f:
            f.write(gitignore_content)

        # 11. 添加、提交、推送（.env 会被 .gitignore 忽略，不会被加入）
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        today = date.today().isoformat()
        commit_msg = f"Update briefing {today}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, capture_output=True)
        if result.returncode != 0:
            logger.info("内容无变化，跳过提交")
        else:
            logger.info("提交成功")

        subprocess.run(["git", "push", "origin", branch, "-f"], cwd=repo_path, check=True)
        logger.info(f"已推送至远程 {branch} 分支")

        # 12. 切回原分支并恢复暂存
        subprocess.run(["git", "checkout", current_branch], cwd=repo_path, check=True)
        if stashed:
            try:
                subprocess.run(["git", "stash", "pop"], cwd=repo_path, check=True)
                logger.info("已恢复暂存的工作区")
            except subprocess.CalledProcessError as e:
                logger.warning(f"恢复暂存时发生冲突，可能需要手动处理: {e}")
        else:
            # 如果没有暂存，但之前备份了 .env，则需要检查 .env 是否存在（孤儿分支切换可能丢失）
            if env_backup is not None and not os.path.exists(env_path):
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(env_backup)
                logger.info(".env 文件已从备份恢复")

        return True

    except Exception as e:
        logger.error("Git 发布失败", error=str(e))
        # 尝试切回原分支
        if current_branch:
            try:
                subprocess.run(["git", "checkout", current_branch], cwd=repo_path, check=False)
                if stashed:
                    subprocess.run(["git", "stash", "pop"], cwd=repo_path, check=False)
            except:
                pass

        # 如果 .env 丢失，尝试从备份恢复
        if env_backup is not None:
            env_path = os.path.join(repo_path, ".env")
            if not os.path.exists(env_path):
                try:
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(env_backup)
                    logger.info(".env 文件已从备份恢复（异常处理）")
                except Exception as ex:
                    logger.error(f"恢复 .env 失败: {ex}")
        return False