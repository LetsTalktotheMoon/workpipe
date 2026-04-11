"""
审计日志 - 不可删除追加写入。
记录所有关键操作：生成、审查、修改、赛马结果。
"""
import json
import os
from datetime import datetime


class AuditLogger:
    def __init__(self, output_dir: str = "output"):
        self.log_dir = os.path.join(output_dir, "audit_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "audit.jsonl")

    def log(self, action: str, data: dict):
        """追加写入一条审计日志（不可删除）"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data,
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
