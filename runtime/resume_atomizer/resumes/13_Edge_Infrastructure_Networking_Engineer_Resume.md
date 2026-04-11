# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Edge Infrastructure & Networking Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **Go**-based **gRPC** microservice development, **Envoy**/**NGINX** edge gateway configuration, **TLS**/**mTLS** enforcement, and **Kubernetes**/**Helm**-orchestrated deployments with **Terraform**-managed **Infrastructure as Code**.
* **End-to-End Platform Delivery:** Designs and ships low-latency **service mesh** infrastructure — from **Protobuf**-governed API contracts and bidirectional **gRPC** streaming to **GitOps** pipelines (**Flux**), **CDN** edge performance diagnostics, and **SLO**-driven reliability engineering across multi-AZ production environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective collaborator bridging platform, security, and operations teams with strong ownership of **production infrastructure**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Infrastructure & GitOps Contributions_**

* Authored **Kubernetes** Deployment manifests, HorizontalPodAutoscaler configurations, and PodDisruptionBudget policies across 3 geographic AZs; service maintained 99.95% uptime SLA through a 6-week staged canary rollout with automated error-rate threshold-based rollback.
* Developed **Terraform** modules provisioning **NGINX**-based edge gateway resources, replacing 400+ lines of manual runbook steps with idempotent **Infrastructure as Code** declarations and reducing environment provisioning time from 2 days to 35 minutes.
* Implemented a **Flux CD** **GitOps** pipeline reconciling **Helm** chart releases from a canonical Git repository to 3 production **Kubernetes** clusters, eliminating manual kubectl apply steps and contributing to a 60% reduction in deployment-related incidents.
* Authored **OpenAPI** 3.0 specifications for 2 internal security signal APIs with linting rules enforced in CI; contract-first standard adopted by 4 downstream consumer teams as the platform API governance baseline.

**_Project: Real-Time Content Security Signal Routing Service_**

* Engineered a **Go**-based **gRPC** bidirectional streaming microservice reducing end-to-end security signal propagation latency from 8–12 seconds to sub-200ms at 120K+ RPS; defined 5 **Protobuf** message schemas as versioned contracts between 3 upstream classifier teams and 4 downstream consumers.
* Configured **Envoy** sidecar proxy for **mTLS** mutual authentication and per-request **OpenTelemetry** trace header propagation across all **service mesh** hops, enabling full-fidelity latency attribution in distributed traces without instrumentation changes to upstream or downstream services.
* Diagnosed a **TLS** certificate rotation failure by correlating OpenSSL handshake error rate spikes with **TCP/IP**-layer connection reset metrics; formalized root-cause analysis as a permanent team runbook, preventing a projected 99.99% availability SLA breach.

**_Project: Distributed Compliance Schema Platform_**

* Designed and implemented a type-safe bidirectional schema conversion engine in **Go** using a **gRPC** + Thrift dual-protocol API surface, modeling 49+ entity variants across 6 gateway types; executed live migration of 1M+ legacy schema entries with 100% data fidelity and zero-downtime cutover.
* Built a **Kafka**-driven event processing pipeline decoupling schema-change producers from downstream compliance consumers; defined 25+ interface specifications across 20 **OpenAPI** domains, establishing a contract-first API governance standard for 10+ internal consumer systems.
* Engineered a distributed compliance workflow state machine with MongoDB optimistic locking ensuring concurrent write safety across multi-team approval pipelines; reduced approval cycle from 7 days to 2 days at 5× throughput.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and owned a cross-region analytics pipeline parsing **Protobuf**-serialized **gRPC** API responses from 6 internal microservices into a unified **SQL** reporting schema serving 15+ stakeholders across 2 time zones.
* Authored **Go** CLI tooling integrated with DiDi's internal RPC service registry to automate recurring data extraction workflows, reducing ad-hoc data fulfillment turnaround from 3 business days to under 4 hours.
* Defined and maintained **Protobuf**-aligned data schemas for 3 newly launched food vertical metrics in collaboration with backend engineers, establishing backward-compatibility conventions that reduced schema-change-induced pipeline breakage from 4 incidents/month to 1.
* Instrumented reproducible **Kubernetes**-hosted analysis environments via **Helm** chart templates, enabling 10 analysts to provision compute environments within 5 minutes versus a prior 2-day manual setup process.
* Produced a Mexico **CDN** edge node geo-latency benchmarking report surfacing a 340ms P99 regression in the food ETA prediction API; traced to an **NGINX** upstream timeout misconfiguration, escalated to infrastructure team, and resolved with a measured 290ms P99 improvement within 48 hours.
* Redesigned A/B experiment holdout segmentation using deterministic hash-based user assignment in **SQL**/**Python**, reducing control group leakage incidents by 28%.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Automated weekly recommendation performance reporting by building **Python** ETL pipelines ingesting 50M+ daily user interaction events, reducing analyst reporting cycle from 12 hours/week to 1.5 hours.
* Authored and maintained 30+ **SQL** metric views standardizing CTR, CVR, and coverage rate definitions across 3 algorithm engineering squads, eliminating cross-team KPI discrepancies.
* Identified a data freshness regression in the item-embedding update pipeline through **HTTP** API response log analysis; produced a reproducible failure trace enabling the algorithm team to reduce embedding update latency from 6 hours to 45 minutes.

---

## Skills

**Languages:** Go, C++, Python, SQL
**Networking & Edge:** Envoy, NGINX, TLS/mTLS, TCP/IP, CDN, Service Mesh, HTTP/2
**Infrastructure:** Kubernetes, Helm, Terraform, Flux CD (GitOps), Docker, Infrastructure as Code
**APIs & Protocols:** gRPC, Protobuf, Thrift, REST APIs, OpenAPI 3.0
**Data & Messaging:** Kafka, MongoDB, Redis, MySQL
**Observability:** OpenTelemetry, Prometheus, Datadog, SLO/SLA Design

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