# Reviewer Pipe Compare

Date: 2026-04-17

## Scope

This round compares:

- Historical baseline from [output/analysis/claude_vs_official_review_report_2026-04-09.md](../output/analysis/claude_vs_official_review_report_2026-04-09.md)
- New isolated 4-stage prompt + deterministic scorer under [reviewer-compare](.)
- Isolated original prompt snapshots:
  - [reviewer-compare/original-review-prompt/reviewer_user.md](original-review-prompt/reviewer_user.md)
  - [reviewer-compare/original-review-prompt/reviewer_system.md](original-review-prompt/reviewer_system.md)

Executed runs used in this assessment:

- Full Codex run: [reviewer-compare/runs/20260417_175343/report.md](runs/20260417_175343/report.md)
- Claude AWS success + Amazon limit hit: [reviewer-compare/runs/20260417_175916/same-aws/case_summary.json](runs/20260417_175916/same-aws/case_summary.json), [reviewer-compare/runs/20260417_175916/same-amazon/case_summary.json](runs/20260417_175916/same-amazon/case_summary.json)

Important run-state note:

- Claude hit hourly limit on Amazon: `You've hit your limit · resets 9pm (America/Chicago)`.
- Per request, no rerun was attempted after hitting the hourly cap.
- Therefore, cross-CLI gap comparison is complete for `same/AWS` only, and partial for the other cases.

## Direct Answers

### 1. 调用不同 CLI 的判分差距更小、更大还是没变？

Current evidence says: **larger**, but only on the fully completed dual-CLI case.

| Case | Old Gap | New Gap | Trend |
| --- | ---: | ---: | --- |
| same/AWS | 0.6 | 2.9 | larger |
| same/Microsoft | 6.3 | unknown | incomplete |
| same/Google | 7.7 | unknown | incomplete |
| same/Amazon | 2.1 | unknown | incomplete |

Interpretation:

- Historical `same/AWS` was nearly converged: official `95.1` vs Claude `94.5`.
- New isolated 4-stage pipe widened the AWS gap to Codex `87.0` vs Claude `84.1`.
- So the new pipe did **not** reduce cross-CLI variance on the completed case; it increased it.

### 2. 同一模型对同一份简历 + 目标 JD 的判分是更高、更低还是没变？

#### Codex vs historical official baseline

All completed cases are **lower** under the new 4-stage pipe.

| Case | Old Official | New Codex | Delta | Direction |
| --- | ---: | ---: | ---: | --- |
| same/Microsoft | 94.2 | 80.3 | -13.9 | lower |
| same/Google | 94.0 | 77.0 | -17.0 | lower |
| same/Amazon | 95.6 | 90.2 | -5.4 | lower |
| same/AWS | 95.1 | 87.0 | -8.1 | lower |

#### Claude vs historical Claude baseline

Only one case completed before the hourly limit, and it is also **lower**.

| Case | Old Claude | New Claude | Delta | Direction |
| --- | ---: | ---: | ---: | --- |
| same/AWS | 94.5 | 84.1 | -10.4 | lower |
| same/Microsoft | 87.9 | unknown | unknown | incomplete |
| same/Google | 86.3 | unknown | unknown | incomplete |
| same/Amazon | 93.5 | limit hit | unknown | incomplete |

### 3. 同一模型对同一份简历 + 目标 JD 的审阅输出如何变化？

#### New Codex output vs historical official reviewer

The new Codex reviewer is structurally different:

- It is much more rule-explicit and stage-explicit. Findings now cluster under stable rule IDs such as `P2-001`, `P2-020`, `P3D-001`, `P3E-002`.
- It is much harsher on top-of-page framing, first-bullet signal quality, and Tier 1 vs Tier 2 metric mix.
- It repeatedly treats the Temu timeline/public-anchor issue as a hard blocker via `P3E-002`, which materially drags scores down across all 4 cases.
- It produces more operational rewrite instructions, but those instructions are often framed as pass/fail gate remediation rather than publication-quality improvement.

Observed recurring Codex themes across the 4 cases:

- `P2-001`: Summary sentence 1 uses low-signal transition framing.
- `P2-020`: first bullet of the lead experience lacks Tier 1 scope anchor.
- `P3D-001`: too many Tier 2 metrics, not enough scope/system-scale anchors.
- `P3C-010`: multi-language breadth in TikTok needs tighter ownership delimitation.
- `P3E-002`: Temu date/public-anchor contradiction escalates to structural risk.

#### New Claude output vs historical Claude reviewer

The completed AWS case shows a different change pattern from Codex:

- Historical Claude on AWS was close to pass-calibrated, with mild concerns on senior/backend framing, formatting cleanup, and denser C++/Embedded evidence.
- New Claude on AWS drops to `84.1 fail` and moves from mild polish feedback to structured fail-oriented rewrite guidance.
- It still emphasizes framing and signal density, but it does **not** follow Codex all the way into `P3E-002` hard-fail behavior on the Temu anchor issue.
- It adds more nuanced JD-bridge reasoning, especially around Builder Experience / GenAI / Codex transferability and language-ownership scoping.

New Claude AWS themes:

- `P2-001`: `Backend Transition Profile` is judged as low-signal transition framing.
- `P2-020`: first TikTok bullet needs a Tier 1 scope anchor.
- `P3B-003`: GenAI/RAG work is not explicitly bridged to builder tooling or code-context retrieval.
- `P3C-010`: Java + Go + C++ all appearing in one intern role needs explicit ownership boundaries.
- `P3D-001`: TikTok and Temu bullets overuse Tier 2 metrics.

Net effect:

- New Codex is the stricter hard-rule gatekeeper.
- New Claude is also much stricter than historical Claude, but its reasoning is still more semantic and role-bridge oriented than Codex on AWS.

## Assessment Of The Two Reviewer Pipes

### Old pipe: `UnifiedReviewer`

Strengths:

- Better calibrated to the project’s existing publication/pass bar.
- Lower false-fail rate on resumes that are substantively strong but imperfectly packaged.
- More willing to credit transferability and semantic evidence instead of exact lexical presence.
- Already integrated with the existing orchestration and rewrite loop.

Weaknesses:

- Underprices top-of-page framing risk.
- Underprices first-screen recruiter interpretation risk.
- Under-enforces exact scope anchoring and some ATS/body-traceability issues.
- Leaves more judgment in-model, so output style can vary without an explicit rule ontology.

### New pipe: `Reviewer_4Stage.md` + `Reviewer_Cal.py`

Strengths:

- Much more auditable. The path from finding to score is explicit.
- Better isolation: prompt, system, artifacts, and scoring are all separable under `reviewer-compare`.
- Easier to compare across models because scoring is deterministic and externalized.
- Produces more stable issue taxonomy and more operational rewrite guidance.

Weaknesses:

- Current calibration is too harsh for this resume corpus.
- The deterministic penalties amplify repeated issue families into fail outcomes quickly.
- `P3E-002` appears to dominate too many cases and may be overfiring relative to the actual intended gate.
- Cross-model variance is not eliminated; on AWS it became worse, not better.

### Practical judgment

If the question is "which pipe is better as the production pass/fail gate right now?":

- **Old pipe is safer today.**

If the question is "which pipe is better as a diagnostic reviewer or shadow evaluator?":

- **New 4-stage pipe is better.**

Reason:

- The old pipe is better calibrated to the existing acceptance bar.
- The new pipe is better at decomposing *why* a resume feels risky, but it is not yet calibrated tightly enough to replace the old gate without increasing false fails.

## Recommendation

Recommended near-term stance:

1. Keep the old pipe as the production gate for now.
2. Run the new 4-stage pipe in shadow mode for comparison and issue mining.
3. Before promoting the new pipe, recalibrate at least three areas:
   - reduce the global score impact of repeated `P3D-001` style density findings,
   - review whether `P3E-002` is too aggressively mapped into ecosystem / hard-fail behavior,
   - validate whether current `85` / `93` thresholds match the new rule density.

Recommended product judgment:

- The new pipe is **better for diagnosis**.
- The old pipe is **better for gating**.
- The new pipe should not replace the old one until score calibration and hard-block policy are revised.
