# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Enterprise Cloud & Data Systems Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery spanning **distributed** event processing, **big data** pipeline engineering (**EMR**/**Spark**, **Kinesis**), **microservice** development on **AWS** and **Azure**, and **SaaS** platform integration (**Dynamics 365**).
* **End-to-End Cloud Delivery:** Designs and ships **scalable** cloud-native data systems — from real-time streaming ingestion on **ECS**/Fargate and **Spark** Structured Streaming to serverless **Function Apps**, **AI/ML integration** layers, and **CI/CD** automation across multi-cloud environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator in **Agile** sprint environments, bridging engineering, operations, and business stakeholders across time zones and regions.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Infrastructure Contributions:_**

* Delivered an end-to-end **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage **Docker** image build/push → **ECS** deployment) within the team's 2-week **Agile** sprint cadence, cutting average deployment cycle from ~45 min to 12 min while maintaining >85% unit test coverage.
* Authored **Azure Function Apps** (**C#**/.NET and Node.js runtimes) as serverless event-driven triggers prototyping a **Dynamics 365**-integrated internal incident management **SaaS** module, enabling automated ticket creation and SLA-based escalation routing on high-severity signal detection.

**_Project: Real-Time Security Event Ingestion & Big Data Processing Platform_**

* Developed a production **Go** **microservice** on **AWS ECS** (Fargate) to ingest, normalize, and route security audit events from 15+ internal services into the centralized detection pipeline via **Amazon Kinesis** data streams; sustained ~15,000 events/min peak throughput at 99.97% uptime and reduced mean time-to-alert from ~4 min to under 30 sec.
* Provisioned **AWS EMR** clusters running **Apache Spark** Structured Streaming to consume from **Kinesis** and perform real-time aggregation, sessionization, and behavioral anomaly scoring across 50M+ daily events; tuned executor configurations and auto-scaling policies to maintain sub-minute detection latency while reducing cluster cost by ~30%.
* Architected the system as a **scalable** event-driven **distributed architecture**: **ECS** stateless ingestion → **Kinesis** durable buffering and fan-out → **EMR**/**Spark** stateful stream processing — each layer independently horizontally scalable, decoupling ingestion throughput from downstream processing capacity.

**_Project: AI-Driven Enterprise Privacy Compliance Platform_**

* Designed and implemented a multi-module enterprise **AI** compliance platform in **Go** on **Kubernetes** (**microservices** architecture), integrating **AWS Lambda** serverless compute for on-demand scan tasks and **AWS S3** for batch artifact staging; replaced 3+ legacy manual review workflows and reduced compliance review turnaround from days to minutes.
* Built an **AI/ML** field annotation pipeline integrating DeepSeek R1 and GPT-4 with automatic failover via multi-model routing; the pipeline infers privacy classifications from field names, data types, and contextual API paths — reducing manual annotation effort by ~70% in internal pilot (**GenAI**/**LLM** integration).
* Implemented a two-layer compliance validation engine: a deterministic rule engine covering ~80% of common violations at sub-100ms, combined with **LLM** semantic analysis for ambiguous edge cases; delivered sub-5-second compliance verdicts with confidence scoring.
* Architected a composable **agentic** SDK for enterprise **LLM** orchestration with synchronous hook-based tool-call interception for permission enforcement and auto-compaction context management sustaining stateful multi-turn interactions without manual overhead.
* Deployed on **Kubernetes** + **AWS Lambda** hybrid infrastructure with protocol-agnostic dispatch supporting **gRPC**, HTTP, and WebSocket; sustained sub-2-second P99 latency under concurrent multi-team compliance scan load.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and operationalized a multi-DAG **Python**/**Apache Airflow** **data pipeline** replacing 7 siloed manual workflows for Mexico Food's weekly KPI reporting across 8 city markets; ingested raw transactional data from **AWS Redshift**, applied **SparkSQL** transformation logic, and reduced report delivery from 3 business days to under 4 hours.
* Curated a canonical **SQL** metric library of 40+ standardized definitions adopted as the org-wide analytical standard; designed for cross-engine compatibility across **Redshift** and **Spark**, achieving 99.1% cross-team metric consistency.
* Engineered a **Python** schema-normalization adapter ingesting raw feeds from 3 third-party logistics **REST APIs**, resolving field-level divergence and delivering a unified model to downstream **Datadog** **SaaS** dashboards consumed daily by a 50-person operations team.
* Integrated demand-forecasting and delivery-time **ML** model outputs into the operational **data pipeline**, enabling the regional ops team to consume model-driven predictive KPIs alongside traditional metrics (**AI/ML integration**).
* Containerized the full pipeline environment in **Docker** and deployed to **AWS** (Redshift, S3), ensuring execution consistency across a 6-person, 2-timezone distributed team.
* Led cross-functional **Agile** sprint planning with engineering, operations, and finance stakeholders across two time zones, coordinating pipeline feature prioritization against **scalable architecture** requirements.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Automated the recommendation team's daily A/B experiment metrics pipeline using **Python** (pandas, SQLAlchemy); extracted and transformed cohort data from a **Spark**-backed Hive data lake containing 1B+ rows, eliminating ~6 manual analyst-hours per week (**big data**).
* Authored and optimized complex **SparkSQL**/**HiveQL** queries against billion-row event datasets on the company's **distributed** Hive/**Spark** cluster to compute core recommendation KPIs, supplying inputs directly to weekly model retraining cycles.
* Built a lightweight **Python** REST API client to retrieve upstream feature-store payloads from **AWS S3**-staged model artifacts, reducing ad-hoc feature attribution turnaround from ~2 days to under 4 hours.
* Supported the **AI/ML** evaluation workflow by preparing feature-engineered datasets and computing offline metrics consumed by the recommendation algorithm team's model comparison framework.

---

## Skills

**Languages:** Go, Python, C#, JavaScript, SQL, SparkSQL, HiveQL
**AWS:** ECS (Fargate), EMR, Kinesis, Lambda, Redshift, S3, CloudWatch
**Azure:** Function Apps, Dynamics 365, Azure DevOps
**Big Data:** Apache Spark (Structured Streaming, PySpark), Apache Airflow, Hive
**AI/ML & GenAI:** LLM Integration, Agentic Systems, GenAI, ML Pipeline Integration
**DevOps:** Docker, Kubernetes, GitHub Actions, CI/CD, Git, Agile/Scrum

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