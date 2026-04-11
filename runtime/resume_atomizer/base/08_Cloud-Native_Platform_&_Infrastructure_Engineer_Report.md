## MODULE 1 — PROFESSIONAL SUMMARY

Data engineer and backend developer with 3+ years of large-scale systems experience across recommendation infrastructure (Temu), cross-regional food-delivery analytics (Didi IBG), and production security backend services (TikTok), now completing dual graduate programs in Information Management (UIUC MSIM) and Computer Science (Georgia Tech OMSCS) concurrently. A cross-disciplinary foundation in behavioral modeling and quantitative risk analysis builds the habit of reasoning from system-level first principles—applied consistently whether designing dimensional data schemas for billion-row event streams, instrumenting distributed pipelines for observability, or decomposing Go-based microservices for fault-isolated, asynchronous processing. Brings production-grade experience in Python pipeline engineering, Go service development, Kubernetes-orchestrated deployments, and Prometheus/OpenTelemetry instrumentation, targeting cloud-native platform roles where data-driven design and infrastructure reliability converge.

---

## MODULE 2 — TECH STACK SNOWBALL DISTRIBUTION MAP

The following table maps each ATS keyword to its first introduction, depth level, and cumulative exposure. **Core anchor technologies (Python, SQL/Data Modeling) must appear in 3 roles to satisfy "3+ years" ATS hard filters.** Go is introduced as a tooling language at Didi and escalates to primary service language at TikTok.

| Technology | Temu `2021–2022` | Didi IBG `2022–2024` | TikTok `2025` | Cumulative Signal |
|---|---|---|---|---|
| **Python** | ✓ ETL scripting, A/B analysis | ✓✓ Pipeline orchestration, PySpark | ✓ Internal tooling refactor | **3+ yrs — anchor** |
| **SQL / Data Modeling** | ✓ Feature extraction queries | ✓✓ Dimensional schema, BigQuery optimization | ✓ Service-layer schema design | **3+ yrs — anchor** |
| **Distributed Systems** | ✓ Large-scale Hive DAG consumption | ✓✓ Spark partition strategy, Kafka stream | ✓✓ Event-driven microservice arch | **3+ yrs (progressive depth)** |
| **Asynchronous Processing** | — | ✓ Kafka topic consumption | ✓✓ Kafka producer/consumer service | **2+ yrs** |
| **Cloud Platforms (GCP/AWS)** | — | ✓ GCP: BigQuery, Dataproc, GCS, Pub/Sub | ✓✓ GCP + AWS: service deployment, IAM | **2+ yrs** |
| **Go / Golang** | — | ✓ Internal metric-export CLI tooling | ✓✓ Primary production service language | **~2.5 yrs** |
| **Observability — Datadog** | — | ✓✓ Dashboard authoring, alert rule config | ✓ Complementary monitoring | **2+ yrs** |
| **Observability — Prometheus / OpenTelemetry** | — | — | ✓✓ Metrics exposition, trace instrumentation | 6 mo (production depth) |
| **APIs (REST / gRPC)** | — | ✓ API consumption + basic interface design | ✓✓ Full gRPC proto design, versioning, REST | **2+ yrs** |
| **Kubernetes** | — | — | ✓✓ Deployment, HPA, PDB, ConfigMap, rollout | 6 mo (production depth) |
| **Microservices** | — | — | ✓✓ Service decomposition, inter-service comms | 6 mo (production depth) |
| **Terraform / IaC** | — | — | ✓ Module configs, IAM bindings, storage bucket | 6 mo (contributing depth) |
| **High Availability** | — | — | ✓✓ HPA autoscaling, PodDisruptionBudget, canary | 6 mo (production depth) |
| **C++** | — | — | ✓ Integration debugging with existing C++ shared libs | 6 mo (exposure) |
| **Istio / Service Mesh** | — | — | ✓ Traffic policy config for canary rollout | 6 mo (exposure) |
| **Backend Development** | — | ✓ Go CLI tools, pipeline backends | ✓✓ Go service full lifecycle | **2+ yrs** |

**Progression narrative:** Python/SQL/Data Modeling establish the three-year depth floor. Distributed systems thinking begins at Temu (large-scale Hive) and deepens through Kafka streams at Didi into event-driven microservice architecture at TikTok. Go enters as a pragmatic tooling choice at Didi (consistent with Didi's Go-heavy engineering culture) and becomes the primary service language at TikTok. Cloud, observability, and Kubernetes follow the canonical analyst-to-engineer trajectory: consuming managed services → instrumenting dashboards → owning deployment manifests.

---

## MODULE 3 — RESUME BULLET POINTS

### Temu · Recommendation Algorithm Data Analyst · Shanghai · Jun 2021 – Feb 2022

- Authored Python ETL scripts to extract, deduplicate, and normalize raw clickstream logs (50M+ daily records) from internal Hive tables, eliminating 4 hours of manual data preparation per analyst per week across a 6-person analytics team.
- Designed and maintained SQL-based feature quality dashboards tracking null rate, value distribution shift, and coverage across 30+ recommendation input signals; identified a silent upstream feature drift incident 72 hours before degradation surfaced in homepage CTR metrics.
- Executed statistical result analysis (t-test, CUPED variance reduction) for 8 recommendation A/B experiments, delivering standardized reporting decks that drove go/no-go decisions for algorithm and product leadership.
- Built a scheduled Python + Hive SQL reconciliation job that cross-validated recommendation serving logs against upstream event-tracking data, reducing discrepancy investigation cycles from 3 business days to same-day resolution.
- Documented data lineage and feature definitions for 3 core recommendation modules in the team's internal data dictionary, reducing new-hire onboarding time for 2 analysts to under 2 weeks.

---

### Didi IBG · Senior Data Analyst, Food Business · Beijing / Mexico City · Sep 2022 – May 2024

- Designed a dimensional data model (fact + dimension star schema on BigQuery) consolidating events from 5 upstream Kafka topics into a single operational data mart; pre-aggregated materialized views reduced ad hoc SLA metric query latency from ~40 minutes to under 90 seconds.
- Built a multi-city demand forecasting pipeline (Python/PySpark on GCP Dataproc) generating daily 7-day order volume predictions for 12 Mexican metros, achieving 8.3% MAPE versus a 17.1% static-average baseline, directly informing monthly rider incentive budget re-allocation.
- Developed a Go-based CLI tool to automate daily business metric export (JSON → GCS → downstream BI dashboards), replacing a 2-hour manual Excel process; the tool was adopted by 3 partner analytics teams within 6 weeks of release.
- Instrumented a Datadog monitoring layer covering 15 SLA-critical metrics (order fulfillment rate, P90 courier dispatch latency, refund rate by failure mode), enabling Mexico City operations to detect and triage service degradation events in under 5 minutes during peak-hour windows.
- Led data modeling reviews for a new-city analytics launch framework, defining 22 standardized KPIs and formal data contracts with 4 upstream engineering owners; framework was reused for 3 subsequent Latin American city rollouts, reducing per-city analytics setup time from 6 weeks to under 2 weeks.
- Coordinated A/B test design and data access across 4 cross-functional stakeholders spanning Beijing (UTC+8) and Mexico City (UTC−6) time zones, delivering validated experiment results within committed sprint cycles.

---

### TikTok · Backend Software Engineer Intern, Security · San Jose · Jun 2025 – Dec 2025

- Designed and implemented a Go-based security event ingestion microservice consuming events from a Kafka topic, applying rule-based enrichment (IP geolocation via internal GeoIP RPC, device fingerprint matching via gRPC lookup service), and routing enriched payloads to downstream alerting and audit archival consumers; service sustained 12,000+ events/second at P99 latency < 18 ms in pre-production load tests.
- Instrumented the service with Prometheus counters and histograms (`kafka_consumer_lag`, `enrichment_duration_seconds`, `rpc_error_rate_by_upstream`) and OpenTelemetry distributed trace spans per enrichment stage, enabling on-call engineers to isolate latency regressions to specific pipeline stages within 3 minutes of alert fire.
- Authored Kubernetes manifests (Deployment, HPA, PodDisruptionBudget, ConfigMap) across dev, staging, and shadow environments; collaborated with the platform team to configure Istio traffic policies for zero-downtime canary rollout.
- Defined a versioned gRPC API (proto v1 with field-level deprecation policy) between the ingestion service and the downstream policy-enforcement module; 2 consumer teams integrated without requiring schema modifications post-launch.
- Refactored a collection of ad hoc forensic Python scripts into a modular `seclog-cli` package (Click-based CLI, pluggable output formatters, GCS-backed log retrieval with parallel download and local caching), reducing analyst log retrieval time from 45+ minutes to under 8 minutes per investigation session.
- Contributed Terraform module configurations (GCS dead-letter bucket, KMS encryption key reference, IAM role bindings) for the service's storage dependencies; changes reviewed and merged to main across 3 environments with zero infrastructure incidents post-apply.

---

## MODULE 4 — KEY PROJECTS

---

### TEMU | Recommendation Feature Quality Monitoring System

*Baseline: The recommendation algorithm team had no automated visibility into upstream feature data health; silent degradation in input signals went undetected until downstream CTR drops triggered post-hoc investigations—by which point impact had already accumulated over multiple days.*

- **Designed** a Python batch monitoring framework executing parameterized Hive SQL queries nightly against 30+ feature columns, computing null rate, out-of-range rate, and 7-day rolling distribution shift for each recommendation signal.
- **Detected** 2 production-impacting data incidents in its first 3 months of operation—including a feature column silently defaulting to 0 due to an upstream pipeline regression—72 hours before degradation surfaced in recommendation CTR, enabling engineering rollback before an estimated GMV exposure of ¥800K+.
- **Reduced** mean time to detection (MTTD) for feature data anomalies from approximately 5 business days (manual periodic review) to under 24 hours via automated Slack-integrated alerting with per-signal threshold configuration.
- **Established** the team's first structured data lineage documentation for 3 core feature modules, adopted by 5 downstream consumers and referenced during 2 subsequent algorithm dependency audits.

---

### DIDI IBG | City-Level Demand Forecasting Pipeline

*Baseline: Rider incentive budgets for DiDi Food Mexico were allocated using static weekly averages; no city-level intra-week demand forecast existed, causing systematic over- and under-incentivization during high-variance demand events (weekends, national holidays, sporting fixtures).*

- **Architected** an end-to-end forecasting pipeline using a Python ensemble model (Facebook Prophet + XGBoost) orchestrated on Apache Spark (GCP Dataproc), ingesting historical order data from BigQuery and real-time demand signals from a Kafka event stream covering 12 Mexican metro areas.
- **Designed** the underlying BigQuery dimensional schema (fact_orders, dim_restaurant, dim_courier, dim_city_calendar) supporting efficient time-series slicing; reduced 90-day rolling window query latency from ~40 minutes to under 90 seconds via partition pruning and materialized view pre-aggregation strategy.
- **Achieved** MAPE of 8.3% on 7-day forward order-volume forecasts versus a 17.1% static-average baseline, directly informing re-allocation of a ¥3.2M-equivalent monthly incentive budget across the Mexico operations team.
- **Automated** daily forecast output delivery as JSON files written to GCS via a Go CLI tool, consumed by two downstream business intelligence dashboards with zero manual handoff steps after initial deployment.

---

### DIDI IBG | Cross-Border Operations Analytics Platform

*Baseline: Mexico City operations analysts and Beijing product managers accessed siloed, mutually inconsistent metric definitions across 5 disconnected upstream data sources, with no single source of truth for SLA-critical food delivery KPIs in the international market.*

- **Designed** a unified operational data mart on BigQuery consolidating 5 upstream Kafka topics (order lifecycle events, courier GPS stream, merchant status, payment events, customer feedback) into a star-schema model with 22 formally defined KPIs and documented data contracts with each upstream engineering owner.
- **Built** PySpark ingestion jobs on GCP Dataproc with idempotent write semantics for the Kafka consumer layer, ensuring zero duplicate order records in downstream SLA reporting across daily full-refresh and incremental update cycles.
- **Instrumented** a Datadog monitoring layer across 15 SLA-critical business metrics with automated anomaly-detection alerts, enabling Mexico ops teams to reduce mean time to response (MTTR) for service degradation events from over 30 minutes to under 5 minutes during live operations.
- **Enabled** 3 subsequent Latin American city launches to inherit the data mart framework and KPI definitions without re-engineering, reducing per-city analytics infrastructure setup time from 6 weeks to under 2 weeks—a direct input to the LatAm expansion velocity roadmap.

---

### TIKTOK | Security Event Ingestion & Enrichment Service

*Baseline: Incoming security events from 8 detection sources arrived as unenriched raw payloads on a shared Kafka topic; forensic and alerting teams spent 45+ minutes per event manually correlating contextual attributes (device fingerprint, IP geolocation, user session history) before any triage action could begin.*

- **Designed and implemented** a Go microservice subscribing to the raw event Kafka topic, applying a configurable rule-based enrichment pipeline (IP geolocation via internal GeoIP RPC, device fingerprint matching via gRPC lookup service), and publishing enriched events to partitioned downstream topics for separate alerting and audit archival consumers.
- **Defined** a versioned gRPC API (proto v1 with field-level deprecation policy, structured error codes) between the ingestion service and the downstream policy-enforcement module; 2 consumer teams integrated the API without requiring schema modifications in the 6 months post-launch.
- **Validated** horizontal scalability via Kubernetes HPA (min: 3, max: 12 replicas, CPU-based autoscaling at 65% threshold), sustaining 12,000+ events/second at P99 end-to-end enrichment latency < 18 ms under pre-production load conditions.
- **Instrumented** Prometheus metrics (`kafka_consumer_lag`, `enrichment_duration_seconds`, histogram by stage, `rpc_error_rate_by_upstream`) and OpenTelemetry trace spans scoped to individual enrichment stages; reduced on-call mean time to detection for enrichment regressions from unstructured log search (~35 min average) to dashboard-pinpointed stage isolation (< 3 min).
- **Contributed** Terraform module configurations for the service's GCS-backed dead-letter storage bucket, KMS encryption key reference, and least-privilege IAM role bindings; merged to main across dev, staging, and shadow environments with zero infrastructure incidents post-apply.
- **Investigated** a race condition reproduced under concurrent gRPC calls in a C++ shared enrichment library consumed by the service; isolated the reproduction case through Go service metrics correlation and delivered a structured reproduction report to the owning team for hotfix prioritization.

---

### TIKTOK | Forensic Log Retrieval CLI Toolchain Refactor

*Baseline: A collection of 11 standalone ad hoc Python scripts with hardcoded GCS paths, no error handling, and inconsistent output formats was the only tooling available for offline security log retrieval; analysts averaged 45+ minutes per investigation session and frequently re-ran failed scripts manually.*

- **Refactored** the 11 legacy scripts into a single modular Python package (`seclog-cli`) with a unified Click-based CLI interface, pluggable output formatters (JSON, CSV, NDJSON), and environment-aware GCS bucket targeting via configuration files.
- **Implemented** GCS authentication via Application Default Credentials (ADC), retry logic with exponential back-off for transient GCS read failures, and local partition-level caching for frequently accessed log date ranges, eliminating the most common class of analyst-reported retrieval failures.
- **Reduced** analyst log retrieval workflow from ~45 minutes to under 8 minutes per investigation session through batched GCS prefix scanning, parallel object download (`concurrent.futures.ThreadPoolExecutor`), and streaming NDJSON output for large result sets.
- **Packaged and distributed** the tool via the team's internal PyPI mirror with pinned dependencies and a hermetic Dockerfile for isolated execution; adopted by 6 forensic analysts within 4 weeks of first release, with zero support tickets in the subsequent 8 weeks.

---

## SUPPLEMENTARY NOTE — Activities & Honors Placement

The Go/Baduk achievement belongs in a standalone `Activities & Honors` section at the resume footer. Suggested one-liner:

> **Go (Baduk) — Amateur 2-Dan, China National Certification** · 2022 Municipal Tournament Champion · 2023 Municipal Tournament 3rd Place · Entirely self-taught; no formal coaching or training program

For a target audience of infrastructure hiring managers, this line is defensible as a proxy signal for adversarial strategic thinking, self-directed mastery under ambiguity, and systematic pattern recognition at scale — all credibly transferable to distributed systems design. Keep it as a factual credential listing with zero interpretive language; let the reader draw the inference.
