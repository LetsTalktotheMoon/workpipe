# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Platform Reliability & Resilience Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **distributed systems** **observability** (**Prometheus**, **Grafana**, **Datadog**, **OpenTelemetry**), **low-latency** event pipeline engineering (**Kafka**, **Kinesis**, **Druid**), **chaos engineering**, and **canary deployment** orchestration.
* **End-to-End Reliability Delivery:** Builds and hardens production systems — from **real-time** event ingestion and **SLO**-gated progressive rollouts to structured **root cause analysis**, fault injection testing, and automated **monitoring**/**alerting** stacks with **PagerDuty** escalation across **cloud** environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator in **Agile** environments, bridging security, platform, and operations teams to drive measurable improvements in system **reliability** and incident response.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Reliability & Observability Contributions:_**

* Instrumented the full microservice stack with **OpenTelemetry** SDKs — **C++** hooks for low-level event parsing, **Python** and **TypeScript** for auxiliary services — exporting distributed traces, metrics, and structured logs to a **Prometheus** + **Grafana** **monitoring**/**alerting** stack with **PagerDuty** escalation; reduced mean time to detection (MTTD) from ~4 min to under 30 sec (**telemetry**).
* Executed **chaos engineering** experiments using **Litmus**-based fault injection (pod termination, network latency injection, Kinesis shard splits) across 12 failure scenarios, identifying 3 undetected single-points-of-failure before production traffic scaling; raised system resilience score from 67% to 94%.
* Built an automated **canary deployment** pipeline via **GitHub Actions** with **SLO**-gated progressive traffic shifting (5% → 25% → 50% → 100%) and automated rollback on error budget exhaustion; zero regression-caused outages across 18 production releases.
* Co-facilitated blameless postmortem processes and authored formal **root cause analysis** documents for 6 production incidents, applying fault-tree analysis and tracking remediation items to closure within **Agile** sprint cycles; established an **auditing** framework recording all configuration changes as immutable event logs.

**_Project: Chaos-Resilient Real-Time Security Event Pipeline_**

* Developed a production **Go** microservice on **AWS ECS** (Fargate) ingesting security event streams from 15+ internal services, normalizing against a unified taxonomy, and publishing to **Amazon Kinesis** for downstream **Apache Druid** **real-time** OLAP aggregation; sustained ~15,000 events/min at P99 < 200ms with 99.97% uptime over the 6-month deployment (**low-latency**, **data pipelines**).
* Defined explicit **distributed** resilience boundaries: ECS handled stateless ingestion with circuit breakers; **Kinesis** provided durable event buffering with per-shard dead-letter queues for **auditing** and replay; **Druid** performed stateful real-time aggregation — partitioned failure domains ensured no single-component failure propagated to downstream detection latency **SLOs**.
* Authored **Azure Function Apps** (**C#**/.NET and **TypeScript** runtimes) as serverless triggers bridging the AWS-hosted pipeline to an internal Dynamics 365 incident management module, enabling automated SLA-based ticket creation and escalation routing on high-severity signal detection (**cloud applications**).

**_Project: API Gateway Compliance Scoring Platform_**

* Designed and deployed a multi-service **Go** microservice platform on **Kubernetes** with HTTP/2 REST + **gRPC** **API** gateway layer, providing compliance scoring, stream quantification, and observability across enterprise gateway traffic for 10+ internal consumer systems.
* Engineered a dual-queue streaming pipeline consuming **Kafka** event feeds in a producer-consumer decoupled architecture; applied schema normalization transforms against compliance event streams and staged encrypted payloads to **AWS S3** asynchronously, sustaining high-throughput ingestion at sub-second latency.
* Implemented a two-tier caching layer — in-process LRU cache for sub-millisecond hot-path reads + distributed Redis for cross-instance score consistency — reducing P95 scoring **API** latency by 78% under high-concurrency load tests.
* Instrumented all services with **OpenTelemetry** distributed tracing, **Prometheus** custom metrics, and structured logging; established end-to-end trace correlation reducing MTTD for pipeline regressions from ~45 min to under 5 min, maintaining 99.9%+ **SLO** compliance for scoring API availability (**observability**).

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and operationalized a multi-DAG **Python**/**Apache Airflow** **data pipeline** replacing 7 siloed manual workflows for Mexico Food's weekly reliability and business KPI reporting across 8 city markets; reduced report delivery from 3 business days to under 4 hours.
* Curated a canonical **SQL** metric library of 40+ standardized definitions and established formal **SLO** targets for delivery-time and order-completion metrics adopted across the regional operations organization.
* Engineered a **Python** schema-normalization adapter ingesting real-time feeds from 3 third-party logistics **APIs**, publishing a unified validated event stream to **Datadog** **monitoring** dashboards and automated **alerting** rules consumed daily by a 50-person operations team.
* Instrumented Airflow DAGs and adapter services with **Datadog** APM tracing, enabling real-time pipeline health **monitoring**, latency regression detection, and structured **root cause analysis** on SLA breaches via distributed trace correlation.
* Implemented staged **canary deployments** of pipeline logic updates to a city-market subset before full rollout, using **SLO** metric-comparison gates to validate behavior before promoting changes to all 8 markets.
* Containerized the full pipeline environment in **Docker** and conducted failure-mode simulation testing (network partition, dependency shutdown) during cross-region migration, verifying pipeline resilience under degraded conditions.

### Machine Learning Data Analyst | Temu · R&D · Recommendation & Ad Ranking Infra | Shanghai

**Jun 2021 – Feb 2022**

* Automated the **ad serving** and recommendation team's daily A/B experiment **monitoring** pipeline using **Python** and Linux cron scheduling, extracting cohort metrics from a **Spark**-backed Hive data lake (1B+ rows) and generating threshold-breach alerts across **SSP**/**DSP** integration paths (**alerting**).
* Authored and optimized **SparkSQL**/**HiveQL** queries against billion-row **programmatic** ad impression and user interaction event datasets to compute delivery KPIs (impression latency percentiles, bid-response error rates, throughput per **ad ranking** model variant), supplying quantitative baselines for **SLO**-adjacent evaluation criteria.
* Performed structured **debugging** and **root cause analysis** on recurring A/B cohort metric anomalies (population drift, **ad server** logging pipeline skew), documenting findings in reproducible investigation templates and reducing repeat investigation incidents by ~35%.
* Standardized **monitoring** scripts and SQL templates under a shared GitLab repository with version-tagged releases, establishing baseline **observability** conventions (structured logging, error categorization) adopted by adjacent **programmatic advertising** analytics teams.

---

## Skills

**Languages:** Go, Python, C++, C#, TypeScript, SQL, SparkSQL
**Observability & Monitoring:** Prometheus, Grafana, Datadog, OpenTelemetry, PagerDuty, SLO/SLA Design
**Resilience:** Chaos Engineering (Litmus), Canary Deployments, Circuit Breakers, Root Cause Analysis, Debugging
**Cloud & Streaming:** AWS (ECS, Kinesis, Redshift, S3), Apache Druid, Apache Kafka, Apache Airflow
**Distributed Systems:** Kubernetes, gRPC, Redis, Distributed Tracing, Low-Latency Architecture
**DevOps:** Docker, GitHub Actions, CI/CD, Agile/Scrum
**Ad Tech:** Programmatic Advertising, SSP/DSP, Ad Server, Ad Ranking, Impression/Bid Metrics

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