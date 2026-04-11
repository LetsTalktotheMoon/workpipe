# Resume Prop — Mobile Platform Engineer Candidate

---

## MODULE 1: Professional Summary

Cross-domain practitioner with a behavioral science and quantitative analytics foundation, now operating at the intersection of data systems and mobile software engineering after 3+ years optimizing large-scale recommendation and operational pipelines at Temu and Didi IBG, followed by applied Kotlin/Java backend and Android SDK engineering at TikTok Safety. The progression from modeling human decision patterns (Psychology/Philosophy) through instrumented mobile event analytics (Didi IBG) to low-latency REST API design and on-device memory management (TikTok) reflects a consistent focus on system performance across abstraction layers — a perspective that translates directly into data-aware, architecture-conscious Android platform development. Currently completing concurrent M.S. degrees in Information Management (UIUC) and Computer Science (Georgia Tech), with active coursework in mobile systems and distributed computing.

---

## MODULE 2: Technology Stack "Snowball" Distribution Strategy

This table governs the internal consistency of all subsequent bullet points. Read left to right as a timeline; read vertically per skill to confirm cumulative depth.

| Skill | Temu `(8 mo)` | Didi IBG `(20 mo)` | TikTok `(6 mo)` | Cumulative Depth |
|---|---|---|---|---|
| **SQL** | ★ foundational — ad-hoc query writing, basic aggregation | ★★★ advanced — multi-schema joins, partition tuning, cross-regional warehouses | — | ~28 months |
| **Python** | ★ scripting — ETL automation, data formatting | ★★ pipeline automation, exception handling | — | ~28 months |
| **REST APIs** | ★ consumer — reads from internal data lake APIs | ★★ consumer + light integration — operational dashboards | ★★★ producer + optimizer — endpoint redesign for mobile SDK clients | ~34 months |
| **Git** | ★ version control — personal query library | ★★ team branching conventions, shared tooling | ★★★ PR workflow, CI-gated merge, Gradle integration | ~34 months |
| **Java** | — | ★ tooling-level — batch reconciliation scripts, non-production automation | ★★★ production — concurrent ingestion service, lifecycle management patterns | ~26 months |
| **Kotlin** | — | — | ★★★ production backend services, serialization layer, MVVM-aligned contracts | ~6 months |
| **Android SDK / Android Studio** | — | ★ adjacent — event schema definition for Android tracking | ★★★ SDK profiling, Memory Profiler, heap dump analysis, ANR resolution | ~8 months |
| **MVVM** | — | — | ★★ service-layer contract design aligned to client MVVM architecture | ~6 months |
| **Jetpack** | — | — | ★★ DataStore-compatible serialization schema design | ~6 months |
| **Mobile CI/CD** | — | ★ adjacent — scheduled pipeline monitoring, shell-based job orchestration | ★★★ Jenkins + Gradle build configs, automated gate checks | ~8 months |
| **Performance Optimization** | — | ★ query-level — index tuning, execution plan analysis | ★★★ API latency profiling, payload compression, GC tuning, load testing | ~26 months |
| **Memory Management** | — | — | ★★★ WeakReference patterns, heap profiling, ANR elimination | ~6 months |

**Escalation narrative (per skill dimension):**

- `Python/SQL`: *ad-hoc reporting tool → complex multi-schema production pipeline → retired from hands-on use (engineering pivot)*
- `Java`: *one-off reconciliation script (no code review process) → team-shared automation tool → production concurrent service under load*
- `REST APIs`: *read-only data ingestion → dashboard integration → API producer responsible for P99 latency SLA*
- `Performance Optimization`: *query execution time reduction → endpoint latency profiling → on-device memory leak diagnosis*

---

## MODULE 3: Resume Bullet Points

### **Temu — Data Analyst, Recommendation Algorithm**
*June 2021 – February 2022 · Shanghai, China*

- Analyzed click-stream behavioral data from 10M+ daily active sessions using SQL and Python to surface underperforming recommendation slots, producing weekly performance decks that directly informed A/B test prioritization for the algorithm team.
- Built a Python automation script consuming the internal data lake's REST APIs to replace a manual daily log extraction process, cutting analyst reporting time from 4 hours to 45 minutes per day across a 3-person team.
- Maintained a SQL query library in Git for cross-team reuse, standardizing version-controlled definitions for 20+ recurring business metrics queried by the recommendation engineering team.
- Partnered with recommendation engineers to define behavioral event schemas for mobile click tracking — mapping tap depth, scroll velocity, and session duration to feature variables consumed by the upstream ranking model.
- Produced bi-weekly data quality audit reports identifying 12 recurring pipeline anomalies per quarter; all escalated findings resolved by the data engineering team within one sprint cycle.

---

### **Didi IBG — Senior Data Analyst, Food Business**
*September 2022 – May 2024 · Beijing, China / Mexico City, Mexico*

- Owned end-to-end analytics for the Latin America food delivery vertical across 3 markets, maintaining SQL reporting pipelines that processed 500K+ daily order records against a distributed multi-region data warehouse.
- Engineered a Java-based batch automation tool to reconcile driver payout discrepancies across 6 currency regions, replacing a 16-FTE-hour weekly manual process and achieving 99.2% first-pass reconciliation accuracy.
- Optimized 30+ cross-regional SQL queries through index tuning and partition pruning, reducing average execution time from 8 minutes to under 90 seconds and eliminating recurring timeout failures in scheduled reports.
- Consumed and documented RESTful APIs exposed by the backend engineering team to integrate real-time delivery ETA signals into internal operational dashboards, enabling ops managers to detect SLA breach risks 20 minutes earlier than the prior static-report workflow.
- Established pipeline health monitoring via shell-scripted scheduled job checks and alerting rules, reducing undetected pipeline failures from a monthly average of 9 incidents to 2.
- Collaborated with the Mexico City product and Android engineering teams to define mobile event instrumentation specifications for the rider app, translating business KPIs into 40+ structured Android tracking event schemas that fed the market performance monitoring framework.

---

### **TikTok — Backend Software Engineer Intern, Safety Platform**
*June 2025 – December 2025 · San Jose, CA, USA*

- Developed and maintained Kotlin-based backend microservices within TikTok's Safety Platform powering the Android-side account security SDK, adhering to MVVM-aligned service layer contracts to preserve consistency with mobile client architecture.
- Optimized three high-frequency REST API endpoints serving the Android safety SDK client, reducing P99 latency from 340ms to 118ms through payload compression, connection pool tuning, and Redis-backed result caching.
- Integrated Jetpack-compatible Protocol Buffer serialization schemas into the backend response layer, enabling the Android SDK team to adopt Room-persisted local caching without breaking existing API contracts.
- Implemented memory-efficient batch ingestion logic in Java to handle concurrent safety event streams from 500K+ simultaneous Android sessions, reducing GC pause frequency by 41% under sustained load-test conditions.
- Contributed to the team's Mobile CI/CD pipeline by authoring Gradle build configurations and adding automated unit test coverage (87% line coverage) to two previously untested service modules integrated into the Jenkins pipeline.
- Conducted Android Studio Memory Profiler sessions on the safety SDK's on-device detection module, identifying and resolving 2 Context reference memory leaks responsible for ANR events on devices with ≤2GB RAM.

---

## MODULE 4: Key Projects

### **TEMU** — Key Project

---

**Project: Recommendation Performance Log Automated Reporting Pipeline**

*Baseline: Daily manual extraction of recommendation event logs consumed 4 analyst-hours and produced inconsistent report formats, limiting the team's capacity for strategic analysis during a period of rapid product iteration.*

- Designed and deployed a Python ETL automation script that consumed the internal data warehouse's REST APIs on a scheduled trigger, replacing all manual file-download and format-normalization steps.
- Implemented parameterized SQL queries to aggregate click-through rates, conversion funnels, and cold-start performance metrics across 15+ product categories, eliminating 60% of duplicated ad-hoc query work across the team.
- Consolidated 8 previously siloed weekly reports into a single unified output format, reducing stakeholder review cadence from 3 meetings per week to 1.
- Managed all code in Git with commit message conventions and README documentation, enabling 2 junior analysts to adopt and modify the script without breaking scheduled runs.
- **Outcome:** Team reporting workload reduced by 20 FTE-hours per week; end-to-end report turnaround time decreased from 4 hours to 45 minutes.

---

### **DIDI IBG** — Key Projects

---

**Project 1: Cross-Regional Driver Payout Reconciliation Automation**

*Baseline: Finance operations were manually reconciling driver payouts across 6 Latin American currency zones each week — a 16-FTE-hour process with a 3–5% undetected discrepancy miss rate that created downstream legal exposure in regulated markets.*

- Architected a Java automation framework that queried payout transaction records via REST APIs, applied exchange-rate normalization logic for 6 currencies, and generated structured exception reports flagged by discrepancy severity tier.
- Built parameterized SQL joins across 4 database schemas to reconcile order-level gross revenue against driver incentive ledger entries, handling NULL-state edge cases that accounted for 70% of prior manual escalations.
- Versioned the entire codebase in Git using a documented branching strategy, enabling 2 additional analysts to contribute without disrupting the weekly production run schedule.
- Validated output accuracy against a manually reconciled ground-truth sample set of 10,000 historical records before promotion to weekly production use.
- **Outcome:** Manual reconciliation effort reduced from 16 FTE-hours to 3 FTE-hours per week; first-pass accuracy improved from ~96% to 99.2%; undetected payout errors eliminated on first-pass review.

---

**Project 2: Latin America Rider App Mobile Event Instrumentation Framework**

*Baseline: The food-delivery rider-facing Android app lacked standardized behavioral event tracking across Latin American markets, making it impossible to attribute driver churn or order rejection spikes to specific in-app interaction failure points.*

- Collaborated with the Mexico City product team and Android engineering team to design a formal event taxonomy covering 40+ structured behavioral events across the app launch, order acceptance, route navigation, and earnings review flows.
- Wrote SQL-based post-release data quality validation queries to audit 6 weeks of incoming Android event streams against the defined schema, identifying 3 structural mismatches that would have invalidated 2 months of concurrent A/B test results.
- Delivered a consolidated SQL-based monitoring dashboard covering rider app core KPIs (acceptance rate, navigation drop-off, app crash correlation), reducing time-to-insight from 3 days (ad-hoc analyst requests) to 4 hours (automated refresh), consumed by 5 cross-functional stakeholders.
- Authored the event instrumentation spec document adopted by the Android engineering team as the canonical reference for all subsequent Latin America market feature releases.
- **Outcome:** Android event coverage of critical user flows increased from 34% to 89% within 2 sprint cycles post-instrumentation; A/B testing infrastructure unblocked across 3 Latin America markets.

---

### **TIKTOK** — Key Projects

---

**Project 1: Safety SDK Backend Service Latency Optimization**

*Baseline: Three REST API endpoints consumed by the Android-side account security SDK exhibited P99 latency of 300–400ms under peak traffic, triggering client-side retry storms that compounded backend load by an estimated 18% and degraded SDK responsiveness for end users.*

- Profiled all three endpoint bottlenecks using distributed tracing and SQL execution plan analysis, isolating root causes to unindexed foreign-key joins (contributing ~55% of latency) and uncompressed JSON payloads (contributing ~30%).
- Re-engineered the data serialization layer in Kotlin to apply Protocol Buffer encoding, reducing average response payload size by 63% and enabling efficient on-device deserialization compatible with the Android SDK team's Jetpack DataStore integration.
- Configured Redis-backed result caching for idempotent safety-check responses with TTL policies calibrated to account-state change frequency, reducing database read load by 35% under sustained peak traffic.
- Added connection pool sizing configuration tuned to observed concurrency patterns from production traffic analysis, eliminating connection exhaustion events that had occurred during 3 of the prior 4 peak-load windows.
- Validated all changes under load tests simulating 500K concurrent Android SDK clients; P99 latency decreased from 340ms to 118ms, falling within the team's 150ms SLA threshold for the first time.
- **Delivery:** Merged via the team's Mobile CI/CD pipeline (Jenkins + Gradle); PR passed all automated regression suites and performance gate checks on first submission.

---

**Project 2: Android Safety SDK On-Device Memory Leak Resolution**

*Baseline: The safety SDK's real-time content-detection module triggered ANR (Application Not Responding) events on Android devices with ≤2GB RAM during sustained background operation, producing a 2.1% crash rate in canary builds that blocked production release.*

- Reproduced ANR conditions using Android Studio's Memory Profiler in heap dump analysis mode, tracing root cause to two static callback registries retaining live `Context` references beyond the `Activity` lifecycle boundary.
- Refactored callback lifecycle management in Java to replace strong `Context` references with `WeakReference` wrappers and introduced explicit deregistration hooks keyed to `onDestroy()` lifecycle callbacks, aligned to Android platform conventions for long-lived SDK components.
- Re-ran Memory Profiler sessions post-fix across 4 device RAM profiles (1GB, 2GB, 3GB, 4GB) under 30-minute sustained background load, confirming full elimination of heap growth anomalies and validating GC pause behavior within acceptable bounds.
- Authored an internal Android SDK development guide entry codifying the `WeakReference` + explicit deregistration pattern as a mandatory code review checklist item for all future callback-heavy SDK components.
- **Outcome:** ANR-triggered crash rate dropped from 2.1% to 0.0% across all tested device profiles in canary validation; fix shipped to production in the subsequent SDK release cycle with no regression incidents reported.

---

*Optional Addendum — Additional Activities (for "Additional Information" section):*

**Interests:** Competitive Go (Weiqi) — China National Certification Amateur 2-Dan; 1st place, 2022 Municipal Open; 3rd place, 2023 Municipal Open; self-taught without formal coaching.
