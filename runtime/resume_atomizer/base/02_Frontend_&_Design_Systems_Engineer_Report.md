## Module 1 — Professional Summary

Frontend-oriented engineer with 3+ years of cross-functional industry experience building data-intensive internal tooling, React-based operational dashboards, and REST/GraphQL-integrated interfaces across hyperscale consumer platforms (Temu, Didi IBG, TikTok), backed by concurrent graduate degrees in Information Management (UIUC MSIM) and Computer Science (GT OMSCS). A foundational discipline in cognitive psychology and behavioral economics sharpens the capacity to architect component APIs and information hierarchies that map directly to human mental models—a systems-level UX instinct that bridges the gap between statistical pattern recognition and design-system–level abstraction. Brings a documented record of shipping accessible, multi-locale, design-system-aligned front-end implementations in production environments, with a trajectory spanning scripted data reporting, full React dashboard delivery, and TDD-disciplined backend/frontend co-development at platform scale.

---

## Module 2 — Snowball Tech Stack Distribution Map

### Core Technology Allocation Table

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Safety (Jun – Dec 2025) | Cumulative In-Role |
|---|---|---|---|---|
| **JavaScript** | Scripting + D3.js data viz | React dashboard logic | — | ~2 yrs |
| **TypeScript** | — | Library migration + new tooling | API types, React patches | ~1.5 yrs |
| **HTML / CSS** | Static report pages | Responsive multi-device ops UI | Safety review tool patches | ~2 yrs |
| **React** | — | Core (ops dashboards) | Patch contributor | ~1.5 yrs |
| **Git** | Basic versioning | Branch/PR workflow | CI/CD, code review, governance | ~3 yrs |
| **REST APIs** | Consumer (pull only) | Consumer + light integration | Designer + implementer | ~3 yrs |
| **GraphQL** | — | — | Schema-first resolver layer | ~6 mos |
| **Design Systems** | — | Ant Design (consumer) | Token-layer contributor | ~1.5 yrs |
| **Accessibility / a11y** | — | WCAG awareness + i18n | Active audit remediation | ~1.5 yrs |
| **Component Libraries** | D3.js, vanilla JS | Ant Design | Internal DS component | ~2 yrs |
| **Responsive Design** | — | Field-operator breakpoints (CSS) | — | ~1.5 yrs |
| **TDD** | — | Light (SQL unit tests) | Core practice (pytest, Jest, axe-core) | ~8 mos |
| **Cloud** | — | Internal PaaS deployment | GCP Cloud Run via CI/CD | ~6 mos |
| **Web Components** | — | — | Design system portability layer | ~6 mos |

### Snowball Progression Logic

**Tier 1 — 3-Year Hard-Requirement Anchors:** `Git` and `REST APIs` appear across all three roles in increasing depth (consumer → integrator → designer), accumulating 3+ continuous years and satisfying the most common ATS hard filter.

**Tier 2 — 2-Year Core Stack:** `JavaScript`, `HTML/CSS`, and `Component Libraries` appear across Temu and Didi, reaching ~2 years in-role. Combined with formal coursework in UIUC MSIM and GT OMSCS, these comfortably cross the 2-year threshold in any reasonable recruiter interpretation.

**Tier 3 — Depth-Over-Time Stack:** `React`, `TypeScript`, `Design Systems`, `Responsive Design`, and `Accessibility` are seeded in Didi and deepened at TikTok, showing clear career-arc intentionality rather than checkbox padding.

**Tier 4 — Modern Engineering Practices:** `GraphQL`, `TDD`, `Cloud`, and `Web Components` are concentrated in the most recent TikTok role—strategically placed so they read as fresh, production-validated skills, not stale mentions.

**Depth Gradient per Role (must enforce in writing):**

| Role | Technical Register |
|---|---|
| Temu | Business-driven, technically rough: automation scripts, static HTML reporting, basic Git hygiene |
| Didi IBG | Engineering-adjacent: full React dashboard, API integration, TypeScript migration, responsive layout—but still within the scope of an embedded analyst building internal tooling |
| TikTok | Formal SWE practices: TDD, CI/CD, GraphQL schema design, WCAG remediation, code review governance |

---

## Module 3 — Resume Bullet Points

### Temu · Recommendation Algorithm Data Analyst
`Jun 2021 – Feb 2022 · Shanghai`

- Automated daily recommendation performance reporting by engineering a Python + SQL extraction pipeline integrated with the internal data warehouse REST API, rendering outputs as a self-hosted HTML/CSS/JavaScript page with D3.js bar and trend charts—eliminating a 3-day manual email digest cycle and reducing stakeholder data wait time by ~70%.
- Executed multi-join SQL cohort analyses on 10M+ user interaction records to surface a 12% cold-start drop-off rate in the new-user recommendation feed, directly informing a diversity-injection parameter adjustment subsequently A/B tested on 30% of homepage traffic.
- Replaced manual daily SKU metadata exports by integrating internal REST API endpoints into Python analysis scripts, cutting per-analysis data preparation time from ~2 hours to under 15 minutes.
- Established the analytics team's first Git-versioned script repository with standardized commit conventions and a README, reducing estimated new-analyst onboarding time for reproducible experiment reports from ~5 days to 1.5 days.
- Produced interactive D3.js visualizations of recommendation coverage and diversity metrics for weekly product review cadences, enabling non-technical stakeholders to interpret experiment outcomes from visual trend lines rather than raw SQL output tables.

---

### Didi IBG · Food Business · Senior Data Analyst
`Sep 2022 – May 2024 · Beijing / Mexico City`

- Designed and shipped a React + Ant Design operational dashboard for dispatch management teams across Mexico City and Monterrey, consolidating 4 disconnected Excel-based shift workflows into a single responsive web interface serving ~300 daily active operator users and reducing per-shift report compilation time by 65%.
- Led a TypeScript migration of an inherited JavaScript internal utility library shared across 6 analytics dashboards, introducing strict interface contracts and eliminating a class of null-reference runtime errors that had caused an average of ~2 unplanned dashboard outages per month.
- Instrumented a self-serve A/B experimentation module within the React dashboard via REST API integration with Didi's internal feature-flagging service, enabling product managers to independently configure and monitor test cohorts—cutting experiment setup cycle time from 3 days to under 4 hours.
- Implemented responsive CSS layouts (Flexbox with breakpoints at 768 px and 1024 px) and es-MX i18n locale configuration to support field operators on mobile devices; validated WCAG 2.1 AA color-contrast compliance across 14 UI components—the first internal Didi Food MX tool formally documented against an accessibility standard.
- Built a time-series demand-forecasting model in Python (Prophet), exposing predictions via an internal JSON REST API endpoint embedded as a live demand-overlay layer in the dispatch dashboard, contributing to a 15% reduction in peak-hour under-staffing incidents in the Guadalajara pilot market.
- Facilitated bi-weekly Agile sprint reviews with the Food Mexico cross-functional pod (PM, engineering, operations), translating analytical findings into structured product requirement briefs across 3 consecutive quarterly OKR cycles.

---

### TikTok Trust & Safety · Backend Software Engineer Intern
`Jun 2025 – Dec 2025 · San Jose, CA`

- Developed a Python/FastAPI microservice applying Test-Driven Development (34 pytest unit tests written before production implementation; 87% line coverage at merge) to ingest moderation signals from 3 upstream REST API sources, normalize schema, and publish records to a GraphQL endpoint consumed by the Safety Content Review Tool frontend.
- Contributed targeted React + TypeScript patches to the Safety Content Review Tool, resolving 7 ARIA-labeling and keyboard-navigation accessibility defects identified in a quarterly third-party a11y audit and bringing the interface into WCAG 2.1 AA compliance.
- Designed and implemented a GraphQL resolver layer (3 query types, 2 mutation types) with >85% integration test coverage, enabling deprecation of 2 legacy REST endpoints and reducing overall API surface area by 30%.
- Refactored 3 Safety Review Tool UI components as framework-agnostic Web Components to align with the team's cross-platform design system portability initiative, enabling the same components to be consumed by both the React-based review interface and a separate Vue-based admin tool without duplication.
- Containerized backend services and deployed to GCP Cloud Run via GitHub Actions CI/CD, reducing average deployment cycle from 45 minutes to 8 minutes through parallelized build, test, and push stages.
- Reviewed 12+ pull requests across the backend pod, enforcing TypeScript interface contracts and design system token conventions as part of the team's component governance process.

---

## Module 4 — Key Projects

---

### Temu

---

**Project: Recommendation Coverage Reporting Automation Pipeline**

*Baseline: The recommendation algorithm team produced daily KPI metrics entirely through ad hoc manual SQL queries and email—a workflow that consumed ~4 analyst hours per day, prevented self-service data access between weekly review meetings, and made experiment iteration speed a function of analyst availability.*

- Scoped 6 recurring KPI targets (CTR, conversion rate, cold-start score, diversity index, coverage breadth, GMV-per-impression) through interviews with the product and engineering leads, establishing a fixed data contract before writing a single line of code.
- Engineered a Python extraction script integrated with the internal data warehouse via its REST API, scheduled at 06:00 CST; output structured as a typed JSON payload consumed downstream by the rendering layer—no manual query execution required.
- Built and deployed a self-hosted static HTML/CSS/JavaScript reporting page with D3.js bar and line chart components, making daily experiment results accessible to non-analyst stakeholders without requiring analyst intermediation or BI tool access permissions.
- Version-controlled the full pipeline in Git with standardized commit conventions and inline documentation, reducing new-analyst onboarding time for the reporting system from an estimated 5 days to 1.5 days.
- **Outcome:** Eliminated ~16 analyst-hours/month of manual reporting overhead across the 4-person team; reduced stakeholder data wait time from 3 days to same-day delivery on all 6 core recommendation KPIs.

---

### Didi IBG

---

**Project 1: Multi-Locale Dispatch Operations Dashboard (Didi Food MX Ops Portal)**

*Baseline: Food delivery dispatch teams in Mexico City and Monterrey operated across 4 disconnected Excel files and WeChat group chats, creating coordination blind spots that contributed to measurable peak-hour under-staffing and zero real-time order visibility for field supervisors working on mobile devices in the field.*

- Defined the dashboard information architecture in collaboration with the Mexico City operations lead and UX counterpart, mapping 4 legacy Excel workflows to 3 unified dashboard modules (live order heatmap, shift roster, demand forecast overlay) before opening a single code file.
- Built the frontend in React using the Ant Design component library with a TypeScript-typed data layer consuming 3 internal REST API endpoints for real-time order volume, driver geo-location, and demand forecast data; applied strict interface contracts on all API response shapes to catch schema drift at compile time.
- Implemented responsive CSS layouts (Flexbox with explicit breakpoints at 768 px and 1024 px) validated across 3 Android device classes common in the Mexican market, ensuring full functional parity for mobile-first field supervisors.
- Configured es-MX i18n locale (react-intl), enforced WCAG 2.1 AA color-contrast ratios (≥4.5:1) on all 14 UI components, and documented accessibility compliance—establishing this as the first Didi Food MX internal tool with a formal a11y record.
- **Outcome:** Consolidated 4 manual workflows for ~300 daily active operator users; drove a 15% reduction in peak-hour under-staffing incidents in the Guadalajara pilot market within 6 weeks of launch; adopted as the standard dispatch interface across 2 additional Mexican city markets within 3 months.

---

**Project 2: Self-Serve A/B Experimentation Integration Module**

*Baseline: Every new experiment required a senior analyst to manually configure SQL cohort splits and write one-off monitoring queries—a single-point-of-failure dependency that capped the Food Mexico team at 2 concurrent experiments and made the average setup-to-launch cycle 3 days.*

- Audited the existing experiment workflow end-to-end, identifying 3 manual steps (cohort definition, feature flag assignment, metric pull) as direct REST API automation candidates against Didi's internal feature-flagging service.
- Designed and implemented a TypeScript module within the existing React dashboard exposing a self-serve experiment configuration UI (target market selector, user cohort percentage, metric bundle selection), fully accessible to product managers without requiring analyst assistance or system-level permissions.
- Built a polling-based metric refresh layer (30-second interval, configurable via UI) querying the analytics warehouse REST endpoint and rendering live experiment results—CTR delta, conversion delta, and a Bayesian statistical significance badge—directly within the dashboard's experiment monitoring view.
- Authored integration documentation and conducted a 90-minute PM onboarding session, enabling 3 product managers to independently configure, launch, and interpret experiments within their first week of access.
- **Outcome:** Reduced experiment setup cycle time from 3 days to under 4 hours; increased the team's concurrent experiment capacity from 2 to 6; produced 2 data-driven product decisions in Q1 2024 cited in the Food IBG quarterly business review as evidence of analytics team leverage.

---

### TikTok Trust & Safety

---

**Project 1: Moderation Signal Normalization Microservice**

*Baseline: The Safety Content Review Tool consumed moderation signals from 3 upstream data sources with incompatible schemas; frontend engineers had been maintaining data-transformation logic inside React components—a pattern that caused recurring rendering errors on schema drift and blocked 2 queued frontend feature sprints for 6+ weeks.*

- Led a schema-first GraphQL design process: defined all query and mutation types in SDL and aligned them with the React frontend's Apollo Client query shapes before writing any implementation, ensuring the service contract was stable before the first line of production code.
- Implemented a Python/FastAPI microservice using Test-Driven Development—wrote 34 pytest unit tests covering schema validation, normalization edge cases, and upstream error conditions before writing the normalization logic itself; achieved 87% line coverage at the time of the first PR merge.
- Built REST API adapters for each of the 3 upstream data sources, implementing exponential backoff retry logic and a dead-letter queue pattern to guarantee zero data loss during transient upstream outages.
- Containerized the service and deployed to GCP Cloud Run via a GitHub Actions CI/CD pipeline with parallelized build, test, and push stages, reducing deployment cycle time from 45 minutes to 8 minutes.
- **Outcome:** Enabled deprecation of 2 legacy REST endpoints (−30% API surface area); eliminated the frontend data-transformation anti-pattern; unblocked 2 queued frontend feature sprints within the first two weeks post-deployment.

---

**Project 2: Safety Content Review Tool — Accessibility Remediation**

*Baseline: A quarterly third-party accessibility audit of the Safety Content Review Tool returned 9 WCAG 2.1 Level AA violations—keyboard navigation traps, missing ARIA labels on dynamic content regions, and non-descriptive link anchor text—creating legal exposure and blocking keyboard-dependent power users who accounted for a disproportionate share of high-volume content reviewers.*

- Triaged all 9 findings with the senior frontend engineer and PM, classifying 7 as must-fix within the current sprint and 2 as design-system component debt requiring a future cycle; drafted a triage doc that was adopted as the team's standard a11y issue classification template.
- Resolved 5 ARIA defects (missing `role`, `aria-label`, and `aria-live` attributes on the moderation action panel) in React + TypeScript, cross-referencing WAI-ARIA 1.2 authoring practices to validate implementation correctness beyond automated tooling output.
- Eliminated 2 keyboard navigation traps in the media preview modal by restructuring React focus-management logic (`useRef` + programmatic `focus()` on modal open/close lifecycle events); validated corrections via manual keyboard-only testing and axe-core automated checks.
- Refactored 3 component instances to align with the team's internal design system color-token set, ensuring accessible contrast ratios (≥4.5:1 for normal text) while maintaining visual consistency with the broader design system—addressing both WCAG conformance and design-system governance in a single pass.
- Introduced axe-core as a mandatory CI gate in the team's GitHub Actions pipeline, blocking merges on any new a11y regression—the first automated accessibility enforcement in the Safety frontend's CI history.
- **Outcome:** Brought the Safety Content Review Tool from 0% to full WCAG 2.1 AA conformance on the 7 sprint-scoped items; established a repeatable a11y enforcement mechanism that prevented regression across all subsequent frontend pull requests during the remainder of the internship.

---

> **Note on the Go achievement:** The 2022/2023 municipal tournament placements (1st and 3rd) and the nationally certified amateur 2-dan rank are strong differentiators for cultural fit signaling and demonstrate self-directed mastery under competitive conditions. These belong in an **Additional Information** section at the bottom of the resume formatted as a single line: `Interests: Go (Weiqi) — China National Amateur 2-dan; Municipal Tournament Champion (2022), 3rd Place (2023); entirely self-taught, no formal coaching.` This line earns disproportionate interview conversation real estate relative to its length.
