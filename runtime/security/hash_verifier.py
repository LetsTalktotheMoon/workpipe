"""
Hash校验器 - 运行时校验关键配置/规则文件的完整性。
防止审查规则被篡改（历史教训：员工曾修改max_bullets_per_exp从6到10）。
"""
import hashlib
import json
import os


class HashVerifier:
    def __init__(self):
        self.baseline_hashes = {}

    def register(self, name: str, content: str):
        """注册一个基准hash"""
        self.baseline_hashes[name] = hashlib.sha256(content.encode()).hexdigest()

    def verify(self, name: str, content: str) -> bool:
        """校验内容是否与基准一致"""
        if name not in self.baseline_hashes:
            return True  # 未注册则跳过
        current = hashlib.sha256(content.encode()).hexdigest()
        return current == self.baseline_hashes[name]

    def verify_all(self, items: dict) -> list:
        """批量校验，返回被篡改的项"""
        tampered = []
        for name, content in items.items():
            if not self.verify(name, content):
                tampered.append(name)
        return tampered
