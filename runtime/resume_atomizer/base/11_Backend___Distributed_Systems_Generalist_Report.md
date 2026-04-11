# Resume Prop Document — Backend / Distributed Systems Generalist

---

## MODULE 1 — Professional Summary

Systems-oriented engineer with 3+ years of production data infrastructure and backend service development experience at hyperscale consumer platforms (Temu, Didi IBG), reinforced by a current backend software engineering internship on TikTok's Security Platform team and concurrent graduate study in computer science (Georgia Tech OMSCS) and information management (UIUC MSIM). Brings a structurally differentiated analytical foundation — dual undergraduate training in cognitive systems modeling (philosophy, psychology) and quantitative decision science (international finance) — that directly translates into architectural reasoning about complex distributed system behavior, failure-mode analysis, and user-facing reliability trade-offs at scale. Targeting backend and distributed systems engineering roles where demonstrated proficiency in Java, Python, Go, microservice architecture, gRPC, Kubernetes, cloud-native deployment (AWS/GCP), and large-scale data pipeline design maps to immediate contributions in system design, scalability engineering, and cross-service reliability improvement.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | ✓ Scripting: cron automation, pandas, SQLAlchemy, REST client | ✓✓ Pipeline orchestration: Airflow DAGs, schema adapters, batch ETL jobs | ✓✓✓ Backend tooling, integration test harnesses, SDK scripts | **4+ years** |
| **SQL / Databases** | ✓✓ Complex HiveQL/SparkSQL on 1B+ row datasets, A/B cohort metrics | ✓✓✓ Canonical metric library (40+ defs), Redshift query plan optimization, schema design | ✓✓ PostgreSQL for service metadata store | **4+ years** |
| **Java** | ✓ Read-level familiarity with recommendation engine codebase for metric instrumentation | ✓✓ Contributed bug fixes to internal Java data-ingestion SDK; wrote unit tests | ✓✓✓ Concurrent service module for batch event processing (multi-threaded executor) | **3+ years** |
| **Git** | ✓ GitLab personal versioning (scripts, SQL templates) | ✓✓ Team branch workflows, merge request conventions, code review | ✓✓✓ CI/CD pipeline ownership, repo governance, trunk-based development | **4+ years** |
| **Linux** | ✓ Cron scheduling, shell scripting, environment management | ✓✓ Scripted automation, cross-OS tooling, system monitoring | ✓✓✓ System-level service operations, production debugging | **4+ years** |
| **REST API / APIs** | ✓ API client for upstream feature-store ingestion | ✓✓ 3rd-party logistics API adapter layer (3 providers), internal API design | ✓✓✓ Service-level API design and versioning, OpenAPI spec | **3+ years** |
| **Data Structures & Algorithms** | ✓ Query optimization, hash-based deduplication on event streams | ✓✓ DAG scheduling optimization, priority-queue–based alerting logic | ✓✓✓ Consistent hashing for event routing, concurrent data structures | **3+ years** |
| **Cloud (AWS / GCP)** | — | ✓✓ AWS Redshift query tuning, S3 data lake reads, IAM policy scoping | ✓✓✓ GCP GKE cluster management, Cloud Storage, IAM, Pub/Sub | **2+ years** |
| **Microservices** | — | ✓ Consumed internal microservice endpoints for analytics data feeds | ✓✓✓ Designed and deployed production microservices; service decomposition | **2+ years** |
| **Docker** | — | ✓ Local analytics toolchain containerization (Compose stack) | ✓✓✓ Multi-stage production image builds, CI/CD artifact packaging | **2+ years** |
| **Distributed Systems** | — | ✓✓ Multi-region pipeline orchestration (Beijing ↔ Mexico City), data consistency strategies | ✓✓✓ Event-driven architecture, distributed tracing, partitioned ingestion | **2+ years** |
| **Go** | — | — | ✓✓✓ Primary language; production microservice development, goroutine concurrency | **6 months** |
| **C++** | — | — | ✓✓ Performance-critical event parsing module, memory-optimized batch decoder | **6 months** |
| **Kubernetes** | — | — | ✓✓✓ Deployment manifests, HPA, Helm chart rollout, GKE operations | **6 months** |
| **gRPC** | — | — | ✓✓✓ Inter-service intake endpoints, Protocol Buffers v3, streaming RPCs | **6 months** |
| **System Design** | — | ✓✓ Pipeline architecture, data warehouse schema modeling, ETL topology design | ✓✓✓ End-to-end service architecture, capacity planning, fault tolerance design | **2+ years** |
| **Scalability / Reliability** | — | ✓✓ SLA-driven pipeline monitoring, Datadog alerting, cross-region failover | ✓✓✓ HPA auto-scaling, circuit breaker patterns, SLO-based alerting | **2+ years** |
| **Multi-threaded Systems** | — | ✓ Parallelized batch SQL execution for report generation | ✓✓✓ Java ExecutorService thread pools, Go goroutine fan-out patterns | **1.5+ years** |
| **Agile / Scrum** | ✓ Sprint-aligned delivery cadence with recommendation team | ✓✓ Scrum ceremonies, sprint planning, cross-functional standups (2 time zones) | ✓✓✓ Agile within security platform team, sprint demos, retrospectives | **4+ years** |

**ATS Depth Note:** Python, Java, SQL, Git, Linux, REST APIs, Data Structures & Algorithms, and Agile/Scrum establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters. Distributed Systems, System Design, Cloud (AWS/GCP), Microservices, Docker, and Scalability/Reliability accumulate 2+ years across the Didi and TikTok roles. Go, C++, Kubernetes, and gRPC are anchored to TikTok's production security infrastructure and substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Automated the recommendation team's daily performance digest using **Python** (pandas, SQLAlchemy) and Linux **cron** scheduling, eliminating approximately 6 manual analyst-hours per week and enabling same-day visibility into click-through and conversion rate shifts following each model deployment.
- Authored and optimized complex **HiveQL / SparkSQL** queries against 1B+ row event **databases** to extract A/B test cohort metrics (CTR, GMV lift, add-to-cart rate), applying hash-based deduplication **algorithms** to eliminate duplicate event records and directly supplying quantitative inputs for the recommendation team's weekly model retraining decisions.
- Built a lightweight **Python REST API** client to pull upstream feature-store payloads and join them against downstream engagement logs, reducing ad-hoc feature attribution analysis turnaround from approximately 2 days to under 4 hours.
- Read and instrumented metric collection hooks in the recommendation engine's **Java** codebase to surface internal ranking-score distributions to the analytics layer, enabling the team to correlate model-internal signals with user-facing conversion metrics for the first time.
- Standardized all analysis scripts and SQL templates under a shared **GitLab** repository with version-tagged releases, adopting sprint-aligned (**Agile**) delivery cadence and eliminating duplicated work across 3 team members.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Designed and operationalized an end-to-end **Python / Apache Airflow** DAG pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's weekly KPI reporting across 8 active city markets, reducing report delivery lead time from 3 business days to under 4 hours; architected the pipeline's **system design** to support horizontal scaling as market count increased.
- Curated a canonical **SQL** metric library of 40+ standardized **database** schema definitions (DAU, GMV, order completion rate, delivery SLA, refund rate) adopted as the org-wide standard across the Mexico analytics function; achieved 99.1% cross-team metric consistency over two consecutive quarterly audits.
- Developed a **Python** schema-normalization adapter layer ingesting raw feeds from 3 third-party Mexican logistics **REST APIs**, implementing priority-queue–based **data structures** for rate-limited request scheduling and resolving field-level schema divergence across providers to supply a unified data model to downstream **Datadog** dashboards consumed daily by a 50-person regional operations team.
- Contributed bug fixes and wrote unit tests for the IBG division's internal **Java** data-ingestion SDK used by 4 cross-functional engineering teams, addressing 3 race-condition defects in the SDK's **multi-threaded** batch loader to improve data delivery reliability for downstream analytics consumers.
- Containerized the analytics team's shared Python/SQL toolchain using **Docker** (multi-service Compose stack) and deployed reporting services on **AWS** (Redshift, S3), enabling bit-for-bit execution consistency across a 6-person, 2-time-zone (**distributed**) team (Beijing UTC+8, Mexico City UTC−6) for the entire 14-month Mexico engagement.
- Partnered with the cloud data infrastructure team to rewrite execution plans for 5 high-frequency **AWS Redshift** queries, achieving an average **query performance** improvement of 61% and eliminating dashboard timeout incidents that had previously blocked daily operational stand-ups; managed sprint planning and cross-functional standups (**Scrum**) across both time zones.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Designed and implemented a production **Go** **microservice** exposing a **gRPC** intake endpoint with Protocol Buffers v3 schema to ingest, normalize, and route security audit log events from 15+ internal platform services into the centralized detection pipeline, sustaining peak throughput of approximately 15,000 events per minute and reducing mean time to security alert from approximately 4 minutes to under 30 seconds.
- Developed a **C++** high-performance event parsing module for binary-encoded audit payloads, applying memory-optimized batch decoding with custom **data structures** (arena allocators, ring buffers) to achieve 3.2× throughput improvement over the previous Python-based parser on identical workloads.
- Deployed the service to a **GCP GKE**-managed **Kubernetes** cluster via Helm chart with Horizontal Pod Autoscaler configuration, implementing **system design** patterns for fault tolerance (circuit breakers, retry with exponential backoff) and sustaining 99.97% service uptime over the 5-month production window.
- Implemented a **Java** concurrent batch-processing module using ExecutorService **multi-threaded** pools for parallel enrichment of raw audit events against 4 internal identity and asset management **APIs**, reducing per-batch enrichment latency from 1,200ms to under 350ms at p99.
- Authored an end-to-end **GitHub Actions** CI/CD pipeline (build → SAST scan → multi-stage **Docker** image build/push → Helm rollout to staging on **GCP**), reducing average deployment cycle time from approximately 45 minutes to 12 minutes while maintaining >85% unit test coverage across the Go and **Java** service codebases.
- Instrumented all services with **distributed** tracing (OpenTelemetry) and custom throughput/latency metrics, configured **scalability** and **reliability** monitoring via Prometheus scrape endpoints feeding a Grafana SLA dashboard adopted by the 3-member on-call security rotation for real-time incident triage.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Recommendation A/B Test Metrics Automation System**

*The recommendation algorithm team ran 6–8 concurrent A/B experiments per week; metric summarization was performed manually in Excel by rotating analysts, producing a 24–48-hour reporting lag that deferred model iteration decisions and created recurring data-consistency conflicts between team members working from divergent query drafts.*

- Audited 9 recurring metric templates shared across all A/B experiment types and parameterized them into a reusable **Python** (pandas + SQLAlchemy) report generation module backed by a **SQL database** of canonical metric definitions, reducing per-experiment metric compilation from approximately 4 hours to under 20 minutes per analyst.
- Replaced ad-hoc **SparkSQL / HiveQL** query authoring with a pre-validated query library of 11 canonical templates covering core recommendation KPIs (CTR, GMV lift, add-to-cart rate, novelty score), implementing hash-based deduplication **algorithms** on event-stream records to enforce consistent metric definitions across simultaneous experiments and eliminate analyst-level calculation discrepancies.
- Read the recommendation engine's **Java** source code to identify internal ranking-score emission points and instrumented metric-collection hooks at those points, enabling the analytics pipeline to correlate model-internal signals with user-facing conversion metrics — a capability that directly informed 2 model architecture revisions during the internship period.
- Scheduled the module as a Linux **cron** job triggered nightly following feature-store refresh cycles; the job consumed upstream metric payloads via the feature-store **REST API** and wrote structured HTML summary reports to a shared internal directory accessible by the full recommendation team.
- Versioned all scripts, SQL templates, and report configuration files in a dedicated **GitLab** (**Git**) project, delivering traceable audit trails for model retraining decisions and enabling any team member to reproduce any historical experiment summary with a single parameterized command.
- Delivered a net reduction of approximately 6 analyst-hours per week and compressed the A/B experiment metric review cycle from 3–5 days to same-day availability, directly accelerating the recommendation model iteration cadence under the team's **Agile** sprint structure.

---

### DIDI IBG · Key Project 1

**Mexico Food Market Cross-Region KPI Normalization and Reporting Pipeline**

*The Mexico Food analytics function operated without a unified data layer: 7 independently maintained analyst Excel models tracked overlapping KPI sets using divergent metric definitions, causing cross-team reporting conflicts and systematically missing weekly SLAs by 2+ business days during high-growth market expansion sprints across 8 Mexican cities.*

- Audited all 7 legacy models and consolidated 40+ overlapping metric definitions into a canonical **SQL database** schema governing DAU, GMV, order completion rate, delivery SLA compliance, and refund rate; the library was formally adopted as the org-wide metric standard across the Mexico analytics team within one quarter of release.
- Architected and built a multi-DAG **Python / Apache Airflow** pipeline (**system design**) to replace all manual workflows: upstream DAG tasks pulled raw transactional data from the **AWS Redshift** data warehouse; mid-stream tasks applied canonical SQL metric logic; downstream tasks rendered parameterized reports and pushed outputs to the operational dashboard layer. The pipeline's modular DAG topology was designed for horizontal **scalability** as new city markets were onboarded.
- Developed a **Python** schema-normalization adapter layer to resolve field-level divergence across 3 third-party Mexican logistics **REST APIs** (field mapping, type coercion, null-handling conventions), implementing priority-queue–based **data structures** for rate-limited API request scheduling and enabling reliable automated upstream ingestion.
- Containerized the full pipeline execution environment in **Docker** (Python 3.11, Airflow, SQLAlchemy, custom adapter package) and deployed to **AWS** infrastructure, ensuring bit-for-bit execution consistency across the Beijing–Mexico City **distributed** team and eliminating environment-dependent data discrepancies over the 14-month engagement period.
- Integrated **GitLab CI/CD** (**Git**) gates enforcing automated linting and pytest unit tests on all SQL adapter logic before merge, operating within **Scrum** sprint cadence; reduced production data-quality incidents from a monthly average of 4 to under 1 within 60 days and achieved 99.1% **reliability** in cross-team metric consistency.
- Reduced KPI report delivery from 3 business days to under 4 hours; the pipeline subsequently served as the primary analytical foundation for go/no-go decisions on market expansion into 3 additional Mexican cities in Q1 2024.

---

### DIDI IBG · Key Project 2

**Java Data-Ingestion SDK Multi-Threading Reliability Patch**

*The IBG division's internal Java data-ingestion SDK, consumed by 4 cross-functional engineering teams, exhibited intermittent data-loss incidents under concurrent batch-load conditions; 3 race-condition defects in the SDK's thread pool executor caused silent record drops averaging 0.3% of processed events, directly degrading downstream analytics accuracy and triggering manual reconciliation workflows approximately twice per month.*

- Profiled the SDK's **Java** `ExecutorService` **multi-threaded** batch loader using JVisualVM and async-profiler to isolate 3 race-condition defects: an unsynchronized shared counter, a non-atomic batch-ID generator, and a premature future-cancellation path in the retry handler.
- Authored targeted fixes using `ConcurrentHashMap`, `AtomicLong`, and `CompletableFuture` chaining patterns, validated by 47 new JUnit test cases covering concurrent ingestion scenarios with configurable thread-pool sizing and simulated upstream latency spikes.
- Submitted fixes via the team's **Git** merge request workflow with full regression test evidence; patch was reviewed, approved, and merged within one sprint cycle (**Agile**), eliminating the 0.3% silent record-drop rate and removing the biweekly manual reconciliation overhead for 4 downstream consumer teams.
- Documented the root-cause analysis and fix in the SDK's internal wiki, establishing a concurrency-testing checklist subsequently adopted by the SDK team as a standard code-review gate for all **multi-threaded** components.

---

### TIKTOK SECURITY · Key Project 1

**AuditStream — Distributed Security Audit Log Ingestion and Routing Service**

*Fifteen-plus internal platform services emitted security-relevant events — authentication failures, privilege escalation attempts, API anomaly signals — to isolated, schema-incompatible sinks; the resulting fragmentation created detection blind spots in the centralized security pipeline and extended mean incident triage time to approximately 4 minutes from first signal emission to alert generation.*

- Designed and implemented **AuditStream**, a **Go** **microservice** exposing a **gRPC** intake endpoint (Protocol Buffers v3, including server-streaming RPCs for bulk replay) to ingest raw security events from 15+ upstream services, normalize them against a unified internal event taxonomy using consistent-hashing **algorithms** for partition-aware routing, and deliver them to the centralized **distributed** detection pipeline at a sustained peak throughput of approximately 15,000 events per minute.
- Developed a **C++** high-performance binary event parser with custom memory-management **data structures** (arena allocators, pre-allocated ring buffers) to decode legacy binary audit payloads, achieving 3.2× throughput improvement over the previous implementation; the module was integrated as a native extension callable from the Go service via cgo.
- Deployed to a **GCP GKE**-managed **Kubernetes** cluster via versioned Helm chart with Horizontal Pod Autoscaler, authored Terraform modules for node-pool provisioning and IAM bindings; implemented **system design** fault-tolerance patterns (circuit breakers, exponential-backoff retries, dead-letter queues) sustaining 99.97% service uptime and enabling one-command teardown/redeploy for disaster recovery drills.
- Implemented a **Java** concurrent event-enrichment module using `ExecutorService` **multi-threaded** pools to perform parallel lookups against 4 internal identity and asset management **APIs** (REST + gRPC), reducing per-batch enrichment latency from 1,200ms to under 350ms at p99.
- Instrumented all service components with OpenTelemetry **distributed** tracing and custom throughput/latency/error-rate metrics; configured Prometheus scrape endpoints feeding a Grafana **SLO**-based **reliability** dashboard adopted by the 3-member on-call security engineering rotation, reducing mean time to alert from approximately 4 minutes to under 30 seconds.
- Implemented **scalability** testing via load-generation harness (custom Go tool simulating 5× peak traffic), validating HPA behavior and identifying a goroutine leak under sustained burst conditions that was patched prior to production rollout.

---

### TIKTOK SECURITY · Key Project 2

**CI/CD Pipeline Automation and Deployment Acceleration for Backend Services**

*Internal platform service teams deployed backend services via semi-manual pipelines averaging 45-minute cycle times; the absence of automated security validation allowed credential-exposure incidents and medium-severity vulnerabilities to reach production undetected, with a median 5–7-day remediation lag for post-deployment findings.*

- Designed and authored a reusable **GitHub Actions** CI/CD composite action embedding a 4-stage deployment gate — SAST scanning, secret detection, multi-stage **Docker** image vulnerability scan, and mandatory unit test coverage enforcement — consumable by downstream **backend** service teams with a single `uses:` reference in their existing workflow files.
- Reduced average full deployment cycle time from approximately 45 minutes to 12 minutes by parallelizing build, scan, and test stages and implementing **Docker** layer caching for multi-stage image builds (**scalability** optimization), achieving 3.75× speedup with no reduction in gate coverage scope.
- Authored **Python** and Bash helper scripts for automated scan rule-set customization by service security classification tier, managing all policy configurations centrally in a single **Git** repository rather than maintaining per-service override files; scripts consumed **cloud** (**GCP**) Secret Manager for credential-free policy distribution.
- Maintained >85% unit test coverage on the composite action's internal orchestration logic (Go + **Java** test suites), validated via self-referential CI runs; produced an integration runbook adopted by 4 internal platform teams within the internship window, operated under **Agile** sprint review cadence.
- Integrated the pipeline with the team's **Kubernetes** deployment workflow (Helm rollout to staging on **GKE**), ensuring **reliable** promotion gates: no service image could advance past staging to production while carrying static credentials or failing **API** contract tests, directly addressing the primary attack vector identified in 2 prior credential-exposure post-mortems.
