function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const state = {
  cards: [],
  paragraphMap: new Map(),
  paragraphDrafts: new Map(),
  blockTemplates: {},
  meta: {},
  saving: false,
};

const promptMeta = document.getElementById("promptMeta");
const promptPathNote = document.getElementById("promptPathNote");
const promptPreviewList = document.getElementById("promptPreviewList");
const promptSaveStatus = document.getElementById("promptSaveStatus");

const ROLE_NAME = {
  writer: "写手",
  reviewer: "审查员",
  planner: "规划器",
};

const STAGE_NAME = {
  shared_writer: "共享写作",
  shared_reviewer: "统一审查",
  downstream_validation: "下游验证",
  planner_validation: "规划验证",
  planner_writer_overlay: "规划写作覆盖",
  planner_revision_overlay: "规划修订覆盖",
  revision: "修订",
  retarget_writer: "Retarget 写作",
  upgrade_revision: "升级改写",
};

const TITLE_NAME = {
  "Writer System Prompt": "写手系统提示词",
  "Strict Revision System Prompt": "严格修订系统提示词",
  "Upgrade Revision System Prompt": "升级改写系统提示词",
  "Writer User Prompt": "写手任务提示词",
  "Reviewer System Prompt": "审查系统提示词",
  "Reviewer User Prompt": "审查任务提示词",
  "Retarget Prompt": "Retarget 任务提示词",
  "Planner System Prompt": "规划系统提示词",
  "Planner User Prompt": "规划任务提示词",
  "Planner-first Writer Prompt": "规划优先生成提示词",
  "Planner-first Revision Prompt": "规划优先修订提示词",
  "Dual-channel Retarget Prompt": "双通道 Retarget 提示词",
  "Dual-channel Continuity Overlay": "双通道连续性补充说明",
  "Upgrade Revision Prompt": "升级改写任务提示词",
};

const BRANCH_LABEL = {
  shared_trunk: "",
  generic_branch: "通用分支",
  bytedance_branch: "ByteDance 分支",
  same_company_branch: "同公司分支",
  mixed: "",
};

const HIDDEN_CARD_TITLES = [
  "Writer Prompt: 目标 JD 信息",
  "Reviewer Prompt: JD 与待审查简历输入",
  "Retarget Prompt: 公司项目池约束",
  "Retarget Prompt: ByteDance 特殊块",
  "Dual-channel Continuity Overlay",
];

const SHELL_LABELS = new Set([
  "目标JD",
  "目标 JD",
  "目标 JD 信息",
  "目标 JD 关键信息",
  "待审查简历",
  "输出格式",
  "审查发现",
  "最优先修改事项",
  "必须技术",
  "审查维度与权重",
  "原始简历",
  "Seed 简历",
  "Historical Starter Resume",
  "Planner Decision",
  "Matcher Evidence",
  "Matcher Packet",
  "Starter Resume",
  "Planner 输入",
  "公司项目池约束",
  "原审查详细修改指令",
  "路由模式",
  "当前上下文",
  "目标模式",
]);

function setStatus(text) {
  promptSaveStatus.textContent = text;
}

function renderMeta(meta = state.meta) {
  if (promptPathNote) {
    promptPathNote.textContent = `写回文件 ${meta.override_path || "match_pipe/prompt_overrides.json"}`;
  }
  promptMeta.innerHTML = `
    <div>运行时 block ${escapeHtml(meta.block_count || 0)}</div>
    <div>完整 prompt ${escapeHtml(meta.prompt_count || 0)}</div>
    <div>可编辑卡片 ${escapeHtml(state.cards.length)}</div>
  `;
}

function translateRole(role) {
  return ROLE_NAME[role] || role;
}

function translateStage(stage) {
  return STAGE_NAME[stage] || stage || "未分段";
}

function normalizeText(text) {
  return String(text ?? "").trim().replace(/\s+/g, " ");
}

function normalizeFamilyTitle(title) {
  let raw = String(title || "").trim();
  raw = raw.replace(/\s*（[^）]*分支[^）]*）\s*/g, "").replace(/\s*\([^)]*branch[^)]*\)\s*/gi, "").trim();
  if (raw.startsWith("Retarget Prompt:")) return "Retarget Prompt";
  if (raw.startsWith("Upgrade Prompt:")) return "Upgrade Revision Prompt";
  if (raw.startsWith("Writer Prompt:")) return "Writer User Prompt";
  if (raw.startsWith("Writer User Prompt:")) return "Writer User Prompt";
  if (raw.startsWith("Reviewer Prompt:")) return "Reviewer User Prompt";
  if (raw.startsWith("Planner Prompt:")) return "Planner User Prompt";
  if (raw.startsWith("Planner-first Writer Prompt:")) return "Planner-first Writer Prompt";
  if (raw.startsWith("Planner-first Revision Prompt:")) return "Planner-first Revision Prompt";
  if (raw === "Planner Writer Overlay") return "Planner-first Writer Prompt";
  if (raw === "Planner Revision Overlay") return "Planner-first Revision Prompt";
  return raw.split(":")[0].trim() || raw;
}

function translateTitle(title) {
  return TITLE_NAME[normalizeFamilyTitle(title)] || title;
}

function cardPriority(card) {
  const stage = String(card.stage || "");
  const priorities = {
    shared_writer: 10,
    shared_reviewer: 20,
    downstream_validation: 30,
    revision: 40,
    planner_validation: 50,
    planner_writer_overlay: 60,
    planner_revision_overlay: 70,
    retarget_writer: 80,
    upgrade_revision: 90,
  };
  return priorities[stage] || 100;
}

function cleanLines(text) {
  return String(text || "")
    .split("\n")
    .map((line) => line.replace(/\s+$/g, ""));
}

function stripFormattingPrefix(text) {
  return String(text || "")
    .replace(/^[#>*\-\d.\s]+/, "")
    .replace(/[*`_]+/g, "")
    .replace(/[：:]+$/g, "")
    .trim();
}

function extractPlaceholders(text) {
  return [
    ...new Set(
      (String(text || "").match(/\{\{?[A-Za-z_][A-Za-z0-9_]*\}\}?/g) || []).map((item) => item.replace(/[{}]/g, "")),
    ),
  ];
}

function looksLikeJsonSchema(text) {
  const raw = String(text || "").trim();
  if (!raw) return false;
  if (/^```json/i.test(raw)) return true;
  if ((raw.startsWith("{") || raw.startsWith("[")) && raw.includes('"') && raw.includes(":")) return true;
  if ((raw.match(/[{}[\]]/g) || []).length >= 6 && (raw.match(/"/g) || []).length >= 6) return true;
  if (/(?:r0_authenticity|weighted_score|overall_verdict|critical_count|revision_instructions|already_covered|missing_or_weak|risk_flags)/.test(raw)) return true;
  if (/(?:<pass\|fail>|<0-10>|<true\|false>|<整数>|sum\(score_i \* weight_i\) \* 10)/.test(raw)) return true;
  return /JSON 格式结果|JSON schema|严格 JSON/.test(raw);
}

function looksLikeJsonLine(text) {
  const raw = String(text || "").trim();
  if (!raw) return false;
  if (/^[\[{]\s*$/.test(raw)) return true;
  if (/^[\]}],?\s*$/.test(raw)) return true;
  if (/^"[^"]+"\s*:/.test(raw)) return true;
  if (/^"[^"]+"\s*$/.test(raw)) return true;
  return false;
}

function isJsonInstructionText(text) {
  const raw = String(text || "").trim();
  return /请严格按以下 JSON 格式输出|只输出 JSON|不要其他内容|不要有任何额外文字|返回 JSON 格式结果|必须输出 JSON|schema 必须包含|revision_instructions|weighted_score|overall_verdict/.test(
    raw,
  );
}

function isShellLikeLabel(line) {
  const plain = stripFormattingPrefix(line).replace(/\s+/g, " ").trim();
  if (!plain) return false;
  if (SHELL_LABELS.has(plain)) return true;
  return [...SHELL_LABELS].some((label) => plain === label || plain.startsWith(`${label}（`) || plain.startsWith(`${label} (`) || plain.startsWith(`${label}:`) || plain.startsWith(`${label}：`));
}

function shouldHideCard(card) {
  return HIDDEN_CARD_TITLES.includes(card.title);
}

function classifyParagraph(card, paragraph) {
  const text = String(paragraph?.text || "").trim();
  if (!text) return { hidden: true, reason: "" };
  if (shouldHideCard(card)) return { hidden: true, reason: card.title };
  if (/^```/.test(text) || /^---+$/.test(text)) return { hidden: true, reason: "" };
  if (looksLikeJsonSchema(text) || looksLikeJsonLine(text) || isJsonInstructionText(text)) {
    return { hidden: true, reason: "JSON schema / 结构示例" };
  }
  if (extractPlaceholders(text).length > 0) return { hidden: true, reason: "运行时输入" };
  if (isShellLikeLabel(text)) return { hidden: true, reason: stripFormattingPrefix(text) };
  return { hidden: false, text };
}

function parseLines(text) {
  return String(text || "").split("\n").map((line) => {
    if (!line.trim()) return { kind: "blank", text: "" };
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) return { kind: "heading", level: heading[1].length, text: heading[2] };
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet) return { kind: "bullet", text: bullet[1] };
    const number = line.match(/^(\d+)\.\s+(.+)$/);
    if (number) return { kind: "number", index: number[1], text: number[2] };
    const quote = line.match(/^>\s?(.*)$/);
    if (quote) return { kind: "quote", text: quote[1] };
    return { kind: "paragraph", text: line };
  });
}

function inlineToHtml(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function htmlToInline(markup) {
  return String(markup || "")
    .replace(/<strong>(.*?)<\/strong>/gi, "**$1**")
    .replace(/<code>(.*?)<\/code>/gi, "`$1`")
    .replace(/<br\s*\/?>/gi, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function sectionBranchLabel(section) {
  if (!section.branchKinds.size) return "";
  if (section.branchKinds.size > 1) return "";
  const kind = [...section.branchKinds][0];
  return BRANCH_LABEL[kind] || "";
}

const MERGE_FORWARD_TEXTS = new Set([
  "工作流程（必须按此两阶段完成）：",
  "## 阶段一：PLAN（在此规划，不输出给最终用户）",
  "请在 <PLAN> 标签内完成：",
  "## 阶段二：RESUME",
  "## 格式硬约束（违反=直接FAIL）",
]);

const MERGE_FORWARD_COMBINED_TEXTS = new Set([
  "## 阶段一：PLAN（在此规划，不输出给最终用户）\n请在 <PLAN> 标签内完成：",
]);

function mergeSectionIntoNext(sections, index) {
  if (index < 0 || index >= sections.length - 1) return false;
  const current = sections[index];
  const next = sections[index + 1];
  next.text = `${current.text}\n${next.text}`.trim();
  next.paragraphIds = [...current.paragraphIds, ...next.paragraphIds];
  current.branchKinds.forEach((item) => next.branchKinds.add(item));
  sections.splice(index, 1);
  return true;
}

function mergeSectionIntoPrevious(sections, index) {
  if (index <= 0 || index >= sections.length) return false;
  const previous = sections[index - 1];
  const current = sections[index];
  previous.text = `${previous.text}\n${current.text}`.trim();
  previous.paragraphIds = [...previous.paragraphIds, ...current.paragraphIds];
  current.branchKinds.forEach((item) => previous.branchKinds.add(item));
  sections.splice(index, 1);
  return true;
}

function normalizeOrphanSections(card) {
  const sections = [...card.sections];
  let index = 0;
  while (index < sections.length) {
    const text = String(sections[index].text || "").trim();
    if (!text) {
      sections.splice(index, 1);
      continue;
    }
    if (MERGE_FORWARD_TEXTS.has(text) || MERGE_FORWARD_COMBINED_TEXTS.has(text)) {
      if (mergeSectionIntoNext(sections, index)) continue;
    }
    if (text === "* Bullet.") {
      if (mergeSectionIntoPrevious(sections, index)) {
        index -= 1;
        continue;
      }
    }
    index += 1;
  }
  return { ...card, sections };
}

function dedupeSectionsGlobally(cards) {
  const ownership = new Map();
  const ownerSection = new Map();
  return cards
    .slice()
    .sort((left, right) => {
      const priorityDelta = cardPriority(left) - cardPriority(right);
      if (priorityDelta !== 0) return priorityDelta;
      return left.title.localeCompare(right.title, "zh-CN");
    })
    .map((card) => {
      const nextSections = [];
      card.sections.forEach((section) => {
        const key = normalizeText(section.text);
        if (!key) return;
        if (!ownership.has(key)) {
          ownership.set(key, card.id);
          ownerSection.set(key, section);
          nextSections.push(section);
          return;
        }
        const ownerCardId = ownership.get(key);
        const targetSection = ownerSection.get(key);
        if (ownerCardId === card.id) {
          targetSection.paragraphIds.push(...section.paragraphIds);
          section.branchKinds.forEach((item) => targetSection.branchKinds.add(item));
          return;
        }
        if (targetSection) {
          targetSection.paragraphIds.push(...section.paragraphIds);
          section.branchKinds.forEach((item) => targetSection.branchKinds.add(item));
        }
      });
      return { ...card, sections: nextSections };
    });
}

function buildDisplayCards(editorMapping) {
  const paragraphMap = new Map((editorMapping.diff_blocks || editorMapping.paragraphs || []).map((item) => [item.id, item]));
  state.paragraphMap = paragraphMap;
  state.blockTemplates = editorMapping.block_templates || {};

  const groupedCards = new Map();
  (editorMapping.cards || []).forEach((card) => {
    const targets = card.targets || [];
    const firstTarget = targets[0] || {};
    const pipeline = firstTarget.pipeline || "match_pipe";
    const stage = firstTarget.stage || "unknown_stage";
    const role = firstTarget.role || "writer";
    const groupKey = `${pipeline}::${stage}::${role}`;
    if (!groupedCards.has(groupKey)) {
      groupedCards.set(groupKey, {
        id: `group:${groupKey}`,
        pipeline,
        stage,
        role,
        rawTitles: new Set(),
        descriptionParts: new Set(),
        hiddenNotes: new Set(),
        sections: [],
      });
    }
    const group = groupedCards.get(groupKey);
    group.rawTitles.add(translateTitle(card.title));
    if (card.description) group.descriptionParts.add(card.description);
    (card.paragraph_ids || []).forEach((paragraphId) => {
      const paragraph = paragraphMap.get(paragraphId);
      if (!paragraph) return;
      const classification = classifyParagraph(card, paragraph);
      if (classification.hidden) {
        if (classification.reason) group.hiddenNotes.add(classification.reason);
        return;
      }
      group.sections.push({
        id: `section:${paragraphId}`,
        text: classification.text,
        paragraphIds: [paragraphId],
        branchKinds: new Set(paragraph.branch_kind && paragraph.branch_kind !== "shared_trunk" ? [paragraph.branch_kind] : []),
      });
    });
  });

  const groupedDisplayCards = [...groupedCards.values()].map((group) => ({
    id: group.id,
    pipeline: group.pipeline,
    stage: group.stage,
    role: group.role,
    title: `${group.pipeline} / ${translateStage(group.stage)} / ${translateRole(group.role)}`,
    description: [...group.descriptionParts].join(" · "),
    hiddenNotes: [...group.hiddenNotes],
    rawTitles: [...group.rawTitles],
    sections: group.sections,
  }));
  return dedupeSectionsGlobally(groupedDisplayCards.map((card) => normalizeOrphanSections(card)))
    .filter((card) => card.sections.length > 0)
    .sort((left, right) => left.title.localeCompare(right.title, "zh-CN"));
}

function sectionText(section) {
  const draft = state.paragraphDrafts.get(section.paragraphIds[0]);
  return draft ?? section.text;
}

function hasCardChanges(card) {
  return card.sections.some((section) => state.paragraphDrafts.has(section.paragraphIds[0]));
}

function resetCardDraft(cardId) {
  const card = state.cards.find((item) => item.id === cardId);
  if (!card) return;
  card.sections.forEach((section) => {
    section.paragraphIds.forEach((paragraphId) => state.paragraphDrafts.delete(paragraphId));
  });
}

function applySectionDraft(section, text) {
  section.paragraphIds.forEach((paragraphId) => state.paragraphDrafts.set(paragraphId, text));
}

function renderEditableSection(cardId, section) {
  const lines = parseLines(sectionText(section));
  const variantLabel = sectionBranchLabel(section);
  return `
    <div class="prompt-section" data-card-id="${escapeHtml(cardId)}" data-section-id="${escapeHtml(section.id)}">
      ${variantLabel ? `<div class="prompt-variant-note">仅用于：${escapeHtml(variantLabel)}</div>` : ""}
      ${lines
        .map((line) => {
          if (line.kind === "blank") return `<div class="prompt-line prompt-line-blank" data-kind="blank"><br></div>`;
          if (line.kind === "heading") return `<div class="prompt-line prompt-line-heading" data-kind="heading" data-level="${line.level}" contenteditable="true">${inlineToHtml(line.text)}</div>`;
          if (line.kind === "bullet") return `<div class="prompt-line prompt-line-bullet" data-kind="bullet" contenteditable="true">${inlineToHtml(line.text)}</div>`;
          if (line.kind === "number") return `<div class="prompt-line prompt-line-number" data-kind="number" data-index="${escapeHtml(line.index)}" contenteditable="true">${inlineToHtml(line.text)}</div>`;
          if (line.kind === "quote") return `<div class="prompt-line prompt-line-quote" data-kind="quote" contenteditable="true">${inlineToHtml(line.text)}</div>`;
          return `<div class="prompt-line prompt-line-paragraph" data-kind="paragraph" contenteditable="true">${inlineToHtml(line.text)}</div>`;
        })
        .join("")}
    </div>
  `;
}

function serializeSection(sectionEl) {
  return [...sectionEl.querySelectorAll(".prompt-line")]
    .map((line) => {
      const kind = line.dataset.kind || "paragraph";
      if (kind === "blank") return "";
      const text = htmlToInline(line.innerHTML.trim());
      if (!text && kind !== "quote") return "";
      if (kind === "heading") return `${"#".repeat(Number(line.dataset.level || 2))} ${text}`;
      if (kind === "bullet") return `- ${text}`;
      if (kind === "number") return `${line.dataset.index || "1"}. ${text}`;
      if (kind === "quote") return `> ${text}`;
      return text;
    })
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function syncCardDraftFromDom(cardId) {
  const card = state.cards.find((item) => item.id === cardId);
  if (!card) return;
  const shell = promptPreviewList.querySelector(`.prompt-card-editor[data-card-id="${CSS.escape(cardId)}"]`);
  if (!shell) return;
  shell.querySelectorAll(".prompt-section").forEach((sectionEl) => {
    const section = card.sections.find((item) => item.id === sectionEl.dataset.sectionId);
    if (!section) return;
    applySectionDraft(section, serializeSection(sectionEl));
  });
}

function buildBlockTextMap() {
  const blockTextMap = {};
  Object.entries(state.blockTemplates).forEach(([blockId, segments]) => {
    const rendered = [];
    segments.forEach((segment) => {
      if (segment.kind === "paragraph") {
        const currentText = state.paragraphDrafts.get(segment.paragraph_id) ?? state.paragraphMap.get(segment.paragraph_id)?.text ?? segment.text ?? "";
        if (String(currentText).trim()) rendered.push(String(currentText).trim());
        return;
      }
      if (String(segment.text || "").trim()) rendered.push(String(segment.text).trim());
    });
    blockTextMap[blockId] = rendered.join("\n\n").trim();
  });
  return blockTextMap;
}

function buildParagraphTextMap(card) {
  const paragraphTextMap = {};
  card.sections.forEach((section) => {
    section.paragraphIds.forEach((paragraphId) => {
      if (!state.paragraphDrafts.has(paragraphId)) return;
      paragraphTextMap[paragraphId] = state.paragraphDrafts.get(paragraphId);
    });
  });
  return paragraphTextMap;
}

function renderSourceNote(card) {
  if (!card.description && !card.hiddenNotes.length && !(card.rawTitles || []).length) return "";
  const parts = [];
  if (card.description) parts.push(card.description);
  if ((card.rawTitles || []).length) parts.push(`来源块: ${card.rawTitles.join("、")}`);
  if (card.hiddenNotes.length) parts.push(`灰色结构说明: ${card.hiddenNotes.join("、")}`);
  return `<div class="prompt-source-note">${escapeHtml(parts.join(" · "))}</div>`;
}

function renderCard(card) {
  const normalizedCard = normalizeOrphanSections(card);
  const saveEnabled = hasCardChanges(card);
  return `
    <section class="prompt-flat-group" data-card-id="${escapeHtml(card.id)}">
      <div class="prompt-flat-head">
        <div>
          <div class="prompt-flat-group-title"><strong>${escapeHtml(card.title)}</strong></div>
          ${renderSourceNote(card)}
        </div>
        <div class="prompt-card-actions">
          <button class="ghost-button small reset-btn" type="button" data-card-id="${escapeHtml(card.id)}" ${saveEnabled ? "" : "disabled"}>还原</button>
          <button class="run-btn save-btn" type="button" data-card-id="${escapeHtml(card.id)}" ${saveEnabled ? "" : "disabled"}>保存</button>
        </div>
      </div>
      <div class="prompt-card-editor" data-card-id="${escapeHtml(card.id)}">
        ${normalizedCard.sections.map((section) => renderEditableSection(card.id, section)).join("")}
      </div>
    </section>
  `;
}

function renderCards() {
  state.cards = state.cards.map((card) => normalizeOrphanSections(card));
  promptPreviewList.innerHTML = state.cards.map((card) => renderCard(card)).join("");
  renderMeta();
}

function refreshCardButtons(cardId) {
  const card = state.cards.find((item) => item.id === cardId);
  const cardEl = promptPreviewList.querySelector(`.prompt-flat-group[data-card-id="${CSS.escape(cardId)}"]`);
  if (!card || !cardEl) return;
  const changed = hasCardChanges(card);
  const saveButton = cardEl.querySelector(".save-btn");
  const resetButton = cardEl.querySelector(".reset-btn");
  if (saveButton) saveButton.disabled = !changed || state.saving;
  if (resetButton) resetButton.disabled = !changed || state.saving;
}

function bindEvents() {
  promptPreviewList.addEventListener("input", (event) => {
    const sectionEl = event.target.closest(".prompt-section");
    if (!sectionEl) return;
    syncCardDraftFromDom(sectionEl.dataset.cardId);
    setStatus("当前有未保存改动。");
    refreshCardButtons(sectionEl.dataset.cardId);
  });

  promptPreviewList.addEventListener("click", async (event) => {
    const resetButton = event.target.closest(".reset-btn");
    if (resetButton) {
      resetCardDraft(resetButton.dataset.cardId);
      setStatus("已还原当前卡片。");
      renderCards();
      return;
    }

    const saveButton = event.target.closest(".save-btn");
    if (!saveButton) return;
    const card = state.cards.find((item) => item.id === saveButton.dataset.cardId);
    if (!card || state.saving || !hasCardChanges(card)) return;

    syncCardDraftFromDom(card.id);
    state.saving = true;
    setStatus("保存中...");
    refreshCardButtons(card.id);

    try {
      const response = await fetch("/api/prompt-library/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paragraphs: buildParagraphTextMap(card) }),
      });
      if (!response.ok) throw new Error(`保存失败: ${response.status}`);
      await response.json();
      setStatus("已保存并写回。");
      state.saving = false;
      loadPromptLibrary();
    } catch (error) {
      state.saving = false;
      setStatus(error instanceof Error ? error.message : "保存失败");
      refreshCardButtons(card.id);
    }
  });
}

async function loadPromptLibrary() {
  const response = await fetch("/api/prompt-library", { cache: "no-store" });
  if (!response.ok) throw new Error(`prompt library 加载失败: ${response.status}`);
  const payload = await response.json();
  state.meta = payload.meta || {};
  state.paragraphDrafts = new Map();
  state.cards = buildDisplayCards(payload.editor_mapping || {});
  setStatus("当前没有未保存改动");
  renderCards();
}

bindEvents();
loadPromptLibrary().catch((error) => {
  promptMeta.textContent = error.message;
  setStatus("加载失败");
});
