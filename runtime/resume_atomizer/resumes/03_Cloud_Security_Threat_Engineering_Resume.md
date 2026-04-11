# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Security Infrastructure & Threat Engineering:** 3+ years of technical experience designing threat detection pipelines, fraud intelligence systems, and backend security infrastructure at hyperscale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**). Production delivery spanning **distributed systems**, **DLP** enforcement, **AI**-driven **anomaly detection**, and **Secure-by-Default** architecture.
* **Research-to-Production Security Delivery:** Builds end-to-end security systems in **C++** and **Go** — from real-time **threat detection** pipelines processing billions of daily events to **ML**-based classification, **vulnerability management** automation, and **incident response** workflow optimization across **cloud** environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic, adversarial thinking. Effective cross-functional collaborator bridging security, infrastructure, product, and legal teams in **Agile** environments. Strong foundation in **data structures and algorithms**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Security Engineering Contributions_**

* Developed **Go**-based microservice components within the Security Platform's **threat detection** system, consuming **Kafka** real-time event streams to compute per-entity behavioral **anomaly** scores across 2B+ daily events and producing risk-tiered signals for downstream SOC alert triage.
* Refactored **C++** alerting module to eliminate redundant rule evaluation passes, reducing false positive alert volume by 31% in A/B shadow comparison and measurably improving SOC analyst throughput on high-fidelity signal triage.
* Implemented **DLP** enforcement middleware integrated into the content inspection API, applying **security primitives** — pattern matching, entropy scoring, token classification — to outbound payloads; reduced policy-violating data exposure events by 23% in controlled UAT.
* Integrated automated vulnerability scanner (**Python** + shell scripting) into the team's **CI/CD** pipeline, detecting 18 critical dependency CVEs across 6 sprint cycles prior to deployment, reinforcing the team's **Secure-by-Default** build posture (**vulnerability management**).
* Mapped red-team attack patterns to **MITRE ATT&CK** TTPs to enrich **incident response** runbooks, reducing mean time to escalation for P0 security events by 40% through standardized detection-to-ticketing **automation** (**offensive security**).

**_Project: AI-Driven Compliance Platform (Crystal AI)_**

* Architected a unified **LLM** routing layer integrating 5+ model providers with automatic failover and cost-optimized dispatch, enabling **AI**-driven compliance **anomaly detection** at field granularity across 1,000+ field APIs; achieved 99.9% call availability at <3s P99 response time.
* Built a dual-layer validation engine: a deterministic rule engine covering 80% of common violations at <50ms, combined with **LLM** semantic analysis for ambiguous edge cases; reduced compliance ticket rejection rate from >50% to <10% across 10+ engineering teams.
* Designed a Sync/Async dual-mode Hooks system as a **security primitive** within the enterprise AI agent framework, enabling synchronous execution-blocking for high-risk tool invocations before completion — achieving zero **security** policy bypass incidents across 50+ instrumented production agent deployments.
* Implemented a protocol-agnostic agent deployment architecture — single **Go** codebase serves via messaging, IDE integration (**MCP**), HTTP REST, and WebSocket — embedding **security** compliance **tooling** natively into developer workflows.

**_Project: Unified Compliance Gateway (Sienna)_**

* Designed a unified schema normalization layer (49+ **Go** structs) consolidating six heterogeneous gateway data formats onto a single **security** policy enforcement surface via composition-over-inheritance; reduced new gateway onboarding from 2 weeks to 3 days (**large-scale systems design**).
* Implemented a bidirectional transformation engine using **Go** generics and visitor-pattern schema traversal to migrate 1.2M+ legacy schema entries with 100% data fidelity and zero-downtime cutover; <5ms per-schema conversion latency.
* Engineered a **distributed** compliance workflow state machine (10+ state transitions) with MongoDB optimistic locking ensuring concurrent write safety; reduced approval cycle from 7 days to 2 days at 5× throughput.
* Delivered dual-protocol API layer over **Kubernetes**-orchestrated **Docker** containers, handling 5M+ daily API calls at <100ms P99 latency and 99.9% availability for 10+ downstream systems.
* Built an **AI**-augmented compliance monitoring engine aggregating cross-module telemetry into organization-wide **security** posture dashboards with 50+ compliance metrics across EU/US/SG regions; >80% test coverage across all gateway types.
* Collaborated with infrastructure team on **distributed** storage evaluation, benchmarking **Google Cloud Spanner**-compatible schema patterns against internal KV store options; findings documented in architecture decision record for post-internship handoff.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Led end-to-end fraud and **risk analytics** for DiDi Food's Latin America market, processing 5M+ daily transaction events in **Python** to detect merchant fraud, promotional coupon abuse, and account takeover patterns across 50K+ active vendor accounts.
* Developed **NLP**-based fake-review classification model by fine-tuning **BERT** on 200K labeled samples, achieving 91% precision at production scale across 300K+ monthly reviews; operationalized as a secondary risk signal in the merchant scoring pipeline (**ML for security**).
* Designed **distributed** batch-processing pipeline on **Apache Spark** to aggregate cross-market behavioral signals, reducing daily risk score refresh latency from 6 hours to 47 minutes and enabling same-day fraud intervention workflows (**big data**).
* Automated monthly regulatory compliance reporting for Mexican financial authorities (CNBV) using **Python** + **SQL** templating, reducing per-cycle generation from 12+ analyst-hours to 45 minutes (**automation**).
* Partnered cross-functionally with product, engineering, and legal teams to establish **Hive/Spark** data marts as single source of truth, resolving metric discrepancies that had blocked two strategic quarterly reviews (**cross-functional collaboration**).

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Implemented **SQL**-based anomaly flag logic to detect statistical drift and null-rate degradation across 40+ recommendation feature columns, identifying 4 confirmed silent data poisoning incidents before propagation to live model serving.
* Queried 100M+ daily user clickstream records via **Hive SQL** to surface behavioral ranking signal patterns, directly informing weekly feature prioritization for the recommendation algorithm team.
* Automated daily ETL reporting pipeline using **Python** and **Apache Airflow**, reducing per-analyst manual data preparation from ~4 hours to 35 minutes (**automation**).

---

## Skills

**Languages:** Go, C++, Python, SQL, Hive SQL
**Security:** DLP, Threat Detection, Anomaly Detection, Security Primitives, MITRE ATT&CK, Vulnerability Management, Incident Response, Secure-by-Default, Offensive Security
**AI/ML:** LLM Integration, NLP/BERT, Machine Learning for Security, scikit-learn
**Systems & Infrastructure:** Distributed Systems, Apache Spark, Kafka, gRPC, MongoDB, Redis, Docker, Kubernetes, Apache Airflow, CI/CD
**Cloud & Storage:** GCP, Google Cloud Spanner, S3-compatible Object Storage, Hive/Spark Data Marts

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