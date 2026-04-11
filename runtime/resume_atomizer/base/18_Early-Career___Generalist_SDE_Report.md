# Resume Prop Document — Early-Career / Generalist SDE Candidate

---

## MODULE 1: Professional Summary

Software engineer with 3+ years of progressive experience translating complex, data-intensive operational problems into automated technical systems, currently completing concurrent graduate degrees in Information Management (UIUC, MSIM) and Computer Science (Georgia Tech, OMSCS); background spans recommendation data pipelines at Temu, distributed operations analytics at Didi IBG across two countries, and production backend service development on TikTok's Trust & Safety platform. Cross-disciplinary training in philosophy (formal logic, epistemology), psychology (behavioral modeling), and quantitative finance provides a differentiated aptitude for requirements decomposition, edge-case reasoning, and structured problem-solving that complements core software engineering competencies in Java, Python, C++, distributed systems, and cloud-native development. Seeking an early-career generalist SDE role to apply end-to-end ownership spanning data modeling, backend service design, and CI/CD-driven delivery within Agile teams building reliable, scalable software systems.

---

## MODULE 2: Technology Stack Distribution Strategy

**Core Principle:** Python, SQL, and Git form the longitudinal backbone across all three roles, establishing credible 3+ year cumulative depth. Object-Oriented Design and Linux usage accrue naturally from the earliest role onward. Java, C++, and distributed systems concepts (multi-threading, networking, cloud services) are introduced at Didi — realistic for a senior analyst operating within a Java/C++ microservice ecosystem — and deepened substantially at TikTok, where the Backend SDE Intern title explicitly supports system-level ownership. AWS/Cloud, CI/CD, and Agile/Scrum mature progressively from consumer-level exposure to production-grade engineering practice.

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Safety (Jun – Dec 2025) |
|---|---|---|---|
| **Python** | Scripting, pandas ETL, batch automation | Advanced pipelines, anomaly detection, internal tooling | Service-layer logic, Kafka consumers, integration tests |
| **SQL** | Parameterized queries, experiment reporting | Complex multi-table analytics, funnel modeling, schema design | Data validation queries, schema migration scripts |
| **Java** | — | Consumed Java-based internal SDK for logistics APIs; read/debugged service code | Implemented backend service modules in Java (Spring Boot) |
| **C++** | — | Read/profiled C++ components in dispatch engine for latency root-cause analysis | Developed multi-threaded log-processing utility |
| **Object-Oriented Design** | Basic Python class hierarchy for ETL modules | Refactored analytics codebase into OOD-structured packages | Full OOD: interface contracts, dependency injection, design patterns |
| **Data Structures & Algorithms** | pandas-level (hash maps, sorting) | Priority queues for alert ranking; tree-based config parsing | LRU caches, bloom filters for deduplication, graph traversal for rule DAGs |
| **Distributed Systems** | — | Consumed distributed service APIs; understood sharding concepts | Designed Kafka-based event-driven microservice; implemented service discovery |
| **Cloud Services / AWS** | — | S3 data lake (read), basic IAM roles | AWS EC2/ECS deployments, CloudWatch monitoring, S3 artifact storage |
| **Git** | Basic version control | Branching workflows, code review participation | GitHub Actions CI/CD, branch protection, automated test gates |
| **CI/CD** | — | — | GitHub Actions pipelines, canary deployments, automated rollback |
| **Agile / Scrum** | — | Bi-weekly cross-functional syncs | Formal sprint ceremonies, Design Reviews, retrospectives |
| **Linux** | Basic command-line ETL scripting | Shell scripting for cron jobs, log analysis | Production service debugging, systemd, strace/perf profiling |
| **Networking** | — | REST API consumption, HTTP debugging | gRPC service contracts, load balancer configuration, TCP/UDP tuning |
| **Security** | — | — | Input validation, authentication middleware, content policy enforcement |
| **Databases** | MySQL read-only queries | PostgreSQL schema design, query optimization | PostgreSQL ownership, Redis caching layer, migration management |
| **Web Services** | — | RESTful API consumption (3rd-party logistics) | RESTful & gRPC API design, implementation, and documentation |
| **Multi-threaded Systems** | — | Multi-process Python scripts for parallel data loads | Java concurrent utilities, thread pool tuning, race condition debugging |
| **.NET / C# / JavaScript / Go** | — | — | Exposure via UIUC/GT graduate coursework projects |

**Snowball Accumulation Summary:**
- **Python:** Entry-level scripting → Advanced ETL & automation → Production service layer *(3 roles, ~3.5 cumulative years)*
- **SQL:** Routine reporting queries → Complex multi-table funnel analytics → Schema ownership & migration *(3 roles)*
- **Java:** SDK consumer / code reader (Didi) → Backend service implementer (TikTok)
- **OOD:** Basic module structure → Package-level refactoring → Full interface-driven design with patterns
- **Linux:** CLI scripting → Cron/shell automation → Production debugging and profiling
- **Cloud / CI/CD / Distributed Systems:** Confined primarily to TikTok — appropriate scope for a backend SDE internship
- **C++ / Multi-threading:** Read-only profiling (Didi) → Active implementation (TikTok)

---

## MODULE 3: Work Experience Bullet Points

---

### TEMU — Recommendation Algorithm Data Analyst | Shanghai | Jun 2021 – Feb 2022

- Extracted and aggregated product-level behavioral data (click, purchase, cart abandonment) from the recommendation team's MySQL databases using parameterized SQL queries to generate weekly algorithm performance dashboards for 12 engineers, eliminating approximately 4 hours of manual data compilation per reporting cycle.
- Developed Python (pandas) automation scripts to batch-process raw user event logs (500K+ daily records), applying rule-based deduplication and feature normalization ahead of upstream model ingestion; reduced pre-processing error rates from ~15% to under 3%.
- Designed a lightweight Python class hierarchy encapsulating data extraction, transformation, and validation logic into reusable OOD modules, enabling the analytics team to onboard new experiment pipelines without rewriting boilerplate code.
- Supported tracking of 6 concurrent A/B experiments for recommendation model variants by authoring parameterized SQL templates to extract cohort-level metrics (CTR, CVR, GMV lift) from the behavioral data warehouse on a Linux-hosted cron schedule, enabling same-day experiment readouts for the algorithm team.
- Maintained all pipeline scripts under Git version control with documented commit history, establishing the team's first reproducible codebase for experiment data preparation.

---

### DIDI IBG — Senior Data Analyst, Food Business | Beijing / Mexico City | Sep 2022 – May 2024

- Owned end-to-end analytical coverage for Didi Food's Mexico operations, designing and maintaining a normalized PostgreSQL reporting schema tracking order funnel KPIs (GMV, completion rate, driver supply/demand balance) across 12 city-level markets; schema served as the authoritative data source for country-level Food operations.
- Built Python ETL pipelines consuming RESTful API endpoints from two third-party logistics providers (Java-based internal SDK integration), normalizing heterogeneous JSON response formats into a unified data warehouse schema on a 30-minute automated refresh cycle and replacing a 48-hour manual export process.
- Developed a Python anomaly detection module monitoring 9 operational KPIs with configurable alert thresholds using priority-queue-based severity ranking; automated Feishu (Lark) notifications reduced median P1 incident response time from 47 minutes to under 9 minutes.
- Authored Linux shell scripts to orchestrate nightly data loads across 4 parallel Python processes, compressing ETL wall-clock time by 60% and enabling pre-market-open data freshness for operations managers across the Mexico timezone.
- Performed latency root-cause analysis on the C++ dispatch engine by profiling hot paths in collaboration with the engineering team, identifying a suboptimal sorting algorithm in the driver-matching module; findings contributed to a subsequent engineering fix that reduced median dispatch latency by 12%.
- Collaborated with operations, product, and engineering counterparts across Beijing HQ and Mexico City in bi-weekly Agile/Scrum review cycles, translating regional regulatory constraints into quantified KPI adjustment targets and engineering backlog items; all work managed via Git branching workflows with peer code review.

---

### TIKTOK — Backend Software Engineering Intern, Trust & Safety | San Jose, CA | Jun 2025 – Dec 2025

- Designed and implemented RESTful and gRPC API endpoints in Java (Spring Boot) within TikTok's Trust & Safety microservice architecture, enabling downstream content moderation pipelines to query and update policy-violation metadata at a throughput of 50M+ daily content events with p99 latency under 45ms.
- Developed a Kafka consumer service in Python subscribing to 4 upstream safety-signal topics, applying configurable rule-based filtering with bloom-filter-based deduplication, and persisting structured violation records to PostgreSQL; achieved end-to-end event latency under 200ms at sustained production load.
- Built a multi-threaded C++ log-processing utility using Java concurrent utilities and POSIX threads to parse and index 2TB+ of daily audit logs, enabling the on-call team to perform sub-second historical lookups during incident triage; utility reduced mean investigation time by 35%.
- Containerized three microservices using Docker and authored Kubernetes deployment manifests (Deployment, HPA, ConfigMap) on AWS ECS/EC2, supporting horizontal auto-scaling during traffic spike periods; p99 service latency reduced by 18% under 3x baseline traffic simulation with CloudWatch-based alerting.
- Integrated the team's policy rule engine into the CI/CD pipeline via GitHub Actions with automated integration test suites, enabling zero-downtime canary deployments with automated rollback across staging and production clusters; compressed policy update deployment cycles from two weeks to two days.
- Participated in 5 Design Reviews and 30+ Code Reviews within formal Agile/Scrum sprint ceremonies, contributing interface proposals for a shared rate-limiting library subsequently adopted across 4 sub-teams; implemented input validation and authentication middleware to enforce security best practices across all new API endpoints.

---

## MODULE 4: Key Projects

---

### TEMU

**Project: Recommendation Feature Preprocessing Automation System**

*The recommendation algorithm team lacked a standardized, version-controlled preprocessing pipeline before model feature ingestion, causing inconsistent training data quality that blocked daily experiment preparation and consumed approximately 12 analyst-hours per week in manual rework.*

- Designed a Python (pandas) pipeline structured as an OOD module hierarchy to ingest raw user behavioral event logs (500K+ daily records across 3 product categories), apply rule-based cleaning and deduplication, and output training-ready feature sets formatted to the algorithm team's model input contract specifications.
- Authored parameterized SQL templates against the MySQL behavioral data warehouse to extract reproducible experiment cohort slices (configurable by product category, user cohort, and time window), eliminating ad-hoc query rewriting between experiment cycles and enforcing consistent data extraction logic.
- Implemented data validation checkpoints using Python's built-in data structures (hash maps for duplicate detection, sorted arrays for range validation) to flag anomalous records before downstream ingestion; reduced data formatting errors from ~15% to <3% within the first week of deployment.
- Automated pipeline execution via Linux cron scheduling with structured logging, enabling unattended daily runs and providing the team with audit-traceable processing records under Git version control.
- Reduced A/B experiment feature preparation time from 3 days to same-day turnaround, enabling the algorithm team to run 2× more concurrent recommendation experiments per quarter without additional analyst headcount.

---

### DIDI IBG

**Project 1: Cross-Market Food Operations Real-Time Analytics Platform**

*Didi Food's Mexico operations team relied on 7 manually compiled, siloed spreadsheet reports that were routinely 48+ hours stale, preventing timely operational intervention across 12 city markets and creating data inconsistencies that led to conflicting executive decisions.*

- Designed a normalized, multi-table PostgreSQL schema integrating order, driver supply, customer lifecycle, and promotional data across 12 Mexican city markets; replaced all 7 disconnected legacy reports and became the authoritative data source for country-level Food operations with documented OOD data-access classes.
- Built Python ETL scripts consuming RESTful API endpoints from two third-party logistics providers via Didi's Java-based internal SDK, normalizing heterogeneous JSON response formats into a unified internal data warehouse schema on a 30-minute automated refresh cycle.
- Implemented a Python anomaly detection module monitoring 9 operational KPIs (order completion rate, driver acceptance rate, delivery SLA adherence) with configurable threshold parameters and priority-queue-based alert severity ranking; automated Feishu notifications reduced P1 incident mean response time by 81% (from 47 minutes to under 9 minutes).
- Orchestrated nightly batch loads using Linux shell scripts managing 4 parallel Python processes, leveraging multi-process concurrency to compress ETL wall-clock time by 60% and achieving pre-market-open data freshness for the Mexico City timezone.
- All pipeline code maintained under Git with branch-based code review workflows; documentation and runbooks stored alongside code, enabling onboarding of 2 new analysts without live training sessions.

---

**Project 2: Dispatch Latency Profiling & Optimization Contribution**

*The Mexico Food division experienced a 23% month-over-month GMV decline in one market; initial hypothesis testing via SQL-based root-cause analysis identified driver dispatch latency as a contributing factor, requiring cross-team investigation into the C++ dispatch engine.*

- Conducted SQL-based funnel analysis isolating the GMV decline to a specific market-time cohort, attributing the primary cause to elevated driver-side cancellation rates correlated with dispatch response latency exceeding the 95th-percentile SLA.
- Profiled hot paths in the C++ dispatch engine in collaboration with the engineering team using Linux performance tools (perf, strace), identifying a suboptimal O(n²) sorting algorithm in the driver-matching module as the primary latency bottleneck.
- Delivered a data-backed root-cause report with quantified latency distributions and SQL-extracted cohort comparisons to the engineering and product teams; the subsequent engineering hotfix (algorithm replacement) recovered full-market GMV within 10 business days.
- Presented findings in bi-weekly Agile/Scrum cross-functional review, establishing a reusable SQL-based diagnostic playbook adopted by the analytics team for future dispatch latency investigations.

---

### TIKTOK SAFETY

**Project 1: Real-Time Safety Signal Processing Service**

*The Trust & Safety team's existing batch-based content signal processing introduced 6–12 hour enforcement delays; policy violations flagged by upstream ML detectors were not actionable until the following day's batch job completed, leaving newly identified content policy violations unaddressed during peak-traffic windows.*

- Designed and implemented a Kafka consumer service in Python subscribing to 4 upstream safety-signal topics, applying configurable rule-based filtering with bloom-filter-based content deduplication, and publishing processed violation events to downstream content review queues; achieved <200ms end-to-end event latency at 50M+ daily events under sustained production load.
- Defined typed Protobuf schemas for cross-service gRPC event contracts in collaboration with 3 upstream ML detector teams, decoupling schema evolution from deployment coordination and preventing downstream breakage during upstream model updates.
- Packaged the service as a Docker image and authored Kubernetes manifests (Deployment, HPA, ConfigMap) deployed on AWS ECS with CloudWatch-based alerting, enabling horizontal auto-scaling during traffic spike windows; p99 event processing latency held under 350ms at 3× baseline load during load simulation.
- Instrumented the service with structured logging and Prometheus-compatible health metrics consumed by the team's Grafana dashboards, establishing real-time SLA visibility and on-call alerting for the production service on Linux-based infrastructure.
- Implemented input validation and security middleware to sanitize incoming event payloads, preventing injection-based abuse vectors identified during the team's threat modeling exercise.

---

**Project 2: Centralized Policy Rule Engine API & CI/CD Integration**

*Content policy rules were hardcoded across multiple enforcement microservices; any policy update required coordinated code changes and synchronized deployments across teams, resulting in a 2-week minimum policy update cycle with significant operational risk and no automated regression protection.*

- Implemented RESTful and gRPC API endpoints in Java (Spring Boot) for the centralized policy rule engine service: a query endpoint enabling downstream enforcement services to retrieve active policy rules at runtime, and a write endpoint enabling policy administrators to push rule updates without service redeployment; system served policy metadata for 50M+ daily content events.
- Designed the service using Object-Oriented Design principles with interface-based dependency injection, strategy pattern for rule evaluation, and an LRU cache backed by Redis for high-frequency rule lookups; reduced median rule-fetch latency from 12ms to under 2ms.
- Integrated the new endpoints into the CI/CD pipeline via GitHub Actions with automated integration test suites (18 test cases covering rule priority conflicts, graceful degradation, and concurrent write race conditions under multi-threaded load), enabling zero-downtime canary deployments that compressed policy update cycles from 2 weeks to 2 days.
- Built a multi-threaded C++ audit log indexer using POSIX threads to parse and index 2TB+ of daily policy enforcement logs, enabling sub-second historical lookups during incident triage on Linux-based production nodes; reduced mean investigation time by 35%.
- Contributed interface design proposals for a shared rate-limiting library in 2 Design Review sessions, with the adopted design serving 4 sub-teams across the Trust & Safety organization; all proposals documented and version-controlled in Git with full Design Review records.

---

## Supplementary Note: Additional / Interests Section

For the resume's closing section, the protagonist's Go achievement should be rendered as follows:

> **Interests:** Competitive Go (Weiqi) — National Amateur 2-Dan certification (China Weiqi Association); 1st place, 2022 Municipal Open Championship; 3rd place, 2023 Municipal Open Championship; entirely self-taught without formal coaching or professional instruction.

**Author's note on fictional utility:** This detail is functionally load-bearing for the character's credibility in an early-career generalist SDE context. Self-teaching a cognitively demanding combinatorial game to national-certification level — and placing competitively in open tournaments — signals three qualities that engineering hiring managers instinctively value for generalist SDE roles: strong algorithmic intuition and pattern recognition under constraint, comfort with deep unstructured problem spaces requiring systematic decomposition, and sustained self-directed learning discipline. For a candidate whose resume intentionally spans data analysis, cross-market operations, and backend engineering, the Go achievement provides a psychologically coherent anchor that frames the breadth as disciplined intellectual range rather than unfocused career drift. No further narrative explanation of the career transition is needed in the resume itself — the Go detail does that work implicitly.
