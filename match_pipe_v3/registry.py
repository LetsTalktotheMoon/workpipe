import json
import re
from pathlib import Path
from typing import Any

import jinja2
import yaml


class PromptRegistry:
    def __init__(self, parts_dir: str | Path, assemblies_dir: str | Path, overrides: dict[str, str] | None = None):
        self.parts_dir = Path(parts_dir)
        self.assemblies_dir = Path(assemblies_dir)
        self._parts: dict[str, str] = self._load_parts()
        self._assemblies: dict[str, dict[str, Any]] = self._load_assemblies()
        self._overrides: dict[str, str] = dict(overrides) if overrides else {}

    def _load_parts(self) -> dict[str, str]:
        parts = {}
        for path in sorted(self.parts_dir.glob("*.md")):
            parts[path.stem] = path.read_text(encoding="utf-8")
        return parts

    def _load_assemblies(self) -> dict[str, dict[str, Any]]:
        assemblies = {}
        for path in sorted(self.assemblies_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assemblies[data["name"]] = data
        return assemblies

    def get_part(self, part_id: str) -> str:
        if part_id in self._overrides:
            return self._overrides[part_id]
        if part_id not in self._parts:
            raise KeyError(f"Unknown part: {part_id}")
        return self._parts[part_id]

    def render_block(self, block_id: str) -> str:
        return self.get_part(block_id)

    def set_override(self, part_id: str, text: str) -> None:
        self._overrides[part_id] = text

    def remove_override(self, part_id: str) -> None:
        self._overrides.pop(part_id, None)

    def load_overrides(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            self._overrides.update(data)
        else:
            raise ValueError("Overrides file must be a JSON object mapping part_id -> text")

    def render_view(self, view_name: str, context: dict[str, Any] | None = None) -> str:
        context = context or {}
        assembly = self._assemblies.get(view_name)
        if assembly is None:
            raise KeyError(f"Unknown view: {view_name}")
        return self._render_sections(assembly.get("sections", []), assembly.get("join", "\n\n"), context)

    def _render_sections(self, sections: list[dict[str, Any]], join: str, context: dict[str, Any]) -> str:
        rendered: list[str] = []
        for section in sections:
            piece = self._render_section(section, context)
            if piece:
                rendered.append(piece)
        return join.join(rendered)

    def _render_section(self, section: dict[str, Any], context: dict[str, Any]) -> str | None:
        # Evaluate condition
        condition = section.get("condition")
        if condition is not None and not self._eval_condition(condition, context):
            return None

        # Group
        if "group" in section or "sections" in section:
            sub_join = section.get("join", "\n\n")
            return self._render_sections(section.get("sections", []), sub_join, context)

        # Part with optional template formatting
        if "part" in section:
            text = self.get_part(section["part"])
            if section.get("template"):
                text = self._format_template(text, section, context)
            if section.get("transform") == "reviewer_bytedance_branch":
                text = self._transform_reviewer_bytedance_branch(text, context)
            return text

        # Template part (read part then format)
        if "template_part" in section:
            text = self.get_part(section["template_part"])
            text = self._format_template(text, section, context)
            return text

        # Inline template (Jinja2)
        if "template" in section and isinstance(section["template"], str):
            return self._render_jinja_template(section["template"], context)

        return None

    def _eval_condition(self, condition: str, context: dict[str, Any]) -> bool:
        # Safe evaluation of simple boolean expressions
        allowed_names = {"true": True, "false": False, "True": True, "False": False}
        allowed_names.update(context)
        try:
            return bool(eval(condition, {"__builtins__": {}}, allowed_names))
        except Exception as e:
            raise ValueError(f"Failed to evaluate condition '{condition}': {e}")

    def _format_template(self, text: str, section: dict[str, Any], context: dict[str, Any]) -> str:
        vars_ref = section.get("vars_ref")
        if vars_ref:
            fmt_ctx = context.get(vars_ref, {})
        else:
            fmt_ctx = {}
            for k, v in section.get("vars", {}).items():
                fmt_ctx[k] = self._resolve_var(v, context)
        try:
            return text.format(**fmt_ctx)
        except KeyError as e:
            raise ValueError(f"Missing template key {e} for part/section {section}")

    def _render_jinja_template(self, text: str, context: dict[str, Any]) -> str:
        tmpl = jinja2.Template(text)
        return tmpl.render(**context)

    def _resolve_var(self, value: Any, context: dict[str, Any]) -> Any:
        if not isinstance(value, str):
            return value
        if "." in value and not value.startswith("("):
            parts = value.split(".")
            obj = context.get(parts[0])
            for attr in parts[1:]:
                if obj is None:
                    return None
                if hasattr(obj, attr):
                    obj = getattr(obj, attr)
                elif isinstance(obj, dict):
                    obj = obj.get(attr)
                else:
                    return None
            return obj
        # Simple string: treat as key into context, fallback to literal
        return context.get(value, value)

    def _transform_reviewer_bytedance_branch(self, text: str, context: dict[str, Any]) -> str:
        # Reproduce _apply_reviewer_bytedance_branch logic from legacy
        from runtime.job_webapp.prompt_library import (
            _apply_reviewer_bytedance_branch,
            get_match_pipe_block_text,
        )

        branch_text = get_match_pipe_block_text("reviewer_user_bytedance")
        return _apply_reviewer_bytedance_branch(text, branch_text)

    @classmethod
    def from_dir(cls, root_dir: str | Path, overrides: dict[str, str] | None = None) -> "PromptRegistry":
        root = Path(root_dir)
        return cls(root / "parts", root / "assemblies", overrides=overrides)
