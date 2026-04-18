from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jinja2
import yaml


class PromptRegistry:
    def __init__(
        self,
        blocks_dir: Path,
        views_dir: Path,
        data_dir: Path | None = None,
        overrides_path: Path | None = None,
    ):
        """加载所有 blocks、views、data 和可选的 overrides。"""
        self.blocks_dir = Path(blocks_dir)
        self.views_dir = Path(views_dir)
        self.data_dir = Path(data_dir) if data_dir else None
        self.overrides_path = Path(overrides_path) if overrides_path else None

        self._data = self._load_data()

        self._jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.blocks_dir)),
            autoescape=False,
        )
        self._jinja_env.globals["data"] = self._data
        self._jinja_env.filters["render_data"] = self._render_data_filter

        self._overrides: dict[str, str] = {}
        if self.overrides_path and self.overrides_path.exists():
            with self.overrides_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                blocks_overrides = data.get("blocks", {})
                if isinstance(blocks_overrides, dict):
                    self._overrides = blocks_overrides
                paragraphs = data.get("paragraphs")
                if paragraphs:
                    import warnings

                    warnings.warn(
                        "Paragraph-level overrides are present but not supported in Phase 1.",
                        UserWarning,
                        stacklevel=2,
                    )

        self._views: dict[str, dict[str, Any]] = {}
        for view_file in sorted(self.views_dir.glob("*.yaml")):
            with view_file.open("r", encoding="utf-8") as f:
                view_data = yaml.safe_load(f)
            if isinstance(view_data, dict) and "view_id" in view_data:
                self._views[view_data["view_id"]] = view_data

    def _load_data(self) -> dict[str, Any]:
        """加载 data_dir 下所有 .yaml 文件，合并为嵌套 dict。
        支持跨文件句子引用：字符串中若仅包含 `{{ data.sentences.xxx }}`，
        会在加载阶段自动解析为 sentences.yaml 中的实际值。
        若字符串中还包含其他 Jinja2 变量（如 {{ mode }}），则保留原样，
        由模板渲染时的 render_data filter 负责解析。
        """
        if not self.data_dir or not self.data_dir.exists():
            return {}

        raw: dict[str, Any] = {}
        for data_file in sorted(self.data_dir.glob("*.yaml")):
            if data_file.name.startswith("_"):
                continue
            with data_file.open("r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
            if isinstance(content, dict):
                raw[data_file.stem] = content

        sentences = raw.get("sentences", {})
        mini_env = jinja2.Environment(autoescape=False)
        mini_env.globals["data"] = {"sentences": sentences}

        def _resolve(obj: Any) -> Any:
            if isinstance(obj, str):
                refs = re.findall(r"\{\{\s*([^\}]+)\s*\}\}", obj)
                # Only auto-resolve if ALL Jinja2 refs are data.sentences.*
                if refs and all("data.sentences." in ref.strip() for ref in refs):
                    return mini_env.from_string(obj).render()
                return obj
            if isinstance(obj, list):
                return [_resolve(item) for item in obj]
            if isinstance(obj, dict):
                return {k: _resolve(v) for k, v in obj.items()}
            return obj

        return {domain: _resolve(content) for domain, content in raw.items()}

    @jinja2.pass_context
    def _render_data_filter(
        self, ctx: jinja2.runtime.Context, value: str | None, **extra: Any
    ) -> str:
        """如果 value 包含 Jinja2 语法，用当前 context 渲染；否则原样返回。"""
        if not isinstance(value, str):
            return str(value) if value is not None else ""
        if "{{" not in value and "{%" not in value:
            return value
        template = self._jinja_env.from_string(value)
        render_ctx = dict(ctx)
        render_ctx.update(extra)
        return template.render(**render_ctx).strip()

    @classmethod
    def from_dir(cls, prompts_dir: str | Path) -> PromptRegistry:
        """从 prompts 根目录初始化。
        预期结构：
          {prompts_dir}/blocks/
          {prompts_dir}/views/
          {prompts_dir}/data/      (可选，新增)
          {prompts_dir}/../overrides.json (相对于 prompts_dir 的父目录)
        """
        prompts_dir = Path(prompts_dir)
        blocks_dir = prompts_dir / "blocks"
        views_dir = prompts_dir / "views"
        data_dir = prompts_dir / "data"
        if not data_dir.exists():
            data_dir = None
        overrides_path = prompts_dir.parent / "overrides.json"
        if not overrides_path.exists():
            overrides_path = None
        return cls(
            blocks_dir=blocks_dir,
            views_dir=views_dir,
            data_dir=data_dir,
            overrides_path=overrides_path,
        )

    def render_block(self, block_id: str, context: dict[str, Any] | None = None) -> str:
        """渲染单个 block。如果该 block 在 overrides 中有覆盖，使用覆盖后的文本。"""
        context = context or {}
        if block_id in self._overrides:
            return str(self._overrides[block_id]).strip()

        template_path = self.blocks_dir / f"{block_id}.jinja2"
        if not template_path.exists():
            raise FileNotFoundError(f"Block template not found: {template_path}")

        template = self._jinja_env.get_template(f"{block_id}.jinja2")
        rendered = template.render(**context)
        return rendered.strip()

    def render_view(self, view_id: str, context: dict[str, Any] | None = None) -> str:
        """按 view 定义的顺序渲染所有 user_blocks，用 \n\n 拼接。
        不渲染 system_block（system 由调用方单独用 render_block 获取）。

        user_blocks 中的元素可以是字符串（block_id）或 dict：
          - block_id: str
          - context: dict (可选，会合并到 view-level context 上)
        """
        context = context or {}
        view = self._views.get(view_id)
        if view is None:
            raise ValueError(f"View not found: {view_id}")

        user_blocks = view.get("user_blocks", [])
        if not isinstance(user_blocks, list):
            raise ValueError(f"Invalid user_blocks for view {view_id}: expected list")

        rendered_blocks: list[str] = []
        for item in user_blocks:
            if isinstance(item, str):
                block_id = item
                block_ctx = context
            elif isinstance(item, dict):
                block_id = item.get("block_id")
                if not block_id:
                    raise ValueError(f"Invalid user_blocks item in view {view_id}: missing block_id")
                block_ctx = {**context, **item.get("context", {})}
            else:
                raise ValueError(f"Invalid user_blocks item in view {view_id}: expected str or dict")
            rendered = self.render_block(block_id, context=block_ctx)
            rendered_blocks.append(rendered)

        return "\n\n".join(rendered_blocks).strip()

    def list_blocks(self) -> list[str]:
        """返回所有可用的 block_id 列表。"""
        block_ids: list[str] = []
        for f in sorted(self.blocks_dir.glob("*.jinja2")):
            block_ids.append(f.stem)
        # Include any override-only blocks
        for block_id in sorted(self._overrides):
            if block_id not in block_ids:
                block_ids.append(block_id)
        return block_ids

    def list_views(self) -> list[str]:
        """返回所有可用的 view_id 列表。"""
        return sorted(self._views.keys())

    def validate(self) -> list[str]:
        """校验并返回错误信息列表：
        - 检查每个 view 引用的 block_id 是否都存在
        - 检查 blocks_dir 和 views_dir 中的文件是否能正常加载
        """
        errors: list[str] = []
        available_blocks = set(self.list_blocks())

        # Validate blocks can be loaded (at least templates exist or are overridden)
        for block_id in available_blocks:
            try:
                self.render_block(block_id)
            except Exception as e:
                errors.append(f"Failed to render block '{block_id}': {e}")

        # Validate views
        for view_file in sorted(self.views_dir.glob("*.yaml")):
            try:
                with view_file.open("r", encoding="utf-8") as f:
                    view_data = yaml.safe_load(f)
            except Exception as e:
                errors.append(f"Failed to load view file '{view_file.name}': {e}")
                continue

            if not isinstance(view_data, dict):
                errors.append(f"Invalid view file '{view_file.name}': expected dict")
                continue

            view_id = view_data.get("view_id")
            if not view_id:
                errors.append(f"Missing view_id in view file '{view_file.name}'")
                continue

            # Check referenced blocks exist
            for key in ("system_block", "user_blocks"):
                if key not in view_data:
                    continue
                if key == "system_block":
                    block_ids = [view_data["system_block"]]
                else:
                    user_blocks = view_data["user_blocks"]
                    if not isinstance(user_blocks, list):
                        errors.append(
                            f"View '{view_id}' has invalid '{key}': expected list"
                        )
                        continue
                    block_ids = []
                    for item in user_blocks:
                        if isinstance(item, str):
                            block_ids.append(item)
                        elif isinstance(item, dict):
                            bid = item.get("block_id")
                            if bid:
                                block_ids.append(bid)
                            else:
                                errors.append(
                                    f"View '{view_id}' has invalid user_blocks item: missing block_id"
                                )
                        else:
                            errors.append(
                                f"View '{view_id}' has invalid user_blocks item: expected str or dict"
                            )

                for block_id in block_ids:
                    if block_id not in available_blocks:
                        errors.append(
                            f"View '{view_id}' references missing block '{block_id}'"
                        )

        return errors
