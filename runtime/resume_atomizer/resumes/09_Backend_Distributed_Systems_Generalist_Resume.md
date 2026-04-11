# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Backend & Distributed Systems Engineer:** 3+ years of technical experience across high-scale consumer platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery spanning **Java**, **Python**, **Go**, and **C++** backend services, **microservice** architecture, **distributed** data pipeline design, and **cloud-native** deployments on **GCP** and **AWS**.
* **End-to-End Systems Delivery:** Designs and ships **large-scale** backend infrastructure — from high-throughput **gRPC** services and **multi-threaded** batch processing to **Kubernetes**-orchestrated deployments, **CI/CD** automation, and **SLO**-driven **reliability** engineering. Strong foundation in **data structures**, **algorithms**, and **system design**.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator in **Agile** environments, bridging security, platform, product, and operations teams to deliver **scalable**, production-grade solutions.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Backend Infrastructure Contributions:_**

* Authored a **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage **Docker** image build/push → **Helm** rollout to staging on **GCP**), cutting average deployment cycle from ~45 min to 12 min while maintaining >85% unit test coverage across **Go** and **Java** codebases.
* Instrumented all services with **OpenTelemetry** distributed tracing and custom **Prometheus** throughput/latency metrics; configured a Grafana SLA dashboard adopted by the 3-member on-call rotation for real-time incident triage (**reliability**).

**_Project: Distributed Security Audit Log Ingestion Service_**

* Designed and shipped a production **Go** microservice with a **gRPC** intake endpoint (**Protocol Buffers** v3, including server-streaming RPCs for bulk replay) to ingest, normalize, and route security audit events from 15+ internal services; sustained peak throughput of ~15,000 events/min and reduced mean time to security alert from ~4 min to under 30 sec.
* Developed a **C++** high-performance event parser using memory-optimized batch decoding with arena allocators and pre-allocated ring buffers, achieving 3.2× throughput improvement over the prior **Python**-based parser; integrated into the **Go** service via cgo.
* Implemented a **Java** concurrent batch-enrichment module using multi-threaded pools for parallel lookups against 4 internal identity and asset management **APIs**, cutting per-batch enrichment latency from 1,200ms to under 350ms at P99 (**multi-threaded systems**).
* Deployed to **GCP GKE**-managed **Kubernetes** cluster via **Helm** chart with HPA; implemented fault-tolerance patterns (circuit breakers, exponential-backoff retry, dead-letter queues) sustaining 99.97% uptime over the 5-month production window.

**_Project: Security Event Schema Governance Platform_**

* Designed a unified security event schema model in **Go** (49+ types spanning HTTP, RPC, and streaming interfaces across 5 gateway zones) and implemented a bidirectional schema conversion engine; migrated 1.1M+ legacy entries from 3 independent systems with full backward compatibility during a multi-month parallel-run window (**large-scale systems**).
* Built a **distributed** compliance ticket workflow state machine (10+ transitions) backed by **MongoDB** optimistic locking for concurrent modification safety; sustained ~1,500 workflow events per day with zero duplicate-approval defects over 4 months in production.
* Architected a multi-module **Go** **microservice** platform exposing 25+ endpoints via **gRPC** + REST, with sharded **MongoDB** collections handling high-write schema ingestion; served 10+ internal consumer systems across security operations and compliance functions.
* Integrated a **Kafka** producer-consumer pipeline for asynchronous schema change event streaming, decoupling ingestion from compliance validation; deployed via **Helm** on **Kubernetes** with **OpenTelemetry** distributed tracing and zero-downtime blue-green deployment strategy.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and operationalized a multi-DAG **Python**/**Apache Airflow** pipeline replacing 7 siloed manual workflows for the Mexico Food vertical's weekly KPI reporting across 8 city markets; reduced report delivery lead time from 3 business days to under 4 hours.
* Diagnosed and resolved 3 race-condition defects in the IBG division's internal **Java** data-ingestion SDK's **multi-threaded** batch loader (consumed by 4 cross-functional engineering teams), eliminating intermittent out-of-order ingestion failures.
* Developed a **Python** schema-normalization adapter layer ingesting raw feeds from 3 third-party logistics **REST APIs**, implementing priority-queue–based **data structures** for rate-limited request scheduling and delivering a unified data model to downstream dashboards.
* Containerized the analytics team's shared **Python**/**SQL** toolchain using **Docker** and deployed reporting services on **AWS** (Redshift, S3), enabling execution consistency across a 6-person, 2-timezone distributed team.
* Partnered with the cloud infrastructure team to rewrite execution plans for 5 high-frequency **AWS Redshift** queries; achieved 61% average runtime improvement, eliminating daily dashboard timeout incidents (**scalability**).
* Curated a canonical **SQL** metric library of 40+ standardized KPI definitions adopted as the org-wide analytics standard; cross-team consistency validated at 99.1% across two consecutive quarterly audits.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Authored and optimized complex **HiveQL**/**SparkSQL** queries against 1B+ row event **databases** to extract A/B test cohort metrics; applied hash-based deduplication **algorithms** to eliminate duplicate records and supply clean inputs for weekly model retraining.
* Read and instrumented metric collection hooks in the recommendation engine's **Java** codebase to surface internal ranking-score distributions to the analytics layer, enabling correlation of model-internal signals with user-facing conversion metrics for the first time.
* Built a lightweight **Python REST API** client to pull upstream feature-store payloads and join them against downstream engagement logs, reducing ad-hoc feature attribution turnaround from ~2 days to under 4 hours.
* Standardized all analysis scripts and **SQL** templates under a shared **Git** repository with version-tagged releases; adopted sprint-aligned **Agile** delivery cadence, eliminating duplicated work across a 3-member team.

---

## Skills

**Languages:** Go, Java, C++, Python, SQL, HiveQL, SparkSQL
**Systems & Architecture:** Distributed Systems, Microservices, System Design, Multi-threaded Systems, Data Structures, Algorithms, Scalability, Reliability
**APIs & Protocols:** gRPC, Protocol Buffers, REST APIs, Thrift
**Cloud & Infrastructure:** GCP (GKE), AWS (Redshift, S3), Kubernetes, Helm, Terraform, Docker
**Databases & Messaging:** MongoDB, MySQL, Redis, Kafka, Apache Airflow
**DevOps & Observability:** GitHub Actions, CI/CD, OpenTelemetry, Prometheus, Grafana, Datadog, Git, Agile

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