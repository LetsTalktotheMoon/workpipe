# 去重审计报告 (Dedup Report)

生成时间: 2026-03-23

去重策略: 只要硬性技术栈不同，就不合并 → 归入 achievement_cluster (pick_one)

---


## ByteDance (TikTok)

总 bullets: 198, 跨简历 clusters: 12, 独立 bullets: 160


### Cluster 1: Dual-Layer Compliance Validation Engine

来源简历: [1, 2, 3, 4, 14]

共享指纹: []

- `BT-001` (R01): Engineered a dual-layer PreCheck validation engine combining a deterministic rule engine (fast-path ...

- `BT-002` (R02): Implemented a two-layer compliance validation engine: a deterministic rule engine covering ~80% of c...

- `BT-003` (R03): Built a dual-layer validation engine: a deterministic rule engine covering 80% of common violations ...

- `BT-004` (R04): Executed staged production rollout (1% → 10% → 50% → 100% traffic over 3 weeks), monitoring latency ...

- `BT-005` (R04): Built a dual-layer validation framework: a deterministic rule engine covering 80% of policy violatio...

- `BT-006` (R14): Built an automated **canary deployment** pipeline via **GitHub Actions** with **SLO**-gated progress...


### Cluster 2: GitHub Actions CI/CD Pipeline (Build→SAST→Deploy)

来源简历: [2, 9, 10, 16]

共享指纹: ['85%', 'kp:test coverage']

- `BT-007` (R02): Delivered an end-to-end **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage **Doc...

- `BT-008` (R09): Authored a **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage **Docker** image b...

- `BT-009` (R10): Owned the team's end-to-end **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage *...

- `BT-010` (R16): Implemented a **GraphQL** resolver layer with >85% integration test coverage to replace legacy REST ...


### Cluster 3: Schema Normalization & Transformation Engine

来源简历: [3, 6, 9, 13]

共享指纹: ['kp:schema conversion']

- `BT-011` (R03): Implemented a bidirectional transformation engine using **Go** generics and visitor-pattern schema t...

- `BT-012` (R06): Implemented a unified schema data model (49+ **Go** structs) and an AST-based transformation engine,...

- `BT-013` (R09): Designed a unified security event schema model in **Go** (49+ types spanning HTTP, RPC, and streamin...

- `BT-014` (R13): Designed and implemented a type-safe bidirectional schema conversion engine in **Go** using a **gRPC...


### Cluster 4: Distributed Compliance Workflow State Machine

来源简历: [3, 6, 7, 13]

共享指纹: ['5×', 'kp:approval cycle', 'kp:mongodb', 'kp:optimistic locking', 'kp:state machine', 'to_2']

- `BT-015` (R03): Engineered a **distributed** compliance workflow state machine (10+ state transitions) with MongoDB ...

- `BT-016` (R06): Built a distributed compliance ticket state machine using **MongoDB** optimistic locking (version-nu...

- `BT-017` (R07): Implemented a distributed compliance workflow state machine in **Go** managing 10+ state transitions...

- `BT-018` (R13): Engineered a distributed compliance workflow state machine with MongoDB optimistic locking ensuring ...


### Cluster 5: Container Deployment & Orchestration (K8s/Docker)

来源简历: [4, 7, 11, 13]

共享指纹: ['kp:kubernetes']

- `BT-019` (R04): Containerized ML **model serving** endpoints using **Docker** (multi-stage builds) and deployed via ...

- `BT-020` (R07): Containerized three microservices with **Docker** and authored **Kubernetes** manifests on **AWS** E...

- `BT-021` (R11): Operated production **Kubernetes** (GKE) multi-namespace cluster infrastructure for **LLM**-powered ...

- `BT-022` (R13): Authored **Kubernetes** Deployment manifests, HorizontalPodAutoscaler configurations, and PodDisrupt...


### Cluster 6: Security Audit Event Ingestion Service

来源简历: [2, 9, 10]

共享指纹: ['from_4', 'kp:audit event', 'kp:security audit']

- `BT-023` (R02): Developed a production **Go** **microservice** on **AWS ECS** (Fargate) to ingest, normalize, and ro...

- `BT-024` (R09): Designed and shipped a production **Go** microservice with a **gRPC** intake endpoint (**Protocol Bu...

- `BT-025` (R10): Developed a production **Go** microservice ingesting security audit events — authentication failures...


### Cluster 7: Kubernetes Cluster Deployment (Helm/HPA)

来源简历: [9, 10, 12]

共享指纹: ['99.97%', 'kp:helm', 'kp:kubernetes']

- `BT-026` (R09): Deployed to **GCP GKE**-managed **Kubernetes** cluster via **Helm** chart with HPA; implemented faul...

- `BT-027` (R10): Deployed to a company-managed **Kubernetes** cluster via versioned **Helm** chart with HPA configure...

- `BT-028` (R12): Deployed and hardened **blockchain** node infrastructure (Geth, Erigon) across 3 availability zones ...


### Cluster 8: Observability & SLO Instrumentation

来源简历: [1, 14]

共享指纹: ['from_45', 'kp:opentelemetry']

- `BT-029` (R01): Instrumented classification microservices with **OpenTelemetry** and **Datadog** SLO dashboards (**t...

- `BT-030` (R14): Instrumented all services with **OpenTelemetry** distributed tracing, **Prometheus** custom metrics,...


### Cluster 9: GitHub Actions CI/CD & Container Deployment

来源简历: [1, 18]

共享指纹: ['kp:github actions', 'to_30']

- `BT-031` (R01): Containerized services with **Docker** and deployed on **AWS EKS** via **Kubernetes** manifests; aut...

- `BT-032` (R18): Designed and maintained a **CI/CD** pipeline (**GitHub Actions**) automating cross-compilation (**CM...


### Cluster 10: Dual-Protocol API Layer (REST + gRPC)

来源简历: [3, 6]

共享指纹: ['5M+', '99.9%', 'kp:docker', 'kp:dual-protocol', 'kp:kubernetes']

- `BT-033` (R03): Delivered dual-protocol API layer over **Kubernetes**-orchestrated **Docker** containers, handling 5...

- `BT-034` (R06): Delivered a **RESTful** and **gRPC** dual-protocol API layer over **Kubernetes**-orchestrated **Dock...


### Cluster 11: Multi-Model LLM Routing Layer

来源简历: [4, 11]

共享指纹: ['99.9%', 'kp:multi-model']

- `BT-035` (R04): Architected a unified **LLM** multi-model routing layer in **Python** integrating GPT-4, Claude-3, a...

- `BT-036` (R11): Built a multi-model **LLM** routing layer (DeepSeek R1, GPT-4, Claude-3, OpenRouter) with unified **...


### Cluster 12: Kafka Event Consumer Service

来源简历: [6, 7]

共享指纹: ['kp:postgresql', 'to_200']

- `BT-037` (R06): Developed a **Kafka** consumer service in **Python** to ingest real-time security events, applying r...

- `BT-038` (R07): Developed a **Kafka** consumer service in **Python** subscribing to 4 upstream **security** event to...


## DiDi IBG

总 bullets: 126, 跨简历 clusters: 4, 独立 bullets: 109


### Cluster 1: ETL / Data Pipeline Engineering

来源简历: [2, 4, 5, 9, 10, 13, 14, 19, 20]

共享指纹: ['from_3']

- `DD-001` (R02): Designed and operationalized a multi-DAG **Python**/**Apache Airflow** **data pipeline** replacing 7...

- `DD-002` (R04): Engineered a **Python** ETL pipeline consolidating 4 heterogeneous data sources into a unified analy...

- `DD-003` (R05): Designed and shipped a **TypeScript**-based **compliance** analytics portal consolidating 14 heterog...

- `DD-004` (R09): Designed and operationalized a multi-DAG **Python**/**Apache Airflow** pipeline replacing 7 siloed m...

- `DD-005` (R10): Designed and operationalized an end-to-end **Python**/**Apache Airflow** DAG pipeline replacing 7 si...

- `DD-006` (R13): Authored **Go** CLI tooling integrated with DiDi's internal RPC service registry to automate recurri...

- `DD-007` (R14): Designed and operationalized a multi-DAG **Python**/**Apache Airflow** **data pipeline** replacing 7...

- `DD-008` (R19): Designed and operationalized a **Python**/**Apache Airflow** pipeline replacing 7 siloed manual work...

- `DD-009` (R20): Designed and operationalized a Python/Apache Airflow DAG pipeline integrating **Zuora Billing** invo...


### Cluster 2: Canonical SQL Metric Library

来源简历: [2, 9, 10]

共享指纹: ['99.1%', 'kp:metric library']

- `DD-010` (R02): Curated a canonical **SQL** metric library of 40+ standardized definitions adopted as the org-wide a...

- `DD-011` (R09): Curated a canonical **SQL** metric library of 40+ standardized KPI definitions adopted as the org-wi...

- `DD-012` (R10): Established a canonical **SQL** metric library of 40+ standardized KPI definitions adopted as the or...


### Cluster 3: Operational Anomaly Detection System

来源简历: [4, 6, 7]

共享指纹: ['kp:anomaly detection', 'to_9']

- `DD-013` (R04): Built an automated anomaly detection system using **PyTorch** LSTM for seasonality modeling, reducin...

- `DD-014` (R06): Built a **Python** anomaly detection system monitoring operational KPIs with configurable thresholds...

- `DD-015` (R07): Developed a **Python** anomaly detection module monitoring 9 operational KPIs with configurable aler...


### Cluster 4: C++ Native Performance Extension (ETA Prediction)

来源简历: [17, 18]

共享指纹: ['14×', 'from_22', 'to_90']

- `DD-016` (R17): Engineered a **C++** native extension (via **Python** ctypes) replacing a pure-Python Haversine dist...

- `DD-017` (R18): Architected a **C++14** native performance extension (Python ctypes) for the delivery ETA prediction...


## Temu

总 bullets: 80, 跨简历 clusters: 5, 独立 bullets: 59


### Cluster 1: Large-Scale Data Analytics (HiveQL/SparkSQL, 1B+ Events)

来源简历: [2, 9, 10, 11, 12, 14, 15, 17, 18, 19, 20, 21]

共享指纹: ['1B+', 'kp:spark']

- `TM-001` (R02): Automated the recommendation team's daily A/B experiment metrics pipeline using **Python** (pandas, ...

- `TM-002` (R09): Authored and optimized complex **HiveQL**/**SparkSQL** queries against 1B+ row event **databases** t...

- `TM-003` (R10): Authored and tuned complex **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract...

- `TM-004` (R11): Authored HiveQL/SparkSQL queries against 1B+ row user-event datasets to extract A/B test cohort metr...

- `TM-005` (R12): Authored HiveQL/SparkSQL queries against 1B+ row transaction datasets to extract **payment** funnel ...

- `TM-006` (R14): Automated the **ad serving** and recommendation team's daily A/B experiment **monitoring** pipeline ...

- `TM-007` (R15): Authored and tuned HiveQL/SparkSQL queries against 1B+ row event datasets to compute **transaction**...

- `TM-008` (R17): Authored and tuned **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract A/B tes...

- `TM-009` (R18): Optimized **HiveQL**/**SparkSQL** queries against 1B+ row datasets via execution plan analysis and p...

- `TM-010` (R19): Authored and tuned **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract A/B tes...

- `TM-011` (R20): Authored and tuned HiveQL/SparkSQL queries against 1B+ row transaction datasets to extract **SaaS Su...

- `TM-012` (R21): Developed **Python**-based automated data validation scripts to verify recommendation model A/B expe...


### Cluster 2: Feature-Store REST API Client

来源简历: [2, 9, 10]

共享指纹: ['from_2', 'kp:feature-store', 'kp:feature-store payload', 'to_4']

- `TM-013` (R02): Built a lightweight **Python** REST API client to retrieve upstream feature-store payloads from **AW...

- `TM-014` (R09): Built a lightweight **Python REST API** client to pull upstream feature-store payloads and join them...

- `TM-015` (R10): Built a lightweight **Python** **REST API** client to pull upstream feature-store payloads and join ...


### Cluster 3: ETL / Data Pipeline Engineering

来源简历: [1, 8]

共享指纹: ['50M+', 'kp:hive']

- `TM-016` (R01): Maintained **Hive**/**Spark SQL** batch jobs processing 50M+ daily user interaction events to genera...

- `TM-017` (R08): Authored **Python** ETL scripts to extract, deduplicate, and normalize raw clickstream logs (50M+ da...


### Cluster 4: Event Log Batch Processing & Preprocessing

来源简历: [6, 7]

共享指纹: ['15%', '3%', 'kp:event log']

- `TM-018` (R06): Automated raw user event log batch processing in **Python** to standardize feature formatting ahead ...

- `TM-019` (R07): Developed **Python** automation scripts to batch-process 500K+ daily raw user event logs with rule-b...


### Cluster 5: Binary Log Parsing Utility

来源简历: [17, 18]

共享指纹: ['from_45', 'kp:binary log', 'to_3']

- `TM-020` (R17): Developed a **C** utility to parse binary log dumps (~200 MB/day) into structured CSV for downstream...

- `TM-021` (R18): Developed **C** binary log parsing utilities using struct-packed I/O and memory-mapped file reads, r...
