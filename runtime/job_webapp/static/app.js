const AUTO_REFRESH_MS = 60_000;
const FILTER_ORDER = ["company_size", "salary", "company", "title", "yoe", "review", "status", "discovered", "published"];

function companySizeLabel(job) {
  if (job.company_size_label) return job.company_size_label;
  const raw = String(job.company_size || "").trim();
  if (raw === "10001+ employees" || raw === "5001-10000 employees") return "大厂(10000+)";
  if (raw === "1001-5000 employees") return "中厂(1001-5000)";
  if (raw === "501-1000 employees") return "中厂(501-1000)";
  if (
    raw === "201-500 employees" ||
    raw === "51-200 employees" ||
    raw === "11-50 employees" ||
    raw === "2-10 employees"
  ) {
    return "小厂(≤500)";
  }
  return "未知";
}

function salaryLabel(job) {
  if (job.salary_label) return job.salary_label;
  const raw = Number(job.min_salary || 0);
  if (raw >= 200000) return "≥200K";
  if (raw >= 150000) return "150-200K";
  if (raw >= 100000) return "100-150K";
  if (raw > 0) return "<100K";
  return "未标薪资";
}

const FILTERS = {
  company_size: {
    label: "公司规模",
    getValue: (job) => companySizeLabel(job),
    sort: (a, b) => {
      const order = ["大厂(10000+)", "中厂(1001-5000)", "中厂(501-1000)", "小厂(≤500)", "未知"];
      const ia = order.indexOf(a) === -1 ? 99 : order.indexOf(a);
      const ib = order.indexOf(b) === -1 ? 99 : order.indexOf(b);
      return ia - ib;
    },
  },
  salary: {
    label: "薪资范围",
    getValue: (job) => salaryLabel(job),
    sort: (a, b) => {
      const order = ["≥200K", "150-200K", "100-150K", "<100K", "未标薪资"];
      const ia = order.indexOf(a) === -1 ? 99 : order.indexOf(a);
      const ib = order.indexOf(b) === -1 ? 99 : order.indexOf(b);
      return ia - ib;
    },
  },
  company: {
    label: "公司名称",
    getValue: (job) => job.company_name || "Unknown",
    sort: (a, b) => a.localeCompare(b, "en", { sensitivity: "base" }),
  },
  title: {
    label: "岗位类别",
    getValue: (job) => job.title_class || "Other",
    sort: (a, b) => {
      const order = ["SWE", "ML/AI", "PM", "Data", "Other"];
      return order.indexOf(a) - order.indexOf(b);
    },
  },
  yoe: {
    label: "YOE",
    getValue: (job) => job.yoe_label || "Unknown",
    sort: (a, b) => {
      if (a === "Unknown") return 1;
      if (b === "Unknown") return -1;
      return Number(a) - Number(b);
    },
  },
  discovered: {
    label: "发现日期",
    getValue: (job) => job.discovered_date || "",
    sort: (a, b) => b.localeCompare(a),
  },
  published: {
    label: "发布日期",
    getValue: (job) => job.publish_date || "",
    sort: (a, b) => b.localeCompare(a),
  },
  review: {
    label: "Review 状态",
    getValue: (job) => job.review_status || "未review",
    sort: (a, b) => {
      const order = ["pass", "conditional_pass", "fail", "reject", "未review", "无简历"];
      const ia = order.indexOf(a) === -1 ? 99 : order.indexOf(a);
      const ib = order.indexOf(b) === -1 ? 99 : order.indexOf(b);
      return ia - ib;
    },
  },
  status: {
    label: "Status",
    getValue: (job) => normalizeApplyUrlStatus(job),
    sort: (a, b) => {
      const order = ["open", "closed", "unknown"];
      const ia = order.indexOf(a) === -1 ? 99 : order.indexOf(a);
      const ib = order.indexOf(b) === -1 ? 99 : order.indexOf(b);
      return ia - ib;
    },
  },
};

const state = {
  jobs: [],
  filteredJobs: [],
  selections: Object.fromEntries(FILTER_ORDER.map((key) => [key, new Set()])),
  searches: Object.fromEntries(FILTER_ORDER.map((key) => [key, ""])),
  updatedAt: "",
  meta: {},
  monitor: {
    processes: [],
    presets: [],
    meta: {},
    generatedAt: "",
  },
  isRefreshing: false,
  sort: {
    key: "",
    direction: "",
  },
};

const monitorBoard = document.getElementById("monitorBoard");
const monitorMeta = document.getElementById("monitorMeta");
const summaryCards = document.getElementById("summaryCards");
const resultSummary = document.getElementById("resultSummary");
const updatedAt = document.getElementById("updatedAt");
const filterGrid = document.getElementById("filterGrid");
const jobTableBody = document.getElementById("jobTableBody");
const filterTemplate = document.getElementById("filterTemplate");
const clearAllBtn = document.getElementById("clearAllBtn");
const refreshBtn = document.getElementById("refreshBtn");
const sortButtons = [...document.querySelectorAll(".sort-button")];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function filterRows(rows, filterKeys) {
  return rows.filter((job) =>
    filterKeys.every((key) => {
      const selected = state.selections[key];
      if (!selected || selected.size === 0) return true;
      return selected.has(FILTERS[key].getValue(job));
    }),
  );
}

function getOptionStats(filterKey) {
  const baseRows = filterRows(
    state.jobs,
    FILTER_ORDER.filter((key) => key !== filterKey),
  );
  const counts = new Map();
  for (const job of baseRows) {
    const value = FILTERS[filterKey].getValue(job);
    if (!value) continue;
    counts.set(value, (counts.get(value) || 0) + 1);
  }

  const denominator = baseRows.length || 1;
  const options = [...counts.entries()]
    .map(([value, count]) => ({
      value,
      count,
      percent: (count / denominator) * 100,
    }))
    .sort((a, b) => FILTERS[filterKey].sort(a.value, b.value));

  return { denominator: baseRows.length, options };
}

function compareNullableNumbers(a, b, direction) {
  const aMissing = a === null || a === undefined || Number.isNaN(a);
  const bMissing = b === null || b === undefined || Number.isNaN(b);
  if (aMissing && bMissing) return 0;
  if (aMissing) return 1;
  if (bMissing) return -1;
  return direction === "desc" ? b - a : a - b;
}

function sortValue(job, key) {
  if (key === "review") {
    return Number(job.review_final_score ?? NaN);
  }
  if (key === "yoe") {
    return job.yoe_value === null || job.yoe_value === undefined ? null : Number(job.yoe_value);
  }
  if (key === "discovered") {
    return job.discovered_at || "";
  }
  if (key === "published") {
    return job.publish_at || "";
  }
  return "";
}

function sortJobs(rows) {
  if (!state.sort.key || !state.sort.direction) {
    return [...rows];
  }
  const direction = state.sort.direction;
  const key = state.sort.key;
  return [...rows].sort((a, b) => {
    if (key === "review" || key === "yoe") {
      const diff = compareNullableNumbers(sortValue(a, key), sortValue(b, key), direction);
      if (diff !== 0) return diff;
    } else {
      const av = String(sortValue(a, key) || "");
      const bv = String(sortValue(b, key) || "");
      const diff = direction === "desc" ? bv.localeCompare(av) : av.localeCompare(bv);
      if (diff !== 0) return diff;
    }
    return 0;
  });
}

function formatProcessStatus(process) {
  const status = process.status || "";
  if (status === "running") return { text: "运行中", className: "status-running" };
  if (status === "starting") return { text: "启动中", className: "status-running" };
  if (status === "waiting_retry") return { text: "等待 5 小时刷新", className: "status-waiting" };
  if (status === "quota_weekly_exit") return { text: "周限额已退出", className: "status-weekly" };
  if (status === "completed") return { text: "已完成", className: "status-completed" };
  if (status === "failed") return { text: "失败", className: "status-failed" };
  if (status === "stopped") return { text: "已停止", className: "status-failed" };
  if (status === "quota_wait_unknown") return { text: "限额命中，待确认", className: "status-failed" };
  return { text: status || "未知", className: "status-completed" };
}

function formatProgress(process) {
  const progress = process.progress || {};
  const metadata = process.metadata || {};
  const parts = [];
  if (progress.accepted_jobs) {
    parts.push(`accepted ${progress.accepted_jobs}`);
  }
  if (progress.rejected_jobs) {
    parts.push(`rejected ${progress.rejected_jobs}`);
  }
  if (progress.staged_jobs) {
    parts.push(`已入队 ${progress.staged_jobs}`);
  }
  if (progress.handled_jobs) {
    parts.push(`已处理 ${progress.handled_jobs}`);
  }
  if (progress.pdf_progress && progress.pdf_progress.total) {
    parts.push(`PDF ${progress.pdf_progress.completed}/${progress.pdf_progress.total}`);
  }
  if (metadata.waiting_queue_count) {
    parts.push(`等待队列 ${metadata.waiting_queue_count}`);
  }
  if (metadata.published_count) {
    parts.push(`已发布 ${metadata.published_count}`);
  }
  if (metadata.reviewed_count) {
    parts.push(`已review ${metadata.reviewed_count}`);
  }
  return parts.join(" · ");
}

function buildDetailLines(process) {
  const metadata = process.metadata || {};
  if (metadata.detail_lines && metadata.detail_lines.length) {
    return metadata.detail_lines;
  }
  if (process.log_tail && process.log_tail.length) {
    return process.log_tail;
  }
  return [];
}

function presetDateHint(preset) {
  const bounds = preset?.date_bounds || {};
  const min = bounds.min || "";
  const max = bounds.max || "";
  if (min && max) return `可选日期范围：${min} 到 ${max}`;
  if (min) return `最早日期：${min}`;
  if (max) return `最晚日期：${max}`;
  return "";
}

function renderMonitor() {
  const processes = state.monitor.processes || [];
  const presets = state.monitor.presets || [];
  const activeProcesses = processes.filter((process) =>
    ["running", "starting", "waiting_retry"].includes(process.status),
  );
  const recentProcesses = processes.filter((process) =>
    !["running", "starting", "waiting_retry"].includes(process.status),
  );

  const runningCount = state.monitor.meta.running_count || 0;
  const waitingRetryCount = state.monitor.meta.waiting_retry_count || 0;
  const weeklyExitCount = state.monitor.meta.weekly_exit_count || 0;
  monitorMeta.textContent = activeProcesses.length
    ? `运行中 ${runningCount} · 等待 5 小时刷新 ${waitingRetryCount} · 周限额退出 ${weeklyExitCount}`
    : `当前空闲 · 周限额退出 ${weeklyExitCount}`;

  const sections = [];

  if (activeProcesses.length > 0) {
    sections.push(
      ...activeProcesses.map((process) => {
        const status = formatProcessStatus(process);
        const progressText = formatProgress(process);
        const isWaiting = process.status === "waiting_retry";
        const detailLines = buildDetailLines(process);
        const currentJob = process.metadata?.current_job || null;
        return `
          <article class="process-card ${isWaiting ? "is-waiting" : "is-running"}" data-process-id="${escapeHtml(process.id)}">
            <div class="process-top">
              <div>
                <div class="process-title">${escapeHtml(process.display_name || process.label || process.command)}</div>
                <div class="process-subtitle">${escapeHtml(process.command || process.effective_command || "")}</div>
              </div>
              <div class="launch-row">
                <span class="status-pill ${escapeHtml(status.className)}">${escapeHtml(status.text)}</span>
                <button class="stop-btn" type="button" data-process-id="${escapeHtml(process.id)}">×</button>
              </div>
            </div>
            <div class="process-details">
              ${process.next_retry_at ? `下次自动重试：${escapeHtml(process.next_retry_at)} · ` : ""}
              ${process.child_pid ? `PID ${escapeHtml(process.child_pid)}` : ""}
            </div>
            ${progressText ? `<div class="process-progress">本轮进度：${escapeHtml(progressText)}</div>` : ""}
            ${
              currentJob && currentJob.job_id
                ? `<div class="process-details">当前处理：#${escapeHtml(currentJob.index)} · ${escapeHtml(
                    currentJob.company_name || "",
                  )} · ${escapeHtml(currentJob.title || "")} · ${escapeHtml(currentJob.state || "")}</div>`
                : ""
            }
            ${detailLines.length ? `<pre class="process-log is-live">${escapeHtml(detailLines.join("\n"))}</pre>` : ""}
          </article>
        `;
      }),
    );
  } else {
    sections.push(`<div class="monitor-empty">当前没有正在运行的程序。可以直接在下方选择指令、tier 和日期范围后启动。</div>`);
    sections.push(
      ...presets.map(
        (preset) => `
          <article class="command-card" data-preset-id="${escapeHtml(preset.id)}">
            <div class="command-top">
              <div>
                <div class="command-title">${escapeHtml(preset.title)}</div>
                <div class="command-desc">${escapeHtml(preset.description || "")}</div>
                ${presetDateHint(preset) ? `<div class="command-desc">${escapeHtml(presetDateHint(preset))}</div>` : ""}
              </div>
              <button class="run-btn" type="button" data-preset-id="${escapeHtml(preset.id)}">Run</button>
            </div>
            ${
              preset.supports_filters
                ? `
                  <div class="launch-controls">
                    <div class="launch-field">
                      <label>Tier</label>
                      <div class="tier-row">
                        <label><input type="checkbox" value="large" checked /> 大厂</label>
                        <label><input type="checkbox" value="mid" /> 中厂</label>
                        <label><input type="checkbox" value="small" /> 小厂</label>
                      </div>
                    </div>
                    <div class="launch-field">
                      <label>起始日期</label>
                      <input class="launch-input launch-start-date" type="date" ${
                        preset?.date_bounds?.min ? `min="${escapeHtml(preset.date_bounds.min)}"` : ""
                      } ${preset?.date_bounds?.max ? `max="${escapeHtml(preset.date_bounds.max)}"` : ""} />
                    </div>
                    <div class="launch-field">
                      <label>结束日期</label>
                      <input class="launch-input launch-end-date" type="date" ${
                        preset?.date_bounds?.min ? `min="${escapeHtml(preset.date_bounds.min)}"` : ""
                      } ${preset?.date_bounds?.max ? `max="${escapeHtml(preset.date_bounds.max)}"` : ""} />
                    </div>
                  </div>
                `
                : ""
            }
          </article>
        `,
      ),
    );
  }

  if (recentProcesses.length > 0) {
    sections.push(`<div class="process-section-title">最近任务</div>`);
    sections.push(
      ...recentProcesses.slice(0, 6).map((process) => {
        const status = formatProcessStatus(process);
        const progressText = formatProgress(process);
        return `
          <article class="process-card">
            <div class="process-top">
              <div>
                <div class="process-title">${escapeHtml(process.display_name || process.label || process.command)}</div>
                <div class="process-subtitle">${escapeHtml(process.command || process.effective_command || "")}</div>
              </div>
              <span class="status-pill ${escapeHtml(status.className)}">${escapeHtml(status.text)}</span>
            </div>
            <div class="process-details">
              ${process.finished_at ? `结束于 ${escapeHtml(process.finished_at)}` : process.updated_at ? `更新于 ${escapeHtml(process.updated_at)}` : ""}
            </div>
            ${progressText ? `<div class="process-progress">本轮进度：${escapeHtml(progressText)}</div>` : ""}
            ${process.last_error ? `<div class="process-error">${escapeHtml(process.last_error)}</div>` : ""}
          </article>
        `;
      }),
    );
  }

  monitorBoard.innerHTML = sections.join("");

  monitorBoard.querySelectorAll(".stop-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const processId = button.dataset.processId;
      try {
        const response = await fetch("/api/process/stop", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ process_id: processId }),
        });
        const payload = await response.json();
        if (!response.ok || !payload.ok) {
          throw new Error(payload.error || "停止失败");
        }
        await loadMonitor();
      } catch (error) {
        window.alert(`停止失败：${error.message}`);
      }
    });
  });

  monitorBoard.querySelectorAll(".run-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const card = button.closest(".command-card");
      const presetId = button.dataset.presetId;
      const preset = (state.monitor.presets || []).find((item) => item.id === presetId) || {};
      const checkedTiers = [...card.querySelectorAll('input[type="checkbox"]:checked')].map((input) => input.value);
      const startDateInput = card.querySelector(".launch-start-date");
      const endDateInput = card.querySelector(".launch-end-date");
      const startDate = startDateInput ? startDateInput.value : "";
      const endDate = endDateInput ? endDateInput.value : "";
      const minDate = preset?.date_bounds?.min || "";
      const maxDate = preset?.date_bounds?.max || "";
      if (startDate && endDate && startDate > endDate) {
        window.alert("起始日期不能晚于结束日期。");
        return;
      }
      if ((minDate && startDate && startDate < minDate) || (minDate && endDate && endDate < minDate)) {
        window.alert(`日期不能早于 ${minDate}。`);
        return;
      }
      if ((maxDate && startDate && startDate > maxDate) || (maxDate && endDate && endDate > maxDate)) {
        window.alert(`日期不能晚于 ${maxDate}。`);
        return;
      }
      try {
        const response = await fetch("/api/process/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            preset_id: presetId,
            tiers: checkedTiers,
            start_date: startDate,
            end_date: endDate,
          }),
        });
        const payload = await response.json();
        if (!response.ok || !payload.ok) {
          throw new Error(payload.error || "启动失败");
        }
        await loadMonitor();
      } catch (error) {
        window.alert(`启动失败：${error.message}`);
      }
    });
  });
}

function renderSummary() {
  const cards = [
    { label: "当前结果", value: state.filteredJobs.length },
    { label: "今日新增", value: state.meta.today_new_jobs || 0 },
    { label: "本周新增", value: state.meta.week_new_jobs || 0 },
    { label: "已申请", value: state.meta.applied_jobs || 0 },
    { label: "Review Pass", value: state.meta.review_passed_jobs || 0 },
    { label: "已关闭", value: state.meta.closed_jobs || 0 },
  ];

  summaryCards.innerHTML = cards
    .map(
      (card) => `
        <article class="stat-card">
          <div class="stat-value">${escapeHtml(card.value)}</div>
          <div class="stat-label">${escapeHtml(card.label)}</div>
        </article>
      `,
    )
    .join("");

  resultSummary.textContent = `当前展示 ${state.filteredJobs.length} / ${state.jobs.length} 条岗位`;
  const refreshText = state.isRefreshing ? "正在刷新..." : `页面每 ${AUTO_REFRESH_MS / 1000} 秒自动刷新`;
  updatedAt.textContent = state.updatedAt ? `数据刷新时间：${state.updatedAt} · ${refreshText}` : refreshText;
}

function renderFilters() {
  filterGrid.innerHTML = "";
  for (const filterKey of FILTER_ORDER) {
    const fragment = filterTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".filter-card");
    const trigger = fragment.querySelector(".filter-trigger");
    const label = fragment.querySelector(".filter-label");
    const selection = fragment.querySelector(".filter-selection");
    const panel = fragment.querySelector(".filter-panel");
    const searchInput = fragment.querySelector(".filter-search");
    const clearBtn = fragment.querySelector(".clear-filter-btn");
    const optionsRoot = fragment.querySelector(".filter-options");

    const stats = getOptionStats(filterKey);
    const selectedValues = state.selections[filterKey];
    const searchTerm = state.searches[filterKey].trim().toLowerCase();

    label.textContent = FILTERS[filterKey].label;
    selection.textContent = selectedValues.size
      ? [...selectedValues].join(", ")
      : `全部 (${stats.denominator})`;

    const visibleOptions = stats.options.filter((option) =>
      option.value.toLowerCase().includes(searchTerm),
    );
    const longestLine = visibleOptions.reduce((max, option) => {
      const line = `${option.count} | ${option.percent.toFixed(1)}% ${option.value}`;
      return Math.max(max, line.length);
    }, 18);
    card.style.setProperty("--panel-width-ch", String(longestLine + 4));

    searchInput.value = state.searches[filterKey];
    searchInput.addEventListener("input", (event) => {
      state.searches[filterKey] = event.target.value;
      renderFilters();
    });

    trigger.addEventListener("click", () => {
      panel.classList.toggle("hidden");
    });

    clearBtn.addEventListener("click", () => {
      state.selections[filterKey].clear();
      applyAllFilters();
    });

    visibleOptions.forEach((option) => {
      const wrapper = document.createElement("label");
      wrapper.className = "filter-option";
      const checked = selectedValues.has(option.value);
      wrapper.innerHTML = `
        <input type="checkbox" ${checked ? "checked" : ""} />
        <span class="option-meta">${escapeHtml(option.count)} | ${escapeHtml(
          option.percent.toFixed(1),
        )}%</span>
        <span class="option-value">${escapeHtml(option.value)}</span>
      `;
      const checkbox = wrapper.querySelector("input");
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
          state.selections[filterKey].add(option.value);
        } else {
          state.selections[filterKey].delete(option.value);
        }
        applyAllFilters();
      });
      optionsRoot.appendChild(wrapper);
    });

    filterGrid.appendChild(fragment);
  }
}

function reviewBadgeClass(job) {
  const kind = job.review_badge_kind || "pending";
  if (kind === "pass") return "review-pass";
  if (kind === "cond") return "review-cond";
  if (kind === "fail") return "review-fail";
  if (kind === "none") return "review-none";
  return "review-pending";
}

function renderReviewCell(job) {
  const badgeText = job.review_display_value || job.review_status || "未review";
  const action = job.review_action
    ? `
        <button
          class="review-action-btn"
          type="button"
          data-job-id="${escapeHtml(job.job_id)}"
          data-action="${escapeHtml(job.review_action)}"
        >${escapeHtml(job.review_action_label || "")}</button>
      `
    : "";
  return `
    <div class="review-cell ${action ? "has-action" : ""}">
      <span class="review-badge ${escapeHtml(reviewBadgeClass(job))}">${escapeHtml(badgeText)}</span>
      ${action}
    </div>
  `;
}

function normalizeApplyUrlStatus(job) {
  const raw = String(job.apply_url_status || "").trim().toLowerCase();
  if (raw === "open" || raw === "closed" || raw === "unknown") return raw;
  if (job.closed) return "closed";
  return "unknown";
}

function renderApplyUrlCell(job) {
  if (!job.apply_url) return "";
  const urlStatus = normalizeApplyUrlStatus(job);
  const linkText = urlStatus === "closed" ? "Closed" : urlStatus === "unknown" ? "Open?" : "Open";
  return `<a
    class="apply-url-link apply-url-status-${escapeHtml(urlStatus)}"
    data-apply-url-status="${escapeHtml(urlStatus)}"
    href="${escapeHtml(job.apply_url)}"
    target="_blank"
    rel="noreferrer"
  >${escapeHtml(linkText)}</a>`;
}

function renderSortIndicators() {
  sortButtons.forEach((button) => {
    const key = button.dataset.sortKey;
    const indicator = button.querySelector(".sort-indicator");
    if (!indicator) return;
    if (state.sort.key !== key || !state.sort.direction) {
      indicator.textContent = "";
      button.classList.remove("is-active");
      return;
    }
    indicator.textContent = state.sort.direction === "desc" ? "↓" : "↑";
    button.classList.add("is-active");
  });
}

function renderTable() {
  if (state.filteredJobs.length === 0) {
    jobTableBody.innerHTML = `
      <tr>
        <td colspan="11" class="empty-state">没有匹配当前筛选条件的岗位。</td>
      </tr>
    `;
    return;
  }

  jobTableBody.innerHTML = state.filteredJobs
    .map(
      (job) => `
        <tr class="${job.processed ? "is-processed" : ""}" data-job-id="${escapeHtml(job.job_id)}">
          <td class="checkbox-cell">
            <input
              type="checkbox"
              class="status-checkbox"
              data-status="applied"
              ${job.applied ? "checked" : ""}
            />
          </td>
          <td class="checkbox-cell">
            <input
              type="checkbox"
              class="status-checkbox"
              data-status="abandoned"
              ${job.abandoned ? "checked" : ""}
            />
          </td>
          <td class="checkbox-cell">
            <input
              type="checkbox"
              class="status-checkbox"
              data-status="closed"
              ${job.closed ? "checked" : ""}
            />
          </td>
          <td>${escapeHtml(job.company_name)}</td>
          <td>${escapeHtml(job.title)}</td>
          <td>${renderReviewCell(job)}</td>
          <td>${escapeHtml(job.yoe_label)}</td>
          <td>${escapeHtml(job.discovered_at)}</td>
          <td>${escapeHtml(job.publish_at)}</td>
          <td>${renderApplyUrlCell(job)}</td>
          <td>
            ${
              job.resume_dir
                ? `<a href="#" class="dir-link" data-job-id="${escapeHtml(job.job_id)}">Open Folder</a>`
                : ""
            }
          </td>
        </tr>
      `,
    )
    .join("");

  jobTableBody.querySelectorAll(".status-checkbox").forEach((checkbox) => {
    checkbox.addEventListener("change", async (event) => {
      const input = event.target;
      const row = input.closest("tr");
      const jobId = row.dataset.jobId;
      const statusKey = input.dataset.status;
      const job = state.jobs.find((item) => item.job_id === jobId);
      if (!job) return;

      if (statusKey === "applied") {
        job.applied = input.checked;
        job.abandoned = input.checked ? false : job.abandoned;
      } else if (statusKey === "abandoned") {
        job.abandoned = input.checked;
        job.applied = input.checked ? false : job.applied;
      } else if (statusKey === "closed") {
        job.closed = input.checked;
      }

      job.processed = job.applied || job.abandoned || job.closed;
      applyAllFilters();

      try {
        await saveStatus(job);
      } catch (error) {
        window.alert(`状态保存失败：${error.message}`);
      }
    });
  });

  jobTableBody.querySelectorAll(".dir-link").forEach((link) => {
    link.addEventListener("click", async (event) => {
      event.preventDefault();
      const jobId = link.dataset.jobId;
      const response = await fetch(`/api/open-dir?job_id=${encodeURIComponent(jobId)}`);
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        window.alert(payload.error || "打开目录失败");
      }
    });
  });

  jobTableBody.querySelectorAll(".review-action-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const response = await fetch("/api/job-action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_id: button.dataset.jobId,
            action: button.dataset.action,
          }),
        });
        const payload = await response.json();
        if (!response.ok || !payload.ok) {
          throw new Error(payload.error || "启动失败");
        }
        await loadMonitor();
      } catch (error) {
        window.alert(`启动失败：${error.message}`);
      }
    });
  });
}

async function saveStatus(job) {
  const response = await fetch("/api/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_id: job.job_id,
      applied: job.applied,
      abandoned: job.abandoned,
      closed: job.closed,
    }),
  });
  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || "保存失败");
  }
  await loadJobs({ silent: true });
}

function applyAllFilters() {
  state.filteredJobs = sortJobs(filterRows(state.jobs, FILTER_ORDER));
  renderFilters();
  renderSummary();
  renderSortIndicators();
  renderTable();
}

async function loadMonitor() {
  const response = await fetch("/api/monitor", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`监控加载失败: ${response.status}`);
  }
  const payload = await response.json();
  state.monitor.processes = payload.processes || [];
  state.monitor.presets = payload.presets || [];
  state.monitor.meta = payload.meta || {};
  state.monitor.generatedAt = payload.generated_at || "";
  renderMonitor();
}

async function loadJobs({ silent = false } = {}) {
  state.isRefreshing = true;
  renderSummary();
  try {
    const response = await fetch("/api/jobs", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`加载失败: ${response.status}`);
    }
    const payload = await response.json();
    state.jobs = payload.jobs || [];
    state.updatedAt = payload.generated_at || "";
    state.meta = payload.meta || {};
    applyAllFilters();
  } catch (error) {
    if (!silent) {
      resultSummary.textContent = `页面加载失败：${error.message}`;
    }
  } finally {
    state.isRefreshing = false;
    renderSummary();
  }
}

async function loadDashboard({ silent = false } = {}) {
  await Promise.all([loadJobs({ silent }), loadMonitor()]);
}

clearAllBtn.addEventListener("click", () => {
  for (const key of FILTER_ORDER) {
    state.selections[key].clear();
    state.searches[key] = "";
  }
  applyAllFilters();
});

refreshBtn.addEventListener("click", () => {
  loadDashboard();
});

sortButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.sortKey;
    if (state.sort.key !== key) {
      state.sort = { key, direction: "desc" };
    } else if (state.sort.direction === "desc") {
      state.sort = { key, direction: "asc" };
    } else if (state.sort.direction === "asc") {
      state.sort = { key: "", direction: "" };
    } else {
      state.sort = { key, direction: "desc" };
    }
    applyAllFilters();
  });
});

document.addEventListener("click", (event) => {
  const insideCard = event.target.closest(".filter-card");
  document.querySelectorAll(".filter-panel").forEach((panel) => {
    if (!insideCard || !panel.parentElement.contains(insideCard)) {
      panel.classList.add("hidden");
    }
  });
});

loadDashboard().catch((error) => {
  resultSummary.textContent = `页面加载失败：${error.message}`;
});

window.setInterval(() => {
  loadDashboard({ silent: true });
}, AUTO_REFRESH_MS);
