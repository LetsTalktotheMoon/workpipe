function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function readJsonScript(id) {
  const node = document.getElementById(id);
  if (!node) return {};
  try {
    return JSON.parse(node.textContent || "{}");
  } catch (error) {
    console.error(`failed to parse json script ${id}`, error);
    return {};
  }
}

const CONFIG = readJsonScript("prompt-review-config");

const state = {
  groups: [],
  groupMap: new Map(),
  mapByGroupId: new Map(),
  revisions: [],
  coverage: null,
  conflicts: null,
  ambiguities: null,
  roundtrip: null,
  meta: {},
  apiAvailable: false,
  frozen: false,
  headRevisionId: null,
  search: "",
  filters: {
    chain: "",
    stage: "",
    role: "",
  },
  showAllChains: false,
  drafts: new Map(),
  saveTimers: new Map(),
  savingGroups: new Set(),
  failedGroups: new Map(),
  activeTargetId: null,
  fingerprintIndex: new Map(),
  blockFingerprintMap: new Map(),
  viewMode: "dedup",
  expandedChains: new Set(["match_pipe"]),
  groupsVersion: 0,
  visibleRenderContext: null,
};

const elements = {
  heroMeta: document.getElementById("heroMeta"),
  connectionBadge: document.getElementById("connectionBadge"),
  autosaveBadge: document.getElementById("autosaveBadge"),
  freezeBadge: document.getElementById("freezeBadge"),
  statusNote: document.getElementById("statusNote"),
  refreshButton: document.getElementById("refreshButton"),
  saveAllButton: document.getElementById("saveAllButton"),
  writebackButton: document.getElementById("writebackButton"),
  searchInput: document.getElementById("searchInput"),
  chainFilter: document.getElementById("chainFilter"),
  stageFilter: document.getElementById("stageFilter"),
  roleFilter: document.getElementById("roleFilter"),
  toolbarSummary: document.getElementById("toolbarSummary"),
  cardList: document.getElementById("cardList"),
  conflictBody: document.getElementById("conflictBody"),
  coverageBody: document.getElementById("coverageBody"),
  ambiguityBody: document.getElementById("ambiguityBody"),
  revisionsList: document.getElementById("revisionsList"),
  reloadRevisionsButton: document.getElementById("reloadRevisionsButton"),
  viewModeTiles: document.getElementById("viewModeTiles"),
  viewModeDedup: document.getElementById("viewModeDedup"),
  showAllChainsButton: document.getElementById("showAllChainsButton"),
  checkConsistencyButton: document.getElementById("checkConsistencyButton"),
  tocRail: document.getElementById("tocRail"),
  tocBody: document.getElementById("tocBody"),
  sideRail: document.getElementById("sideRail"),
  sideRailToggle: document.getElementById("sideRailToggle"),
};

const ALLOWED_TAGS = new Set([
  "SECTION",
  "ARTICLE",
  "DIV",
  "P",
  "BR",
  "STRONG",
  "B",
  "EM",
  "I",
  "CODE",
  "PRE",
  "SPAN",
  "UL",
  "OL",
  "LI",
  "BLOCKQUOTE",
  "H1",
  "H2",
  "H3",
  "H4",
  "H5",
  "H6",
  "HR",
]);

function setStatus(message) {
  elements.statusNote.textContent = message;
}

function updateConnectionBadge(online) {
  state.apiAvailable = online;
  elements.connectionBadge.textContent = online ? "后端在线" : "仅本地草稿";
  elements.connectionBadge.className = `status-badge ${online ? "online" : "offline"}`;
}

function updateAutosaveBadge() {
  const dirtyCount = [...state.drafts.values()].filter((item) => item.dirty).length;
  const savingCount = state.savingGroups.size;
  const failedCount = state.failedGroups.size;
  if (savingCount) {
    elements.autosaveBadge.textContent = `自动保存中 ${savingCount}`;
    return;
  }
  if (failedCount) {
    elements.autosaveBadge.textContent = `保存失败 ${failedCount}`;
    return;
  }
  if (dirtyCount) {
    elements.autosaveBadge.textContent = `待保存草稿 ${dirtyCount}`;
    return;
  }
  elements.autosaveBadge.textContent = "自动保存待命";
}

function updateFreezeBadge() {
  const frozen = Boolean(state.frozen);
  elements.freezeBadge.hidden = !frozen;
  elements.freezeBadge.className = `status-badge frozen`;
  elements.freezeBadge.textContent = frozen ? "FROZEN" : "";
}

function syncGlobalButtons() {
  elements.saveAllButton.disabled = !state.apiAvailable;
  elements.reloadRevisionsButton.disabled = false;
}

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function safeObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((left, right) => String(left).localeCompare(String(right), "zh-CN"));
}

function formatTime(value) {
  if (!value) return "未知时间";
  try {
    return new Date(value).toLocaleString("zh-CN", { hour12: false });
  } catch (_error) {
    return String(value);
  }
}

function formatRatio(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "0.00";
  return value.toFixed(2);
}

function textToHtml(text) {
  const source = String(text ?? "").replace(/\r\n/g, "\n");
  const lines = source.split("\n");
  const chunks = [];
  let listBuffer = null;

  function flushList() {
    if (!listBuffer || !listBuffer.items.length) return;
    const tag = listBuffer.kind === "ol" ? "ol" : "ul";
    chunks.push(
      `<${tag}>${listBuffer.items
        .map((item) => `<li>${item}</li>`)
        .join("")}</${tag}>`,
    );
    listBuffer = null;
  }

  lines.forEach((line) => {
    const raw = String(line || "");
    const trimmed = raw.trim();
    if (!trimmed) {
      flushList();
      chunks.push("<p><br></p>");
      return;
    }
    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      flushList();
      chunks.push(`<h${heading[1].length}>${escapeHtml(heading[2])}</h${heading[1].length}>`);
      return;
    }
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      if (!listBuffer || listBuffer.kind !== "ul") {
        flushList();
        listBuffer = { kind: "ul", items: [] };
      }
      listBuffer.items.push(escapeHtml(bullet[1]));
      return;
    }
    const numbered = trimmed.match(/^\d+\.\s+(.+)$/);
    if (numbered) {
      if (!listBuffer || listBuffer.kind !== "ol") {
        flushList();
        listBuffer = { kind: "ol", items: [] };
      }
      listBuffer.items.push(escapeHtml(numbered[1]));
      return;
    }
    const quoted = trimmed.match(/^>\s?(.*)$/);
    if (quoted) {
      flushList();
      chunks.push(`<blockquote><p>${escapeHtml(quoted[1] || "")}</p></blockquote>`);
      return;
    }
    flushList();
    chunks.push(`<p>${escapeHtml(trimmed)}</p>`);
  });
  flushList();
  return chunks.join("");
}

function sanitizeRichHtml(html) {
  const template = document.createElement("template");
  template.innerHTML = String(html ?? "");

  function sanitizeNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      return document.createTextNode(node.textContent || "");
    }
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return null;
    }
    const tag = node.tagName.toUpperCase();
    if (tag === "SCRIPT" || tag === "STYLE" || tag === "IFRAME" || tag === "OBJECT") {
      return null;
    }
    if (!ALLOWED_TAGS.has(tag)) {
      const fragment = document.createDocumentFragment();
      [...node.childNodes].forEach((child) => {
        const sanitized = sanitizeNode(child);
        if (sanitized) fragment.appendChild(sanitized);
      });
      return fragment;
    }
    const element = document.createElement(node.tagName.toLowerCase());
    [...node.attributes].forEach((attribute) => {
      if (attribute.name === "class" || attribute.name.startsWith("data-")) {
        element.setAttribute(attribute.name, attribute.value);
      }
    });
    [...node.childNodes].forEach((child) => {
      const sanitized = sanitizeNode(child);
      if (sanitized) element.appendChild(sanitized);
    });
    return element;
  }

  const container = document.createElement("div");
  [...template.content.childNodes].forEach((child) => {
    const sanitized = sanitizeNode(child);
    if (sanitized) container.appendChild(sanitized);
  });
  return container.innerHTML.trim();
}

function htmlToPlainText(html) {
  const temp = document.createElement("div");
  temp.innerHTML = String(html ?? "");
  return temp.innerText.replace(/\u00a0/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

function jsonForScript(value) {
  return JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/<\/script/gi, "<\\/script");
}

function normalizeSourceRef(ref) {
  if (!ref || typeof ref !== "object") return null;
  return {
    path: ref.path || ref.file || "",
    line_start: ref.line_start ?? ref.line ?? null,
    line_end: ref.line_end ?? null,
    key: ref.key || ref.object_path || ref.key_path || "",
    function: ref.function || ref.callsite || "",
    source_type: ref.source_type || ref.type || "",
    primary: Boolean(ref.primary || ref.is_primary),
    mirror: Boolean(ref.mirror || ref.is_mirror),
    inherited: Boolean(ref.inherited || ref.is_inherited),
  };
}

function normalizeBlock(block, index) {
  if (typeof block === "string") {
    return {
      block_id: block,
      text: "",
      normalized_text: "",
      source_refs: [],
      source_priority: null,
      primary_source: null,
      placeholder_refs: [],
      merge_rule: "",
      write_policy: "",
      propagation_rule: "",
      confidence: null,
      duplicate_fingerprint: "",
      notes: "",
      display_order: index,
    };
  }
  const sourceRefs = safeArray(block.source_refs).map(normalizeSourceRef).filter(Boolean);
  return {
    block_id: block.block_id || block.id || `block-${index + 1}`,
    title: block.title || block.label || block.block_id || block.id || `block-${index + 1}`,
    text: block.text || "",
    normalized_text: block.normalized_text || "",
    source_refs: sourceRefs,
    source_priority: block.source_priority ?? null,
    primary_source: normalizeSourceRef(block.primary_source) || sourceRefs.find((item) => item.primary) || null,
    placeholder_refs: safeArray(block.placeholder_refs),
    merge_rule: block.merge_rule || "",
    write_policy: block.write_policy || "",
    propagation_rule: block.propagation_rule || "",
    confidence: block.confidence ?? null,
    duplicate_fingerprint: block.duplicate_fingerprint || "",
    notes: block.notes || "",
    html: sanitizeRichHtml(block.rich_text || block.html || textToHtml(block.text || "")),
    display_order: block.display_order ?? index,
  };
}

function buildBlocksFromMap(group, mapEntry) {
  const mapBlocks = safeArray(mapEntry?.blocks);
  if (mapBlocks.length) return mapBlocks.map(normalizeBlock);
  return safeArray(group.blocks).map(normalizeBlock);
}

function normalizePromptReviewRichText(richText, blocks) {
  const template = document.createElement("template");
  template.innerHTML = sanitizeRichHtml(richText || "");
  const normalizedSections = [];
  const directPromptBlocks = template.content.querySelectorAll(".prompt-block");
  if (directPromptBlocks.length) {
    directPromptBlocks.forEach((blockEl, index) => {
      const blockId = blockEl.dataset.blockId || blocks[index]?.block_id || `block-${index + 1}`;
      const matchedBlock = blocks.find((item) => item.block_id === blockId) || blocks[index];
      const bodySource =
        blockEl.querySelector(".prompt-block-body") ||
        blockEl.querySelector("pre") ||
        blockEl.querySelector("blockquote, ul, ol, p, h1, h2, h3, h4, h5, h6, div");
      const bodyHtml = sanitizeRichHtml(bodySource?.innerHTML || blockEl.innerHTML || "<p><br></p>");
      normalizedSections.push(`
        <section class="prompt-block" data-block-id="${escapeHtml(blockId)}" data-write-policy="${escapeHtml(matchedBlock?.write_policy || blockEl.dataset.writePolicy || "")}" data-merge-rule="${escapeHtml(matchedBlock?.merge_rule || blockEl.dataset.mergeRule || "")}">
          <div class="prompt-block-meta" contenteditable="false">${matchedBlock ? renderBlockMeta(matchedBlock) : `<span>${escapeHtml(blockId)}</span>`}</div>
          <div class="prompt-block-body">${bodyHtml || "<p><br></p>"}</div>
        </section>
      `);
    });
    return normalizedSections.join("");
  }

  const promptReviewBlocks = template.content.querySelectorAll(".prompt-review-block");
  if (promptReviewBlocks.length) {
    promptReviewBlocks.forEach((blockEl, index) => {
      const blockId = blockEl.dataset.blockId || blocks[index]?.block_id || `block-${index + 1}`;
      const matchedBlock = blocks.find((item) => item.block_id === blockId) || blocks[index];
      const sourceRefsAttr = blockEl.dataset.sourceRefs;
      if (sourceRefsAttr && matchedBlock && !matchedBlock.source_refs.length) {
        try {
          matchedBlock.source_refs = safeArray(JSON.parse(sourceRefsAttr)).map(normalizeSourceRef).filter(Boolean);
        } catch (_error) {
          // ignore malformed embedded source refs
        }
      }
      const titleNode = blockEl.querySelector("h1, h2, h3, h4, h5, h6");
      const preNode = blockEl.querySelector("pre");
      const bodyHtml = preNode ? textToHtml(preNode.textContent || "") : sanitizeRichHtml(blockEl.innerHTML || "<p><br></p>");
      if (matchedBlock && !matchedBlock.title && titleNode) matchedBlock.title = titleNode.textContent || matchedBlock.block_id;
      normalizedSections.push(`
        <section class="prompt-block" data-block-id="${escapeHtml(blockId)}" data-write-policy="${escapeHtml(matchedBlock?.write_policy || "")}" data-merge-rule="${escapeHtml(matchedBlock?.merge_rule || "")}">
          <div class="prompt-block-meta" contenteditable="false">${matchedBlock ? renderBlockMeta(matchedBlock) : `<span>${escapeHtml(blockId)}</span>`}</div>
          <div class="prompt-block-body">${bodyHtml || "<p><br></p>"}</div>
        </section>
      `);
    });
    return normalizedSections.join("");
  }

  const article = template.content.querySelector("article");
  if (article) {
    const preNode = article.querySelector("pre");
    const bodyHtml = preNode ? textToHtml(preNode.textContent || "") : sanitizeRichHtml(article.innerHTML || "<p><br></p>");
    return `
      <section class="prompt-block" data-block-id="${escapeHtml(blocks[0]?.block_id || "group-shell")}">
        <div class="prompt-block-meta" contenteditable="false">${blocks[0] ? renderBlockMeta(blocks[0]) : "<span>group-shell</span>"}</div>
        <div class="prompt-block-body">${bodyHtml || "<p><br></p>"}</div>
      </section>
    `;
  }

  return "";
}

function buildEditorHtml(group, blocks) {
  const richText = String(group.editable_rich_text || "").trim();
  if (richText) {
    const normalized = normalizePromptReviewRichText(richText, blocks);
    if (normalized) return normalized;
    return sanitizeRichHtml(richText);
  }
  if (blocks.length) {
    return blocks
      .slice()
      .sort((left, right) => (left.display_order ?? 0) - (right.display_order ?? 0))
      .map((block) => {
        const primary = block.primary_source?.path ? `${block.primary_source.path}${block.primary_source.line_start ? `:${block.primary_source.line_start}` : ""}` : "";
        return `
          <section class="prompt-block" data-block-id="${escapeHtml(block.block_id)}" data-write-policy="${escapeHtml(block.write_policy || "")}" data-merge-rule="${escapeHtml(block.merge_rule || "")}">
            <div class="prompt-block-meta" contenteditable="false">
              <span>${escapeHtml(block.block_id)}</span>
              ${block.write_policy ? `<span>${escapeHtml(block.write_policy)}</span>` : ""}
              ${primary ? `<span>${escapeHtml(primary)}</span>` : ""}
            </div>
            <div class="prompt-block-body">${block.html || "<p><br></p>"}</div>
          </section>
        `;
      })
      .join("");
  }
  return `
    <section class="prompt-block" data-block-id="group-shell" data-write-policy="ambiguous">
      <div class="prompt-block-meta" contenteditable="false"><span>group-shell</span></div>
      <div class="prompt-block-body">${textToHtml(group.display_text || "") || "<p><br></p>"}</div>
    </section>
  `;
}

function splitGroupIdTokens(groupId) {
  return String(groupId || "")
    .split("::")
    .map((token) => String(token || "").trim())
    .filter(Boolean);
}

const SAME_COMPANY_MERGE_TARGETS = new Set([
  "match_pipe::old_match_anchor::writer",
  "match_pipe::new_dual_channel::writer",
]);

function buildCanonicalPairTokens(groupId) {
  const tokens = splitGroupIdTokens(groupId);
  const baseTokens = tokens.filter((t) => t !== "bytedance" && t !== "same_company");
  const baseKey = baseTokens.join("::");
  if (SAME_COMPANY_MERGE_TARGETS.has(baseKey)) {
    return baseTokens;
  }
  let removedByteDance = false;
  return tokens.filter((token) => {
    if (!removedByteDance && token === "bytedance") {
      removedByteDance = true;
      return false;
    }
    return true;
  });
}

function formatPairLabelToken(token, index, options = {}) {
  const value = String(token || "");
  if (!value) return "";
  if (options.prettifyChain && index === 0) {
    return value.replaceAll("_", " ");
  }
  return value;
}

function buildPairLabelFromTokens(tokens, options = {}) {
  return safeArray(tokens)
    .map((token, index) => formatPairLabelToken(token, index, options))
    .filter(Boolean)
    .join(" / ");
}

function buildCanonicalPairMeta(groupId, fallbackLabel = "") {
  const pairTokens = buildCanonicalPairTokens(groupId);
  const pairKey = pairTokens.join("::") || String(groupId || "");
  const isByteDance = splitGroupIdTokens(groupId).includes("bytedance");
  const pairLabel = buildPairLabelFromTokens(pairTokens, { prettifyChain: true }) || fallbackLabel;
  const pairScopeLabel = buildPairLabelFromTokens(pairTokens.slice(1)) || pairLabel;
  return {
    pairTokens,
    pairKey,
    pairLabel,
    pairScopeLabel,
    isByteDance,
  };
}

function normalizeGroup(group, mapEntry, index) {
  const productionChain = group.production_chain || group.pipeline || "unknown_pipeline";
  const stage = group.stage || "unknown_stage";
  const role = group.role || "unknown_role";
  const groupId = group.group_id || group.id || `${productionChain}::${stage}::${role}::${index + 1}`;
  const groupLabel = group.group_label || group.label || `${productionChain} / ${stage} / ${role}`;
  const pairMeta = buildCanonicalPairMeta(groupId, groupLabel);
  const isSameCompany = splitGroupIdTokens(groupId).includes("same_company");
  const blocks = buildBlocksFromMap(group, mapEntry);
  const editorHtml = buildEditorHtml(group, blocks);
  const displayText = group.display_text || htmlToPlainText(editorHtml);
  const sourceRefs = uniqueSorted(
    blocks.flatMap((block) => safeArray(block.source_refs).map((ref) => ref.path)).filter(Boolean),
  );
  const prefix = `${productionChain} / `;
  const shortLabel = groupLabel.startsWith(prefix) ? groupLabel.slice(prefix.length) : groupLabel;
  return {
    group_id: groupId,
    group_label: groupLabel,
    short_label: shortLabel || groupLabel,
    pair_key: pairMeta.pairKey,
    pair_tokens: pairMeta.pairTokens,
    pair_label: pairMeta.pairLabel,
    pair_scope_label: pairMeta.pairScopeLabel,
    is_bytedance: pairMeta.isByteDance,
    is_same_company: isSameCompany,
    variant_label: pairMeta.isByteDance
      ? (isSameCompany ? "ByteDance + same_company" : "ByteDance")
      : (isSameCompany ? "same_company" : "generic"),
    production_chain: productionChain,
    stage,
    role,
    display_order: group.display_order ?? index,
    display_text: displayText,
    editable_rich_text: editorHtml,
    prompt_kind: group.prompt_kind || "full_prompt",
    blocks,
    target_refs: safeArray(group.target_refs),
    status: group.status || "clean",
    notes: group.notes || "",
    source_paths: sourceRefs,
    search_blob: [
      groupLabel,
      pairMeta.pairLabel,
      productionChain,
      stage,
      role,
      pairMeta.isByteDance ? "bytedance" : "generic",
      displayText,
      sourceRefs.join(" "),
      blocks.map((block) => [block.block_id, block.text, block.notes].join(" ")).join(" "),
    ]
      .join("\n")
      .toLowerCase(),
  };
}

function normalizeRevisionPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.revisions)) return payload.revisions;
  if (payload.index && Array.isArray(payload.index.revisions)) return payload.index.revisions;
  return [];
}

function unwrapReviewPayload(payload) {
  if (!payload || typeof payload !== "object") return {};
  if (Array.isArray(payload.groups)) return payload;
  if (payload.review && Array.isArray(payload.review.groups)) return payload.review;
  if (payload.edited && Array.isArray(payload.edited.groups)) return payload.edited;
  if (payload.data && Array.isArray(payload.data.groups)) return payload.data;
  if (payload.payload && Array.isArray(payload.payload.groups)) return payload.payload;
  return payload;
}

function unwrapMapPayload(payload) {
  if (!payload || typeof payload !== "object") return {};
  if (Array.isArray(payload.groups)) return payload;
  if (payload.map && Array.isArray(payload.map.groups)) return payload.map;
  if (payload.review_map && Array.isArray(payload.review_map.groups)) return payload.review_map;
  return payload;
}

function unwrapCoveragePayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  if (payload.coverage && typeof payload.coverage === "object") return payload.coverage;
  return payload;
}

function unwrapConflictPayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  if (payload.conflict && typeof payload.conflict === "object") return payload.conflict;
  return payload;
}

function unwrapAmbiguityPayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  if (payload.ambiguities && typeof payload.ambiguities === "object") return payload.ambiguities;
  return payload;
}

class JsonResponseError extends Error {
  constructor(message, payload, status) {
    super(message);
    this.name = "JsonResponseError";
    this.payload = payload;
    this.status = status;
  }
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  let payload = null;
  try {
    payload = await response.json();
  } catch (_error) {
    payload = null;
  }
  if (!response.ok) {
    const errorMessage =
      payload?.error || payload?.message || payload?.detail || `${url} -> ${response.status}`;
    throw new JsonResponseError(String(errorMessage), payload, response.status);
  }
  return payload;
}

async function tryFetchJson(url, options = {}) {
  try {
    return await fetchJson(url, options);
  } catch (_error) {
    return null;
  }
}

function buildFingerprintIndex(groups) {
  const fingerprintIndex = new Map();
  const blockFingerprintMap = new Map();
  for (const group of groups) {
    for (const block of safeArray(group.blocks)) {
      const fp = block.duplicate_fingerprint || "";
      if (!fp) continue;
      const key = `${group.group_id}::${block.block_id}`;
      blockFingerprintMap.set(key, fp);
      const entry = {
        group_id: group.group_id,
        block_id: block.block_id,
        primary_source: block.primary_source,
      };
      if (!fingerprintIndex.has(fp)) {
        fingerprintIndex.set(fp, []);
      }
      fingerprintIndex.get(fp).push(entry);
    }
  }
  return { fingerprintIndex, blockFingerprintMap };
}

function getSharedCount(block) {
  const fp = block?.duplicate_fingerprint || "";
  if (!fp) return 0;
  return state.fingerprintIndex.get(fp)?.length || 0;
}

function removeTooltip() {
  const existing = document.getElementById("shared-tooltip");
  if (existing) existing.remove();
}

function showTooltip(anchor, fp) {
  removeTooltip();
  const refs = state.fingerprintIndex.get(fp) || [];
  if (refs.length <= 1) return;
  const listItems = refs
    .map((ref) => {
      const group = state.groupMap.get(ref.group_id);
      const label = group ? escapeHtml(group.group_label) : escapeHtml(ref.group_id);
      return `<li><button type="button" data-jump-group="${escapeHtml(ref.group_id)}">${label}</button></li>`;
    })
    .join("");
  const tooltip = document.createElement("div");
  tooltip.id = "shared-tooltip";
  tooltip.className = "shared-tooltip";
  tooltip.innerHTML = `<div><strong>Shared by ${refs.length} roles</strong></div><ul>${listItems}</ul>`;
  document.body.appendChild(tooltip);
  const rect = anchor.getBoundingClientRect();
  const ttRect = tooltip.getBoundingClientRect();
  let top = rect.bottom + 8;
  let left = rect.left;
  if (left + ttRect.width > window.innerWidth - 16) {
    left = window.innerWidth - ttRect.width - 16;
  }
  tooltip.style.top = `${top + window.scrollY}px`;
  tooltip.style.left = `${left + window.scrollX}px`;
}

function replaceBlockHtmlInGroupHtml(groupId, blockId, newHtml) {
  const group = state.groupMap.get(groupId);
  if (!group) return null;
  const draft = getDraft(groupId);
  const baseHtml = draft?.html || group.editable_rich_text || "";
  const template = document.createElement("template");
  template.innerHTML = sanitizeRichHtml(baseHtml);
  let blockEl = template.content.querySelector(`[data-block-id="${CSS.escape(blockId)}"]`);
  if (blockEl) {
    const bodyEl = blockEl.querySelector(".prompt-block-body");
    if (bodyEl) bodyEl.innerHTML = newHtml;
  } else {
    blockEl = document.createElement("section");
    blockEl.className = "prompt-block";
    blockEl.dataset.blockId = blockId;
    const meta = document.createElement("div");
    meta.className = "prompt-block-meta";
    meta.innerHTML = `<span>${escapeHtml(blockId)}</span>`;
    const body = document.createElement("div");
    body.className = "prompt-block-body";
    body.innerHTML = newHtml;
    blockEl.append(meta, body);
    template.content.appendChild(blockEl);
  }
  const updatedHtml = sanitizeRichHtml(template.innerHTML);
  const displayText = htmlToPlainText(updatedHtml);
  return { html: updatedHtml, displayText };
}

function getMegaCardGroupIds(megaCard) {
  return parseJsonDataAttribute(megaCard?.dataset?.megaGroups, []);
}

function parseJsonDataAttribute(value, fallback) {
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function normalizeOwnerRefs(value) {
  return uniqueInOrder(
    safeArray(value)
      .map((ref) => {
        if (!ref || typeof ref !== "object") return null;
        const groupId = String(ref.groupId || ref.group_id || "").trim();
        const blockId = String(ref.blockId || ref.block_id || "").trim();
        if (!groupId || !blockId) return null;
        return `${groupId}\u0001${blockId}`;
      })
      .filter(Boolean)
  ).map((item) => {
    const [groupId, blockId] = item.split("\u0001");
    return { groupId, blockId };
  });
}

function getEntryOwnerRefs(entry) {
  const ownerBlockIds = uniqueInOrder(entry?.ownerBlockIds?.length ? entry.ownerBlockIds : [entry?.blockId]).filter(Boolean);
  return ownerBlockIds.map((blockId) => ({
    groupId: entry.groupId,
    blockId,
  }));
}

function elementOwnsBlock(element, groupId, blockId) {
  if (!element || !groupId) return false;
  const ownerRefs = normalizeOwnerRefs(parseJsonDataAttribute(element.dataset.ownerRefs, []));
  if (ownerRefs.length) {
    return ownerRefs.some((ref) => ref.groupId === groupId && (!blockId || ref.blockId === blockId));
  }
  const ownerGroupIds = parseJsonDataAttribute(element.dataset.ownerGroupIds, []);
  if (ownerGroupIds.length && !ownerGroupIds.includes(groupId)) return false;
  if (!blockId) return true;
  const ownerBlockIds = parseJsonDataAttribute(element.dataset.ownerBlockIds, []);
  if (ownerBlockIds.length) return ownerBlockIds.includes(blockId);
  return true;
}

const MEGA_CARD_BLOCK_TAGS = new Set([
  "ADDRESS",
  "ARTICLE",
  "ASIDE",
  "BLOCKQUOTE",
  "DIV",
  "DL",
  "FIELDSET",
  "FIGCAPTION",
  "FIGURE",
  "FOOTER",
  "FORM",
  "H1",
  "H2",
  "H3",
  "H4",
  "H5",
  "H6",
  "HEADER",
  "HR",
  "LI",
  "MAIN",
  "NAV",
  "OL",
  "P",
  "PRE",
  "SECTION",
  "TABLE",
  "TD",
  "TH",
  "TR",
  "UL",
]);

function megaCardNodeToPlainText(node) {
  if (!node) return "";
  if (node.nodeType === Node.TEXT_NODE) {
    return (node.textContent || "").replace(/\u00a0/g, " ");
  }
  if (node.nodeType !== Node.ELEMENT_NODE) return "";
  const tag = node.tagName.toUpperCase();
  if (tag === "BR") return "\n";
  if (MEGA_CARD_BLOCK_TAGS.has(tag)) {
    return megaCardElementToPlainText(node);
  }
  return [...node.childNodes].map((child) => megaCardNodeToPlainText(child)).join("");
}

function megaCardElementToPlainText(element) {
  const meaningfulChildren = [...element.childNodes].filter((child) => {
    if (child.nodeType === Node.TEXT_NODE) return Boolean(child.textContent);
    return true;
  });
  const isEmptyBlockPlaceholder =
    meaningfulChildren.length > 0 &&
    meaningfulChildren.every((child) =>
      (child.nodeType === Node.ELEMENT_NODE && child.tagName.toUpperCase() === "BR") ||
      (child.nodeType === Node.TEXT_NODE && !child.textContent)
    );
  if (isEmptyBlockPlaceholder) return "";
  const parts = [];
  let hasBlockChild = false;
  for (const child of [...element.childNodes]) {
    const isBlockChild = child.nodeType === Node.ELEMENT_NODE && MEGA_CARD_BLOCK_TAGS.has(child.tagName.toUpperCase());
    const chunk = megaCardNodeToPlainText(child);
    if (isBlockChild) {
      if (parts.length) parts.push("\n");
      hasBlockChild = true;
      parts.push(chunk);
      continue;
    }
    parts.push(chunk);
  }
  if (!hasBlockChild && element.tagName?.toUpperCase() === "PRE") {
    return (element.textContent || "").replace(/\u00a0/g, " ");
  }
  return parts.join("");
}

function megaCardBodyToPlainText(bodyEl) {
  if (!bodyEl) return "";
  const parts = [];
  for (const child of [...bodyEl.childNodes]) {
    const isBlockChild = child.nodeType === Node.ELEMENT_NODE && MEGA_CARD_BLOCK_TAGS.has(child.tagName.toUpperCase());
    const chunk = megaCardNodeToPlainText(child);
    if (isBlockChild && parts.length) parts.push("\n");
    parts.push(chunk);
  }
  return parts.join("");
}

function rebuildBlockTextFromDom(megaBlock, groupId, targetBlockId = "") {
  const containers = [...megaBlock.children].filter(
    (el) => el.classList.contains("segment-common") || el.classList.contains("segment-diff")
  );
  let text = "";
  for (const container of containers) {
    if (container.classList.contains("segment-common")) {
      if (!elementOwnsBlock(container, groupId, targetBlockId)) continue;
      const body = container.querySelector(".prompt-block-body");
      text += megaCardBodyToPlainText(body);
    } else {
      const cols = [...container.querySelectorAll(".diff-col")].filter((col) => {
        if (col.dataset.groupId && col.dataset.groupId !== groupId) return false;
        return elementOwnsBlock(col, groupId, targetBlockId);
      });
      cols.forEach((col) => {
        const body = col.querySelector(".prompt-block-body");
        text += megaCardBodyToPlainText(body);
      });
    }
  }
  return text;
}

function handleMegaCardInput(bodyEl) {
  const megaCard = bodyEl.closest(".mega-card");
  if (!megaCard) return false;
  const blockId = bodyEl.dataset.megaBlockId;
  if (!blockId) return false;
  const megaBlock = megaCard.querySelector(`.mega-block[data-mega-block-id="${CSS.escape(blockId)}"]`);
  if (!megaBlock) return false;
  const presentGroupIds = parseJsonDataAttribute(megaBlock.dataset.megaPresentGroups, []);
  const ownerBlockMap = parseJsonDataAttribute(megaBlock.dataset.megaOwnerBlockMap, {});
  for (const gid of presentGroupIds) {
    const group = state.groupMap.get(gid);
    if (!group) continue;
    const targetBlockIds = uniqueInOrder(
      safeArray(Array.isArray(ownerBlockMap[gid]) ? ownerBlockMap[gid] : [ownerBlockMap[gid] || blockId]).filter(Boolean)
    );
    if (!targetBlockIds.length) continue;
    for (const targetBlockId of targetBlockIds) {
      const newText = rebuildBlockTextFromDom(megaBlock, gid, targetBlockId);
      const newBlockHtml = plainTextToSimpleHtml(newText);
      const result = replaceBlockHtmlInGroupHtml(gid, targetBlockId, newBlockHtml);
      if (!result) continue;
      const snapshot = buildDraftSnapshotFromHtml(group, result.html);
      setDraft(gid, {
        html: snapshot.html,
        displayText: snapshot.displayText,
        blocks: snapshot.blocks,
        blockOrder: snapshot.blockOrder,
        updatedAt: new Date().toISOString(),
        dirty: true,
        baseRevisionId: state.headRevisionId,
      });
      applyDraftSnapshotToGroup(group, snapshot);
      state.failedGroups.delete(gid);
      syncDraftToSharedBlocks(gid, targetBlockId);
    }
    refreshCardChrome(gid);
    queueAutosave(gid);
  }
  updateAutosaveBadge();
  collectHeroStats();
  return true;
}

function syncDraftToSharedBlocks(sourceGroupId, blockId) {
  const sourceGroup = state.groupMap.get(sourceGroupId);
  if (!sourceGroup) return;
  const sourceBlock = sourceGroup.blocks.find((b) => b.block_id === blockId);
  if (!sourceBlock) return;
  const fp = sourceBlock.duplicate_fingerprint || "";
  if (!fp) return;
  const refs = state.fingerprintIndex.get(fp) || [];
  if (refs.length <= 1) return;

  const sourceDraft = getDraft(sourceGroupId);
  const sourceHtml = sourceDraft?.html || sourceGroup.editable_rich_text || "";
  const template = document.createElement("template");
  template.innerHTML = sanitizeRichHtml(sourceHtml);
  const sourceBlockEl = template.content.querySelector(`[data-block-id="${CSS.escape(blockId)}"]`);
  const newBlockHtml = sourceBlockEl?.querySelector(".prompt-block-body")?.innerHTML;
  if (newBlockHtml === undefined) return;

  let syncedCount = 0;
  for (const ref of refs) {
    if (ref.group_id === sourceGroupId) continue;
    const result = replaceBlockHtmlInGroupHtml(ref.group_id, ref.block_id, newBlockHtml);
    if (!result) continue;
    const targetGroup = state.groupMap.get(ref.group_id);
    if (!targetGroup) continue;
    const snapshot = buildDraftSnapshotFromHtml(targetGroup, result.html);
    setDraft(ref.group_id, {
      html: snapshot.html,
      displayText: snapshot.displayText,
      blocks: snapshot.blocks,
      blockOrder: snapshot.blockOrder,
      updatedAt: new Date().toISOString(),
      dirty: true,
      baseRevisionId: state.headRevisionId,
    });
    applyDraftSnapshotToGroup(targetGroup, snapshot);
    syncedCount++;
    const cardEl = document.querySelector(`[data-group-id="${CSS.escape(ref.group_id)}"]`);
    if (cardEl) {
      cardEl.classList.remove("sync-highlight");
      void cardEl.offsetWidth;
      cardEl.classList.add("sync-highlight");
      setTimeout(() => cardEl.classList.remove("sync-highlight"), 1200);
    }
    const editorEl = cardEl?.querySelector(`[data-editor-group="${CSS.escape(ref.group_id)}"]`);
    if (editorEl) {
      const targetBlockEl = editorEl.querySelector(`[data-block-id="${CSS.escape(ref.block_id)}"] .prompt-block-body`);
      if (targetBlockEl) targetBlockEl.innerHTML = newBlockHtml;
    }
    refreshCardChrome(ref.group_id);
  }
  if (syncedCount > 0) {
    updateAutosaveBadge();
    collectHeroStats();
  }
}

function mergeMapEntries(reviewDoc, mapDoc) {
  const mapGroups = new Map();
  safeArray(unwrapMapPayload(mapDoc)?.groups).forEach((entry) => {
    if (!entry) return;
    const key = entry.group_id || entry.id;
    if (key) mapGroups.set(key, entry);
  });
  return safeArray(unwrapReviewPayload(reviewDoc)?.groups).map((group, index) => normalizeGroup(group, mapGroups.get(group.group_id || group.id), index));
}

function collectHeroStats() {
  const groupCount = state.groups.length;
  const blockCount = state.groups.reduce((sum, group) => sum + group.blocks.length, 0);
  const dirtyCount = [...state.drafts.values()].filter((item) => item.dirty).length;
  const html = [
    `<span class="meta-pill">group ${escapeHtml(groupCount)}</span>`,
    `<span class="meta-pill">block ${escapeHtml(blockCount)}</span>`,
    `<span class="meta-pill">head revision ${escapeHtml(state.headRevisionId || "unknown")}</span>`,
    `<span class="meta-pill ${dirtyCount ? "status-edited" : ""}">本地草稿 ${escapeHtml(dirtyCount)}</span>`,
  ];
  elements.heroMeta.innerHTML = html.join("");
}

function populateFilter(selectEl, values, selectedValue) {
  selectEl.innerHTML = ['<option value="">全部</option>']
    .concat(values.map((value) => `<option value="${escapeHtml(value)}" ${value === selectedValue ? "selected" : ""}>${escapeHtml(value)}</option>`))
    .join("");
}

function renderFilters() {
  populateFilter(elements.chainFilter, uniqueSorted(state.groups.map((item) => item.production_chain)), state.filters.chain);
  populateFilter(elements.stageFilter, uniqueSorted(state.groups.map((item) => item.stage)), state.filters.stage);
  populateFilter(elements.roleFilter, uniqueSorted(state.groups.map((item) => item.role)), state.filters.role);
}

function groupMatchesFilters(group) {
  const effectiveChain = state.showAllChains ? state.filters.chain : "match_pipe";
  if (effectiveChain && group.production_chain !== effectiveChain) return false;
  if (state.filters.stage && group.stage !== state.filters.stage) return false;
  if (state.filters.role && group.role !== state.filters.role) return false;
  if (state.search && !group.search_blob.includes(state.search.toLowerCase())) return false;
  return true;
}

function getVisibleRenderContext() {
  const key = [
    state.viewMode,
    state.showAllChains ? "1" : "0",
    state.filters.chain || "",
    state.filters.stage || "",
    state.filters.role || "",
    state.search || "",
    state.groupsVersion || 0,
  ].join("\u0001");
  if (state.visibleRenderContext?.key === key) {
    return state.visibleRenderContext;
  }

  const visibleGroups = state.groups.filter(groupMatchesFilters);
  const context = {
    key,
    visibleGroups,
  };

  if (state.viewMode === "dedup") {
    context.megaCards = buildMegaCards(visibleGroups);
  } else {
    context.pairs = buildPairs(visibleGroups);
  }

  state.visibleRenderContext = context;
  return context;
}

function getDraft(groupId) {
  return state.drafts.get(groupId) || null;
}

function getCurrentEditorHtml(group) {
  const draft = getDraft(group.group_id);
  return draft?.html || group.editable_rich_text;
}

function getCurrentCardStatus(group) {
  if (state.savingGroups.has(group.group_id)) return "saving";
  if (state.failedGroups.has(group.group_id)) return "error";
  const draft = getDraft(group.group_id);
  if (draft?.dirty) return "dirty";
  if (group.status === "frozen" || state.frozen) return "frozen";
  return "clean";
}

function cardStatusLabel(status) {
  if (status === "saving") return "保存中";
  if (status === "error") return "保存失败";
  if (status === "dirty") return "待保存";
  if (status === "frozen") return "冻结";
  return "已同步";
}

function summarizeSources(group) {
  if (!group.source_paths.length) return "未提供 source_refs";
  if (group.source_paths.length === 1) return group.source_paths[0];
  return `${group.source_paths[0]} 等 ${group.source_paths.length} 项来源`;
}

function renderBlockMeta(block) {
  const sourceCount = safeArray(block.source_refs).length;
  const confidence = typeof block.confidence === "number" ? `confidence ${block.confidence}` : "";
  const primary = block.primary_source?.path ? `${block.primary_source.path}${block.primary_source.line_start ? `:${block.primary_source.line_start}` : ""}` : "";
  const sharedCount = getSharedCount(block);
  const sharedBadge = sharedCount > 1
    ? ` <button type="button" class="shared-badge" data-shared-fp="${escapeHtml(block.duplicate_fingerprint)}">shared by ${sharedCount} roles</button>`
    : "";
  return [
    `<span>${escapeHtml(block.block_id)}</span>`,
    block.write_policy ? `<span>${escapeHtml(block.write_policy)}</span>` : "",
    sourceCount ? `<span>source ${escapeHtml(sourceCount)}</span>` : "",
    confidence ? `<span>${escapeHtml(confidence)}</span>` : "",
    primary ? `<span>${escapeHtml(primary)}</span>` : "",
    sharedBadge,
  ].join("");
}

function buildCardEditorHtml(group) {
  const template = document.createElement("template");
  template.innerHTML = sanitizeRichHtml(getCurrentEditorHtml(group) || "");
  if (!template.content.querySelector(".prompt-block")) {
    const fallback = document.createElement("section");
    fallback.className = "prompt-block";
    fallback.dataset.blockId = "group-shell";

    const meta = document.createElement("div");
    meta.className = "prompt-block-meta";
    meta.setAttribute("contenteditable", "false");
    meta.innerHTML = "<span>group-shell</span>";

    const body = document.createElement("div");
    body.className = "prompt-block-body";
    body.innerHTML = template.innerHTML || "<p><br></p>";
    fallback.append(meta, body);
    template.innerHTML = "";
    template.content.appendChild(fallback);
  }

  [...template.content.querySelectorAll(".prompt-block")].forEach((blockEl, index) => {
    if (!blockEl.dataset.blockId) {
      blockEl.dataset.blockId = group.blocks[index]?.block_id || `group-shell-${index + 1}`;
    }
    const matchedBlock = group.blocks.find((item) => item.block_id === blockEl.dataset.blockId);
    let metaEl = blockEl.querySelector(".prompt-block-meta");
    let bodyEl = blockEl.querySelector(".prompt-block-body");
    if (!bodyEl) {
      bodyEl = document.createElement("div");
      bodyEl.className = "prompt-block-body";
      [...blockEl.childNodes].forEach((node) => {
        if (node !== metaEl) bodyEl.appendChild(node.cloneNode(true));
      });
      [...blockEl.childNodes].forEach((node) => {
        if (node !== metaEl) node.remove();
      });
      blockEl.appendChild(bodyEl);
    }
    if (!metaEl) {
      metaEl = document.createElement("div");
      metaEl.className = "prompt-block-meta";
      blockEl.prepend(metaEl);
    }
    metaEl.setAttribute("contenteditable", "false");
    metaEl.innerHTML = matchedBlock ? renderBlockMeta(matchedBlock) : `<span>${escapeHtml(blockEl.dataset.blockId)}</span>`;
    bodyEl.classList.add("prompt-block-body");
    bodyEl.setAttribute("contenteditable", "true");
    bodyEl.setAttribute("spellcheck", "false");
  });

  return template.innerHTML;
}

function renderCard(group, options = {}) {
  const status = getCurrentCardStatus(group);
  const draft = getDraft(group.group_id);
  const error = state.failedGroups.get(group.group_id);
  const frozenForGroup =
    state.frozen && safeArray(state.conflicts?.affected_groups).includes(group.group_id);
  const title = options.title || group.group_label;
  const subtitle = options.subtitle || `${group.prompt_kind} · ${group.production_chain} / ${group.stage} / ${group.role}`;
  const metaPills = safeArray(options.metaPills).length
    ? options.metaPills
    : [group.production_chain, group.stage, group.role, `blocks ${group.blocks.length}`];
  const metaPillHtml = metaPills
    .map((pill) => `<span class="meta-pill">${escapeHtml(pill)}</span>`)
    .join("");
  return `
    <article
      class="prompt-card"
      id="card-${escapeHtml(group.group_id)}"
      data-group-id="${escapeHtml(group.group_id)}"
      data-production-chain="${escapeHtml(group.production_chain)}"
      data-stage="${escapeHtml(group.stage)}"
      data-role="${escapeHtml(group.role)}"
      data-status="${escapeHtml(status)}"
      data-frozen="${frozenForGroup ? "true" : "false"}"
    >
      <header class="card-header">
        <div>
          <h3 class="card-title">${escapeHtml(title)}</h3>
          <div class="card-subtitle">${escapeHtml(subtitle)}</div>
          <div class="card-source-summary">source: ${escapeHtml(summarizeSources(group))}</div>
          <div class="pill-row">
            ${metaPillHtml}
            <span class="meta-pill card-status-pill ${status === "dirty" ? "status-edited" : status === "frozen" ? "status-frozen" : ""}">${escapeHtml(cardStatusLabel(status))}</span>
          </div>
        </div>
        <div class="card-status-box">
          <div class="card-status-text card-last-edited">最后编辑：${escapeHtml(formatTime(draft?.updatedAt || state.meta.updated_at || state.meta.created_at))}</div>
          <div class="card-actions">
            <button class="secondary-button compact-button" type="button" data-action="jump" data-group-id="${escapeHtml(group.group_id)}">定位</button>
            <button class="secondary-button compact-button" type="button" data-action="save" data-group-id="${escapeHtml(group.group_id)}" ${state.apiAvailable ? "" : "disabled"}>立即保存</button>
          </div>
        </div>
      </header>
      <div class="card-body">
        <div class="card-message-slot">
          ${frozenForGroup ? `<div class="card-banner warning">此 group 处于 conflict / frozen 影响范围内。前端仍保留 edited 草稿，不会自行覆盖。</div>` : ""}
          ${error ? `<div class="card-banner error">${escapeHtml(error)}</div>` : ""}
        </div>
        <div class="prompt-editor" data-editor-group="${escapeHtml(group.group_id)}">
          ${buildCardEditorHtml(group)}
        </div>
        <footer class="card-footer">
          <div>group_id: <code>${escapeHtml(group.group_id)}</code></div>
          <div>target refs: <code>${escapeHtml(JSON.stringify(group.target_refs || []))}</code></div>
        </footer>
      </div>
      <script class="hidden-json group-meta-json" type="application/json">${jsonForScript({
          group_id: group.group_id,
          group_label: group.group_label,
          production_chain: group.production_chain,
          stage: group.stage,
          role: group.role,
          status: group.status,
          target_refs: group.target_refs,
          blocks: group.blocks.map((block) => ({
            block_id: block.block_id,
            source_refs: block.source_refs,
            write_policy: block.write_policy,
            merge_rule: block.merge_rule,
            propagation_rule: block.propagation_rule,
            confidence: block.confidence,
            placeholder_refs: block.placeholder_refs,
          })),
        })}</script>
    </article>
  `;
}

function refreshCardChrome(groupId) {
  const group = state.groupMap.get(groupId);
  const cardEl = document.querySelector(`[data-group-id="${CSS.escape(groupId)}"]`);
  if (!group || !cardEl) return;
  const status = getCurrentCardStatus(group);
  cardEl.dataset.status = status;
  const statusPill = cardEl.querySelector(".card-status-pill, .cluster-status-pill");
  if (statusPill) {
    statusPill.textContent = cardStatusLabel(status);
    const baseClass = statusPill.classList.contains("cluster-status-pill") ? "meta-pill cluster-status-pill" : "meta-pill card-status-pill";
    statusPill.className = `${baseClass} ${status === "dirty" ? "status-edited" : status === "frozen" ? "status-frozen" : ""}`.trim();
  }
  const lastEdited = cardEl.querySelector(".card-last-edited");
  if (lastEdited) {
    const draft = getDraft(groupId);
    lastEdited.textContent = `最后编辑：${formatTime(draft?.updatedAt || state.meta.updated_at || state.meta.created_at)}`;
  }
  const saveButton = cardEl.querySelector('[data-action="save"]');
  if (saveButton) {
    saveButton.disabled = !state.apiAvailable;
  }
  const messageSlot = cardEl.querySelector(".card-message-slot");
  if (messageSlot) {
    const frozenForGroup =
      state.frozen && safeArray(state.conflicts?.affected_groups).includes(group.group_id);
    const error = state.failedGroups.get(groupId);
    messageSlot.innerHTML = [
      frozenForGroup ? '<div class="card-banner warning">此 group 处于 conflict / frozen 影响范围内。前端仍保留 edited 草稿，不会自行覆盖。</div>' : "",
      error ? `<div class="card-banner error">${escapeHtml(error)}</div>` : "",
    ]
      .filter(Boolean)
      .join("");
  }
}

function getClusterId(cluster) {
  return "cluster-" + cluster.map((g) => g.group_id).join("-").replace(/[^a-zA-Z0-9_-]/g, "-");
}

function longestCommonPrefix(strings) {
  if (!strings.length) return "";
  let prefix = strings[0];
  for (let i = 1; i < strings.length; i++) {
    let j = 0;
    while (j < prefix.length && j < strings[i].length && prefix[j] === strings[i][j]) j++;
    prefix = prefix.slice(0, j);
    if (!prefix) break;
  }
  return prefix;
}

function longestCommonSuffix(strings) {
  if (!strings.length) return "";
  let suffix = strings[0];
  for (let i = 1; i < strings.length; i++) {
    let j = 0;
    while (j < suffix.length && j < strings[i].length && suffix[suffix.length - 1 - j] === strings[i][strings[i].length - 1 - j]) j++;
    if (j === 0) return "";
    suffix = suffix.slice(-j);
    if (!suffix) break;
  }
  return suffix;
}

const MIN_EXACT_COMMON_SEGMENT_LENGTH = 2;

function isStableExactCommonSegment(text) {
  const value = String(text || "");
  return value.length >= MIN_EXACT_COMMON_SEGMENT_LENGTH && /\S/.test(value);
}

function findLongestExactCommonSegment(strings) {
  const values = strings.map((text) => String(text ?? ""));
  if (!values.length) return null;
  let shortestIndex = 0;
  for (let i = 1; i < values.length; i++) {
    if (values[i].length < values[shortestIndex].length) shortestIndex = i;
  }
  const anchor = values[shortestIndex];
  if (!anchor || anchor.length < MIN_EXACT_COMMON_SEGMENT_LENGTH) return null;
  const seen = new Set();
  for (let len = anchor.length; len >= MIN_EXACT_COMMON_SEGMENT_LENGTH; len--) {
    for (let start = 0; start + len <= anchor.length; start++) {
      const candidate = anchor.slice(start, start + len);
      if (seen.has(candidate) || !isStableExactCommonSegment(candidate)) continue;
      seen.add(candidate);
      const positions = Array(values.length).fill(-1);
      positions[shortestIndex] = start;
      let matched = true;
      for (let i = 0; i < values.length; i++) {
        if (i === shortestIndex) continue;
        const pos = values[i].indexOf(candidate);
        if (pos === -1) {
          matched = false;
          break;
        }
        positions[i] = pos;
      }
      if (matched) return { text: candidate, positions };
    }
  }
  return null;
}

function alignTexts(texts) {
  const t = texts.map((s) => String(s ?? ""));
  if (t.every((s) => s === t[0])) {
    return [{ type: "common", text: t[0] }];
  }
  const exactCommon = findLongestExactCommonSegment(t);
  if (exactCommon?.text) {
    const before = t.map((text, index) => text.slice(0, exactCommon.positions[index]));
    const after = t.map((text, index) => text.slice(exactCommon.positions[index] + exactCommon.text.length));
    return [
      ...alignTexts(before),
      { type: "common", text: exactCommon.text },
      ...alignTexts(after),
    ];
  }
  return [{ type: "diff", texts: [...t] }];
}

function getBlockFingerprint(block) {
  return String(block?.duplicate_fingerprint || "").trim();
}

function getClusterDisplayOrder(groups) {
  return Math.min(...groups.map((group) => group.display_order ?? Number.MAX_SAFE_INTEGER));
}

function isMeaningfulText(text) {
  return Boolean(String(text ?? "").replace(/\s+/g, " ").trim());
}

function getDedupBlockText(block) {
  if (!block) return "";
  if (isMeaningfulText(block.text)) return String(block.text || "");
  if (isMeaningfulText(block.normalized_text)) return String(block.normalized_text || "");
  return "";
}

function getDedupScope(group) {
  const chain = String(group.production_chain || "unknown_pipeline");
  const stage = String(group.stage || "unknown_stage");
  const role = String(group.role || "unknown_role");
  return {
    key: `${chain}::${stage}::${role}`,
    title: `${chain}::${stage}::${role}`,
    label: `${chain} / ${stage} / ${role}`,
    badgeLabel: `${stage} · ${role}`,
  };
}

function getDedupCardDisplayOrder(card) {
  if (card.type === "single") return card.group.display_order ?? Number.MAX_SAFE_INTEGER;
  return getClusterDisplayOrder(card.groups);
}

function comparePairGroups(left, right) {
  const variantDelta = Number(Boolean(left?.is_bytedance)) - Number(Boolean(right?.is_bytedance));
  if (variantDelta) return variantDelta;
  const sameCompanyDelta = Number(Boolean(left?.is_same_company)) - Number(Boolean(right?.is_same_company));
  if (sameCompanyDelta) return sameCompanyDelta;
  return (left?.display_order ?? 0) - (right?.display_order ?? 0) ||
    String(left?.group_id || "").localeCompare(String(right?.group_id || ""));
}

function buildPairCardMeta(groups) {
  const orderedGroups = safeArray(groups).slice().sort(comparePairGroups);
  const firstGroup = orderedGroups[0];
  const pairKey = firstGroup?.pair_key || firstGroup?.group_id || "empty_pair";
  const title = firstGroup?.pair_label || firstGroup?.group_label || pairKey;
  const scopeLabel = firstGroup?.pair_scope_label || title;
  const variantLabels = uniqueInOrder(orderedGroups.map((group) => group.variant_label || (group.is_bytedance ? "ByteDance" : "generic")));
  const variantSummary = variantLabels.join(" + ") || `${orderedGroups.length} variants`;
  return {
    key: `pair__${pairKey}`,
    title,
    label: title,
    badgeLabel: scopeLabel,
    scopeLabel,
    variantSummary,
    subtitle: orderedGroups.length > 1 ? `${orderedGroups.length} variants · ${variantSummary}` : variantSummary,
  };
}

function getCanonicalPairRenderGroups(groups) {
  const orderedGroups = safeArray(groups).slice().sort(comparePairGroups);
  if (orderedGroups.length < 2) return [];
  return orderedGroups;
}

function isCanonicalPairGroups(groups) {
  return getCanonicalPairRenderGroups(groups).length > 1;
}

function getPairFallbackBlockId(group) {
  return group?.blocks?.[0]?.block_id || "group-shell";
}

function createPairPlaceholderEntry(group, familyKey = "") {
  const blockId = getPairFallbackBlockId(group);
  return {
    groupId: group.group_id,
    blockId,
    ownerKey: `${group.group_id}\u0001${blockId}`,
    ownerBlockIds: [blockId],
    familyKey,
    text: "",
    fingerprint: "",
    missing: true,
    sentenceTokens: [],
    sentenceTokenKeys: [],
  };
}

function getCurrentGroupDisplayText(group) {
  const draft = getDraft(group?.group_id);
  if (typeof draft?.displayText === "string") return draft.displayText;
  if (typeof group?.display_text === "string") return group.display_text;
  return htmlToPlainText(getCurrentEditorHtml(group) || "");
}

function buildPairFallbackAlignedBlocks(groups) {
  const pairGroups = getCanonicalPairRenderGroups(groups);
  if (!pairGroups.length) return [];
  const familyKey = "__pair_group_shell__";
  const ownerSortIndex = {};
  const entries = pairGroups.map((group, index) => {
    const blockId = getPairFallbackBlockId(group);
    ownerSortIndex[`${group.group_id}\u0001${blockId}`] = index;
    return {
      groupId: group.group_id,
      familyKey,
      blockId,
      ownerBlockIds: [blockId],
      text: getCurrentGroupDisplayText(group),
      block: null,
      groupDisplayOrder: group.display_order ?? index,
      blockDisplayOrder: index,
    };
  });
  const meaningfulEntries = entries.filter((entry) => isMeaningfulText(entry.text));
  const ownerBlockMap = Object.fromEntries(
    pairGroups.map((group) => [group.group_id, [getPairFallbackBlockId(group)]])
  );
  const ownerRefs = pairGroups.map((group) => ({
    groupId: group.group_id,
    blockId: getPairFallbackBlockId(group),
  }));
  if (!meaningfulEntries.length) {
    return [{
      blockId: familyKey,
      displayBlockId: "group-shell",
      familyKey,
      isUniform: false,
      uniformText: "",
      segments: [{
        type: "segment",
        familyKey,
        textMap: Object.fromEntries(pairGroups.map((g) => [g.group_id, ""])),
        presentGroups: pairGroups.map((g) => g.group_id),
        ownerBlockMap,
        ownerRefs,
      }],
      presentGroupIds: pairGroups.map((group) => group.group_id),
      sharedFingerprint: "",
      entries,
      ownerBlockMap,
      ownerRefs,
      groupOwnerCounts: Object.fromEntries(pairGroups.map((group) => [group.group_id, 1])),
      familyBlockIds: pairGroups.map((group) => getPairFallbackBlockId(group)),
    }];
  }
  const allTextsEqual =
    meaningfulEntries.length === pairGroups.length &&
    meaningfulEntries.every((entry) => entry.text === meaningfulEntries[0].text);
  if (allTextsEqual) {
    return [{
      blockId: familyKey,
      displayBlockId: "group-shell",
      familyKey,
      isUniform: true,
      uniformText: meaningfulEntries[0].text,
      segments: null,
      presentGroupIds: pairGroups.map((group) => group.group_id),
      sharedFingerprint: "",
      entries,
      ownerBlockMap,
      ownerRefs,
      groupOwnerCounts: Object.fromEntries(pairGroups.map((group) => [group.group_id, 1])),
      familyBlockIds: pairGroups.map((group) => getPairFallbackBlockId(group)),
    }];
  }
  const sentenceEntries = meaningfulEntries.map((entry) => ({
    ...entry,
    ownerBlockIds: uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]),
    sentenceTokens: tokenizeSentenceText(entry.text),
  }));
  const columns = buildSentenceAlignmentColumns(sentenceEntries);
  const segments = buildSegmentRuns(columns, { familyKey, pairGroups });
  return [{
    blockId: familyKey,
    displayBlockId: "group-shell",
    familyKey,
    isUniform: false,
    uniformText: "",
    segments,
    presentGroupIds: pairGroups.map((group) => group.group_id),
    sharedFingerprint: "",
    entries,
    ownerBlockMap,
    ownerRefs,
    groupOwnerCounts: Object.fromEntries(pairGroups.map((group) => [group.group_id, 1])),
    familyBlockIds: pairGroups.map((group) => getPairFallbackBlockId(group)),
  }];
}

function isWordLikeChar(char) {
  return /[0-9A-Za-z\u4e00-\u9fff]/.test(char || "");
}

function uniqueInOrder(values) {
  const seen = new Set();
  const result = [];
  for (const value of safeArray(values)) {
    if (value === null || value === undefined || seen.has(value)) continue;
    seen.add(value);
    result.push(value);
  }
  return result;
}

function getBlockIdFamilyCandidates(blockId) {
  const value = String(blockId || "").trim();
  if (!value) return [];
  const parts = value.split("::");
  const leaf = parts.pop() || "";
  const namespacePrefix = parts.length ? `${parts.join("::")}::` : "";
  const leafPieces = leaf.split("_").filter(Boolean);
  const candidates = [value];
  for (let i = leafPieces.length - 1; i >= 1; i--) {
    candidates.push(`${namespacePrefix}${leafPieces.slice(0, i).join("_")}`);
  }
  return uniqueInOrder(candidates);
}

function resolveAlignmentFamilyKey(blockId, availableBlockIds) {
  const candidates = getBlockIdFamilyCandidates(blockId);
  for (let i = 1; i < candidates.length; i++) {
    if (availableBlockIds.has(candidates[i])) return candidates[i];
  }
  return candidates[0] || String(blockId || "");
}

function getGroupBlocksByFamily(group, availableBlockIds) {
  const familyMap = new Map();
  for (const block of safeArray(group?.blocks)) {
    const familyKey = resolveAlignmentFamilyKey(block.block_id, availableBlockIds);
    if (!familyMap.has(familyKey)) familyMap.set(familyKey, []);
    familyMap.get(familyKey).push(block);
  }
  return familyMap;
}

function getGroupFamilyOrder(group, availableBlockIds) {
  return uniqueInOrder(safeArray(group?.blocks).map((block) => resolveAlignmentFamilyKey(block.block_id, availableBlockIds)));
}

const SENTENCE_BOUNDARY_CHARS = new Set(["。", "！", "？", ".", "!", "?", ";", "；", "\n"]);
const SENTENCE_TRAILING_CLOSERS = new Set(['"', "'", "”", "’", "」", "』", "）", ")", "]", "】"]);

function normalizeSentenceTokenText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function tokenizeSentenceText(text) {
  const value = String(text ?? "");
  if (!value) return [];
  const tokens = [];
  let start = 0;
  for (let index = 0; index < value.length; index++) {
    const char = value[index];
    if (!SENTENCE_BOUNDARY_CHARS.has(char)) continue;
    let end = index + 1;
    while (end < value.length && SENTENCE_TRAILING_CLOSERS.has(value[end])) end++;
    while (end < value.length && /\s/.test(value[end])) end++;
    const rawText = value.slice(start, end);
    const normalized = normalizeSentenceTokenText(rawText);
    if (normalized) {
      tokens.push({
        text: rawText,
        normalized,
        key: normalized,
      });
    }
    start = end;
    index = end - 1;
  }
  if (start < value.length) {
    const rawText = value.slice(start);
    const normalized = normalizeSentenceTokenText(rawText);
    if (normalized) {
      tokens.push({
        text: rawText,
        normalized,
        key: normalized,
      });
    }
  }
  if (!tokens.length && normalizeSentenceTokenText(value)) {
    tokens.push({
      text: value,
      normalized: normalizeSentenceTokenText(value),
      key: normalizeSentenceTokenText(value),
    });
  }
  return tokens.map((token, index) => ({
    ...token,
    index,
  }));
}

function joinSentenceTokens(tokens) {
  return safeArray(tokens).map((token) => token?.text || "").join("");
}

function buildSentenceOwnerRefs(entries) {
  return safeArray(entries).flatMap((entry) =>
    safeArray(entry?.ownerBlockIds?.length ? entry.ownerBlockIds : [entry?.blockId])
      .filter(Boolean)
      .map((blockId) => ({
        groupId: entry.groupId,
        blockId,
      }))
  );
}

function buildSentenceDiffMetadata(entries) {
  const bucketMap = new Map();
  safeArray(entries).forEach((entry) => {
    safeArray(entry.sentenceTokens).forEach((token) => {
      const key = token?.key || "";
      if (!key) return;
      if (!bucketMap.has(key)) {
        bucketMap.set(key, {
          key,
          text: token.text,
          ownerGroupIds: new Set(),
          ownerBlockIds: new Set(),
        });
      }
      const bucket = bucketMap.get(key);
      bucket.ownerGroupIds.add(entry.groupId);
      safeArray(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]).forEach((blockId) => {
        if (blockId) bucket.ownerBlockIds.add(blockId);
      });
    });
  });
  return [...bucketMap.values()]
    .filter((bucket) => bucket.ownerGroupIds.size > 1)
    .map((bucket) => ({
      key: bucket.key,
      text: bucket.text,
      ownerGroupIds: [...bucket.ownerGroupIds],
      ownerBlockIds: [...bucket.ownerBlockIds],
    }));
}

function compactExactSegments(segments) {
  const compacted = [];
  for (const segment of safeArray(segments)) {
    if (segment.type === "common" && !segment.text) continue;
    if (segment.type === "diff" && safeArray(segment.texts).every((text) => !String(text || ""))) continue;
    const previous = compacted[compacted.length - 1];
    if (previous?.type === "common" && segment.type === "common") {
      previous.text += segment.text;
      continue;
    }
    if (previous?.type === "diff" && segment.type === "diff") {
      previous.texts = previous.texts.map((text, index) => `${text}${segment.texts[index] || ""}`);
      continue;
    }
    compacted.push(segment.type === "common"
      ? { type: "common", text: segment.text }
      : { type: "diff", texts: [...safeArray(segment.texts).map((text) => String(text || ""))] });
  }
  return compacted;
}

function rebalanceExactSegments(segments) {
  const normalized = compactExactSegments(segments);
  for (let i = 0; i < normalized.length; i++) {
    const current = normalized[i];
    if (!current || current.type !== "diff") continue;
    const diffTexts = safeArray(current.texts).map((text) => String(text || ""));
    if (!diffTexts.length || diffTexts.some((text) => !text)) continue;
    const previous = normalized[i - 1];
    const next = normalized[i + 1];
    if (previous?.type !== "common" || next?.type !== "common") continue;
    if (previous?.type === "common" && previous.text.length > 1) {
      const shifted = previous.text.slice(-1);
      if (isWordLikeChar(shifted)) {
        previous.text = previous.text.slice(0, -1);
        current.texts = diffTexts.map((text) => `${shifted}${text}`);
      }
    }
    if (next?.type === "common" && next.text.length > 1) {
      const shifted = next.text.slice(0, 1);
      if (isWordLikeChar(shifted)) {
        next.text = next.text.slice(1);
        current.texts = safeArray(current.texts).map((text) => `${text}${shifted}`);
      }
    }
  }
  return compactExactSegments(normalized);
}

function buildExactSegmentsFromEntries(entries) {
  const texts = entries.map((entry) => String(entry.text || ""));
  const segments = rebalanceExactSegments(alignTexts(texts));
  return segments.map((segment) => {
    if (segment.type === "common") {
      return { type: "common", text: segment.text };
    }
    return {
      type: "diff",
      entries: entries.map((entry, index) => ({
        groupId: entry.groupId,
        text: String(segment.texts[index] || ""),
        fingerprint: getBlockFingerprint(entry.block),
        missing: !entry.block,
      })),
    };
  });
}

function findLongestCommonSentenceRun(entrySlices) {
  const slices = safeArray(entrySlices).map((entry) => ({
    ...entry,
    sentenceTokens: safeArray(entry.sentenceTokens),
    sentenceTokenKeys: safeArray(entry.sentenceTokens).map((token) => token?.key || ""),
  }));
  if (!slices.length || slices.some((entry) => !entry.sentenceTokenKeys.length)) return null;
  let shortestIndex = 0;
  for (let i = 1; i < slices.length; i++) {
    if (slices[i].sentenceTokenKeys.length < slices[shortestIndex].sentenceTokenKeys.length) shortestIndex = i;
  }
  const anchorKeys = slices[shortestIndex].sentenceTokenKeys;
  const seen = new Set();
  for (let len = anchorKeys.length; len >= 1; len--) {
    for (let start = 0; start + len <= anchorKeys.length; start++) {
      const candidateKeys = anchorKeys.slice(start, start + len);
      const candidateKey = candidateKeys.join("\u0002");
      if (!candidateKey || seen.has(candidateKey)) continue;
      seen.add(candidateKey);
      const positions = Array(slices.length).fill(-1);
      positions[shortestIndex] = start;
      let matched = true;
      for (let i = 0; i < slices.length; i++) {
        if (i === shortestIndex) continue;
        const haystack = slices[i].sentenceTokenKeys;
        let found = -1;
        for (let j = 0; j + len <= haystack.length; j++) {
          let same = true;
          for (let offset = 0; offset < len; offset++) {
            if (haystack[j + offset] !== candidateKeys[offset]) {
              same = false;
              break;
            }
          }
          if (same) {
            found = j;
            break;
          }
        }
        if (found === -1) {
          matched = false;
          break;
        }
        positions[i] = found;
      }
      if (matched) {
        return {
          positions,
          length: len,
          tokens: slices[shortestIndex].sentenceTokens.slice(start, start + len),
        };
      }
    }
  }
  return null;
}

function buildSentenceAlignmentOps(leftKeys, rightKeys) {
  const rows = leftKeys.length;
  const cols = rightKeys.length;
  const dp = Array.from({ length: rows + 1 }, () => Array(cols + 1).fill(0));
  for (let i = 1; i <= rows; i++) {
    for (let j = 1; j <= cols; j++) {
      dp[i][j] = leftKeys[i - 1] === rightKeys[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  const ops = [];
  let i = rows;
  let j = cols;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && leftKeys[i - 1] === rightKeys[j - 1]) {
      ops.unshift({ type: "match", leftIndex: i - 1, rightIndex: j - 1 });
      i--;
      j--;
      continue;
    }
    if (i > 0 && (j === 0 || dp[i - 1][j] >= dp[i][j - 1])) {
      ops.unshift({ type: "delete", leftIndex: i - 1 });
      i--;
      continue;
    }
    ops.unshift({ type: "insert", rightIndex: j - 1 });
    j--;
  }
  return ops;
}

function countSentenceAlignmentScore(leftKeys, rightKeys) {
  const rows = leftKeys.length;
  const cols = rightKeys.length;
  const dp = Array.from({ length: rows + 1 }, () => Array(cols + 1).fill(0));
  for (let i = 1; i <= rows; i++) {
    for (let j = 1; j <= cols; j++) {
      dp[i][j] = leftKeys[i - 1] === rightKeys[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  return dp[rows][cols];
}

function buildSentenceColumnEntry(entry, token, tokenIndex) {
  const ownerBlockIds = uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]);
  const tokenKey = token?.key || "";
  return {
    groupId: entry.groupId,
    blockId: entry.blockId,
    ownerKey: `${entry.groupId}\u0001${entry.blockId || ownerBlockIds.join("\u0002")}`,
    ownerBlockIds,
    familyKey: entry.familyKey || "",
    text: token?.text || "",
    fingerprint: getBlockFingerprint(entry.block),
    missing: !entry.block,
    sentenceTokens: token ? [token] : [],
    sentenceTokenKeys: tokenKey ? [tokenKey] : [],
    tokenIndex,
  };
}

function createSentenceColumn(entry, token, tokenIndex) {
  const column = {
    tokenKey: token?.key || "",
    tokenText: token?.text || "",
    entriesByOwnerKey: new Map(),
  };
  const columnEntry = buildSentenceColumnEntry(entry, token, tokenIndex);
  column.entriesByOwnerKey.set(columnEntry.ownerKey, columnEntry);
  return column;
}

function appendSentenceTokenToColumn(column, entry, token, tokenIndex) {
  const tokenKey = token?.key || "";
  if (!column.tokenKey) column.tokenKey = tokenKey;
  if (!column.tokenText) column.tokenText = token?.text || "";
  const columnEntry = buildSentenceColumnEntry(entry, token, tokenIndex);
  column.entriesByOwnerKey.set(columnEntry.ownerKey, columnEntry);
}

function sortSentenceColumnEntries(entries, meta = {}) {
  const ownerSortIndex = meta.ownerSortIndex || {};
  return safeArray(entries).slice().sort((left, right) => {
    const leftKey = left?.ownerKey || `${left?.groupId || ""}\u0001${left?.blockId || ""}`;
    const rightKey = right?.ownerKey || `${right?.groupId || ""}\u0001${right?.blockId || ""}`;
    const leftIndex = ownerSortIndex[leftKey] ?? Number.MAX_SAFE_INTEGER;
    const rightIndex = ownerSortIndex[rightKey] ?? Number.MAX_SAFE_INTEGER;
    if (leftIndex !== rightIndex) return leftIndex - rightIndex;
    return leftKey.localeCompare(rightKey);
  });
}

function mergeSentenceColumns(existingColumns, entry) {
  const nextTokenKeys = safeArray(entry.sentenceTokens).map((token) => token?.key || "");
  if (!existingColumns.length) {
    return nextTokenKeys.map((_, index) => createSentenceColumn(entry, entry.sentenceTokens[index], index));
  }
  const currentKeys = existingColumns.map((column) => column.tokenKey);
  const ops = buildSentenceAlignmentOps(currentKeys, nextTokenKeys);
  const merged = [];
  let leftIndex = 0;
  let rightIndex = 0;
  for (const op of ops) {
    if (op.type === "match") {
      const column = existingColumns[leftIndex++];
      appendSentenceTokenToColumn(column, entry, entry.sentenceTokens[rightIndex], rightIndex);
      merged.push(column);
      rightIndex++;
      continue;
    }
    if (op.type === "delete") {
      merged.push(existingColumns[leftIndex++]);
      continue;
    }
    merged.push(createSentenceColumn(entry, entry.sentenceTokens[rightIndex], rightIndex));
    rightIndex++;
  }
  return merged;
}

function buildSentenceAlignmentColumns(entries) {
  const normalizedEntries = safeArray(entries).map((entry) => ({
    ...entry,
    ownerBlockIds: uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]),
    sentenceTokens: safeArray(entry.sentenceTokens),
    sentenceTokenKeys: safeArray(entry.sentenceTokens).map((token) => token?.key || ""),
  }));
  const meaningfulEntries = normalizedEntries.filter((entry) => entry.sentenceTokens.length > 0);
  if (!meaningfulEntries.length) return [];
  let seedIndex = 0;
  let seedScore = -1;
  meaningfulEntries.forEach((candidate, index) => {
    const score = meaningfulEntries.reduce(
      (sum, other) => sum + countSentenceAlignmentScore(candidate.sentenceTokenKeys, other.sentenceTokenKeys),
      0,
    );
    if (
      score > seedScore ||
      (score === seedScore && candidate.sentenceTokenKeys.length > meaningfulEntries[seedIndex]?.sentenceTokenKeys.length)
    ) {
      seedIndex = index;
      seedScore = score;
    }
  });
  let columns = meaningfulEntries[seedIndex].sentenceTokens.map((token, index) => createSentenceColumn(meaningfulEntries[seedIndex], token, index));
  for (let index = 0; index < meaningfulEntries.length; index++) {
    if (index === seedIndex) continue;
    columns = mergeSentenceColumns(columns, meaningfulEntries[index]);
  }
  return columns;
}

function buildSegmentRuns(columns, meta = {}) {
  const runs = [];
  let currentRun = [];
  let currentPresentGroups = null;

  for (const column of safeArray(columns)) {
    const presentGroups = uniqueInOrder([...column.entriesByOwnerKey.values()].map((entry) => entry.groupId));
    if (!presentGroups.length) continue;

    if (currentRun.length === 0) {
      currentRun.push(column);
      currentPresentGroups = presentGroups;
    } else if (JSON.stringify(currentPresentGroups) === JSON.stringify(presentGroups)) {
      currentRun.push(column);
    } else {
      runs.push({ columns: currentRun, presentGroups: currentPresentGroups });
      currentRun = [column];
      currentPresentGroups = presentGroups;
    }
  }
  if (currentRun.length) {
    runs.push({ columns: currentRun, presentGroups: currentPresentGroups });
  }

  return runs.map((run) => {
    const textMap = {};
    const ownerBlockMap = {};
    const ownerRefs = [];

    for (const groupId of run.presentGroups) {
      textMap[groupId] = "";
    }

    for (const column of run.columns) {
      for (const [ownerKey, entry] of column.entriesByOwnerKey) {
        if (!run.presentGroups.includes(entry.groupId)) continue;
        textMap[entry.groupId] += entry.text || column.tokenText;
        if (!ownerBlockMap[entry.groupId]) ownerBlockMap[entry.groupId] = [];
        ownerBlockMap[entry.groupId].push(...safeArray(entry.ownerBlockIds));
      }
    }

    for (const groupId of Object.keys(ownerBlockMap)) {
      ownerBlockMap[groupId] = uniqueInOrder(ownerBlockMap[groupId]);
    }

    for (const groupId of run.presentGroups) {
      const blockIds = ownerBlockMap[groupId] || [];
      for (const blockId of blockIds) {
        ownerRefs.push({ groupId, blockId });
      }
    }

    return {
      type: "segment",
      familyKey: meta.familyKey || "",
      textMap,
      presentGroups: run.presentGroups,
      ownerBlockMap,
      ownerRefs,
    };
  });
}

function buildSentenceCommonSegment(columns, meta = {}) {
  const columnEntries = columns.map((column) => [...column.entriesByOwnerKey.values()]);
  const ownerGroupIds = uniqueInOrder(columnEntries.flatMap((entries) => entries.map((entry) => entry.groupId)));
  const ownerBlockIds = uniqueInOrder(columnEntries.flatMap((entries) => entries.flatMap((entry) => entry.ownerBlockIds)));
  const sentenceTokens = columns.map((column) => ({ text: column.tokenText, key: column.tokenKey }));
  return {
    type: "common",
    strategy: "sentence_common",
    familyKey: meta.familyKey || "",
    text: columns.map((column) => column.tokenText).join(""),
    sentenceTokens,
    sentenceTokenKeys: columns.map((column) => column.tokenKey),
    ownerGroupIds,
    ownerBlockIds,
    ownerRefs: buildSentenceOwnerRefs(columnEntries.flat()),
  };
}

function buildSentenceDiffSegmentFromColumns(columns, meta = {}) {
  const entryMap = new Map();
  const orderedOwnerKeys = [];
  for (const column of columns) {
    const columnEntries = sortSentenceColumnEntries([...column.entriesByOwnerKey.values()], meta);
    if (!columnEntries.length) continue;
    for (const entry of columnEntries) {
      const ownerKey = entry.ownerKey || `${entry.groupId}\u0001${entry.blockId || ""}`;
      if (!entryMap.has(ownerKey)) {
        entryMap.set(ownerKey, {
          groupId: entry.groupId,
          blockId: entry.blockId,
          ownerKey,
          ownerBlockIds: uniqueInOrder(entry.ownerBlockIds),
          familyKey: entry.familyKey || meta.familyKey || "",
          text: "",
          fingerprint: entry.fingerprint,
          missing: entry.missing,
          sentenceTokens: [],
          sentenceTokenKeys: [],
        });
        orderedOwnerKeys.push(ownerKey);
      }
      const target = entryMap.get(ownerKey);
      target.text += entry.text || column.tokenText;
      target.sentenceTokens = [...safeArray(target.sentenceTokens), ...(entry.sentenceTokens?.length ? entry.sentenceTokens : [{ text: entry.text || column.tokenText, key: column.tokenKey }])];
      target.sentenceTokenKeys = [...safeArray(target.sentenceTokenKeys), ...(entry.sentenceTokenKeys?.length ? entry.sentenceTokenKeys : [column.tokenKey])];
    }
  }
  const pairGroups = getCanonicalPairRenderGroups(meta.pairGroups);
  const entries = orderedOwnerKeys.map((ownerKey) => entryMap.get(ownerKey)).filter(Boolean);
  const normalizedEntries = pairGroups.length
    ? pairGroups.flatMap((group) => {
        const matches = entries.filter((entry) => entry.groupId === group.group_id);
        return matches.length ? matches : [createPairPlaceholderEntry(group, meta.familyKey || "")];
      })
    : entries;
  return {
    type: "diff",
    strategy: "sentence_diff",
    familyKey: meta.familyKey || "",
    ownerGroupIds: pairGroups.length ? pairGroups.map((group) => group.group_id) : uniqueInOrder(normalizedEntries.map((entry) => entry.groupId)),
    ownerBlockIds: uniqueInOrder(normalizedEntries.flatMap((entry) => entry.ownerBlockIds)),
    ownerRefs: buildSentenceOwnerRefs(normalizedEntries),
    sentenceBuckets: buildSentenceDiffMetadata(normalizedEntries),
    entries: normalizedEntries,
    pairGroupIds: pairGroups.map((group) => group.group_id),
  };
}

function buildSentenceSegmentsFromColumns(columns, meta = {}) {
  const segments = [];
  let commonRun = [];
  let diffRun = [];
  const flushCommonRun = () => {
    if (!commonRun.length) return;
    segments.push(buildSentenceCommonSegment(commonRun, meta));
    commonRun = [];
  };
  const flushDiffRun = () => {
    if (!diffRun.length) return;
    segments.push(buildSentenceDiffSegmentFromColumns(diffRun, meta));
    diffRun = [];
  };
  const totalGroups = meta.pairGroups?.length || 0;
  for (const column of safeArray(columns)) {
    const ownerGroupIds = uniqueInOrder([...column.entriesByOwnerKey.values()].map((entry) => entry.groupId));
    if (totalGroups > 0 ? ownerGroupIds.length === totalGroups : ownerGroupIds.length >= 2) {
      flushDiffRun();
      const previous = commonRun[commonRun.length - 1];
      const previousOwners = previous ? uniqueInOrder([...previous.entriesByOwnerKey.values()].map((entry) => entry.groupId)) : [];
      if (previous && JSON.stringify(previousOwners) === JSON.stringify(ownerGroupIds)) {
        commonRun.push(column);
      } else {
        flushCommonRun();
        commonRun.push(column);
      }
      continue;
    }
    flushCommonRun();
    diffRun.push(column);
  }
  flushCommonRun();
  flushDiffRun();
  return segments;
}

function alignSentenceEntries(entrySlices, meta = {}) {
  const normalizedSlices = safeArray(entrySlices).map((entry) => ({
    ...entry,
    ownerBlockIds: uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]),
    sentenceTokens: safeArray(entry.sentenceTokens),
  }));
  const meaningfulSlices = normalizedSlices.filter((entry) => entry.sentenceTokens.length > 0);
  if (!meaningfulSlices.length) return [];
  const columns = buildSentenceAlignmentColumns(meaningfulSlices);
  return buildSentenceSegmentsFromColumns(columns, meta);
}

function buildSentenceSegmentsFromEntries(entries, meta = {}) {
  const sentenceEntries = safeArray(entries).map((entry) => ({
    ...entry,
    ownerBlockIds: uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]),
    sentenceTokens: tokenizeSentenceText(entry.text),
  }));
  return alignSentenceEntries(sentenceEntries, meta);
}

function buildDedupClusterMeta(groups, scope, index, totalClusters) {
  const key = `${scope.key}__cluster_${index + 1}__${groups.map((group) => group.group_id).sort().join("__")}`;
  const groupLabels = uniqueSorted(groups.map((group) => group.short_label || group.group_label || group.group_id));
  const suffix = totalClusters > 1 ? ` · cluster ${index + 1}` : "";
  const detail = groupLabels.length <= 3 ? groupLabels.join(" / ") : `${groupLabels.length} groups`;
  return {
    key,
    title: `${scope.title}${suffix}`,
    label: `${scope.label}${suffix}${detail ? ` · ${detail}` : ""}`,
    badgeLabel: scope.badgeLabel,
  };
}

function buildFingerprintSharingClusters(groups) {
  if (groups.length <= 1) return groups.map((group) => [group]);
  const uf = new UnionFind(groups);
  const ownersByBlockFingerprint = new Map();
  for (const group of groups) {
    for (const block of safeArray(group.blocks)) {
      const fingerprint = getBlockFingerprint(block);
      if (!fingerprint || !isMeaningfulText(getDedupBlockText(block))) continue;
      const key = `${block.block_id}::${fingerprint}`;
      if (!ownersByBlockFingerprint.has(key)) ownersByBlockFingerprint.set(key, new Set());
      ownersByBlockFingerprint.get(key).add(group.group_id);
    }
  }
  const sharedFingerprintCounts = new Map();
  for (const ownerIds of ownersByBlockFingerprint.values()) {
    const ids = [...ownerIds];
    if (ids.length < 2) continue;
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const pairKey = [ids[i], ids[j]].sort().join("\u0001");
        sharedFingerprintCounts.set(pairKey, (sharedFingerprintCounts.get(pairKey) || 0) + 1);
      }
    }
  }
  for (const [pairKey, sharedCount] of sharedFingerprintCounts.entries()) {
    if (sharedCount < 2) continue;
    const [leftId, rightId] = pairKey.split("\u0001");
    uf.union(leftId, rightId);
  }
  const buckets = new Map();
  for (const group of groups) {
    const root = uf.find(group.group_id);
    if (!buckets.has(root)) buckets.set(root, []);
    buckets.get(root).push(group);
  }
  return [...buckets.values()]
    .map((cluster) => cluster.slice().sort((left, right) =>
      (left.display_order ?? 0) - (right.display_order ?? 0) || left.group_id.localeCompare(right.group_id)
    ))
    .sort((left, right) => getClusterDisplayOrder(left) - getClusterDisplayOrder(right));
}

const SUPER_CARD_MERGE_RULES = [
  {
    key: "match_pipe::writer_group",
    pairKeys: new Set([
      "match_pipe::no_starter::writer",
      "match_pipe::old_match_anchor::writer",
      "match_pipe::new_dual_channel::writer",
      "match_pipe::planner_write::writer",
    ]),
  },
  {
    key: "match_pipe::reviewer_group",
    pairKeys: new Set([
      "match_pipe::reviewer::full",
      "match_pipe::planner_direct_review::reviewer",
    ]),
  },
];

const SUPER_CARD_META = {
  "match_pipe::writer_group": {
    key: "pair__match_pipe_writer_group",
    title: "match_pipe / writer group",
    label: "match_pipe / writer group",
    badgeLabel: "writer group",
  },
  "match_pipe::reviewer_group": {
    key: "pair__match_pipe_reviewer_group",
    title: "match_pipe / reviewer group",
    label: "match_pipe / reviewer group",
    badgeLabel: "reviewer group",
  },
};

function buildMegaCards(groups) {
  const mpGroups = groups.filter((g) => g.production_chain === "match_pipe");
  const pairBuckets = new Map();
  for (const group of mpGroups) {
    const pairKey = group.pair_key || group.group_id;
    if (!pairBuckets.has(pairKey)) {
      pairBuckets.set(pairKey, []);
    }
    pairBuckets.get(pairKey).push(group);
  }

  const mergedBuckets = new Map();
  for (const [pairKey, pairGroups] of pairBuckets) {
    let targetKey = pairKey;
    for (const rule of SUPER_CARD_MERGE_RULES) {
      if (rule.pairKeys.has(pairKey)) {
        targetKey = rule.key;
        break;
      }
    }
    if (!mergedBuckets.has(targetKey)) {
      mergedBuckets.set(targetKey, []);
    }
    mergedBuckets.get(targetKey).push(...pairGroups);
  }

  const cards = [];
  const orderedPairs = [...mergedBuckets.entries()].sort(
    (left, right) => getClusterDisplayOrder(left[1]) - getClusterDisplayOrder(right[1]),
  );
  orderedPairs.forEach(([bucketKey, bucketGroups]) => {
    const orderedGroups = bucketGroups.slice().sort(comparePairGroups);
    const meta = buildPairCardMeta(orderedGroups);
    if (SUPER_CARD_META[bucketKey]) {
      Object.assign(meta, SUPER_CARD_META[bucketKey]);
    }
    if (orderedGroups.length === 1) {
      cards.push({
        type: "single",
        key: meta.key,
        group: orderedGroups[0],
        title: meta.title,
        label: meta.label,
        badgeLabel: meta.badgeLabel,
        subtitle: `${orderedGroups[0].prompt_kind} · ${meta.variantSummary}`,
        variantSummary: meta.variantSummary,
      });
      return;
    }
    const alignedBlocks = buildMegaBlockAlignments(orderedGroups);
    if (!alignedBlocks.length) {
      if (isCanonicalPairGroups(orderedGroups)) {
        cards.push({
          type: "mega",
          key: meta.key,
          title: meta.title,
          label: meta.label,
          badgeLabel: meta.badgeLabel,
          subtitle: meta.subtitle,
          variantSummary: meta.variantSummary,
          groups: orderedGroups,
          alignedBlocks: buildPairFallbackAlignedBlocks(orderedGroups),
        });
        return;
      }
      orderedGroups.forEach((group) => {
        cards.push({
          type: "single",
          key: `${meta.key}__${group.group_id}`,
          group,
          title: meta.title,
          label: meta.label,
          badgeLabel: meta.badgeLabel,
          subtitle: `${group.prompt_kind} · ${group.variant_label || (group.is_bytedance ? "ByteDance" : "generic")}`,
          variantSummary: group.variant_label || (group.is_bytedance ? "ByteDance" : "generic"),
        });
      });
      return;
    }
    cards.push({
      type: "mega",
      key: meta.key,
      title: meta.title,
      label: meta.label,
      badgeLabel: meta.badgeLabel,
      subtitle: meta.subtitle,
      variantSummary: meta.variantSummary,
      groups: orderedGroups,
      alignedBlocks,
    });
  });
  return cards.sort((left, right) => getDedupCardDisplayOrder(left) - getDedupCardDisplayOrder(right));
}

function lcsMerge(a, b) {
  const dp = Array(a.length + 1).fill(null).map(() => Array(b.length + 1).fill(0));
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
      else dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  const result = [];
  let i = a.length, j = b.length;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) {
      result.unshift(a[i - 1]);
      i--;
      j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift(b[j - 1]);
      j--;
    } else {
      result.unshift(a[i - 1]);
      i--;
    }
  }
  return result;
}

function mergeBlockOrders(orders) {
  if (!orders.length) return [];
  let result = orders[0];
  for (let i = 1; i < orders.length; i++) {
    result = lcsMerge(result, orders[i]);
  }
  return result;
}

function isStageExclusiveBlock(presentGroupIds, allGroups) {
  const stageMap = new Map();
  for (const g of allGroups) {
    if (!stageMap.has(g.stage)) stageMap.set(g.stage, []);
    stageMap.get(g.stage).push(g.group_id);
  }
  const presentSet = new Set(presentGroupIds);
  for (const [, stageGroupIds] of stageMap) {
    if (stageGroupIds.length !== presentSet.size) continue;
    if (stageGroupIds.every((id) => presentSet.has(id))) return true;
  }
  return false;
}

function buildMegaBlockAlignments(groups) {
  const availableBlockIds = new Set(
    groups.flatMap((group) => safeArray(group.blocks).map((block) => block.block_id)).filter(Boolean)
  );
  const familyMapByGroupId = new Map(
    groups.map((group) => [group.group_id, getGroupBlocksByFamily(group, availableBlockIds)])
  );
  const familyOrders = groups.map((group) => getGroupFamilyOrder(group, availableBlockIds));
  const allFamilyKeys = mergeBlockOrders(familyOrders);
  return allFamilyKeys.map((familyKey) => {
    const visibleEntries = groups.flatMap((group, groupIndex) => {
      const familyBlocks = safeArray(familyMapByGroupId.get(group.group_id)?.get(familyKey));
      return familyBlocks
        .filter((block) => isMeaningfulText(getDedupBlockText(block)))
        .map((block) => ({
          groupId: group.group_id,
          familyKey,
          blockId: block.block_id,
          ownerBlockIds: [block.block_id],
          text: getDedupBlockText(block),
          block,
          groupDisplayOrder: group.display_order ?? groupIndex,
          blockDisplayOrder: block.display_order ?? Number.MAX_SAFE_INTEGER,
        }));
    });
    if (!visibleEntries.length) return null;
    const presentGroupIds = uniqueInOrder(visibleEntries.map((entry) => entry.groupId));
    const ownerBlockMap = {};
    const groupOwnerCounts = {};
    visibleEntries.forEach((entry) => {
      if (!entry.blockId) return;
      if (!ownerBlockMap[entry.groupId]) ownerBlockMap[entry.groupId] = [];
      ownerBlockMap[entry.groupId].push(entry.blockId);
      groupOwnerCounts[entry.groupId] = (groupOwnerCounts[entry.groupId] || 0) + 1;
    });
    Object.keys(ownerBlockMap).forEach((groupId) => {
      ownerBlockMap[groupId] = uniqueInOrder(ownerBlockMap[groupId]);
    });
    const sentenceEntries = visibleEntries.map((entry) => ({
      ...entry,
      ownerBlockIds: uniqueInOrder(entry.ownerBlockIds?.length ? entry.ownerBlockIds : [entry.blockId]),
      sentenceTokens: tokenizeSentenceText(entry.text),
    }));
    const columns = buildSentenceAlignmentColumns(sentenceEntries);
    const fingerprints = visibleEntries.map((entry) => getBlockFingerprint(entry.block));
    const hasSingleVisibleEntryPerGroup =
      visibleEntries.length === presentGroupIds.length &&
      presentGroupIds.length === groups.length;
    const sharedFingerprint =
      hasSingleVisibleEntryPerGroup &&
      visibleEntries.length > 1 &&
      fingerprints[0] &&
      fingerprints.every((fingerprint) => fingerprint === fingerprints[0])
        ? fingerprints[0]
        : "";
    const isUniform = Boolean(sharedFingerprint);
    let segments = null;
    if (!isUniform) {
      const textMap = {};
      const segOwnerBlockMap = {};
      visibleEntries.forEach((entry) => {
        textMap[entry.groupId] = (textMap[entry.groupId] || "") + entry.text;
        if (!segOwnerBlockMap[entry.groupId]) segOwnerBlockMap[entry.groupId] = [];
        segOwnerBlockMap[entry.groupId].push(...entry.ownerBlockIds);
      });
      Object.keys(segOwnerBlockMap).forEach((groupId) => {
        segOwnerBlockMap[groupId] = uniqueInOrder(segOwnerBlockMap[groupId]);
      });
      const segOwnerRefs = [];
      Object.keys(textMap).forEach((groupId) => {
        (segOwnerBlockMap[groupId] || []).forEach((blockId) => {
          segOwnerRefs.push({ groupId, blockId });
        });
      });
      segments = [{
        type: "segment",
        familyKey,
        textMap,
        presentGroups: Object.keys(textMap),
        ownerBlockMap: segOwnerBlockMap,
        ownerRefs: segOwnerRefs,
      }];
    }
    const displayBlockIds = uniqueInOrder(visibleEntries.map((entry) => entry.blockId).filter(Boolean));
    return {
      blockId: familyKey,
      displayBlockId: displayBlockIds.length === 1 ? displayBlockIds[0] : familyKey,
      familyKey,
      isUniform,
      uniformText: isUniform ? visibleEntries[0].text : "",
      segments,
      presentGroupIds,
      sharedFingerprint,
      entries: visibleEntries,
      ownerBlockMap,
      ownerRefs: buildSentenceOwnerRefs(visibleEntries),
      groupOwnerCounts,
      familyBlockIds: uniqueInOrder(visibleEntries.flatMap((entry) => entry.ownerBlockIds)),
    };
  }).filter(Boolean);
}

function getMegaCardId(key) {
  return "mega-" + key.replace(/[^a-zA-Z0-9_-]/g, "-");
}

function plainTextToSimpleHtml(text) {
  const lines = String(text ?? "").split("\n");
  if (lines.length === 1 && !lines[0]) return "<p><br></p>";
  return lines.map((line) => `<p>${escapeHtml(line) || "<br>"}</p>`).join("");
}

function getPipelineLabel(group) {
  if (!group?.group_id) return "unknown";
  const parts = group.group_id.split("::");
  return parts[1] || parts[0] || "unknown";
}

function buildShareDistributionLabel(groups) {
  const map = new Map();
  for (const g of safeArray(groups)) {
    const pipeline = getPipelineLabel(g);
    const variant = g.variant_label || "unknown";
    if (!map.has(pipeline)) map.set(pipeline, []);
    map.get(pipeline).push(variant);
  }
  const parts = [];
  for (const [pipeline, variants] of map) {
    parts.push(`${pipeline}(${uniqueInOrder(variants).join(",")})`);
  }
  return parts.join(" + ");
}

function buildBlockDistributionSummary(alignedBlock, allGroups) {
  const presentSet = new Set(alignedBlock.presentGroupIds || []);
  const present = safeArray(allGroups).filter((g) => presentSet.has(g.group_id));
  const absent = safeArray(allGroups).filter((g) => !presentSet.has(g.group_id));

  const summarize = (list) => {
    const map = new Map();
    for (const g of list) {
      const pipeline = getPipelineLabel(g);
      map.set(pipeline, (map.get(pipeline) || 0) + 1);
    }
    return Array.from(map.entries())
      .map(([p, c]) => `${p}(${c})`)
      .join(" + ");
  };

  const presentText = present.length ? `present: ${summarize(present)} = ${present.length}` : "present: none";
  const absentText = absent.length ? `absent: ${summarize(absent)} = ${absent.length}` : "";
  return [presentText, absentText].filter(Boolean).join(" | ");
}

function renderMegaBlock(alignedBlock, groups) {
  const {
    blockId,
    displayBlockId,
    familyKey,
    isUniform,
    uniformText,
    segments,
    presentGroupIds,
    ownerBlockMap,
    ownerRefs,
    familyBlockIds,
  } = alignedBlock;
  const ownerGroupIdsJson = escapeHtml(JSON.stringify(presentGroupIds));
  const ownerBlockRefsJson = escapeHtml(JSON.stringify(familyBlockIds || []));
  const ownerBlockMapJson = escapeHtml(JSON.stringify(ownerBlockMap || {}));
  const ownerRefsJson = escapeHtml(JSON.stringify(ownerRefs || []));
  const distributionSummary = buildBlockDistributionSummary(alignedBlock, groups);

  if (isUniform || groups.length === 0) {
    return `
      <div class="mega-block"
           data-mega-block-id="${escapeHtml(blockId)}"
           data-mega-family-key="${escapeHtml(familyKey || blockId)}"
           data-mega-present-groups="${ownerGroupIdsJson}"
           data-mega-owner-block-map="${ownerBlockMapJson}">
        <div class="mega-block-header">${escapeHtml(displayBlockId || blockId)}</div>
        <div class="mega-block-distribution">${escapeHtml(distributionSummary)}</div>
        <div class="segment-common"
             data-owner-group-ids="${ownerGroupIdsJson}"
             data-owner-block-ids="${ownerBlockRefsJson}"
             data-owner-refs="${ownerRefsJson}">
          <div class="prompt-block-body"
               contenteditable="true"
               spellcheck="false"
               data-mega-block-id="${escapeHtml(blockId)}"
               data-segment-idx="0"
               data-mega-common="true">${plainTextToSimpleHtml(uniformText)}</div>
        </div>
      </div>
    `;
  }

  const segmentHtmls = safeArray(segments).map((seg, segIdx) => {
    const presentSet = new Set(seg.presentGroups || []);
    const segTextMap = seg.textMap || {};
    const segOwnerBlockMap = seg.ownerBlockMap || {};
    const segOwnerRefs = seg.ownerRefs || [];

    const groupItems = groups.map((group) => ({
      group,
      present: presentSet.has(group.group_id),
      text: segTextMap[group.group_id] || "",
    }));

    groupItems.sort((a, b) => {
      if (a.present !== b.present) return a.present ? -1 : 1;
      if (!a.present || !b.present) return 0;
      return String(a.text).localeCompare(String(b.text));
    });

    const items = [];
    let i = 0;
    while (i < groupItems.length) {
      const item = groupItems[i];
      if (!item.present) {
        items.push({ type: "empty", group: item.group });
        i++;
        continue;
      }
      const text = item.text;
      let j = i + 1;
      while (j < groupItems.length) {
        const nextItem = groupItems[j];
        if (!nextItem.present || nextItem.text !== text) break;
        j++;
      }
      if (j - i >= 2) {
        items.push({ type: "share", groups: groupItems.slice(i, j).map((gi) => gi.group), text });
        i = j;
      } else {
        items.push({ type: "diff", group: item.group, text });
        i++;
      }
    }

    const clusteredItems = [];
    let idx = 0;
    while (idx < items.length) {
      const item = items[idx];
      if (item.type !== "empty") {
        clusteredItems.push(item);
        idx++;
        continue;
      }
      const empties = [];
      while (idx < items.length && items[idx].type === "empty") {
        empties.push(items[idx]);
        idx++;
      }
      if (empties.length === 1) {
        clusteredItems.push(empties[0]);
      } else {
        clusteredItems.push({
          type: "empty-cluster",
          groups: empties.map((e) => e.group),
          count: empties.length,
          clusterId: `ec-${segIdx}-${Math.random().toString(36).slice(2, 9)}`,
        });
      }
    }

    const colsHtml = clusteredItems.map((item) => {
      if (item.type === "empty") {
        const gid = item.group.group_id;
        const itemOwnerRefs = segOwnerRefs.filter((r) => r.groupId === gid);
        const itemOwnerBlockIds = segOwnerBlockMap[gid] || [];
        return `
          <div class="diff-col diff-col-empty collapsed"
               style="flex-grow: 1;"
               data-group-id="${escapeHtml(gid)}"
               data-owner-group-ids="${escapeHtml(JSON.stringify([gid]))}"
               data-owner-block-ids="${escapeHtml(JSON.stringify(itemOwnerBlockIds))}"
               data-owner-refs="${escapeHtml(JSON.stringify(itemOwnerRefs))}">
            <div class="diff-col-label">${escapeHtml(item.group.variant_label || gid)}</div>
            <div class="prompt-block-body"
                 contenteditable="true"
                 spellcheck="false"
                 data-mega-block-id="${escapeHtml(blockId)}"
                 data-segment-idx="${segIdx}"
                 data-group-id="${escapeHtml(gid)}"
                 data-mega-diff="true"><p><br></p></div>
          </div>
        `;
      }
      if (item.type === "empty-cluster") {
        const clusterClass = item.clusterId;
        const collapsedHtml = `
          <div class="diff-col diff-col-empty diff-col-empty-cluster collapsed ${clusterClass}"
               style="flex-grow: 1;"
               data-empty-cluster-class="${escapeHtml(clusterClass)}"
               data-empty-cluster-groups="${escapeHtml(JSON.stringify(item.groups.map((g) => g.group_id)))}"
               data-empty-cluster-count="${item.count}">
            <div class="diff-col-label">${item.count}</div>
          </div>
        `;
        const expandedHtml = item.groups.map((g) => {
          const gid = g.group_id;
          const itemOwnerRefs = segOwnerRefs.filter((r) => r.groupId === gid);
          const itemOwnerBlockIds = segOwnerBlockMap[gid] || [];
          return `
            <div class="diff-col diff-col-empty ${clusterClass}"
                 style="flex-grow: 1; display: none;"
                 data-group-id="${escapeHtml(gid)}"
                 data-owner-group-ids="${escapeHtml(JSON.stringify([gid]))}"
                 data-owner-block-ids="${escapeHtml(JSON.stringify(itemOwnerBlockIds))}"
                 data-owner-refs="${escapeHtml(JSON.stringify(itemOwnerRefs))}">
              <div class="diff-col-label">${escapeHtml(g.variant_label || gid)}</div>
              <div class="prompt-block-body"
                   contenteditable="true"
                   spellcheck="false"
                   data-mega-block-id="${escapeHtml(blockId)}"
                   data-segment-idx="${segIdx}"
                   data-group-id="${escapeHtml(gid)}"
                   data-mega-diff="true"><p><br></p></div>
            </div>
          `;
        }).join("");
        return collapsedHtml + expandedHtml;
      }
      if (item.type === "diff") {
        const gid = item.group.group_id;
        const itemOwnerRefs = segOwnerRefs.filter((r) => r.groupId === gid);
        const itemOwnerBlockIds = segOwnerBlockMap[gid] || [];
        const label = item.group.variant_label || gid;
        return `
          <div class="diff-col diff-col-filled"
               style="flex-grow: 1;"
               data-group-id="${escapeHtml(gid)}"
               data-owner-group-ids="${escapeHtml(JSON.stringify([gid]))}"
               data-owner-block-ids="${escapeHtml(JSON.stringify(itemOwnerBlockIds))}"
               data-owner-refs="${escapeHtml(JSON.stringify(itemOwnerRefs))}">
            <div class="diff-col-label">${escapeHtml(label)}</div>
            <div class="prompt-block-body"
                 contenteditable="true"
                 spellcheck="false"
                 data-mega-block-id="${escapeHtml(blockId)}"
                 data-segment-idx="${segIdx}"
                 data-group-id="${escapeHtml(gid)}"
                 data-mega-diff="true">${plainTextToSimpleHtml(item.text)}</div>
          </div>
        `;
      }
      const shareGroupIds = item.groups.map((g) => g.group_id);
      const shareLabel = buildShareDistributionLabel(item.groups);
      const shareOwnerBlockIds = uniqueInOrder(item.groups.flatMap((g) => segOwnerBlockMap[g.group_id] || []));
      const shareOwnerRefs = segOwnerRefs.filter((r) => shareGroupIds.includes(r.groupId));
      return `
        <div class="diff-col diff-col-share"
             style="flex-grow: ${groups.length}; width: 0; min-width: 0;"
             data-share-groups="${escapeHtml(JSON.stringify(shareGroupIds))}"
             data-owner-group-ids="${escapeHtml(JSON.stringify(shareGroupIds))}"
             data-owner-block-ids="${escapeHtml(JSON.stringify(shareOwnerBlockIds))}"
             data-owner-refs="${escapeHtml(JSON.stringify(shareOwnerRefs))}">
          <div class="diff-col-label">${escapeHtml(shareLabel)}</div>
          <div class="prompt-block-body"
               contenteditable="true"
               spellcheck="false"
               data-mega-block-id="${escapeHtml(blockId)}"
               data-segment-idx="${segIdx}"
               data-share-groups="${escapeHtml(JSON.stringify(shareGroupIds))}"
               data-mega-diff="true">${plainTextToSimpleHtml(item.text)}</div>
        </div>
      `;
    }).join("");

    const familyBlockIdsForSeg = uniqueInOrder(Object.values(segOwnerBlockMap).flat());
    return `
      <div class="segment-diff"
           data-owner-group-ids="${escapeHtml(JSON.stringify(seg.presentGroups || []))}"
           data-owner-block-ids="${escapeHtml(JSON.stringify(familyBlockIdsForSeg))}">
        ${colsHtml}
      </div>
    `;
  });

  return `
    <div class="mega-block"
         data-mega-block-id="${escapeHtml(blockId)}"
         data-mega-family-key="${escapeHtml(familyKey || blockId)}"
         data-mega-present-groups="${ownerGroupIdsJson}"
         data-mega-owner-block-map="${ownerBlockMapJson}">
      <div class="mega-block-header">${escapeHtml(displayBlockId || blockId)}</div>
      <div class="mega-block-distribution">${escapeHtml(distributionSummary)}</div>
      ${segmentHtmls.join("")}
    </div>
  `;
}

function renderMegaCard(mega) {
  const cardId = getMegaCardId(mega.key);
  const title = mega.title || `match_pipe::${mega.key}`;
  const groupIdsJson = JSON.stringify(mega.groups.map((g) => g.group_id));
  return `
    <article class="mega-card" id="${cardId}" data-mega-groups="${escapeHtml(groupIdsJson)}">
      <header class="card-header">
        <div>
          <h3 class="card-title">${escapeHtml(title)}</h3>
          <div class="card-subtitle">${escapeHtml(mega.subtitle || `${mega.groups.length} variants`)}</div>
          <div class="pill-row">
            <span class="meta-pill">match_pipe</span>
            <span class="meta-pill">${escapeHtml(mega.badgeLabel || mega.label || "pair")}</span>
            <span class="meta-pill">${escapeHtml(mega.variantSummary || `${mega.groups.length} variants`)}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="secondary-button compact-button" type="button" data-action="save-mega" data-mega-key="${escapeHtml(mega.key)}" ${state.apiAvailable ? "" : "disabled"}>保存全部</button>
        </div>
      </header>
      <div class="mega-card-body">
        ${mega.alignedBlocks.map((b) => renderMegaBlock(b, mega.groups)).join("")}
      </div>
    </article>
  `;
}

function renderToc() {
  if (!elements.tocBody) return;
  const { megaCards, pairs } = getVisibleRenderContext();
  if (state.viewMode === "dedup") {
    const items = megaCards.map((card) => {
      const label = card.type === "mega"
        ? (card.label || `match_pipe::${card.key}`)
        : (card.label || card.title || card.group.pair_label || `${card.group.production_chain} / ${card.group.stage} / ${card.group.role}`);
      const firstId = card.type === "mega" ? getMegaCardId(card.key) : `card-${card.group.group_id}`;
      const active = state.activeTargetId === firstId;
      return `<button type="button" class="toc-item ${active ? "active-target" : ""}" data-jump-target="${escapeHtml(firstId)}">${escapeHtml(label)}</button>`;
    });
    elements.tocBody.innerHTML = items.join("");
    return;
  }
  const items = pairs.map((pair) => {
    const label = pair.map((g) => `${g.production_chain}::${g.stage}::${g.role}`).join(" / ");
    const firstId = `card-${pair[0].group_id}`;
    const active = state.activeTargetId === firstId || pair.some((g) => g.group_id === state.activeTargetId);
    return `<button type="button" class="toc-item ${active ? "active-target" : ""}" data-jump-target="${escapeHtml(firstId)}">${escapeHtml(label)}</button>`;
  });
  elements.tocBody.innerHTML = items.join("");
}

function _textLength(group) {
  return group.display_text?.length || group.blocks.map((b) => b.text?.length || 0).reduce((a, b) => a + b, 0);
}

function countChineseChars(text) {
  const m = String(text || "").match(/[\u4e00-\u9fff]/g);
  return m ? m.length : 0;
}

function getGroupChineseCount(group) {
  const draft = getDraft(group.group_id);
  return countChineseChars(draft?.displayText || group.display_text);
}

function getCardChineseCount(card) {
  if (card.type === "single") return getGroupChineseCount(card.group);
  return card.groups.reduce((sum, g) => sum + getGroupChineseCount(g), 0);
}

function _normalizedForSim(text) {
  return String(text || "").toLowerCase().replace(/\s+/g, " ").trim();
}

function _tokenSet(text) {
  const t = _normalizedForSim(text);
  const set = new Set();
  for (let i = 0; i < t.length - 1; i++) {
    set.add(t.slice(i, i + 2));
  }
  return set;
}

function _jaccard(a, b) {
  if (!a.size && !b.size) return 1;
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter++;
  return inter / (a.size + b.size - inter);
}

function _simScore(a, b) {
  const afp = a.blocks[0]?.duplicate_fingerprint || "";
  const bfp = b.blocks[0]?.duplicate_fingerprint || "";
  if (afp && afp === bfp) return 1.0;
  return _jaccard(_tokenSet(a.display_text), _tokenSet(b.display_text));
}

class UnionFind {
  constructor(items) {
    this.parent = new Map();
    for (const item of items) this.parent.set(item.group_id, item.group_id);
  }
  find(x) {
    if (this.parent.get(x) !== x) {
      this.parent.set(x, this.find(this.parent.get(x)));
    }
    return this.parent.get(x);
  }
  union(x, y) {
    const rx = this.find(x);
    const ry = this.find(y);
    if (rx !== ry) this.parent.set(rx, ry);
  }
}

function buildGroupClusters(groups, threshold = 0.82) {
  if (groups.length <= 1) return [groups];
  const uf = new UnionFind(groups);
  for (let i = 0; i < groups.length; i++) {
    for (let j = i + 1; j < groups.length; j++) {
      if (_simScore(groups[i], groups[j]) >= threshold) {
        uf.union(groups[i].group_id, groups[j].group_id);
      }
    }
  }
  const clusters = new Map();
  for (const g of groups) {
    const root = uf.find(g.group_id);
    if (!clusters.has(root)) clusters.set(root, []);
    clusters.get(root).push(g);
  }
  return [...clusters.values()].map((cluster) =>
    cluster.sort((a, b) => _textLength(b) - _textLength(a))
  ).sort((a, b) => _textLength(b[0]) - _textLength(a[0]));
}

function buildPairs(groups) {
  if (groups.length <= 2) return [groups];
  const remaining = groups.slice();
  const pairs = [];
  while (remaining.length > 0) {
    if (remaining.length === 1) {
      pairs.push([remaining.pop()]);
      break;
    }
    let bestI = 0;
    let bestJ = 1;
    let bestScore = -1;
    for (let i = 0; i < remaining.length; i++) {
      for (let j = i + 1; j < remaining.length; j++) {
        const score = _simScore(remaining[i], remaining[j]);
        if (score > bestScore) {
          bestScore = score;
          bestI = i;
          bestJ = j;
        }
      }
    }
    const a = remaining.splice(bestJ, 1)[0];
    const b = remaining.splice(bestI, 1)[0];
    const pair = [a, b].sort((x, y) => _textLength(y) - _textLength(x));
    pairs.push(pair);
  }
  pairs.sort((pa, pb) => {
    const la = Math.max(...pa.map(_textLength));
    const lb = Math.max(...pb.map(_textLength));
    return lb - la;
  });
  return pairs;
}

function renderCards() {
  const { visibleGroups, megaCards, pairs } = getVisibleRenderContext();
  if (state.viewMode === "dedup") {
    elements.cardList.classList.add("view-dedup");
    if (!megaCards.length) {
      elements.cardList.innerHTML = '<div class="empty-state">没有检测到可合并的 prompt group。</div>';
      elements.toolbarSummary.textContent = "0 个 mega card";
      return;
    }
    const megaCount = megaCards.filter((c) => c.type === "mega").length;
    const singleCount = megaCards.filter((c) => c.type === "single").length;
    elements.toolbarSummary.textContent = `${megaCount} 个 mega card · ${singleCount} 个 single`;
    elements.cardList.innerHTML = megaCards.map((card) =>
      card.type === "mega"
        ? renderMegaCard(card)
        : renderCard(card.group, {
            title: card.title || card.group.pair_label || card.group.group_label,
            subtitle: card.subtitle || `${card.group.prompt_kind} · ${card.variantSummary || card.group.variant_label || card.group.role}`,
            metaPills: [
              "match_pipe",
              card.badgeLabel || card.group.pair_scope_label || `${card.group.stage} / ${card.group.role}`,
              card.variantSummary || card.group.variant_label || (card.group.is_bytedance ? "ByteDance" : "generic"),
              `blocks ${card.group.blocks.length}`,
            ],
          })
    ).join("");
    return;
  }
  elements.cardList.classList.remove("view-dedup");
  if (!visibleGroups.length) {
    elements.cardList.innerHTML = '<div class="empty-state">当前筛选条件下没有匹配的 prompt group。</div>';
    elements.toolbarSummary.textContent = "0 个 group 可见。";
    return;
  }
  elements.toolbarSummary.textContent = `${visibleGroups.length} / ${state.groups.length} 个 group 可见`;
  visibleGroups.sort((a, b) => getGroupChineseCount(b) - getGroupChineseCount(a));
  pairs.sort((pa, pb) => {
    const ca = Math.max(...pa.map(getGroupChineseCount));
    const cb = Math.max(...pb.map(getGroupChineseCount));
    return cb - ca;
  });
  const ordered = pairs.flat();
  elements.cardList.innerHTML = ordered.map(renderCard).join("");
}

function renderCoverage() {
  const coverage = unwrapCoveragePayload(state.coverage);
  if (!coverage) {
    elements.coverageBody.innerHTML = '<div class="empty-state">未加载 coverage.report。</div>';
    return;
  }
  elements.coverageBody.innerHTML = `
    <div>覆盖率：<strong>${escapeHtml(formatRatio(coverage.coverage_ratio ?? 0))}</strong></div>
    <div>source item：${escapeHtml(coverage.source_item_count ?? coverage.total_source_item_count ?? 0)} / covered ${escapeHtml(
      coverage.covered_source_item_count ?? coverage.covered_count ?? 0,
    )}</div>
    <div>未覆盖：${escapeHtml(safeArray(coverage.uncovered).length)}</div>
    <div>低置信：${escapeHtml(safeArray(coverage.low_confidence).length)}</div>
    <div>镜像集群：${escapeHtml(safeArray(coverage.mirrors).length)}</div>
  `;
}

function renderAmbiguities() {
  const payload = unwrapAmbiguityPayload(state.ambiguities);
  const items = safeArray(payload?.items || payload);
  if (!items.length) {
    elements.ambiguityBody.innerHTML = '<div class="empty-state">当前没有歧义项。</div>';
    return;
  }
  elements.ambiguityBody.innerHTML = items
    .slice(0, 8)
    .map(
      (item) => `
        <div class="revision-item">
          <div class="revision-id">${escapeHtml(item.ambiguity_id || item.id || "ambiguity")}</div>
          <div>${escapeHtml(item.group_id || "")}</div>
          <div>${escapeHtml(item.reason || "")}</div>
        </div>
      `,
    )
    .join("");
}

function renderConflicts() {
  const conflict = unwrapConflictPayload(state.conflicts);
  if (!conflict || !conflict.frozen) {
    elements.conflictBody.innerHTML = '<div class="empty-state">当前没有 active conflict，系统不在冻结态。</div>';
    return;
  }
  elements.conflictBody.innerHTML = `
    <div><strong>冻结原因：</strong>${escapeHtml(conflict.reason || "unknown")}</div>
    <div><strong>触发 revision：</strong>${escapeHtml(conflict.trigger_revision_id || "unknown")}</div>
    <div><strong>影响 group：</strong>${escapeHtml(safeArray(conflict.affected_groups).join("、") || "未提供")}</div>
    <div><strong>下一步：</strong>${escapeHtml(conflict.next_action || "human_review_required")}</div>
  `;
}

function renderRevisions() {
  if (!state.revisions.length) {
    elements.revisionsList.innerHTML = '<div class="empty-state">当前没有 revision 列表。</div>';
    return;
  }
  elements.revisionsList.innerHTML = state.revisions
    .slice()
    .sort((left, right) => String(right.timestamp || "").localeCompare(String(left.timestamp || "")))
    .map((revision) => {
      const isHead = revision.revision_id === state.headRevisionId;
      const patchCount = safeArray(revision.patch_ids).length;
      return `
        <div class="revision-item">
          <div class="revision-head">
            <div class="revision-id">${escapeHtml(revision.revision_id || "unknown")}</div>
            ${isHead ? '<span class="meta-pill status-edited">HEAD</span>' : ""}
          </div>
          <div class="revision-meta">${escapeHtml(formatTime(revision.timestamp))}</div>
          <div class="revision-meta">trigger: ${escapeHtml(revision.trigger || "unknown")} · patches ${escapeHtml(patchCount)}</div>
          <button class="secondary-button compact-button" type="button" data-action="restore" data-revision-id="${escapeHtml(
            revision.revision_id || "",
          )}" ${state.apiAvailable ? "" : "disabled"}>恢复到此版本</button>
        </div>
      `;
    })
    .join("");
}

function persistDraftCache() {
  const payload = {};
  state.drafts.forEach((draft, key) => {
    payload[key] = draft;
  });
  try {
    localStorage.setItem(CONFIG.localCacheKey, JSON.stringify(payload));
  } catch (error) {
    console.warn("failed to persist draft cache", error);
  }
}

function loadDraftCache() {
  try {
    const raw = localStorage.getItem(CONFIG.localCacheKey);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    Object.entries(parsed).forEach(([groupId, draft]) => {
      if (!draft || typeof draft !== "object") return;
      state.drafts.set(groupId, draft);
    });
  } catch (error) {
    console.warn("failed to load draft cache", error);
  }
}

function clearDraft(groupId) {
  state.drafts.delete(groupId);
  state.failedGroups.delete(groupId);
  persistDraftCache();
}

function setDraft(groupId, draft) {
  state.drafts.set(groupId, draft);
  persistDraftCache();
}

function extractBlockPayloads(editorEl, group) {
  return [...editorEl.querySelectorAll(".prompt-block")].map((blockEl, index) => {
    const blockId = blockEl.dataset.blockId || group.blocks[index]?.block_id || `block-${index + 1}`;
    const bodyEl = blockEl.querySelector(".prompt-block-body");
    const bodyHtml = sanitizeRichHtml(bodyEl?.innerHTML || "<p><br></p>");
    const block = group.blocks.find((item) => item.block_id === blockId);
    return {
      block_id: blockId,
      html: bodyHtml,
      rich_text: bodyHtml,
      text: htmlToPlainText(bodyHtml),
      source_refs: block?.source_refs || [],
      write_policy: block?.write_policy || "",
      merge_rule: block?.merge_rule || "",
      propagation_rule: block?.propagation_rule || "",
      confidence: block?.confidence ?? null,
    };
  });
}

function buildDraftSnapshotFromHtml(group, html) {
  const sanitizedHtml = sanitizeRichHtml(html || "");
  const editorEl = document.createElement("div");
  editorEl.className = "prompt-editor";
  editorEl.innerHTML = sanitizedHtml;
  const extractedBlocks = extractBlockPayloads(editorEl, group);
  const existingBlocksById = new Map(safeArray(group.blocks).map((block) => [block.block_id, block]));
  const blocks = extractedBlocks.map((payload) => {
    const existing = existingBlocksById.get(payload.block_id) || {};
    return {
      ...existing,
      ...payload,
    };
  });
  const displayText = htmlToPlainText(sanitizedHtml);
  const searchBlob = [
    group.group_label,
    group.production_chain,
    group.stage,
    group.role,
    displayText,
    safeArray(group.source_paths).join(" "),
    blocks.map((block) => [block.block_id, block.text, block.notes].join(" ")).join(" "),
  ]
    .join("\n")
    .toLowerCase();
  return {
    html: sanitizedHtml,
    displayText,
    blocks,
    blockOrder: blocks.map((item) => item.block_id),
    searchBlob,
  };
}

function applyDraftSnapshotToGroup(group, snapshot) {
  group.editable_rich_text = snapshot.html;
  group.display_text = snapshot.displayText;
  group.blocks = snapshot.blocks.map((block) => ({ ...block }));
  group.search_blob = snapshot.searchBlob;
}

function captureEditorState(groupId) {
  const cardEl = document.querySelector(`[data-group-id="${CSS.escape(groupId)}"]`);
  if (!cardEl) return null;
  const group = state.groupMap.get(groupId);
  if (!group) return null;
  const editorEl = cardEl.querySelector(".prompt-editor");
  if (!editorEl) return null;

  [...editorEl.querySelectorAll(".prompt-block-meta")].forEach((node) => node.setAttribute("contenteditable", "false"));
  [...editorEl.querySelectorAll(".prompt-block-body")].forEach((node) => {
    node.setAttribute("contenteditable", "true");
    node.setAttribute("spellcheck", "false");
  });

  const html = sanitizeRichHtml(editorEl.innerHTML);
  const displayText = htmlToPlainText(html);
  const blockPayloads = extractBlockPayloads(editorEl, group);
  return {
    html,
    displayText,
    blocks: blockPayloads,
    blockOrder: blockPayloads.map((item) => item.block_id),
    updatedAt: new Date().toISOString(),
  };
}

function queueAutosave(groupId) {
  const existing = state.saveTimers.get(groupId);
  if (existing) window.clearTimeout(existing);
  const timer = window.setTimeout(() => {
    state.saveTimers.delete(groupId);
    saveGroup(groupId)
      .then(async () => {
        await saveAllDirtyGroups();
      })
      .catch((error) => {
        console.error("autosave failed", error);
      });
  }, CONFIG.autosaveDelayMs || 900);
  state.saveTimers.set(groupId, timer);
}

async function saveGroup(groupId) {
  const group = state.groupMap.get(groupId);
  const draft = getDraft(groupId);
  if (!group || !draft?.dirty) return;
  if (!state.apiAvailable) {
    updateAutosaveBadge();
    return;
  }
  state.savingGroups.add(groupId);
  state.failedGroups.delete(groupId);
  updateAutosaveBadge();
  refreshCardChrome(groupId);
  try {
    const payload = {
      group_id: group.group_id,
      editable_rich_text: draft.html,
      display_text: draft.displayText,
      blocks: draft.blocks,
      client_revision_id: state.headRevisionId,
      editor_meta: {
        group_label: group.group_label,
        production_chain: group.production_chain,
        stage: group.stage,
        role: group.role,
        block_order: draft.blockOrder,
        client_saved_at: new Date().toISOString(),
        editor_version: CONFIG.editorVersion,
        local_cache_used: true,
      },
    };
    const response = await fetchJson(CONFIG.endpoints.save, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (response && response.ok === false) {
      throw new JsonResponseError(response.error || "save failed", response, 200);
    }
    group.editable_rich_text = draft.html;
    group.display_text = draft.displayText;
    group.status = "edited";
    const responseGroup = response.group || response.edited_group || response.updated_group || null;
    if (responseGroup?.editable_rich_text) {
      group.editable_rich_text = buildEditorHtml(responseGroup, buildBlocksFromMap(responseGroup, state.mapByGroupId.get(group.group_id)));
      group.display_text = responseGroup.display_text || htmlToPlainText(group.editable_rich_text);
    }
    const syncedSnapshot = buildDraftSnapshotFromHtml(group, group.editable_rich_text);
    group.blocks = syncedSnapshot.blocks.map((block) => ({ ...block }));
    group.search_blob = syncedSnapshot.searchBlob;
    const newRevisionId = response.new_revision_id || response.head_revision_id || response.revision_id;
    if (newRevisionId) state.headRevisionId = newRevisionId;
    if (response.frozen !== undefined) state.frozen = Boolean(response.frozen);
    clearDraft(groupId);
    setStatus(`已保存 ${group.group_label}`);
    if (response.revisions) {
      state.revisions = normalizeRevisionPayload(response.revisions);
    } else {
      await loadRevisions();
    }
    if (response.conflicts || response.conflict) {
      state.conflicts = unwrapConflictPayload(response.conflicts || response.conflict);
      state.frozen = Boolean(state.conflicts?.frozen);
    } else {
      await loadConflicts();
    }
  } catch (error) {
    if (error instanceof JsonResponseError && error.payload) {
      const conflict = unwrapConflictPayload(error.payload.conflict || error.payload.conflicts || error.payload);
      if (conflict) {
        state.conflicts = conflict;
        state.frozen = Boolean(conflict.frozen);
      }
    }
    state.failedGroups.set(groupId, error instanceof Error ? error.message : "保存失败");
    setStatus(`保存失败：${group.group_label}`);
  } finally {
    state.savingGroups.delete(groupId);
    updateAutosaveBadge();
    updateFreezeBadge();
    collectHeroStats();
    refreshCardChrome(groupId);
    renderRevisions();
    renderConflicts();
  }
}

async function saveAllDirtyGroups() {
  const dirtyIds = [...state.drafts.entries()].filter(([, draft]) => draft.dirty).map(([groupId]) => groupId);
  for (const groupId of dirtyIds) {
    await saveGroup(groupId);
  }
}

async function restoreRevision(revisionId) {
  if (!state.apiAvailable || !revisionId) return;
  setStatus(`正在恢复 ${revisionId}`);
  try {
    const response = await fetchJson(CONFIG.endpoints.restore, {
      method: "POST",
      body: JSON.stringify({
        revision_id: revisionId,
        client_revision_id: state.headRevisionId,
        trigger: "frontend_restore",
      }),
    });
    if (response && response.ok === false) {
      throw new JsonResponseError(response.error || "restore failed", response, 200);
    }
    if (response.head_revision_id) state.headRevisionId = response.head_revision_id;
    state.drafts.clear();
    persistDraftCache();
    await loadAll();
    setStatus(`已恢复到 ${revisionId}`);
  } catch (error) {
    if (error instanceof JsonResponseError && error.payload) {
      const conflict = unwrapConflictPayload(error.payload.conflict || error.payload.conflicts || error.payload);
      if (conflict) {
        state.conflicts = conflict;
        state.frozen = Boolean(conflict.frozen);
        renderConflicts();
        updateFreezeBadge();
      }
    }
    setStatus(error instanceof Error ? error.message : "restore 失败");
  }
}

async function loadRevisions() {
  const payload = await tryFetchJson(CONFIG.endpoints.revisions);
  if (payload) {
    state.revisions = normalizeRevisionPayload(payload);
    return;
  }
  const fallback = await tryFetchJson(CONFIG.fallbackFiles.revisions);
  state.revisions = normalizeRevisionPayload(fallback);
}

async function loadConflicts() {
  const payload = await tryFetchJson(CONFIG.endpoints.conflicts);
  if (payload) {
    state.conflicts = unwrapConflictPayload(payload);
    state.frozen = Boolean(state.conflicts?.frozen);
    return;
  }
  const fallback = await tryFetchJson(CONFIG.fallbackFiles.conflicts);
  state.conflicts = unwrapConflictPayload(fallback);
  state.frozen = Boolean(state.conflicts?.frozen);
}

async function loadCoverage() {
  const payload = await tryFetchJson(CONFIG.endpoints.coverage);
  if (payload) {
    state.coverage = unwrapCoveragePayload(payload);
    return;
  }
  state.coverage = unwrapCoveragePayload(await tryFetchJson(CONFIG.fallbackFiles.coverage));
}

async function loadAmbiguities() {
  const payload = await tryFetchJson(CONFIG.endpoints.ambiguities);
  if (payload) {
    state.ambiguities = unwrapAmbiguityPayload(payload);
    return;
  }
  state.ambiguities = unwrapAmbiguityPayload(await tryFetchJson(CONFIG.fallbackFiles.ambiguities));
}

function applyCachedDrafts() {
  state.groups.forEach((group) => {
    const draft = state.drafts.get(group.group_id);
    if (!draft) return;
    if (draft.baseRevisionId && state.headRevisionId && draft.baseRevisionId !== state.headRevisionId) return;
    if (draft.html) {
      group.editable_rich_text = sanitizeRichHtml(draft.html);
      group.display_text = draft.displayText || htmlToPlainText(group.editable_rich_text);
    }
  });
}

async function loadReviewBundle() {
  const apiPayload = await tryFetchJson(CONFIG.endpoints.review);
  if (apiPayload) {
    updateConnectionBadge(true);
    const reviewDoc = unwrapReviewPayload(apiPayload.review || apiPayload.edited || apiPayload);
    const mapDoc = unwrapMapPayload(apiPayload.map || (await tryFetchJson(CONFIG.fallbackFiles.map)) || {});
    state.meta = {
      ...safeObject(apiPayload.meta),
      baseline_path: apiPayload.baseline_path || "",
      files: safeObject(apiPayload.files),
    };
    state.headRevisionId =
      apiPayload.head_revision_id ||
      reviewDoc.head_revision_id ||
      apiPayload.revisions?.head_revision_id ||
      state.meta.head_revision_id ||
      state.headRevisionId;
    state.groups = mergeMapEntries(reviewDoc, mapDoc);
    state.groupsVersion += 1;
    state.mapByGroupId = new Map(safeArray(unwrapMapPayload(mapDoc).groups).map((entry) => [entry.group_id, entry]));
    if (apiPayload.revisions) state.revisions = normalizeRevisionPayload(apiPayload.revisions);
    if (apiPayload.conflict || apiPayload.conflicts) {
      state.conflicts = unwrapConflictPayload(apiPayload.conflict || apiPayload.conflicts);
      state.frozen = Boolean(state.conflicts?.frozen);
    }
    if (apiPayload.coverage) state.coverage = unwrapCoveragePayload(apiPayload.coverage);
    if (apiPayload.ambiguities) state.ambiguities = unwrapAmbiguityPayload(apiPayload.ambiguities);
    return;
  }
  updateConnectionBadge(false);
  const reviewDoc = unwrapReviewPayload((await tryFetchJson(CONFIG.fallbackFiles.review)) || {});
  const mapDoc = unwrapMapPayload((await tryFetchJson(CONFIG.fallbackFiles.map)) || {});
  state.meta = safeObject(reviewDoc.meta);
  state.headRevisionId = reviewDoc.head_revision_id || state.meta.head_revision_id || state.headRevisionId;
  state.groups = mergeMapEntries(reviewDoc, mapDoc);
  state.groupsVersion += 1;
  state.mapByGroupId = new Map(safeArray(unwrapMapPayload(mapDoc).groups).map((entry) => [entry.group_id, entry]));
}

function runConsistencyCheck() {
  let issues = 0;
  for (const [fp, refs] of state.fingerprintIndex.entries()) {
    if (refs.length <= 1) continue;
    const texts = [];
    for (const ref of refs) {
      const draft = getDraft(ref.group_id);
      const group = state.groupMap.get(ref.group_id);
      if (!group) continue;
      const baseHtml = draft?.html || group.editable_rich_text || "";
      const template = document.createElement("template");
      template.innerHTML = sanitizeRichHtml(baseHtml);
      const blockEl = template.content.querySelector(`[data-block-id="${CSS.escape(ref.block_id)}"] .prompt-block-body`);
      const text = htmlToPlainText(blockEl?.innerHTML || "");
      texts.push({ group_id: ref.group_id, text });
    }
    const first = texts[0]?.text;
    const mismatch = texts.filter((t) => t.text !== first);
    if (mismatch.length) {
      issues++;
      for (const m of mismatch) {
        const cardEl = document.querySelector(`[data-group-id="${CSS.escape(m.group_id)}"]`);
        if (cardEl) {
          const slot = cardEl.querySelector(".card-message-slot");
          if (slot && !slot.querySelector(".consistency-warning")) {
            const warn = document.createElement("div");
            warn.className = "card-banner error consistency-warning";
            warn.textContent = `一致性警告：此 group 中 block 的文本与其 fingerprint 聚类中的其他 ${texts.length - 1} 个引用不一致。`;
            slot.appendChild(warn);
          }
        }
      }
    }
  }
  if (issues) {
    setStatus(`一致性检查完成：发现 ${issues} 个不一致的重复聚类。`);
  } else {
    setStatus("一致性检查完成：所有重复聚类的内容完全一致。");
  }
}

function bindStaticEvents() {
  elements.searchInput.addEventListener("input", (event) => {
    state.search = String(event.target.value || "");
    renderToc();
    renderCards();
  });
  elements.chainFilter.addEventListener("change", (event) => {
    state.filters.chain = String(event.target.value || "");
    renderToc();
    renderCards();
  });
  elements.stageFilter.addEventListener("change", (event) => {
    state.filters.stage = String(event.target.value || "");
    renderToc();
    renderCards();
  });
  elements.roleFilter.addEventListener("change", (event) => {
    state.filters.role = String(event.target.value || "");
    renderToc();
    renderCards();
  });
  elements.refreshButton.addEventListener("click", () => {
    loadAll().catch((error) => {
      setStatus(error instanceof Error ? error.message : "刷新失败");
    });
  });
  elements.saveAllButton.addEventListener("click", () => {
    saveAllDirtyGroups().catch((error) => {
      setStatus(error instanceof Error ? error.message : "批量保存失败");
    });
  });
  elements.reloadRevisionsButton.addEventListener("click", () => {
    loadRevisions()
      .then(renderRevisions)
      .catch((error) => setStatus(error instanceof Error ? error.message : "revision 刷新失败"));
  });

  if (elements.viewModeTiles) {
    elements.viewModeTiles.addEventListener("click", () => {
      state.viewMode = "tiles";
      elements.viewModeTiles.classList.add("active");
      elements.viewModeDedup?.classList.remove("active");
      renderToc();
      renderCards();
    });
  }
  if (elements.viewModeDedup) {
    elements.viewModeDedup.addEventListener("click", () => {
      state.viewMode = "dedup";
      elements.viewModeDedup.classList.add("active");
      elements.viewModeTiles?.classList.remove("active");
      renderToc();
      renderCards();
    });
  }

  if (elements.checkConsistencyButton) {
    elements.checkConsistencyButton.addEventListener("click", () => {
      runConsistencyCheck();
    });
  }
  if (elements.showAllChainsButton) {
    elements.showAllChainsButton.addEventListener("click", () => {
      state.showAllChains = !state.showAllChains;
      elements.showAllChainsButton.textContent = state.showAllChains ? "仅显示 match_pipe" : "显示全部链路";
      elements.showAllChainsButton.classList.toggle("active", state.showAllChains);
      renderToc();
      renderCards();
    });
  }
  if (elements.sideRailToggle && elements.sideRail) {
    elements.sideRailToggle.addEventListener("click", () => {
      const closed = elements.sideRail.classList.toggle("closed");
      elements.sideRailToggle.textContent = closed ? "☰" : "✕";
      elements.sideRailToggle.title = closed ? "打开边栏" : "关闭边栏";
    });
  }
  if (elements.tocRail) {
    elements.tocRail.addEventListener("click", (event) => {
      const item = event.target.closest("[data-jump-target]");
      if (!item) return;
      const targetId = item.dataset.jumpTarget;
      const target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  document.addEventListener("click", (event) => {
    const badge = event.target.closest(".shared-badge");
    if (badge) {
      event.stopPropagation();
      const fp = badge.dataset.sharedFp;
      if (fp) showTooltip(badge, fp);
      return;
    }
    if (!event.target.closest("#shared-tooltip")) {
      removeTooltip();
    }
  });

  elements.writebackButton.addEventListener("click", async () => {
    try {
      setStatus("正在执行 writeback dry-run...");
      const dryRunReport = await fetchJson(CONFIG.endpoints.writeback, {
        method: "POST",
        body: JSON.stringify({ dry_run: true, force_docs: false }),
      });
      const patched = dryRunReport.patched_count || 0;
      const blocked = dryRunReport.blocked_count || 0;
      const errors = dryRunReport.error_count || 0;
      const lines = [
        `Dry-run 结果: 可写回 ${patched} 个, 被阻止 ${blocked} 个, 错误 ${errors} 个。`,
        blocked > 0 ? "被阻止项包含 python_function / inline_string / source_reference 等暂不支持自动回写的类型。" : "",
        errors > 0 ? "存在错误，建议先查看日志。" : "",
        "确认要执行真正的 source writeback 吗？",
      ].filter(Boolean);
      const confirmed = window.confirm(lines.join("\n"));
      if (!confirmed) {
        setStatus("已取消 writeback。");
        return;
      }
      setStatus("正在执行 source writeback...");
      const report = await fetchJson(CONFIG.endpoints.writeback, {
        method: "POST",
        body: JSON.stringify({ dry_run: false, force_docs: false }),
      });
      const finalPatched = report.patched_count || 0;
      const finalBlocked = report.blocked_count || 0;
      const finalErrors = report.error_count || 0;
      setStatus(`Writeback 完成: 成功 ${finalPatched} 个, 被阻止 ${finalBlocked} 个, 错误 ${finalErrors} 个。`);
      if (report.ok && finalErrors === 0) {
        updateConnectionBadge(true);
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "writeback 失败");
    }
  });

  elements.cardList.addEventListener("input", (event) => {
    const body = event.target.closest(".prompt-block-body");
    if (!body) return;

    if (body.closest(".mega-card")) {
      if (handleMegaCardInput(body)) return;
    }

    const cardEl = event.target.closest("[data-group-id]");
    if (!cardEl) return;
    const groupId = cardEl.dataset.groupId;
    const blockEl = body.closest(".prompt-block");
    const blockId = blockEl?.dataset.blockId || "";
    const snapshot = captureEditorState(groupId);
    if (!snapshot) return;
    setDraft(groupId, {
      html: snapshot.html,
      displayText: snapshot.displayText,
      blocks: snapshot.blocks,
      blockOrder: snapshot.blockOrder,
      updatedAt: snapshot.updatedAt,
      dirty: true,
      baseRevisionId: state.headRevisionId,
    });
    state.failedGroups.delete(groupId);
    updateAutosaveBadge();
    collectHeroStats();
    refreshCardChrome(groupId);
    if (blockId) syncDraftToSharedBlocks(groupId, blockId);
    queueAutosave(groupId);
  });

  elements.cardList.addEventListener("click", (event) => {
    const emptyCluster = event.target.closest(".diff-col-empty-cluster");
    if (emptyCluster) {
      const clusterClass = emptyCluster.dataset.emptyClusterClass;
      if (clusterClass) {
        emptyCluster.style.display = "none";
        const segmentDiff = emptyCluster.closest(".segment-diff");
        if (segmentDiff) {
          segmentDiff.querySelectorAll(`.${clusterClass}`).forEach((el) => {
            if (el !== emptyCluster) {
              el.style.display = "flex";
            }
          });
        }
      }
      event.stopPropagation();
      return;
    }

    const emptyCol = event.target.closest(".diff-col-empty");
    if (emptyCol) {
      emptyCol.classList.toggle("collapsed");
      const lane = emptyCol.closest(".diff-pair-lane");
      if (lane) {
        const cols = lane.querySelectorAll(":scope > .diff-col");
        const allCollapsed = [...cols].every((c) => c.classList.contains("collapsed"));
        lane.classList.toggle("collapsed", allCollapsed);
      }
      event.stopPropagation();
      return;
    }
  });

  elements.cardList.addEventListener("click", async (event) => {
    const jumpBtn = event.target.closest("[data-jump-group]");
    if (jumpBtn) {
      const groupId = jumpBtn.dataset.jumpGroup;
      state.activeTargetId = groupId;
      renderToc();
      const cardEl = document.getElementById(`card-${groupId}`);
      if (cardEl) cardEl.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) return;
    const action = actionButton.dataset.action;
    if (action === "jump") {
      const groupId = actionButton.dataset.groupId;
      state.activeTargetId = groupId;
      renderToc();
      const cardEl = document.getElementById(`card-${groupId}`);
      if (cardEl) cardEl.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    if (action === "save") {
      const groupId = actionButton.dataset.groupId;
      const snapshot = captureEditorState(groupId);
      if (snapshot) {
        setDraft(groupId, {
          html: snapshot.html,
          displayText: snapshot.displayText,
          blocks: snapshot.blocks,
          blockOrder: snapshot.blockOrder,
          updatedAt: snapshot.updatedAt,
          dirty: true,
          baseRevisionId: state.headRevisionId,
        });
      }
      saveGroup(groupId)
        .then(async () => {
          await saveAllDirtyGroups();
        })
        .catch((error) => {
          setStatus(error instanceof Error ? error.message : "保存失败");
        });
      return;
    }
    if (action === "save-mega") {
      const megaKey = actionButton.dataset.megaKey;
      const megaCard = document.getElementById(getMegaCardId(megaKey));
      if (megaCard) {
        const groupIds = getMegaCardGroupIds(megaCard);
        for (const gid of groupIds) {
          const draft = getDraft(gid);
          if (draft?.dirty) {
            await saveGroup(gid).catch(() => {});
          }
        }
        await saveAllDirtyGroups().catch((error) => {
          setStatus(error instanceof Error ? error.message : "保存失败");
        });
      }
      return;
    }
    if (action === "restore") {
      const revisionId = actionButton.dataset.revisionId;
      restoreRevision(revisionId).catch((error) => {
        setStatus(error instanceof Error ? error.message : "restore 失败");
      });
    }
  });
}

async function loadAll() {
  setStatus("正在加载 prompt review 数据。");
  await loadReviewBundle();
  await Promise.all([loadRevisions(), loadConflicts(), loadCoverage(), loadAmbiguities()]);
  state.groupMap = new Map(state.groups.map((group) => [group.group_id, group]));
  const { fingerprintIndex, blockFingerprintMap } = buildFingerprintIndex(state.groups);
  state.fingerprintIndex = fingerprintIndex;
  state.blockFingerprintMap = blockFingerprintMap;
  applyCachedDrafts();
  renderFilters();
  collectHeroStats();
  updateFreezeBadge();
  updateAutosaveBadge();
  syncGlobalButtons();
  if (elements.showAllChainsButton) {
    elements.showAllChainsButton.textContent = state.showAllChains ? "仅显示 match_pipe" : "显示全部链路";
    elements.showAllChainsButton.classList.toggle("active", state.showAllChains);
  }
  renderToc();
  renderCards();
  renderCoverage();
  renderAmbiguities();
  renderConflicts();
  renderRevisions();
  setStatus(state.apiAvailable ? "已加载后端 prompt review 数据。" : "后端未提供 prompt review API，当前仅加载本地 sidecar 文件。");
}

loadDraftCache();
bindStaticEvents();
loadAll().catch((error) => {
  console.error(error);
  updateConnectionBadge(false);
  updateAutosaveBadge();
  setStatus(error instanceof Error ? error.message : "加载失败");
  elements.cardList.innerHTML = '<div class="empty-state">prompt review 页面加载失败。请检查 JSON sidecar 或后端 API。</div>';
  renderCoverage();
  renderAmbiguities();
  renderConflicts();
  renderRevisions();
});
