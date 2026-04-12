"""
LLM client shim.

支持四种 transport：
1. OpenAI Responses API（配置了 OPENAI_API_KEY 时优先）
2. Local `codex exec` CLI fallback
3. Claude Code CLI（使用 `claude -p`，推荐用于批量简历生成）
4. Kimi Code API（Anthropic 协议兼容）
"""
import glob as _glob
import json
import hashlib
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

CODEX_BIN = shutil.which("codex") or ""


def _find_claude_code_bin() -> str:
    """定位 Claude Code CLI 二进制。优先 PATH，再搜索 macOS 标准安装路径。"""
    in_path = shutil.which("claude")
    if in_path:
        return in_path
    # macOS: ~/Library/Application Support/Claude/claude-code/<version>/claude.app/...
    pattern = os.path.expanduser(
        "~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude"
    )
    matches = sorted(_glob.glob(pattern), reverse=True)  # 按版本号降序，取最新
    for m in matches:
        if os.path.isfile(m):
            return m
    return ""


CLAUDE_CODE_BIN = _find_claude_code_bin()
KIMI_API_KEY_ENV_VARS = ("KIMI_API_KEY", "API_KEY")
KIMI_BASE_URL_ENV_VARS = ("KIMI_BASE_URL", "BASE_URL", "ANTHROPIC_BASE_URL")
DEFAULT_KIMI_BASE_URL = "https://api.kimi.com/coding"
DEFAULT_KIMI_MAX_TOKENS = 8192

# Keep old aliases working so existing scripts do not need to change.
MODEL_ALIASES = {
    "opus": "gpt-5.4",
    "sonnet": "gpt-5.4-mini",
    "haiku": "gpt-5-mini",
}

# 当 transport=claude 时，将任意模型名映射到 Claude 模型 ID
CLAUDE_MODEL_ALIASES: dict[str, str] = {
    # OpenAI 模型名 → Claude 等效
    "gpt-5.4": "claude-sonnet-4-6",
    "gpt-5.4-mini": "claude-sonnet-4-6",
    "gpt-5-mini": "claude-haiku-4-5",
    # 旧 Anthropic 别名
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
    # 直传（已是 Claude 模型 ID）
    "claude-opus-4-6": "claude-opus-4-6",
    "claude-sonnet-4-6": "claude-sonnet-4-6",
    "claude-haiku-4-5": "claude-haiku-4-5",
    "claude-haiku-4-5-20251001": "claude-haiku-4-5-20251001",
}

DEFAULT_WRITE_MODEL = "gpt-5.4"
DEFAULT_REVIEW_MODEL = "gpt-5.4-mini"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_CODEX_EXEC_ROOT = "/tmp/resume-pipeline-codex"
DEFAULT_TRANSPORT = "auto"


class AnthropicClient:
    """
    Compatibility wrapper over Codex CLI.

    The class name is preserved because multiple modules already import
    `AnthropicClient` and helper functions from this file.
    """

    ENABLE_ENV_VAR = "RESUME_PIPELINE_ENABLE_LLM"
    TRANSPORT_ENV_VAR = "RESUME_PIPELINE_LLM_TRANSPORT"
    API_KEY_ENV_VAR = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"

    def __init__(
        self,
        write_model: str = DEFAULT_WRITE_MODEL,
        review_model: str = DEFAULT_REVIEW_MODEL,
        enabled: Optional[bool] = None,
        timeout: int = 900,
        max_retries: int = 2,
        retry_delay: float = 5.0,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        exec_root: str = DEFAULT_CODEX_EXEC_ROOT,
        transport: str = DEFAULT_TRANSPORT,
    ):
        self.write_model = _normalize_model_name(write_model)
        self.review_model = _normalize_model_name(review_model)
        self.enabled = self._resolve_enabled(enabled)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.reasoning_effort = reasoning_effort
        self.exec_root = exec_root
        self.transport = self._resolve_transport(transport)
        self._cache: dict[str, str] = {}
        self._api_client = None
        self._kimi_client = None

    @classmethod
    def _resolve_enabled(cls, enabled: Optional[bool]) -> bool:
        if enabled is not None:
            return enabled
        val = os.environ.get(cls.ENABLE_ENV_VAR, "").strip().lower()
        return val in {"1", "true", "yes", "on"}

    def configure(
        self,
        *,
        enabled: Optional[bool] = None,
        write_model: Optional[str] = None,
        review_model: Optional[str] = None,
        transport: Optional[str] = None,
    ) -> None:
        if enabled is not None:
            self.enabled = enabled
        if write_model:
            self.write_model = _normalize_model_name(write_model)
        if review_model:
            self.review_model = _normalize_model_name(review_model)
        if transport:
            self.transport = self._resolve_transport(transport)

    @classmethod
    def _resolve_transport(cls, transport: Optional[str]) -> str:
        raw = (transport or os.environ.get(cls.TRANSPORT_ENV_VAR, DEFAULT_TRANSPORT)).strip().lower()
        if raw not in {"auto", "api", "cli", "claude", "kimi"}:
            logger.warning("未知 transport=%s，回退到 auto", raw)
            return DEFAULT_TRANSPORT
        return raw

    def _api_key_present(self) -> bool:
        return bool(os.environ.get(self.API_KEY_ENV_VAR, "").strip())

    @staticmethod
    def _first_present_env(names: tuple[str, ...]) -> str:
        for name in names:
            value = os.environ.get(name, "").strip()
            if value:
                return value
        return ""

    def _kimi_api_key(self) -> str:
        return self._first_present_env(KIMI_API_KEY_ENV_VARS)

    def _kimi_base_url(self) -> str:
        return self._first_present_env(KIMI_BASE_URL_ENV_VARS) or DEFAULT_KIMI_BASE_URL

    def _selected_transport(self) -> str:
        if self.transport == "auto":
            if self._api_key_present():
                return "api"
            if CLAUDE_CODE_BIN and os.path.isfile(CLAUDE_CODE_BIN):
                return "claude"
            return "cli"
        return self.transport

    def is_available(self) -> bool:
        if not self.enabled:
            logger.info(
                "LLM 调用已禁用。设置 %s=1 或在入口传入 enable_llm=True 后启用。",
                self.ENABLE_ENV_VAR,
            )
            return False
        transport = self._selected_transport()
        if transport == "api":
            if not self._api_key_present():
                logger.warning("未配置 %s，无法使用 OpenAI API transport", self.API_KEY_ENV_VAR)
                return False
            try:
                self._get_api_client()
            except Exception as exc:
                logger.warning("初始化 OpenAI API client 失败: %s", exc)
                return False
            return True
        if transport == "claude":
            if not CLAUDE_CODE_BIN or not os.path.isfile(CLAUDE_CODE_BIN):
                logger.warning("未找到 Claude Code CLI: %s", CLAUDE_CODE_BIN or "<未发现>")
                return False
            return True
        if transport == "kimi":
            if not self._kimi_api_key():
                logger.warning("未配置 Kimi API key: %s", ", ".join(KIMI_API_KEY_ENV_VARS))
                return False
            try:
                self._get_kimi_client()
            except Exception as exc:
                logger.warning("初始化 Kimi client 失败: %s", exc)
                return False
            return True
        # cli (codex)
        if not CODEX_BIN or not os.path.isfile(CODEX_BIN):
            logger.warning("未找到 codex CLI: %s", CODEX_BIN or "<未发现>")
            return False
        return True

    def _get_api_client(self):
        if self._api_client is not None:
            return self._api_client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("未安装 openai Python SDK") from exc

        kwargs = {}
        api_key = os.environ.get(self.API_KEY_ENV_VAR, "").strip()
        if api_key:
            kwargs["api_key"] = api_key
        base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
        if base_url:
            kwargs["base_url"] = base_url
        organization = os.environ.get("OPENAI_ORG_ID", "").strip()
        if organization:
            kwargs["organization"] = organization
        project = os.environ.get("OPENAI_PROJECT_ID", "").strip()
        if project:
            kwargs["project"] = project

        self._api_client = OpenAI(timeout=self.timeout, **kwargs)
        return self._api_client

    def _get_kimi_client(self):
        if self._kimi_client is not None:
            return self._kimi_client
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("未安装 anthropic Python SDK") from exc

        api_key = self._kimi_api_key()
        if not api_key:
            raise RuntimeError("未配置 Kimi API key")

        self._kimi_client = Anthropic(
            api_key=api_key,
            base_url=self._kimi_base_url(),
            timeout=self.timeout,
        )
        return self._kimi_client

    def _run_cli(self, prompt: str, model: str) -> str:
        """底层 Codex CLI 调用。"""
        exec_root = Path(self.exec_root)
        exec_root.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            prefix="codex-last-message-",
            suffix=".txt",
            dir="/tmp",
            delete=False,
        ) as tmp:
            output_path = tmp.name

        cmd = [
            CODEX_BIN,
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "-C",
            str(exec_root),
            "-o",
            output_path,
            "-m",
            model,
            "-c",
            f'model_reasoning_effort="{self.reasoning_effort}"',
        ]

        env = os.environ.copy()

        try:
            try:
                result = subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(f"codex CLI timed out after {self.timeout}s") from exc

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()

            if result.returncode != 0:
                excerpt = _best_error_excerpt(stdout, stderr)
                raise RuntimeError(
                    f"codex CLI exit {result.returncode}: {excerpt}"
                )

            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    return text

            fallback = _extract_last_meaningful_stdout(stdout)
            if fallback:
                return fallback

            raise RuntimeError("codex CLI succeeded but produced no final message")
        finally:
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass

    def _run_claude_code_cli(self, prompt: str, model: str, system: str = "") -> str:
        """通过 Claude Code CLI (`claude -p`) 调用。纯文本输出，不加载工具。"""
        claude_model = CLAUDE_MODEL_ALIASES.get(model, model)
        full_prompt = f"{system.strip()}\n\n{prompt}" if system else prompt

        cmd = [
            CLAUDE_CODE_BIN,
            "-p",
            "--model",
            claude_model,
            "--output-format",
            "text",
            "--tools",
            "",  # 禁用所有工具，纯文本生成
        ]

        env = os.environ.copy()

        try:
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Claude Code CLI timed out after {self.timeout}s") from exc

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if result.returncode != 0:
            excerpt = _best_error_excerpt(stdout, stderr)
            raise RuntimeError(f"Claude Code CLI exit {result.returncode}: {excerpt}")

        if stdout:
            return stdout

        raise RuntimeError("Claude Code CLI succeeded but produced no output")

    def _run_api(self, prompt: str, model: str, system: str = "") -> str:
        client = self._get_api_client()
        kwargs: dict[str, Any] = {
            "model": model,
            "input": prompt,
        }
        if system:
            kwargs["instructions"] = system
        if self.reasoning_effort:
            kwargs["reasoning"] = {"effort": self.reasoning_effort}

        response = client.responses.create(**kwargs)
        text = getattr(response, "output_text", "") or ""
        if text:
            return text.strip()

        extracted = _extract_response_output_text(response)
        if extracted:
            return extracted
        raise RuntimeError("OpenAI Responses API succeeded but produced no text output")

    def _run_kimi_api(self, prompt: str, model: str, system: str = "") -> str:
        client = self._get_kimi_client()
        request: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": int(os.environ.get("KIMI_MAX_TOKENS", DEFAULT_KIMI_MAX_TOKENS)),
        }
        if system:
            request["system"] = system

        response = client.messages.create(**request)
        parts: list[str] = []
        for item in getattr(response, "content", None) or []:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
        if parts:
            return "\n".join(parts).strip()
        raise RuntimeError("Kimi API succeeded but produced no text output")

    def call(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        cache_key: str = "",
        system: str = "",
    ) -> str:
        """
        调用 Codex CLI。

        Args:
            prompt: 用户消息（system 会拼接到 prompt 前面）
            model:  覆盖默认模型（None = 使用 write_model）
            cache_key: 可选缓存键（相同 key 直接返回缓存结果）
            system: 可选系统提示（拼接到 prompt 首部传入 CLI）
        """
        if cache_key and cache_key in self._cache:
            logger.debug("命中LLM缓存: %s", cache_key[:40])
            return self._cache[cache_key]

        if not self.is_available():
            raise LLMUnavailableError("Codex CLI 不可用或未启用")

        use_model = _normalize_model_name(model or self.write_model)
        transport = self._selected_transport()

        last_error: Optional[Exception] = None
        transport_label = {
            "api": "OpenAI API",
            "claude": "Claude Code CLI",
            "cli": "Codex CLI",
            "kimi": "Kimi API",
        }.get(transport, transport)
        for attempt in range(1, self.max_retries + 2):
            try:
                if transport == "api":
                    text = self._run_api(prompt, use_model, system=system)
                elif transport == "claude":
                    text = self._run_claude_code_cli(prompt, use_model, system=system)
                elif transport == "kimi":
                    text = self._run_kimi_api(prompt, use_model, system=system)
                else:
                    full_prompt = f"{system.strip()}\n\n{prompt}" if system else prompt
                    text = self._run_cli(full_prompt, use_model)
                if cache_key:
                    self._cache[cache_key] = text
                return text
            except Exception as exc:
                last_error = exc
                if attempt > self.max_retries:
                    break
                wait = self.retry_delay * attempt
                logger.warning(
                    "%s 调用失败，第%d次重试前等待%.1fs: %s",
                    transport_label,
                    attempt, wait, exc,
                )
                time.sleep(wait)

        raise LLMUnavailableError(
            str(last_error) if last_error else "未知 LLM 调用失败"
        )

    def call_review(
        self, prompt: str, *, cache_key: str = "", system: str = ""
    ) -> str:
        """使用 review_model 调用，默认映射到 gpt-5.4-mini。"""
        return self.call(
            prompt, model=self.review_model, cache_key=cache_key, system=system
        )

    def call_json(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        cache_key: str = "",
        system: str = "",
        use_review_model: bool = False,
    ) -> Any:
        """调用 CLI 并解析 JSON 响应（自动处理 markdown code fence）。"""
        use_model = model or (
            self.review_model if use_review_model else self.write_model
        )
        raw = self.call(prompt, model=use_model, cache_key=cache_key, system=system)
        return _parse_json_response(raw)

    @staticmethod
    def make_cache_key(*parts: str) -> str:
        raw = ":".join(str(p) for p in parts)
        return hashlib.md5(raw.encode()).hexdigest()


def _normalize_model_name(model: str) -> str:
    normalized = (model or "").strip()
    if not normalized:
        return DEFAULT_WRITE_MODEL
    return MODEL_ALIASES.get(normalized, normalized)


def _best_error_excerpt(stdout: str, stderr: str) -> str:
    for text in (stderr, stdout):
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            return " | ".join(lines[-3:])[:800]
    return "无可用错误输出"


def _extract_last_meaningful_stdout(stdout: str) -> str:
    if not stdout:
        return ""

    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    for line in reversed(lines):
        if line.startswith("{") and '"type"' in line:
            continue
        if line.startswith("WARNING:") or line.startswith("ERROR:"):
            continue
        if line.startswith("tokens used"):
            continue
        if line == "codex":
            continue
        if line.startswith("OpenAI Codex"):
            continue
        return line
    return ""


def _extract_response_output_text(response: Any) -> str:
    output = getattr(response, "output", None)
    if not output:
        return ""

    chunks: list[str] = []
    for item in output:
        content = getattr(item, "content", None) or []
        for part in content:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def _parse_json_response(raw: str) -> Any:
    """从 LLM 响应中提取并解析 JSON（处理 markdown code fence）。"""
    cleaned = _strip_code_fences(raw.strip())
    candidates = [cleaned]

    balanced = _extract_balanced_json_candidate(cleaned)
    if balanced and balanced not in candidates:
        candidates.append(balanced)

    expanded: list[str] = []
    for candidate in candidates:
        expanded.append(candidate)
        stripped_commas = re.sub(r",(\s*[}\]])", r"\1", candidate)
        if stripped_commas != candidate:
            expanded.append(stripped_commas)

    last_error: Exception | None = None
    for candidate in expanded:
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except Exception as exc:
            last_error = exc
        try:
            import yaml

            parsed = yaml.safe_load(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except Exception as exc:
            last_error = exc

    raise last_error or ValueError("无法从响应中解析 JSON")


def _strip_code_fences(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.split("\n")
    json_lines = []
    in_block = False
    for line in lines:
        if line.strip().startswith("```") and not in_block:
            in_block = True
            continue
        if line.strip() == "```" and in_block:
            break
        if in_block:
            json_lines.append(line)
    return "\n".join(json_lines).strip()


def _extract_balanced_json_candidate(text: str) -> str:
    start_positions = [idx for idx, ch in enumerate(text) if ch in "{["]
    for start in start_positions:
        open_char = text[start]
        close_char = "}" if open_char == "{" else "]"
        depth = 0
        in_string = False
        escaped = False
        for idx in range(start, len(text)):
            ch = text[idx]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == "\"":
                    in_string = False
                continue
            if ch == "\"":
                in_string = True
                continue
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return text[start : idx + 1].strip()
    return ""


class LLMUnavailableError(Exception):
    """LLM 不可用或调用失败时抛出。"""


_default_client: Optional[AnthropicClient] = None


def get_llm_client() -> AnthropicClient:
    global _default_client
    if _default_client is None:
        _default_client = AnthropicClient()
    return _default_client


def configure_llm_client(
    *,
    enabled: Optional[bool] = None,
    write_model: Optional[str] = None,
    review_model: Optional[str] = None,
    transport: Optional[str] = None,
) -> AnthropicClient:
    """供入口统一配置全局 LLM client。"""
    client = get_llm_client()
    client.configure(
        enabled=enabled,
        write_model=write_model,
        review_model=review_model,
        transport=transport,
    )
    return client
