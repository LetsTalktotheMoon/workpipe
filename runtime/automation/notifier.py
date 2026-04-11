"""
resume_pipeline 通知模块 — 通过 ServerChan 推送微信消息。
与 job-tracker/notifier.py 共享同一个 SERVERCHAN_KEY。
"""
from __future__ import annotations

import os
from datetime import datetime

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# SERVERCHAN_KEY 从环境变量读取，与 job-tracker 共用同一个 key
_SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")


def _send(title: str, body: str) -> bool:
    key = os.environ.get("SERVERCHAN_KEY", _SERVERCHAN_KEY)
    if not key:
        print("⚠️  SERVERCHAN_KEY 未设置，跳过通知。")
        return False
    if not _HAS_REQUESTS:
        print("⚠️  requests 未安装，跳过通知。")
        return False
    try:
        resp = _requests.post(
            f"https://sctapi.ftqq.com/{key}.send",
            data={"title": title, "desp": body},
            timeout=10,
        )
        if resp.ok:
            print("📨  ServerChan (WeChat) 通知已发送。")
            return True
        else:
            print(f"⚠️  ServerChan 错误: {resp.status_code} {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"⚠️  ServerChan 发送失败: {e}")
        return False


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def notify_pipeline_started(n_new: int, n_accepted: int, n_rejected: int):
    """新岗位发现，pipeline 开始运行。"""
    title = f"🚀 Resume Pipeline 启动 | +{n_accepted} 待生成 | {_now()}"
    body = (
        f"**Pipeline 启动 ({_now()})**\n\n"
        f"- 新增岗位: {n_new}\n"
        f"- accepted (进入生成): {n_accepted}\n"
        f"- rejected (筛出): {n_rejected}\n"
    )
    _send(title, body)


def notify_pipeline_complete(
    n_generated: int,
    n_reused: int,
    n_failed: int,
    details: list[dict] | None = None,
):
    """Pipeline 正常完成。"""
    title = f"✅ Resume Pipeline 完成 | +{n_generated} 份简历 | {_now()}"
    parts = [
        f"**Pipeline 完成 ({_now()})**\n",
        f"- 生成简历: {n_generated}",
        f"- 复用 seed (跳过): {n_reused}",
        f"- 失败: {n_failed}",
    ]
    if details:
        parts.append("\n**生成明细:**")
        parts.append("| # | 公司 | 职位 | 状态 |")
        parts.append("|---|------|------|------|")
        for i, r in enumerate(details[:20], 1):
            status_icon = {"generated": "✅", "reuse": "♻️", "error": "❌", "dry_run": "⏸️"}.get(r.get("status", ""), "?")
            parts.append(f"| {i} | {r.get('company','?')[:20]} | {r.get('title','?')[:30]} | {status_icon} {r.get('status','')} |")
    _send(title, "\n".join(parts))


def notify_quota_exhausted(error_msg: str, n_completed: int, n_remaining: int):
    """Codex/Claude CLI 额度耗尽，进程已截断。"""
    title = f"⚠️ CLI 额度耗尽 — Pipeline 已截断 | {_now()}"
    body = (
        f"**额度耗尽 ({_now()})**\n\n"
        f"- 已完成: {n_completed} 份简历\n"
        f"- 剩余未处理: {n_remaining} 个岗位\n\n"
        f"**错误信息:**\n```\n{error_msg[:500]}\n```\n\n"
        f"下次 scrape 触发时，未处理岗位会自动重新入队。"
    )
    _send(title, body)


def notify_error(error_msg: str):
    """Pipeline 发生非 quota 类错误。"""
    title = f"❌ Resume Pipeline 错误 | {_now()}"
    body = (
        f"**错误 ({_now()})**\n\n"
        f"```\n{error_msg[:800]}\n```"
    )
    _send(title, body)
