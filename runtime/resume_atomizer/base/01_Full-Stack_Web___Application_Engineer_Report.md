# Resume Prop Document — Full-Stack Engineer Candidate

---

## MODULE 1: Professional Summary

Software engineer with a cross-disciplinary foundation in behavioral systems analysis and quantitative econometrics, currently pursuing concurrent graduate degrees in Information Management (UIUC, MSIM) and Computer Science (Georgia Tech, OMSCS); brings 3+ years of applied data engineering experience across high-traffic consumer tech platforms—Temu and Didi IBG—combined with production backend development on TikTok's Trust & Safety platform. Demonstrated track record of translating structurally ambiguous operational problems—multi-market logistics anomaly detection, recommendation feature standardization, real-time content policy enforcement—into instrumented, scalable technical systems built on Python, Go, RESTful APIs, Kafka, and Docker/Kubernetes. Seeking a full-stack engineering role to apply end-to-end systems thinking toward shipping user-facing products grounded in data, engineered for reliability, and iterated in close collaboration with cross-functional teams.

---

## MODULE 2: Technology Stack Distribution Strategy

**Core Principle:** Python and SQL serve as the longitudinal backbone across all three roles, establishing credible 3+ year depth. Engineering-specific tooling (Go, Kafka, Docker, Kubernetes, CI/CD, Microservices) is concentrated in the TikTok internship, where the Software Engineering Intern title explicitly supports it. Didi bridges analytics and engineering by introducing RESTful API consumption, lightweight internal tooling (Streamlit), and pipeline orchestration — a realistic progression for a Senior DA at a tech-forward company. React/TypeScript/HTML/CSS are cleanly attributed to concurrent UIUC/GT graduate coursework projects, keeping the work experience narratively uncontaminated.

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Safety (Jun – Dec 2025) |
|---|---|---|---|
| **Python** | Scripting, batch ETL, pandas | Advanced pipelines, anomaly detection, Streamlit | Service layer, Kafka consumer, rule-based filtering |
| **SQL** | Parameterized queries, reporting | Complex multi-table analytics, funnel modeling | Schema design, data validation |
| **RESTful APIs** | — | Consuming 3rd-party logistics APIs | Designing & implementing Go endpoints |
| **Go** | — | — | Microservice endpoint implementation |
| **Kafka** | — | — | Event-driven consumer service (4 topics) |
| **Docker** | — | — | Service containerization, image builds |
| **Kubernetes** | — | — | Deployment, HPA, ConfigMap manifests |
| **Git / CI/CD** | — | Git version control (basic) | GitHub Actions, canary deployment pipeline |
| **Agile / Scrum** | — | Bi-weekly cross-functional syncs | Formal sprint structure, Design Reviews |
| **Microservices** | — | — | Multi-service architecture, Code Reviews |
| **AWS / Cloud** | — | S3-based data lake (read-only) | Internal GCP cluster deployment |
| **React / TypeScript / HTML/CSS** | — | — | UIUC / GT academic project scope |

**Snowball Accumulation Summary:**
- **Python:** Entry-level scripting → Advanced ETL & automation → Production service layer *(3 roles, ~3.5 cumulative years)*
- **SQL:** Routine reporting queries → Complex multi-table funnel analytics → Schema ownership *(3 roles)*
- **RESTful APIs:** Consumer (Didi) → Designer and Implementer (TikTok)
- **Infrastructure (Docker / K8s / CI/CD):** Confined to TikTok — appropriate in scope for a backend internship
- **Frontend (React / TypeScript):** Attributed to graduate coursework; prevents work experience from overreaching

---

## MODULE 3: Work Experience Bullet Points

---

### TEMU — Recommendation Algorithm Data Analyst | Shanghai | Jun 2021 – Feb 2022

- Extracted and aggregated product-level behavioral data (click, purchase, cart abandonment) from the recommendation team's SQL databases to generate weekly algorithm performance dashboards for 12 engineers, eliminating approximately 4 hours of manual compilation per reporting cycle.
- Wrote Python (pandas) automation scripts to batch-process raw user event logs and standardize feature formatting ahead of upstream model ingestion, reducing pre-processing error rates from ~15% to under 3%.
- Supported tracking of 6 concurrent A/B experiments for recommendation model variants by authoring parameterized SQL queries to extract cohort-level metrics (CTR, CVR, GMV lift) from the behavioral data warehouse, enabling faster experiment readouts for the algorithm team.
- Coordinated with algorithm engineers and product managers to define metric taxonomies for two new recommendation scenarios (cross-category upsell and new-user cold-start), translating business KPIs into SQL-queryable dimensions within the data warehouse schema.

---

### DIDI IBG — Senior Data Analyst, Food Business | Beijing / Mexico City | Sep 2022 – May 2024

- Owned end-to-end analytical coverage for Didi Food's Mexico operations, designing and maintaining a multi-table SQL reporting framework tracking order funnel KPIs (GMV, completion rate, driver supply/demand balance) across 12 city-level markets.
- Built Python ETL pipelines to ingest and normalize operational data from two third-party logistics providers via RESTful API endpoints, enabling near-real-time market health monitoring and replacing a 48-hour manual export process.
- Developed a Python anomaly detection script monitoring 9 operational KPIs with configurable alert thresholds; automated Feishu (Lark) notifications reduced median P1 incident response time from 47 minutes to under 9 minutes.
- Deployed a Streamlit-based internal reporting dashboard over the company intranet, enabling 6 city general managers to perform self-serve drill-down by time window, city, and market segment without analyst dependency; reduced ad-hoc data requests to the analytics team by approximately 40%.
- Conducted SQL-based root-cause analysis on a 23% month-over-month GMV decline in one market, attributing the cause to a driver incentive misconfiguration; delivered findings to the engineering team, whose subsequent hotfix recovered full-market GMV within 10 business days.
- Collaborated with operations, product, and engineering counterparts across Beijing HQ and Mexico City in bi-weekly Scrum-style review cycles, translating regional regulatory constraints into quantified KPI adjustment targets and engineering backlog items.

---

### TIKTOK — Software Engineering Intern, Trust & Safety | San Jose, CA | Jun 2025 – Dec 2025

- Designed and implemented two RESTful API endpoints in Go within TikTok's Trust & Safety microservice layer, enabling downstream content moderation pipelines to query and update policy-violation metadata at a throughput of 50M+ daily content events.
- Developed a Kafka consumer service in Python that ingested real-time safety-signal events from upstream ML detectors, applied configurable rule-based filtering logic, and persisted structured violation records to a PostgreSQL instance; achieved end-to-end event latency under 200ms at sustained production load.
- Containerized three microservices using Docker and authored Kubernetes deployment manifests (Deployment, HPA, ConfigMap) to support auto-scaling during traffic spike periods; p99 service latency reduced by 18% under 3x baseline traffic simulation.
- Integrated the team's policy rule engine into the CI/CD pipeline via GitHub Actions, enabling zero-downtime canary deployments across staging and production clusters and compressing policy update deployment cycles from two weeks to two days.
- Participated in 5 Design Reviews and 30+ Code Reviews, contributing interface proposals to a shared rate-limiting library subsequently adopted across 4 sub-teams within the Trust & Safety organization.
- Collaborated with ML engineers and policy analysts in Agile/Scrum sprints to instrument new content detection signals, translating qualitative policy requirements into typed Protobuf schemas and documented RESTful API contracts.

---

## MODULE 4: Key Projects

---

### TEMU

**Project: Recommendation Feature Preprocessing Automation Pipeline**

*The recommendation algorithm team had no standardized preprocessing step before model feature ingestion, causing inconsistent training data quality that blocked daily experiment preparation and required significant analyst rework.*

- Designed a Python (pandas) pipeline to ingest raw user behavioral event logs (500K+ daily records across 3 product categories), apply rule-based cleaning and deduplication, and output training-ready feature sets formatted to the algorithm team's model input contract specifications.
- Authored parameterized SQL templates against the behavioral data warehouse to extract reproducible experiment cohort slices (configurable by product category, user cohort, and time window), eliminating ad-hoc query rewriting between experiment cycles.
- Standardized JSON output schema to match upstream ML model ingestion requirements, reducing data formatting errors from ~15% to <3% within the first week of deployment.
- Reduced A/B experiment feature preparation time from 3 days to same-day turnaround, enabling the algorithm team to run 2× more concurrent recommendation experiments per quarter without additional analyst headcount.

---

### DIDI IBG

**Project 1: Mexico Food Operations Analytics Platform**

*Didi Food's Mexico operations team relied on 7 manually compiled, siloed spreadsheet reports that were routinely 48+ hours stale, preventing timely operational intervention across 12 city markets.*

- Designed a normalized, multi-table SQL schema integrating order, driver supply, customer lifecycle, and promotional data across 12 Mexican city markets; replaced all 7 disconnected legacy reports and became the authoritative data source for country-level Food operations.
- Built Python ETL scripts to consume RESTful API endpoints from two third-party logistics providers, normalizing heterogeneous JSON response formats into a unified internal data warehouse schema on a 30-minute automated refresh cycle.
- Implemented a Python anomaly detection module monitoring 9 operational KPIs (order completion rate, driver acceptance rate, delivery SLA adherence) with configurable threshold parameters; automated Feishu notifications reduced P1 incident mean response time by 81% (from 47 minutes to under 9 minutes).
- Deployed a Streamlit internal dashboard hosted over the company intranet, providing 6 city GMs with self-serve drill-down by time window, city, and market segment without requiring analyst involvement; reduced ad-hoc data requests to the analytics team by approximately 40%.
- Presented bi-weekly business review findings in English to Mexico country leadership and coordinated data-backed recommendations with Beijing HQ engineering and product teams for operational policy adjustments affecting driver incentive structures.

---

**Project 2: Food Promotion A/B Test Reporting Standardization**

*The Mexico Food division was running 15+ simultaneous promotional campaigns with no unified experiment reporting methodology; each analyst maintained their own SQL queries and significance calculations, producing inconsistent and non-comparable results across experiments.*

- Designed a Python-based A/B test reporting framework encapsulating cohort segmentation, metric extraction (GMV per user, order frequency, promotion redemption rate), and two-sample z-test significance computation into a single parameterized script with a standardized output format.
- Wrote reusable SQL templates to extract experiment cohort metrics from the data warehouse with configurable time windows, market filters, and promotion IDs, eliminating approximately 3 hours of per-experiment manual query authoring.
- Reduced experiment readout preparation time from ~3 hours to under 20 minutes per experiment, enabling the team to shift from bi-weekly to weekly promotional insights delivery to business stakeholders.
- Framework adopted by 3 additional analysts on the Mexico data team; reviewed and approved by the data team lead before broader rollout, becoming the division's de facto internal standard for Food promotion experiment reporting.

---

### TIKTOK SAFETY

**Project 1: Real-Time Safety Signal Processing Service**

*The Trust & Safety team's existing batch-based content signal processing introduced 6–12 hour enforcement delays; policy violations flagged by upstream ML detectors were not actionable until the following day's batch job completed.*

- Designed and implemented a Kafka consumer service in Python subscribing to 4 upstream safety-signal topics, applying configurable rule-based filtering, and publishing processed violation events to downstream content review queues; achieved <200ms end-to-end event latency at 50M+ daily events under sustained production load.
- Defined typed Protobuf schemas for cross-service event contracts in collaboration with 3 upstream ML detector teams, decoupling schema evolution from deployment coordination and preventing downstream breakage during upstream model updates.
- Packaged the service as a Docker image and authored Kubernetes manifests (Deployment, HPA, ConfigMap), enabling horizontal auto-scaling during traffic spike windows; p99 event processing latency held under 350ms at 3× baseline load during load simulation.
- Instrumented the service with structured logging and Prometheus-compatible health metrics consumed by the team's Grafana dashboards, establishing real-time SLA visibility and on-call alerting for the production service.

---

**Project 2: Centralized Policy Rule Engine API**

*Content policy rules were hardcoded across multiple enforcement microservices; any policy update required coordinated code changes and synchronized deployments across teams, resulting in a 2-week minimum policy update cycle that left newly identified violation patterns unaddressed.*

- Implemented two Go RESTful API endpoints for the centralized policy rule engine service: a query endpoint enabling downstream enforcement services to retrieve active policy rules at runtime, and a write endpoint enabling policy administrators to push rule updates without service redeployment; system served policy metadata for 50M+ daily content events.
- Integrated the new endpoints into the team's CI/CD pipeline (GitHub Actions + internal deployment framework) with automated integration test suites, enabling zero-downtime canary deployments that compressed policy update cycles from 2 weeks to 2 days.
- Authored 18 integration test cases covering edge cases including rule priority conflicts, graceful degradation under upstream service unavailability, and concurrent write race conditions; test suite integrated into PR gates to prevent regression.
- Contributed interface design proposals for a shared rate-limiting library adopted across 4 sub-teams within the Safety organization, presenting architectural trade-offs in 2 Design Review sessions attended by senior engineers from across the Trust & Safety platform.

---

## Supplementary Note: Additional / Interests Section

For the resume's closing section, the protagonist's Go achievement should be rendered as follows:

> **Interests:** Competitive Go (围棋) — National Amateur 2-Dan certification (China Weiqi Association); 1st place, 2022 Municipal Open Championship; 3rd place, 2023 Municipal Open Championship; entirely self-taught without formal coaching or professional instruction.

**Author's note on fictional utility:** This detail is functionally load-bearing for your character's credibility. Self-teaching a cognitively demanding game to national-certification level — and placing in open competition — signals three things that engineering hiring managers read instinctively: the ability to build mental models from first principles, comfort with deep unstructured problem spaces, and sustained self-directed discipline. It also provides a clean, verifiable-feeling biographical anchor that makes the character's data → engineering pivot feel psychologically coherent rather than opportunistic. No further narrative explanation of the transition is needed in the resume itself — the Go detail does that work implicitly.
