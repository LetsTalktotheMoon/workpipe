# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Cloud-Native Platform & Infrastructure Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **Go**-based **microservice** development, **Kubernetes**-orchestrated **distributed systems**, and **observability** infrastructure (**Prometheus**, **OpenTelemetry**, **Datadog**). Production delivery spanning security event pipelines, compliance platforms, and cross-regional data systems.
* **End-to-End Infrastructure Delivery:** Designs and ships **cloud-native** backend services — from **asynchronous processing** pipelines and versioned **API** contracts to **Terraform**-managed **Infrastructure as Code**, **Istio** service mesh policies, and **SLO**-driven **reliability** engineering across **GCP** and **AWS** environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective collaborator bridging platform, security, product, and operations teams with strong **ownership** of **production infrastructure**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Platform Infrastructure Contributions_**

* Authored **Kubernetes** manifests (Deployment, HPA, PodDisruptionBudget, ConfigMap) across dev/staging/shadow environments; collaborated with the platform team on **Istio** traffic policies enabling zero-downtime canary rollouts with no SLA impact (**high availability**).
* Contributed **Terraform** modules (GCS dead-letter bucket with configurable retention, KMS encryption key reference, least-privilege IAM bindings) deployed across 3 **GCP** environments with zero infrastructure incidents post-apply (**Infrastructure as Code**).
* Refactored ad hoc forensic **Python** scripts into a modular CLI package with pluggable output formatters and GCS-backed parallel log retrieval, cutting analyst log-retrieval time from 45+ minutes to under 8 minutes per investigation.

**_Project: Distributed Security Event Enrichment Pipeline_**

* Designed and implemented a production **Go** **microservice** consuming high-volume **Kafka** event streams, applying configurable rule-based enrichment (IP geolocation, device fingerprint resolution via **gRPC** lookup) and routing enriched payloads to partitioned downstream consumers; sustained 12,000+ events/second at P99 latency <18ms under pre-production load.
* Defined a versioned **gRPC API** contract with field-level deprecation policy and structured error codes between the ingestion service and downstream policy enforcement module; 2 consumer teams integrated without schema modifications over 6 months post-launch.
* Instrumented enrichment stages with **Prometheus** counters/histograms and **OpenTelemetry** distributed trace spans, enabling on-call engineers to isolate latency regressions to specific pipeline stages within <3 minutes of alert fire (reduced from ~35 minutes of unstructured log search) (**observability**).
* Validated horizontal **scalability** via **Kubernetes** HPA (CPU autoscaling at 65% threshold) and PodDisruptionBudget; sustained target throughput with zero SLA breaches during staged rollout.

**_Project: Gateway Compliance Scoring & Observability Platform_**

* Architected a **Go** **microservice** ecosystem providing compliance scoring, stream quantification, and **API** observability for enterprise gateway traffic across 6+ gateway types; defined all inter-service contracts via IDL with code-generated handler scaffolding, eliminating contract drift.
* Built the batch scoring engine using an Iterator-Worker concurrency pattern with a configurable worker pool, enabling gateway-type extensibility via a polymorphic interface — onboarding a new gateway required only interface implementation with zero changes to core scoring logic (**systems design**).
* Implemented dual **asynchronous** consumers (**Kafka** + RocketMQ) in a producer-consumer decoupled architecture; large file payloads routed to **AWS S3** via async upload with KMS field-level encryption to satisfy cross-regional **data sovereignty** requirements (**SaaS protection**).
* Designed a two-level compliance metadata caching layer: in-process cache for sub-millisecond hot-path reads + distributed Redis for cross-instance consistency; instrumented with **OpenTelemetry** tracing and **Prometheus** metrics for end-to-end pipeline visibility.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Architected a dimensional **data model** (fact + dimension star schema on **GCP BigQuery**) consolidating events from 5 upstream **Kafka** topics into a unified cross-regional operational data mart; pre-aggregated materialized views reduced ad hoc query latency from ~40 minutes to under 90 seconds across 12 markets.
* Designed and led delivery of a multi-city demand forecasting pipeline (**Python**/**PySpark** on **GCP** Dataproc) generating daily 7-day predictions, achieving 8.3% MAPE versus a 17.1% static-average baseline; findings informed reallocation of a ¥3.2M-equivalent monthly incentive budget.
* Built a **Go**-based CLI tool to automate daily business metric export (JSON → GCS → downstream BI dashboards), replacing a 2-hour manual process; adopted by 3 partner analytics teams within 6 weeks.
* Deployed a **Datadog** monitoring layer covering 15 SLA-critical metrics; enabled Mexico City operations to detect and triage service degradation in under 5 minutes during peak-hour windows (**observability**, **reliability**).
* Defined 22 standardized KPIs and formal data contracts with 4 upstream engineering owners for a new-city analytics launch framework; reused across 3 subsequent city rollouts, reducing per-city analytics setup from 6 weeks to under 2 weeks.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Authored **Python** ETL scripts to extract, deduplicate, and normalize raw clickstream logs (50M+ daily records) from internal **Hive** tables, eliminating 4 hours of manual data preparation per analyst per week.
* Designed and maintained **SQL**-based feature quality dashboards tracking null rate, value distribution shift, and signal coverage across 30+ recommendation input signals; surfaced a silent upstream feature drift incident 72 hours before degradation appeared in production metrics.
* Built a scheduled **Python** + **Hive SQL** reconciliation job cross-validating recommendation serving logs against upstream event-tracking data, reducing discrepancy investigation cycles from 3 business days to same-day resolution.

---

## Skills

**Languages:** Go, Python, C++, SQL, HiveQL
**Cloud & Infrastructure:** GCP (BigQuery, Dataproc, GCS, GKE), AWS (S3), Kubernetes, Terraform, Docker, Istio
**Observability:** Prometheus, OpenTelemetry, Datadog, SLO/SLA Design, Reliability Analysis
**Data & Streaming:** Kafka, RocketMQ, BigQuery, Hive, PySpark, Spark, Protobuf
**APIs & Architecture:** gRPC, REST APIs, Microservices, Distributed Systems, Asynchronous Processing, Data Modeling

---

## Education

| Degree | Institution | Period |
| --- | --- | --- |
| M.S. Computer Science (OMSCS) | Georgia Institute of Technology | Expected May 2026 |
| M.S. Information Management (MSIM) | University of Illinois Urbana-Champaign | Expected May 2026 |
| M.A. International Business (Finance) | Beijing International Studies University | Sep 2018 – Jun 2021 |
| B.A. Philosophy & Psychology | Beijing Normal University | Sep 2014 – Jun 2018 |

---

## Additional Information

* **Go (Weiqi):** National 2-Dan (China Weiqi Association); 1st Place, 2022 Municipal Open Championship; 3rd Place, 2023 Municipal Open Championship.