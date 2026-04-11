## MODULE 1 — Professional Summary

> *3 sentences. ATS-safe. Zero narrative sentiment.*

Systems-oriented engineer with 4+ years of progressive technical depth across data infrastructure and backend development at hyperscale consumer internet platforms (Temu · Didi · TikTok), applying a cross-disciplinary academic foundation in behavioral science and quantitative modeling to bring rigorous observability instincts to distributed system diagnostics and service reliability analysis. Hands-on engineering scope spans Go-based gRPC microservice development, Kubernetes/Helm deployment orchestration, Envoy service mesh configuration, and Terraform-managed edge gateway IaC on TikTok Safety's production infrastructure, built on 20+ months of Protobuf schema ownership and data pipeline instrumentation across Didi's international food delivery operations. Currently completing dual graduate programs concentrated in distributed systems and computer networking (UIUC MSIM · Georgia Tech OMSCS), with targeted preparation in low-latency transport protocol engineering, CDN edge service orchestration, and cloud-native infrastructure reliability.

---

## MODULE 2 — Snowball Distribution Strategy

### Technology Progression Map

| Technology | Temu (2021.06–2022.02) | Didi IBG (2022.09–2024.05) | TikTok Safety (2025.06–2025.12) |
|---|---|---|---|
| **Python / SQL** | ✓ ETL scripting · REST API consumption · metric dashboards | ✓ Pipeline engineering · A/B holdout logic · complex aggregations | — |
| **HTTP / REST** | ✓ Consuming internal APIs · log analysis | ✓ API data contract review · latency benchmarking | ✓ **Deep:** HTTP/2 · header manipulation · API spec authoring |
| **gRPC / Protobuf** | — | ✓ Consuming RPC responses · schema co-authoring with backend teams | ✓ **Building:** bidirectional streaming · service definition ownership |
| **Go** | — | ✓ CLI tooling for automated data extraction against internal RPC registry | ✓ **Primary:** microservice dev · middleware · request routing logic |
| **Kubernetes / Helm** | — | ✓ Awareness: K8s-hosted notebook environments · Helm chart consumption | ✓ **Hands-on:** manifest authoring · HPA · PodDisruptionBudget · multi-AZ |
| **Terraform / IaC** | — | ✓ Basic: data analysis environment provisioning (from 2023 Q1) | ✓ **Production:** module authoring · edge gateway lifecycle management |
| **NGINX / Envoy** | — | ✓ Awareness: upstream latency analysis · reporting NGINX config regression | ✓ **Hands-on:** Envoy sidecar config · mTLS termination · proxy tuning |
| **TLS / TCP/IP** | — | — | ✓ **Deep:** certificate rotation · handshake diagnostics · connection-level tracing |
| **CDN / Edge Services** | — | ✓ Data: geo-latency benchmarking across Mexico PoPs | ✓ **Engineering:** edge gateway provisioning · traffic routing rules |
| **Service Mesh** | — | — | ✓ **Production:** Envoy-based mesh · mTLS enforcement · distributed tracing |
| **GitOps / Flux / Helm** | — | ✓ Basic: Helm chart template consumption from data platform team | ✓ **Production:** Flux CD pipeline · Helm release Git reconciliation |
| **OpenAPI** | — | ✓ Consumer: reading internal API specs for pipeline integration | ✓ **Authoring:** schema definition · versioning contracts · CI linting |

### Cumulative Experience Claims (as of graduation 2026.05)

| Skill | First Exposure | Duration Claim | Legitimacy Basis |
|---|---|---|---|
| Go | Didi 2022.09 | **~3.5 years** | CLI tooling (Didi) → primary language (TikTok) |
| gRPC / Protobuf | Didi 2022.09 | **~3.5 years** | Consumer/schema co-author (Didi) → service builder (TikTok) |
| Kubernetes | Didi 2022.09 | **~3.5 years** | Environment awareness (Didi) → deployment ownership (TikTok) |
| Terraform / IaC | Didi 2023.03 | **~3 years** | Basic provisioning (Didi) → module authoring (TikTok) |
| HTTP / API Systems | Temu 2021.06 | **~5 years** | Consumer → contract reviewer → deep protocol engineering |

---

## MODULE 3 — Bullet Points (Output-Ready)

### Temu · Recommendation Algorithm Data Analyst · Shanghai · 2021.06 – 2022.02

- Automated weekly recommendation performance reporting by building Python ETL pipelines ingesting 50M+ daily user interaction events from internal data warehouses, reducing analyst reporting cycle from 12 hours/week to 1.5 hours.
- Authored and maintained 30+ SQL metric views standardizing CTR, CVR, recall precision, and coverage rate definitions across 3 algorithm engineering squads, eliminating cross-team KPI discrepancies that had previously caused 2 inconclusive A/B experiment rollbacks.
- Developed Python scripts consuming internal REST APIs to programmatically extract A/B experiment assignment logs, enabling self-serve data access for 6 non-technical product managers and reducing data pull request queue backlog by ~40%.
- Identified a data freshness regression in the item-embedding update pipeline through HTTP API response log analysis; produced a reproducible failure trace that enabled the algorithm team to reduce embedding update latency from 6 hours to 45 minutes.
- Documented all metric views and data lineage in the team's internal data catalog, reducing new analyst onboarding time from 2 weeks to 3 days.

---

### Didi IBG · Food Business · Senior Data Analyst · Beijing / Mexico City · 2022.09 – 2024.05

- Designed and owned a cross-region food order analytics pipeline aggregating real-time delivery metrics from Mexico and China operations, parsing Protobuf-serialized gRPC API responses from 6 internal microservices into a unified SQL reporting schema serving 15+ stakeholders across 2 time zones.
- Authored Go CLI tooling integrated with Didi's internal RPC service registry to automate recurring data extraction workflows, reducing ad-hoc data fulfillment turnaround from 3 business days to under 4 hours across 8 repeating analytical tasks.
- Defined and maintained Protobuf-aligned data schemas for 3 newly launched food vertical metrics in collaboration with backend engineers, establishing backward-compatibility conventions that reduced schema-change-induced pipeline breakage from 4 incidents/month to 1.
- Instrumented reproducible Kubernetes-hosted analysis environments via Helm chart templates from the data platform team, enabling 10 analysts to provision compute environments within 5 minutes versus a prior 2-day manual setup process.
- Redesigned A/B experiment holdout segmentation using deterministic hash-based user assignment in SQL/Python, reducing control group leakage incidents by 28% and cutting average experiment conclusion cycle by 1.5 weeks across 12 live ranking algorithm experiments.
- Produced a Mexico CDN edge node geo-latency benchmarking report surfacing a 340ms P99 regression in the food ETA prediction API; traced to an NGINX upstream timeout misconfiguration, escalated to the infrastructure team, and resolved within 48 hours with a measured 290ms P99 improvement post-fix.

---

### TikTok Safety · Backend Software Engineer Intern · San Jose, CA · 2025.06 – 2025.12

- Engineered a Go-based content safety signal routing microservice processing 120K+ RPS, implementing bidirectional gRPC streaming with Protobuf-defined message schemas and mutual TLS (mTLS) enforcement via Envoy sidecar proxy within TikTok's internal service mesh.
- Authored Kubernetes Deployment manifests, HorizontalPodAutoscaler configurations, and PodDisruptionBudget policies for the routing service across 3 geographic availability zones; service maintained 99.95% uptime SLA through a 6-week staged canary rollout.
- Developed Terraform modules provisioning NGINX-based edge gateway resources on TikTok's internal cloud platform, replacing 400+ lines of manual runbook steps with idempotent IaC declarations and reducing environment provisioning time from 2 days to 35 minutes.
- Implemented a GitOps deployment pipeline using Flux CD to reconcile Helm chart releases from a canonical Git repository to production Kubernetes clusters, eliminating manual `kubectl apply` steps and contributing to a 60% reduction in deployment-related incidents over the internship period.
- Diagnosed a TLS certificate rotation failure in an Envoy proxy configuration by correlating OpenSSL handshake error logs with TCP-layer connection reset metrics; produced a root-cause analysis report adopted as a permanent team runbook, preventing a projected 99.99% availability SLA breach.
- Authored OpenAPI 3.0 specifications for 2 new internal safety signal APIs; integrated Spectral-based linting rules into the CI pipeline for automated contract validation, adopted by 4 downstream consumer teams as the team's contract-first API development standard.

---

## MODULE 4 — Key Projects (Output-Ready)

---

### TEMU · 2021.06 – 2022.02

#### Project 1: Recommendation Algorithm Performance Monitoring Suite

*No automated reporting infrastructure existed; weekly business reviews depended on ad-hoc SQL queries and manual spreadsheet compilation consuming 12+ analyst-hours per cycle with inconsistent metric definitions across teams.*

- Built Python ETL pipeline ingesting 50M+ daily user interaction events via scheduled internal REST API calls, normalizing raw logs into 8 standardized category-level metric tables; reduced weekly reporting cycle from 12 hours to 1.5 hours.
- Authored 30+ SQL metric views standardizing CTR, CVR, recall precision, and coverage rate KPI definitions across 3 algorithm engineering squads; eliminated cross-team metric discrepancies that had produced 2 reverted A/B experiments in the prior quarter.
- Implemented HTTP-based API polling logic to detect data freshness degradation across 4 recommendation model pipeline stages, surfacing a 5.5-hour embedding update lag that was traced, escalated, and resolved within one sprint cycle.
- Documented all metric views and data lineage in the team's internal data catalog, reducing new analyst onboarding ramp time from 2 weeks to 3 days.

---

### DIDI IBG · 2022.09 – 2024.05

#### Project 1: Cross-Region Food Delivery Analytics Unification Pipeline

*Mexico and China food business metrics were siloed in incompatible schemas across separate data warehouses, forcing analysts to manually reconcile figures before each weekly business review; no standardized cross-region metric definitions existed.*

- Designed a unified ingestion layer parsing Protobuf-serialized gRPC API responses from 6 internal microservices across Mexico City and Beijing operations into a consolidated SQL reporting schema; pipeline processed ~3M+ daily Mexico delivery events alongside China counterpart feeds, serving 15+ stakeholders across 2 time zones.
- Authored Go CLI tool integrated with Didi's internal RPC service registry to auto-discover available data service endpoints and pull schema metadata; reduced time to onboard new upstream data sources from 3 business days to under 2 hours.
- Defined Protobuf data schemas for 3 new food vertical metrics in coordination with backend engineers; enforced backward-compatibility review conventions that reduced schema-change-induced pipeline incidents from 4/month to 1/month over the following 6 months.
- Benchmarked CDN edge node response latencies across 8 Mexico PoPs using geo-distributed delivery event samples; surfaced a 340ms P99 regression in the food ETA prediction API attributed to an NGINX upstream timeout misconfiguration, escalation resolved with a 290ms P99 improvement.

#### Project 2: A/B Experiment Data Integrity Framework for Food Ranking Algorithms

*Multiple food ranking algorithm A/B experiments had suffered control group contamination due to inconsistent holdout logic, producing 2 inconclusive rollback decisions in Q4 2022 and eroding confidence in experiment-driven product iteration.*

- Redesigned holdout segmentation using deterministic hash-based user assignment logic in SQL/Python, reducing control group leakage incidents by 28% across 12 subsequent food ranking experiments.
- Built Python-based pre-launch health-check scripts consuming internal REST APIs to validate assignment balance, exposure counts, and metric variance before experiment activation; integrated into a pre-experiment sign-off checklist that shortened average time-to-statistical-significance by 1.5 weeks.
- Standardized experiment compute environments as Kubernetes-hosted Jupyter instances via Helm chart templates from the data platform team; 10 analysts able to provision reproducible environments in under 5 minutes, eliminating library dependency drift as a confounding variable.
- Documented experiment design standards and holdout governance rules adopted as the team's internal wiki baseline for food business A/B methodology.

---

### TIKTOK SAFETY · 2025.06 – 2025.12

#### Project 1: Real-Time Content Safety Signal Routing Service

*Safety signal fan-out from upstream content classifiers was handled by a monolithic Python batch job with 8–12 second end-to-end latency and no availability SLA, creating a structural gap in real-time content moderation coverage.*

- Architected and delivered a Go-based gRPC microservice with bidirectional streaming for safety signal routing, reducing end-to-end signal propagation latency from 8–12 seconds to sub-200ms at 120K+ RPS under production load.
- Defined Protobuf message schemas for 5 safety signal payload types; negotiated schema contracts with 3 upstream classifier teams and 4 downstream consumer services, versioned in Git and validated via CI pipeline.
- Configured Envoy sidecar proxy for mTLS mutual authentication and per-request observability instrumentation using OpenTelemetry trace propagation headers, enabling latency attribution across all service mesh hops in distributed traces.
- Authored Kubernetes Deployment, HPA, and PodDisruptionBudget manifests targeting 3 geographic AZs; service maintained 99.95% uptime SLA through a 6-week canary rollout with automated rollback on error-rate threshold breach.
- Diagnosed a TLS certificate rotation failure by correlating OpenSSL handshake error rate spikes with TCP connection reset metrics in production observability dashboards; root-cause analysis and remediation steps formalized as a permanent team runbook.

#### Project 2: Infrastructure-as-Code Migration for Safety Backend Edge Gateways

*Safety team's NGINX-based edge gateway resources were manually provisioned via 400+ line runbooks with no version control or change audit trail, resulting in 3 environment drift incidents in H1 2025 and multi-day provisioning lead times blocking deployment velocity.*

- Authored Terraform modules for NGINX edge gateway resource lifecycle management on TikTok's internal cloud platform; replaced manual runbook steps with idempotent IaC declarations, cutting new environment provisioning time from 2 days to 35 minutes.
- Implemented Flux CD GitOps pipeline reconciling Helm chart releases from a canonical Git repository to 3 production Kubernetes clusters; eliminated manual `kubectl apply` steps and contributed to a 60% reduction in deployment-related incidents over the 6-month internship.
- Defined Helm chart configurations for the safety routing service covering ConfigMap management, Kubernetes External Secrets integration, and per-environment rolling update strategies parameterized across staging, canary, and production tiers.
- Authored OpenAPI 3.0 specifications for 2 new internal safety signal APIs with Spectral linting rules enforced in CI; adopted by 4 downstream teams as the contract-first API development standard for the safety platform.
