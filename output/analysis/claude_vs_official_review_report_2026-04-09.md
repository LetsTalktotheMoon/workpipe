# Claude vs Official Reviewer Comparison

Date: 2026-04-09

## Scope

This report compares:

- Official portfolio reviews already stored in `review.json`
- Claude Sonnet 4.6 re-reviews produced by `claude_reuse_source_target_full_review.py`

Important: this run used the same production `UnifiedReviewer` pipeline and prompt, but a different model/transport. That means the earlier 30-40 point gap caused by the ad hoc `/tmp/run_reuse_test.py` harness has mostly been eliminated. The remaining gap is primarily model judgment/calibration drift.

Only 4 `same/*` cases completed both source-JD and target-JD reviews:

- same/Microsoft
- same/Google
- same/Amazon
- same/Amazon Web Services

The `cross/*` cases did not complete and are not included in the comparison.

## Score Summary

| Case | Official Source | Claude Source | Delta | Official Target | Claude Target | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| same/Microsoft | 93.8 | 93.0 | -0.8 | 94.2 | 87.9 | -6.3 |
| same/Google | 94.4 | 85.0 | -9.4 | 94.0 | 86.3 | -7.7 |
| same/Amazon | 93.6 | 85.3 | -8.3 | 95.6 | 93.5 | -2.1 |
| same/AWS | 94.4 | 93.0 | -1.4 | 95.1 | 94.5 | -0.6 |

Aggregate:

- Average source delta: -5.0
- Average target delta: -4.2

Interpretation:

- The huge prior discrepancy is gone.
- Remaining disagreement is meaningful but much smaller.
- Claude is still directionally stricter, especially on Google and Microsoft target cases.

## What Changed vs the Earlier Broken Test

The earlier `/tmp/run_reuse_test.py` comparison was invalid because it mixed the wrong resume, wrong JD pairing, wrong prompt, missing company context, and a simplified output schema.

This new comparison does not have those problems:

- Same production reviewer prompt
- Same weighted dimensions
- Same resume under review for source/target comparison
- Same `UnifiedReviewer` logic

Therefore the current gap is much more trustworthy as a model-comparison result.

## Case-by-Case Comparison

### same/Microsoft

Official:

- Source: 93.8 pass
- Target: 94.2 pass
- No revision priority on either side

Claude:

- Source: 93.0 pass
- Target: 87.9 fail

Main Claude objections on target:

- High severity on Summary header: `Strategic Problem Solving`
- Medium severity on `transitioning from data analytics`
- Medium severity on exact top-of-page keyword signaling: `Distributed Systems`, `Code Review`
- Medium severity on category naming: `Cloud`

Assessment:

- Claude is plausibly over-penalizing a single header choice and a few lexical/labeling issues.
- However, the Microsoft target critique is not noise: for a senior Microsoft backend/systems role, the resume really does undersignal senior/backend identity in the Summary compared with the strength of the actual experience bullets.
- Official reviewer likely underweighted this senior-framing issue.

Bottom line:

- Score gap is too large.
- But Claude identified a real blind spot around top-of-page senior positioning.

### same/Google

Official:

- Source: 94.4 pass
- Target: 94.0 pass
- Source suggestions were light: remove non-technical bolding, add one explicit performance/test-gate bullet
- Target had no revision priority

Claude:

- Source: 85.0 fail
- Target: 86.3 fail

Main Claude objections:

- Exact year claim: `3+ years` vs 34 months actual work history
- Exact lexical traceability of `Semantic Layer Design`, `Metric Definition`, `Design Review`
- Skills taxonomy mislabeling: `APIs` category is semantically wrong
- Summary framing is data-modeling first rather than infrastructure/performance first
- For target, ATS-like insistence that Looker/semantic-layer signals appear as exact phrases in body text

Assessment:

- This is the clearest divergence.
- Claude is harsher on exact-match ATS semantics than our official reviewer.
- Several of Claude's findings are genuinely useful:
  - the `3+ years` arithmetic claim
  - category naming quality
  - exact body evidence for high-value semantic-layer terms
- But failing the entire resume at mid-80s is likely too harsh given the candidate still has strong Java/Kotlin/SQL/data-modeling evidence and a coherent Looker-adjacent story.

Bottom line:

- Claude is catching real ATS and recruiter-scan weaknesses.
- Official reviewer is probably too lenient here.
- Claude's final score is still lower than necessary.

### same/Amazon

Official:

- Source: 93.6 pass
- Target: 95.6 pass

Claude:

- Source: 85.3 fail
- Target: 93.5 pass

Main Claude objections on source:

- High severity on `Embedded` as a JD must-have with too-thin evidence
- Summary and keyword-density issues
- Tech breadth plausibility concerns in TikTok

Main Claude objections on target:

- Mostly medium/low suggestions only
- Matlab signal too thin
- Category naming and summary positioning tweaks

Assessment:

- This is a healthy comparison result.
- Claude passes the target JD and fails the source JD, which suggests the model is not just globally harsh.
- The source-JD failure is largely due to ATS-style exactness around `Embedded` and keyword density.
- Official reviewer likely gives more credit for semantic evidence and transferability than Claude does.

Bottom line:

- Claude is probably somewhat too strict on the source side.
- But its criticism about must-have evidence density is worth considering.

### same/Amazon Web Services

Official:

- Source: 94.4 pass
- Target: 95.1 pass

Claude:

- Source: 93.0 pass
- Target: 94.5 pass

Shared themes between both reviewers:

- Mild concern about senior/backend ownership framing
- Formatting cleanup
- C++/Embedded evidence could be denser

Assessment:

- This is strong alignment.
- When the resume-story is already close to the JD and the top-level framing is solid, Claude and official reviewer converge.

Bottom line:

- This case is evidence that the current official reviewer is not fundamentally too lenient everywhere.
- The large disagreements are concentrated in specific narrative/ATS-sensitive cases.

## Pattern Differences

### Where Claude is Stronger

- Better at ATS lexical exactness:
  - exact skill phrase appears in body text or not
  - category naming quality
  - duplicate brand/skill noise
- Better at recruiter first-screen framing:
  - summary header quality
  - seniority signal density
  - "transitioning from ..." as a downward anchor
- Better at arithmetic / literal consistency:
  - `3+ years` vs actual month count

### Where Claude is Too Harsh

- It often escalates medium polish issues into overall fail territory.
- It overweights wording defects that do not clearly break HR trust:
  - single summary header choice
  - exact category label mismatch
  - exact lexical absence when semantic evidence is already strong
- It behaves more like an ATS exact-match checker plus skeptical recruiter than a calibrated publication reviewer.

### Where Official Reviewer is Stronger

- Better calibration against the intended bar:
  - no critical/high should generally land in the low-to-mid 90s
- Better at recognizing transferable evidence rather than exact token matching
- Lower false-fail rate on resumes that are substantively strong but imperfectly packaged

### Where Official Reviewer is Weaker

- Underweights top-of-page narrative framing risk
- Underweights exact ATS/body-traceability for a few high-value skills
- Underweights precise year arithmetic and some category-label quality issues
- Can let a resume pass even when a recruiter's first 7-second read would misclassify the candidate direction

## Practical Judgment

Overall answer to the core question:

- It is not just that Claude is "too strict".
- It is also not the case that our reviewer is obviously wrong across the board.
- The truth is mixed:
  - Claude is too punitive in aggregate
  - but it is surfacing a real class of issues our reviewer currently underprices

Best synthesis:

- Earlier huge discrepancy: mostly caused by the wrong test harness
- Current remaining discrepancy: real model calibration difference
- The most valuable Claude signals to incorporate are:
  - exact YOE arithmetic guardrails
  - better top-of-page seniority/framing checks
  - stricter enforcement for body evidence of a few JD-critical skills
  - category-label sanity checks
- The least valuable Claude behavior to copy is:
  - turning medium packaging issues into fail
  - over-penalizing exact lexical absence when semantic evidence is already strong

## Recommendation

Do not replace the official reviewer with Claude's scoring behavior wholesale.

Instead, keep the official calibration philosophy and add a small number of deterministic or semi-deterministic checks inspired by Claude:

1. Add a year-claim consistency check for `X+ years`.
2. Add a stricter check for exact body evidence on a small whitelist of JD-critical must-have skills.
3. Add a skill-category label sanity check (`Cloud`, `APIs`, etc.).
4. Add a first-screen summary-framing check for senior targets:
   - penalize `transitioning from ...` when it suppresses stronger senior/backend evidence.

This would capture the strongest Claude insights without inheriting its over-strict overall pass/fail behavior.
