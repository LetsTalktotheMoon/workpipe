# Resume Prop Document — Enterprise Cloud & Big Data Engineer

---

## MODULE 1 — Professional Summary

Enterprise-grade data and cloud systems engineer with 3+ years of progressive production experience building scalable data pipelines, distributed processing architectures, and microservice-based platforms at hyperscale consumer technology companies (Temu, Didi IBG), complemented by a backend software engineering internship at TikTok and concurrent graduate study at UIUC (MSIM) and Georgia Tech (OMSCS). Brings a structurally differentiated analytical foundation — dual undergraduate training in cognitive-behavioral modeling and quantitative finance — that underpins a consistent track record of decomposing ambiguous, cross-functional business problems into measurable data-engineering solutions spanning batch and streaming pipelines, cloud-native service architectures, and AI/ML integration layers. Targeting Enterprise Cloud and Big Data Engineering roles where demonstrated proficiency in AWS/Azure ecosystem services (EMR/Spark, Kinesis, ECS, Function Apps), distributed systems design, SaaS platform development (Dynamics 365), and Agile delivery translates directly into building and operating scalable, production-grade data infrastructure.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | ✓ Scripting: pandas, SQLAlchemy, cron-based automation | ✓✓ Pipeline orchestration: Airflow DAGs, schema adapters, batch ETL | ✓✓✓ Distributed data tooling, AI/ML integration scripts, SDK development | **4+ years** |
| **SQL** | ✓✓ Complex SparkSQL/HiveQL on 1B+ row datasets, A/B cohort analytics | ✓✓✓ Canonical metric library (40+ defs), Redshift/Spark query optimization | ✓✓ Analytical queries for security event telemetry | **4+ years** |
| **AWS** | ✓ S3 data lake reads, basic IAM for analytics access | ✓✓ Redshift warehouse tuning, S3-based data staging, CloudWatch alerting | ✓✓✓ ECS container orchestration, Kinesis stream provisioning, EMR/Spark cluster management | **3+ years** |
| **Spark** | ✓✓ SparkSQL queries on billion-row Hive tables for recommendation metrics | ✓✓ PySpark batch transformations in Airflow pipelines | ✓✓✓ EMR-based distributed processing, Spark Structured Streaming | **3+ years** |
| **Distributed Systems** | ✓ Consumer of distributed data platform (Hive/Spark cluster) | ✓✓ Multi-region pipeline design (Beijing ↔ Mexico City), cross-timezone sync | ✓✓✓ Microservice architecture design, event-driven distributed processing | **3+ years** |
| **Microservices** | — | ✓ Schema-normalization adapter services for 3rd-party API ingestion | ✓✓✓ Production Go microservice design, gRPC inter-service communication | **2+ years** |
| **Docker** | — | ✓ Containerized analytics toolchain (Compose stack) | ✓✓✓ Multi-stage production image builds, ECS task definitions | **2+ years** |
| **Data Pipelines** | ✓ Cron-scheduled Python ETL scripts | ✓✓✓ Multi-DAG Airflow pipelines, automated schema normalization | ✓✓✓ Real-time event ingestion pipelines (Kinesis → Spark → S3) | **4+ years** |
| **Java** | — | ✓ Read/maintain Java-based internal data services | ✓✓ JVM-based service contributions, Spark on JVM configuration | **1.5+ years** |
| **JavaScript** | — | ✓ Internal dashboard scripting (Datadog custom widgets) | ✓✓ Azure Function Apps (Node.js runtime), lightweight API endpoints | **1.5+ years** |
| **C#** | — | — | ✓✓ Dynamics 365 plugin development, Azure Function Apps (.NET runtime) | **6 months** |
| **Azure** | — | — | ✓✓✓ Function Apps, Azure Data Factory, Dynamics 365 integration, Azure DevOps | **6 months** |
| **Dynamics 365** | — | — | ✓✓ Plugin development, entity customization, Power Platform integration | **6 months** |
| **ECS** | — | — | ✓✓✓ Task definition authoring, service auto-scaling, Fargate deployment | **6 months** |
| **Kinesis** | — | — | ✓✓✓ Data stream provisioning, consumer application development | **6 months** |
| **EMR** | — | — | ✓✓✓ Cluster provisioning, Spark job submission, auto-scaling policies | **6 months** |
| **Function Apps** | — | — | ✓✓ Serverless event-driven compute (Azure), timer/HTTP triggers | **6 months** |
| **SaaS** | — | ✓ Consumer of SaaS analytics tooling (Datadog, internal BI) | ✓✓ SaaS platform extension development (Dynamics 365) | **2+ years** |
| **AI/ML Integration** | ✓ Feature-store API consumption for recommendation model support | ✓✓ ML model output integration into operational dashboards | ✓✓✓ GenAI/LLM pipeline integration, agentic workflow prototyping | **3+ years** |
| **GenAI / LLMs / Agentic Systems** | — | — | ✓✓✓ LLM-powered anomaly classification, agentic security triage prototype | **6 months** |
| **Scalable Architecture** | ✓ Operated on horizontally scaled Hive/Spark clusters | ✓✓ Designed multi-region pipeline architecture for 8 city markets | ✓✓✓ ECS auto-scaling, EMR elastic clusters, event-driven serverless design | **3+ years** |
| **Agile** | ✓ Sprint-based delivery within recommendation team | ✓✓ Scrum ceremonies, cross-functional stakeholder coordination (engineering, ops, finance) | ✓✓✓ 2-week sprint cycles, daily stand-ups, retrospectives | **4+ years** |
| **Git / CI/CD** | ✓ GitLab versioning | ✓✓ GitLab CI/CD: lint + test gates | ✓✓✓ GitHub Actions: full build → test → deploy pipeline | **4+ years** |

**ATS Depth Note:** Python, SQL, AWS, Spark, Data Pipelines, Distributed Systems, Scalable Architecture, AI/ML Integration, and Agile establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters. Azure, Dynamics 365, ECS, Kinesis, EMR, Function Apps, C#, and GenAI/LLM capabilities are anchored to TikTok's production infrastructure and substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Automated the recommendation team's daily A/B experiment metrics pipeline using **Python** (pandas, SQLAlchemy) and Linux cron scheduling, extracting and transforming experiment cohort data from a **Spark**-backed Hive data lake containing 1B+ user-event rows, eliminating approximately 6 manual analyst-hours per week and enabling same-day model iteration decisions.
- Authored and tuned complex **SparkSQL / HiveQL** queries against billion-row event datasets on the company's **distributed** Hive/Spark cluster to compute core recommendation KPIs (CTR, GMV lift, add-to-cart rate, novelty score), directly supplying the quantitative inputs for weekly model retraining cycles.
- Built a lightweight **Python** REST API client to pull upstream feature-store payloads from **AWS S3**-staged model artifacts and join them against downstream engagement logs, reducing ad-hoc feature attribution analysis turnaround from approximately 2 days to under 4 hours.
- Supported the **AI/ML** model evaluation workflow by preparing feature-engineered datasets and computing offline evaluation metrics (precision@k, recall@k) consumed by the recommendation algorithm team's model comparison framework.
- Standardized all analysis scripts and SQL templates under a shared GitLab repository with version-tagged releases, operating within the team's **Agile** sprint cadence and introducing reproducible re-run conventions that eliminated duplicated analytical work across 3 team members.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Designed and operationalized a multi-DAG **Python / Apache Airflow** data pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's weekly KPI reporting across 8 active city markets, pulling raw transactional data from **AWS Redshift**, applying **SparkSQL** transformation logic, and reducing report delivery lead time from 3 business days to under 4 hours.
- Curated a canonical **SQL** metric library of 40+ standardized definitions (DAU, GMV, order completion rate, delivery SLA, refund rate) adopted as the org-wide analytical standard; designed the library for compatibility with both **Redshift** and **Spark** execution engines, achieving 99.1% cross-team metric consistency over two consecutive quarterly audits.
- Engineered a **Python** schema-normalization **microservice** adapter layer ingesting raw feeds from 3 third-party Mexican logistics REST APIs, resolving field-level schema divergence across providers and supplying a unified **data pipeline** input to downstream Datadog **SaaS** dashboards consumed daily by a 50-person regional operations team.
- Containerized the full pipeline execution environment in **Docker** (multi-service Compose stack) and deployed it to the team's internal registry, ensuring bit-for-bit execution consistency across analyst workstations in Beijing and Mexico City — a **distributed systems** challenge spanning 2 time zones (UTC+8 / UTC−6) — and eliminating environment-dependent data discrepancies over the 14-month engagement period.
- Integrated **ML** model output (demand-forecasting predictions, delivery-time estimation scores) into the operational **data pipeline**, enabling the regional ops team to consume model-driven insights alongside traditional KPIs without manual post-processing, and accelerating go/no-go decisions for market expansion into 3 additional Mexican cities.
- Led cross-functional **Agile** sprint planning and retrospectives with engineering, operations, and finance stakeholders across Beijing and Mexico City, coordinating pipeline feature prioritization and ensuring analytical deliverables met the **scalable architecture** requirements of the expanding multi-region deployment.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Developed a production **Go** microservice on **AWS ECS** (Fargate) to ingest, normalize, and route security audit log events from 15+ internal platform services into the centralized detection pipeline via **Amazon Kinesis** data streams, processing peak throughput of approximately 15,000 events per minute and reducing mean time to security alert from approximately 4 minutes to under 30 seconds.
- Provisioned and managed **AWS EMR** clusters running **Apache Spark** (Structured Streaming) to perform real-time aggregation, sessionization, and anomaly scoring on security event streams consumed from **Kinesis**, enabling sub-minute detection latency on behavioral threat patterns across 50M+ daily events.
- Authored **Azure Function Apps** (Node.js and .NET/**C#** runtimes) to prototype serverless event-driven compute triggers for a **Dynamics 365**-based internal incident management SaaS module, enabling automated ticket creation and escalation routing upon detection of high-severity security signals.
- Integrated a **GenAI/LLM**-powered anomaly classification layer into the security event pipeline, deploying a fine-tuned large language model behind an internal API gateway to generate natural-language threat summaries and severity assessments, reducing manual analyst triage time by approximately 40% during the pilot evaluation window.
- Built an **agentic** security triage prototype using a multi-step LLM orchestration framework that autonomously correlated alerts across log sources, queried internal knowledge bases, and proposed remediation actions — evaluated by the security engineering team as a candidate for production integration in Q1 2026.
- Authored an end-to-end **GitHub Actions** CI/CD pipeline (build → SAST scan → multi-stage **Docker** image build/push → ECS task deployment) executing within the team's 2-week **Agile** sprint cycle, reducing average deployment cycle time from approximately 45 minutes to 12 minutes while maintaining >85% unit test coverage.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Recommendation Experiment Metrics Automation Platform**

*The recommendation algorithm team ran 6–8 concurrent A/B experiments per week on a Spark-backed data lake exceeding 1 billion user-event rows; metric summarization was performed manually in Excel by rotating analysts, producing a 24–48-hour reporting lag that deferred model iteration decisions and introduced recurring data-consistency conflicts between team members working from divergent query drafts.*

- Audited 9 recurring metric templates shared across all A/B experiment types and parameterized them into a reusable **Python** (pandas + SQLAlchemy) report generation module executing against the company's **distributed** Hive/**Spark** cluster, reducing per-experiment metric compilation from approximately 4 hours to under 20 minutes per analyst.
- Replaced ad-hoc query authoring with a pre-validated **SparkSQL / HiveQL** query library of 11 canonical templates covering core recommendation KPIs (CTR, GMV lift, add-to-cart rate, novelty score), enforcing consistent metric definitions across simultaneous experiments and eliminating analyst-level calculation discrepancies.
- Integrated the pipeline with upstream **AI/ML** model feature-store payloads via a **Python** REST API client pulling artifacts staged on **AWS S3**, enabling automated feature-attribution analysis as a standard step in the experiment evaluation workflow.
- Scheduled the module as a Linux cron job triggered nightly following feature-store refresh cycles; outputs were written as structured summary reports to a shared internal directory, compressing the A/B metric review cycle from 3–5 days to same-day availability and directly accelerating the recommendation model iteration cadence.
- Delivered a net reduction of approximately 6 analyst-hours per week across the 5-person team, operating within the team's **Agile** sprint framework with version-controlled SQL templates and scripts in GitLab.

---

### DIDI IBG · Key Project

**Mexico Food Market Cross-Region Data Pipeline and KPI Normalization Engine**

*The Mexico Food analytics function operated without a unified data layer: 7 independently maintained analyst Excel models tracked overlapping KPI sets using divergent metric definitions across 8 city markets spanning 2 time zones, causing cross-team reporting conflicts, systematically missing weekly SLAs by 2+ business days, and blocking data-driven market expansion decisions during high-growth sprints.*

- Consolidated 40+ overlapping metric definitions into a canonical **SQL** library governing DAU, GMV, order completion rate, delivery SLA compliance, and refund rate; designed for execution compatibility across both **AWS Redshift** and **Spark** engines, and formally adopted as the org-wide metric standard within one quarter of release.
- Built a multi-DAG **Python / Apache Airflow** **data pipeline**: upstream tasks extracted raw transactional data from **AWS Redshift**; mid-stream **PySpark** transformation tasks applied the canonical metric logic at **scalable** batch volumes; downstream tasks rendered Jinja-templated reports and pushed outputs to the Datadog **SaaS** dashboard layer consumed by the 50-person regional operations team.
- Developed a **Python** schema-normalization **microservice** adapter resolving field-level divergence across 3 third-party Mexican logistics REST APIs (field mapping, type coercion, null-handling conventions), providing reliable automated upstream ingestion and eliminating a previously recurring 2–4-hour weekly manual data reconciliation step.
- Containerized the full execution environment in **Docker** (Python 3.11, Airflow, SQLAlchemy, adapter packages) and maintained **distributed** deployment parity across analyst workstations in Beijing and Mexico City, eliminating a class of environment-dependent data discrepancies entirely over the 14-month engagement period.
- Integrated demand-forecasting **ML** model outputs into the pipeline's downstream reporting layer, enabling the regional ops team to consume **AI**-driven predictive metrics (estimated delivery volume, SLA breach probability) alongside traditional KPIs and accelerating go/no-go decisions on expansion into 3 new Mexican cities in Q1 2024.
- Reduced KPI report delivery from 3 business days to under 4 hours; the pipeline subsequently served as the primary analytical foundation for market expansion strategy, coordinated through cross-functional **Agile** sprint ceremonies spanning engineering, operations, and finance stakeholders.

---

### TIKTOK SECURITY · Key Project 1

**EventForge — Real-Time Security Event Ingestion and Big Data Processing Platform**

*Fifteen-plus internal platform services emitted security-relevant events — authentication failures, privilege escalation attempts, API anomaly signals — to isolated, schema-incompatible sinks totaling 50M+ daily events; the resulting fragmentation created detection blind spots in the centralized security pipeline, extended mean incident triage time to approximately 4 minutes, and prevented the security team from performing cross-source behavioral analysis at scale.*

- Designed and implemented **EventForge**, a **Go** microservice deployed on **AWS ECS** (Fargate) to ingest raw security events from 15+ upstream services via **gRPC** intake endpoints, normalize them against a unified internal event taxonomy, and publish them to **Amazon Kinesis** data streams for downstream consumption; the service sustained peak throughput of approximately 15,000 events per minute with 99.97% uptime over the 5-month production window.
- Provisioned **AWS EMR** clusters running **Apache Spark** Structured Streaming to consume from **Kinesis**, performing real-time aggregation, sessionization, and anomaly scoring across the full event stream; tuned Spark executor configurations and **EMR** auto-scaling policies to maintain sub-minute processing latency at 50M+ daily event volume while optimizing cluster cost by approximately 30% versus static provisioning.
- Integrated a **GenAI/LLM**-powered classification layer behind an internal API gateway: a fine-tuned large language model consumed enriched event payloads from the Spark processing stage and generated natural-language threat summaries with severity assessments, reducing manual analyst triage time by approximately 40% during the 8-week pilot evaluation window.
- Authored **Azure Function Apps** (Node.js and **C#**/.NET runtimes) as serverless triggers bridging the AWS-hosted detection pipeline to an internal **Dynamics 365** **SaaS** incident management module, enabling automated ticket creation and SLA-based escalation routing upon detection of high-severity security signals — a cross-cloud integration pattern evaluated for broader enterprise adoption.
- Architected the end-to-end system as a **scalable**, event-driven **distributed** architecture: ECS handled stateless ingestion, Kinesis provided durable buffering and fan-out, and EMR/Spark performed stateful stream processing — a separation-of-concerns design that allowed independent horizontal scaling of each tier and simplified capacity planning for projected 3× event volume growth in 2026.
- Authored a **GitHub Actions** CI/CD pipeline (build → SAST scan → multi-stage **Docker** image build/push → **ECS** task deployment) within 2-week **Agile** sprint cycles, reducing average deployment cycle time from approximately 45 minutes to 12 minutes while maintaining >85% unit test coverage.

---

### TIKTOK SECURITY · Key Project 2

**Sentinel Agent — LLM-Powered Agentic Security Triage System**

*The security engineering team's manual alert triage process required analysts to correlate signals across multiple disconnected log sources, consult internal knowledge bases, and formulate remediation actions — a workflow averaging 25–35 minutes per high-severity incident that created bottlenecks during alert surges and limited the team's effective incident throughput to approximately 15 high-severity cases per analyst per shift.*

- Designed and prototyped **Sentinel Agent**, an **agentic** multi-step LLM orchestration system that autonomously received enriched alert payloads from the EventForge **Kinesis** stream, correlated them against historical incident patterns stored in **AWS S3**-backed vector indices, queried internal runbook knowledge bases, and proposed structured remediation actions — evaluated by the security engineering team as a candidate for production integration in Q1 2026.
- Implemented the orchestration framework in **Python** using a tool-augmented **LLM** agent architecture: the agent executed multi-turn reasoning chains with tool calls to internal APIs (log search, asset inventory, Dynamics 365 incident lookup), enabling end-to-end triage from alert receipt to remediation proposal in under 3 minutes versus the previous 25–35-minute manual workflow.
- Deployed the agent inference pipeline on **AWS ECS** with GPU-optimized task definitions and integrated **Kinesis** consumer groups for event-driven triggering, ensuring the system scaled horizontally with alert volume while maintaining deterministic latency SLAs for high-severity event processing.
- Built an evaluation harness using **Spark** on **EMR** to batch-process historical incident data and compute precision/recall metrics against analyst ground-truth labels, enabling systematic comparison of LLM prompt strategies and retrieval configurations; the best-performing configuration achieved 82% agreement with senior analyst triage decisions on a 500-incident validation set.
- Authored **Azure Function Apps** (**JavaScript**/Node.js runtime) as lightweight webhook endpoints bridging agent outputs to the **Dynamics 365** incident management platform, enabling automated ticket enrichment with LLM-generated summaries and proposed remediation steps within the existing **SaaS** workflow.
- Documented the full system architecture, prompt engineering methodology, and evaluation results in an internal technical design document; presented findings to engineering leadership as part of the team's **Agile** sprint demo cycle, securing endorsement for a production pilot in the subsequent quarter.
