"""Generate an interactive HTML editor for viewing and editing shared sentences across full prompts."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))

from match_pipe_v2.registry import PromptRegistry


def _make_registry() -> PromptRegistry:
    return PromptRegistry.from_dir(ROOT)


class _MockContext(dict):
    """Return '{{ key }}' for any missing key so the editor shows template variables."""

    def __missing__(self, key):
        return f"{{{{ {key} }}}}"


_REGISTRY = _make_registry()
_SENTENCES = _REGISTRY._data.get("sentences", {})
_VIEWS = _REGISTRY.list_views()

# Pre-render raw texts for all views
_VIEW_TEXTS: dict[str, str] = {}
for vid in _VIEWS:
    try:
        _VIEW_TEXTS[vid] = _REGISTRY.render_view(vid, context=_MockContext())
    except Exception as e:
        _VIEW_TEXTS[vid] = f"[ERROR rendering {vid}: {e}]"

# Build view metadata from YAML files
_VIEW_META: dict[str, dict] = {}
for vf in sorted((ROOT / "views").glob("*.yaml")):
    import yaml

    data = yaml.safe_load(vf.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "view_id" in data:
        _VIEW_META[data["view_id"]] = data


def _escape_js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def main() -> None:
    output = ROOT / "PROMPT_EDITOR.html"

    view_texts_json = _escape_js_string(json.dumps(_VIEW_TEXTS, ensure_ascii=False))
    sentences_json = _escape_js_string(json.dumps(_SENTENCES, ensure_ascii=False))
    view_meta_json = _escape_js_string(json.dumps(_VIEW_META, ensure_ascii=False))

    view_options = "".join(
        f'<option value="{html.escape(vid)}">{html.escape(vid)}</option>' for vid in _VIEWS
    )

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Match Pipe V2 — Interactive Prompt Editor</title>
<style>
  :root {{
    --bg: #f7f8fa;
    --panel-bg: #ffffff;
    --border: #d0d7de;
    --shared-bg: #e6f4ff;
    --shared-border: #1890ff;
    --shared-hover: #bae0ff;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: var(--font);
    background: var(--bg);
    color: #1f2328;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  header {{
    background: var(--panel-bg);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }}
  header h1 {{
    font-size: 16px;
    margin: 0;
    font-weight: 600;
  }}
  header .desc {{
    font-size: 13px;
    color: #656d76;
  }}
  header button {{
    margin-left: auto;
    padding: 6px 14px;
    font-size: 13px;
    border: 1px solid var(--border);
    background: #fff;
    border-radius: 6px;
    cursor: pointer;
  }}
  header button:hover {{
    background: #f3f4f6;
  }}
  main {{
    flex: 1;
    display: flex;
    overflow: hidden;
  }}
  .pane {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    border-right: 1px solid var(--border);
  }}
  .pane:last-child {{ border-right: none; }}
  .pane-header {{
    padding: 10px 16px;
    background: var(--panel-bg);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .pane-header select {{
    flex: 1;
    padding: 6px 8px;
    font-size: 13px;
    border: 1px solid var(--border);
    border-radius: 6px;
  }}
  .pane-header label {{
    font-size: 12px;
    color: #656d76;
    font-weight: 500;
  }}
  .prompt-view {{
    flex: 1;
    overflow: auto;
    padding: 20px;
    white-space: pre-wrap;
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.6;
    background: var(--panel-bg);
  }}
  .shared-sentence {{
    background: var(--shared-bg);
    border-bottom: 2px dotted var(--shared-border);
    border-radius: 3px;
    padding: 0 2px;
    cursor: text;
    transition: background 0.15s;
  }}
  .shared-sentence:hover {{
    background: var(--shared-hover);
  }}
  .shared-sentence:focus {{
    outline: 2px solid var(--shared-border);
    background: #fff;
  }}
  .toast {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #1f2328;
    color: #fff;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 13px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }}
  .toast.show {{ opacity: 1; }}
</style>
</head>
<body>
<header>
  <h1>Match Pipe V2 — Interactive Prompt Editor</h1>
  <span class="desc">蓝色下划线 = 共享句子。修改一处，所有视图实时联动。</span>
  <button id="exportBtn">Export sentences.yaml</button>
</header>
<main>
  <div class="pane">
    <div class="pane-header">
      <label>View A</label>
      <select id="selectA">{view_options}</select>
    </div>
    <div class="prompt-view" id="paneA"></div>
  </div>
  <div class="pane">
    <div class="pane-header">
      <label>View B</label>
      <select id="selectB">{view_options}</select>
    </div>
    <div class="prompt-view" id="paneB"></div>
  </div>
</main>
<div class="toast" id="toast">已更新</div>

<script>
const viewTexts = JSON.parse({view_texts_json});
let sentences = JSON.parse({sentences_json});
const viewMeta = JSON.parse({view_meta_json});

function escapeHtml(text) {{
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}}

function escapeRegExp(string) {{
  return string.replace(/[.*+?^${{}}()|[\]\\]/g, '\\$&');
}}

function wrapSentences(text) {{
  const entries = Object.entries(sentences).sort((a, b) => b[1].length - a[1].length);
  if (entries.length === 0) return escapeHtml(text);

  let result = text;
  let placeholderIndex = 0;
  const placeholders = {{}};

  for (const [key, value] of entries) {{
    if (!value) continue;
    const regex = new RegExp(escapeRegExp(value), 'g');
    result = result.replace(regex, (match) => {{
      const ph = "___PH" + (placeholderIndex++) + "___";
      placeholders[ph] = {{ key, match }};
      return ph;
    }});
  }}

  result = escapeHtml(result);

  for (const [ph, {{ key, match }}] of Object.entries(placeholders)) {{
    const span = '<span class="shared-sentence" data-key="' + key + '" contenteditable="true" title="Shared: ' + key + '">' + escapeHtml(match) + '</span>';
    result = result.split(ph).join(span);
  }}

  return result;
}}

function renderPane(paneId, viewId) {{
  const container = document.getElementById(paneId);
  const text = viewTexts[viewId] || "[View not found]";
  container.innerHTML = wrapSentences(text);

  container.querySelectorAll('.shared-sentence').forEach(span => {{
    span.addEventListener('blur', (e) => {{
      const key = e.target.dataset.key;
      const newText = e.target.innerText;
      if (newText !== sentences[key]) {{
        sentences[key] = newText;
        showToast("共享句子已更新，重新渲染所有视图…");
        // Re-render both panes so the change reflects everywhere
        renderPane('paneA', document.getElementById('selectA').value);
        renderPane('paneB', document.getElementById('selectB').value);
      }}
    }});
  }});
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}}

function downloadYaml() {{
  const lines = ["# Shared sentences for match_pipe_v2\\n"];
  for (const [key, value] of Object.entries(sentences)) {{
    lines.push(key + ": |");
    for (const line of value.split("\\n")) {{
      lines.push("  " + line);
    }}
  }}
  const blob = new Blob([lines.join("\\n")], {{ type: "text/yaml" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "sentences.yaml";
  a.click();
  URL.revokeObjectURL(url);
  showToast("已下载 sentences.yaml");
}}

document.getElementById('selectA').addEventListener('change', (e) => renderPane('paneA', e.target.value));
document.getElementById('selectB').addEventListener('change', (e) => renderPane('paneB', e.target.value));
document.getElementById('exportBtn').addEventListener('click', downloadYaml);

// Initialize with sensible defaults
document.getElementById('selectA').value = "prompt_writer_generate";
document.getElementById('selectB').value = "prompt_retarget_old_match";
renderPane('paneA', "prompt_writer_generate");
renderPane('paneB', "prompt_retarget_old_match");
</script>
</body>
</html>
"""

    output.write_text(html_content, encoding="utf-8")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()
