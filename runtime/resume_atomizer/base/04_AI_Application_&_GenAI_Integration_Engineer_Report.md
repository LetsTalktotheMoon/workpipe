## Module 1: Professional Summary

Cross-domain systems professional with 3+ years of production experience spanning recommendation algorithm analytics and international operations data infrastructure, currently completing concurrent M.S. degrees in Information Management (UIUC) and Computer Science (Georgia Tech); a career arc from behavioral science through quantitative finance to production backend engineering provides an atypical but high-signal foundation for decomposing ambiguous stakeholder requirements into structured, auditable AI architectures. Brings direct hands-on experience designing and deploying RAG pipelines, LLM-based content classification systems with structured confidence scoring, and Python/Java microservices on AWS—delivered within a Trust & Safety production environment at scale during a backend engineering internship at TikTok. Carries a documented capacity for independent mastery of complex, high-dimensional formal systems under zero institutional scaffolding, applied consistently across data product ownership, cross-border business operations, and large-scale AI integration engineering.

> **Design note on the last sentence:** The Go achievement (self-taught to national 2-dan certification, zero professional coaching) is embedded here as a structural signal rather than a trivia line. A senior hiring manager reads it as: "can self-onboard to systems of extreme complexity without hand-holding." It stays out of the Summary section itself—placed in a dedicated **Awards & Activities** section at the bottom of the actual resume, formatted as:
> `Amateur 2-Dan, China Weiqi Association Certification | 2022 Shanghai Municipal Championship (1st) · 2023 (3rd) | Self-taught; no institutional training`

---

## Module 2: Technology Stack Snowball Distribution Strategy

### Core Logic

| Technology | Temu (2021.6–2022.2) | Didi IBG (2022.9–2024.5) | TikTok Security (2025.6–2025.12) | Cumulative Signal |
|---|---|---|---|---|
| **Python** | ● Entry — pandas, scripting, matplotlib | ●● Mid — ETL orchestration, Kafka consumers, Flask REST | ●●● Advanced — RAG integration, LLM harnesses, Pydantic validation | **3+ years**, compounding context |
| **SQL / HiveQL** | ● Operational — A/B query extraction | ●● Analytical — multi-table aggregations, funnel analysis | ○ Supporting role only | **3+ years** |
| **Kafka** | — | ● Consumption — event stream ingestion for ops dashboards | ●● Architecture — consumer design, offset management | ~2 years |
| **REST APIs** | — | ● Integration context — internal data platform calls | ●● Design & ownership — 6 endpoints, Spring Boot | ~2 years |
| **Java / Spring Boot** | — | — | ● Core development — microservice implementation | 6 months |
| **LLM / RAG / GenAI** | — | — | ●● Primary deliverable — production classification system | 6 months |
| **LangChain / LangGraph** | — | — | ●● Pipeline + agent orchestration | 6 months |
| **Vector Stores (Pinecone)** | — | — | ●● Document ingestion, chunking, retrieval | 6 months |
| **Prompt Engineering** | — | — | ●● Structured output contracts, eval harnesses | 6 months |
| **Pydantic** | — | — | ● Schema validation, LLM output parsing | 6 months |
| **AWS / EKS** | — | — | ● Deployment target | 6 months |
| **Kubernetes / CI/CD** | — | — | ● Operational ownership | 6 months |
| **Confidence Scoring** | — | — | ●● Classification scoring, taxonomy matching | 6 months |
| **Telemetry / Observability** | — | — | ●● OpenTelemetry + Datadog SLO dashboards | 6 months |

### Snowball Narrative in One Paragraph

Python and SQL anchor across all three roles, providing the mandatory "3+ years" ATS signal. Kafka first appears at Didi IBG as a passive consumption tool for operational dashboards (analyst-level usage), then resurfaces at TikTok as an actively designed consumer service—demonstrating compounding depth. REST APIs follow the same arc: at Didi, the candidate consumes internal APIs as a data consumer; at TikTok, they design and own API surface area. The entire AI/GenAI stack (LLM, RAG, LangChain, LangGraph, Pinecone, Pydantic, Prompt Engineering, Confidence Scoring) is concentrated in the TikTok internship, which is accurate and defensible—this is exactly when and where a data professional transitioning through graduate CS study would first build production AI systems.

---

## Module 3: Resume Bullet Points

---

### Data Analyst, Recommendation Algorithms · Temu (PDD Holdings) · Shanghai · Jun 2021 – Feb 2022

- Authored and maintained 12 parameterized HiveQL query templates to extract daily click-stream, impression, and conversion events from A/B experiment partition tables, reducing ad-hoc data request turnaround for the algorithm product team by approximately 40%
- Automated weekly experiment summary reporting via Python (pandas, openpyxl), eliminating ~6 hours of manual spreadsheet consolidation per analyst per experiment cycle
- Partnered with 3 algorithm engineers and 2 product managers to define 8 standardized offline evaluation metrics for cold-start item recommendation quality, supporting a controlled experiment that yielded a 3.2% lift in new-item click-through rate over Q3 2021
- Maintained Hive/Spark SQL batch jobs processing 50M+ daily user interaction events to generate offline feature analysis datasets consumed by the recommendation model training pipeline
- Documented data dictionary for 4 core recommendation event tables, reducing onboarding time for new analysts and decreasing schema-related data pulls errors by an estimated 60%

---

### Senior Data Analyst, Food — International Business Group · Didi Global · Beijing / Mexico City · Sep 2022 – May 2024

- Led end-to-end data analysis for Didi Food's Mexico market launch across 5 cities, defining a 47-metric KPI framework spanning merchant acquisition, order completion rate, delivery SLA compliance, and customer retention—adopted as the cross-market reporting standard across 4 international Food markets
- Engineered Python ETL pipelines integrating 3 internal data platforms (order management system, merchant operations, financial settlement) via REST API and batch extracts, consolidating cross-market data into a single analytical dataset and reducing monthly reconciliation time from 72 hours to 4 hours
- Developed incremental Kafka event consumers in Python to capture real-time order lifecycle events, powering operational dashboards with same-day merchant fulfillment visibility for the Mexico City launch team
- Constructed complex multi-table SQL analytical queries—joining order, merchant, and geo data across 6 tables—to track weekly merchant performance trends, surfaced in VP-level business review decks presented to leadership in both Beijing and Mexico City
- Collaborated cross-functionally with product, engineering, and local operations teams across two time zones to instrument 15 new behavioral events for funnel analysis; findings directly informed a product decision that improved cart-to-order conversion by 8.7% in the Mexico City pilot
- Partnered with business intelligence and finance stakeholders to establish data governance standards for the international Food reporting layer, resolving 3 conflicting KPI definitions that had caused repeated discrepancies in HQ vs. local reporting

---

### Software Engineer Intern, Trust & Safety Platform · TikTok (ByteDance) · San Jose, CA · Jun 2025 – Dec 2025

- Developed Java/Spring Boot microservices for the policy management API within TikTok's Trust & Safety platform, implementing 6 new REST endpoints to support content classification workflow automation and integrating with upstream Kafka event queues for asynchronous policy update propagation
- Designed and implemented a Retrieval-Augmented Generation (RAG) pipeline in Python using LangChain and a Pinecone vector store, ingesting 200+ policy documents to enable policy-aware context injection at LLM inference time—improving classification confidence scores by 18% versus the keyword-matching baseline in controlled A/B evaluation
- Engineered structured Prompt Engineering templates and Pydantic-validated JSON output schemas for TikTok's internal content safety LLM, enabling deterministic downstream confidence scoring across 4 violation taxonomy categories
- Built a LangGraph-based multi-step AI agent workflow to handle ambiguous content cases requiring cross-reference across multiple taxonomy nodes, reducing manual review escalation rate by 12% in the pilot evaluation cohort
- Instrumented classification microservices with OpenTelemetry distributed tracing and Datadog SLO dashboards, reducing mean incident detection latency from ~45 minutes to under 8 minutes and producing audit-ready telemetry records for compliance review
- Containerized services with Docker and deployed on AWS EKS via Kubernetes manifests; automated build and deployment through GitHub Actions + ArgoCD CI/CD pipelines, compressing deployment cycle time from 2 days to under 30 minutes

---

## Module 4: Key Projects

---

### Temu — Recommendation Experiments

---

**Project: Recommendation Experiment Offline Metrics Automation System**

*The recommendation algorithm team managed 8–12 concurrent A/B experiments with no standardized offline evaluation infrastructure; analysts wrote one-off HiveQL queries from scratch for each experiment cycle, producing inconsistent metric definitions that made cross-experiment comparison unreliable and consumed 4+ analyst-hours per experiment per week.*

- Designed a Python-based query template engine that parameterized 12 reusable HiveQL templates covering click-through rate, cart conversion, new-item exposure rate, and GMV lift, enabling standardized evaluation output across all active A/B experiments
- Integrated pandas-based post-processing scripts to compute statistical significance flags and confidence intervals per experiment variant, providing algorithm engineers with directly actionable offline signals without requiring additional data pulls
- Reduced per-experiment metric extraction time from 4+ hours of manual query authoring to under 20 minutes via automated batch dataset generation triggered by experiment table partition availability
- Standardized output schema across 12 experiment types, enabling apples-to-apples cross-experiment ranking for the first time—directly supporting the algorithm team's monthly model selection review process
- Validated metric definitions in 3 working sessions with algorithm engineers and product managers, resolving 2 conflicting definitions for "conversion" that had previously caused discrepancies between algorithm reports and product dashboards

---

### Didi IBG — Food International

---

**Project: Mexico Food Operations Cross-Market Analytics Pipeline**

*Didi Food's Mexico launch operated without a unified data layer connecting in-country operational events to Beijing HQ reporting systems; business reviews were powered by manually assembled SQL extracts, a process requiring 3 days of analyst effort per monthly cycle and introducing reconciliation errors that delayed strategic decision-making by 5–7 business days.*

- Designed a Python ETL orchestration pipeline with incremental Kafka event consumption to capture order lifecycle events (placed, accepted, dispatched, delivered, cancelled) from 5 Mexican cities in near real-time, replacing T+1 batch exports as the operational data source
- Integrated REST API calls to 3 internal platforms—order management, merchant operations, and financial settlement—normalizing data schemas across systems with inconsistent field naming conventions and timezone handling
- Reduced monthly cross-market reconciliation time from 72 hours to 4 hours, freeing 2 analyst FTEs from manual data consolidation and enabling same-week strategic response to operational trends
- Defined and documented a 47-metric KPI taxonomy covering merchant acquisition funnel, fulfillment SLA compliance, cancellation attribution, and customer LTV proxies; the taxonomy was subsequently adopted as the international Food metrics standard across Mexico, Brazil, South Africa, and Australia
- Delivered weekly data-driven business review decks to Director and VP-level stakeholders across Beijing and Mexico City, translating pipeline output into operational recommendations that informed merchant incentive budget allocation decisions

---

**Project: Real-Time Merchant Fulfillment Performance Monitoring System**

*Operations managers in Mexico had no live visibility into merchant-level SLA degradation; relying exclusively on T+1 batch reports meant fulfillment breaches affecting hundreds of orders were identified an average of 18 hours after onset, with no escalation pathway before customer complaint volumes spiked.*

- Built Python Kafka consumer services to subscribe to the order event stream and apply sliding-window aggregation logic, computing rolling 15-minute fulfillment SLA compliance rates per merchant with configurable alert thresholds
- Developed Python/Flask REST API endpoints serving computed merchant performance scores to the operations dashboard, supporting concurrent access by 30+ operations staff across Mexico City, Guadalajara, and Monterrey
- Implemented anomaly detection rules flagging merchants with SLA compliance rates below 85% for two consecutive 15-minute windows, triggering automated escalation notifications to the regional operations lead
- Reduced average SLA breach detection latency from 18 hours to under 1 hour, enabling proactive merchant intervention before customer complaint rates reached escalation thresholds

---

### TikTok Security — Trust & Safety Platform

---

**Project: Policy-Aware Content Classification RAG System**

*TikTok's Trust & Safety automated content review pipeline applied a static keyword-matching classifier against 200+ pages of evolving policy documentation spanning 4 violation taxonomy categories; the classifier had no mechanism to reference updated policy language at inference time, causing persistent edge-case misclassification that inflated manual review queues and created compliance exposure.*

- Designed a RAG pipeline using Python and LangChain to ingest 200+ policy documents, applying 512-token chunk segmentation with metadata tagging by taxonomy category (Hate Speech, CSAM-Adjacent, Misinformation, Platform Integrity) and embedding storage in a Pinecone vector store
- Engineered a multi-turn Prompt Engineering framework using Pydantic BaseModel schemas to enforce structured JSON output contracts from the LLM, binding each inference call to a required output format of `{violation_category, confidence_score, supporting_policy_clauses, recommended_action}`
- Achieved an 18% improvement in classification confidence scores compared to the keyword-matching baseline, validated on a 10,000-sample holdout set drawn from historical human-reviewed cases
- Integrated the RAG classification service as a new REST endpoint within the existing Spring Boot policy management microservice, with request payload validation via Pydantic and P95 latency maintained below 300ms under load testing at 500 RPS in the staging environment
- Implemented a LangGraph-based multi-step agent workflow for ambiguous cases requiring cross-taxonomy policy reconciliation, routing low-confidence results through a secondary retrieval step before final classification output—reducing manual escalation rate by 12% in the pilot evaluation cohort against a 3,000-case validation set

---

**Project: Classification Pipeline Observability & Event Ingestion Infrastructure**

*The content classification pipeline lacked a standardized observability layer; production incidents were diagnosed through unstructured log searches across distributed services, extending mean incident resolution time to 45+ minutes and leaving the team unable to produce auditable SLO evidence for quarterly compliance reviews.*

- Built Java/Spring Boot Kafka consumer services to ingest 200K+ daily content classification events from upstream moderation queues, applying Pydantic-equivalent schema validation at the Java layer to enforce structured event payloads and reject malformed records before pipeline entry
- Instrumented all classification service components with OpenTelemetry distributed traces and custom Datadog metrics, establishing 12 SLO dashboards covering P50/P95/P99 latency, error rates by taxonomy category, confidence score distribution drift, and Kafka consumer lag
- Reduced mean incident detection time from ~45 minutes to 8 minutes post-instrumentation, with telemetry records directly cited in the team's Q4 2025 compliance audit submission as evidence of monitoring adequacy under the platform's internal AI governance framework
- Containerized the classification microservice using Docker and deployed on AWS EKS via versioned Kubernetes manifests; established GitHub Actions + ArgoCD CI/CD automation with branch-based environment promotion, compressing deployment cycle from 2 days to under 30 minutes and enabling same-day hotfix deployment during the pilot rollout window

---

> **Completeness note for production use:** The four modules above cover Summary, Stack Strategy, Bullet Points, and Key Projects. A production-ready resume would additionally require: (1) **Education** section listing UIUC MSIM and GT OMSCS as concurrent degrees "Expected May 2026"; (2) **Technical Skills** section organizing the ATS keyword pool by category (Languages, Frameworks, AI/ML, Cloud & Infra, Data); (3) **Awards & Activities** section for the Go certification and championships. These can be generated on request.
