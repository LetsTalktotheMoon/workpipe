# Resume Prop Document — DevOps / Platform Automation Engineer

---

## MODULE 1 — Professional Summary

Data systems practitioner with 3+ years of production analytics engineering experience at hyperscale consumer technology platforms (Temu, Didi IBG), pivoting into platform automation engineering through a backend software engineering internship on TikTok's Security Platform team and concurrent graduate study at Georgia Tech (OMSCS) and UIUC (MSIM). Brings a structurally uncommon synthesis: behavioral systems modeling from a dual undergraduate background in cognitive science and international finance, end-to-end data pipeline automation at scale (1B+ event datasets, multi-region cross-border deployments), and production-grade backend service development in Go/Python for security-critical infrastructure. Targeting DevOps and Platform Automation engineering roles where demonstrated proficiency in CI/CD pipeline design, Kubernetes-native service deployment, infrastructure-as-code (Terraform), and DevSecOps toolchain integration translates directly into measurable improvements in engineering velocity, system reliability, and organizational security posture.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | ✓ Scripting: cron automation, pandas, SQLAlchemy, REST client | ✓✓ Pipeline automation: Airflow DAGs, schema adapters, batch jobs | ✓✓✓ Tooling & internal SDK scripts | **4+ years** |
| **SQL** | ✓✓ Complex HiveQL/SparkSQL on 1B+ row datasets, A/B cohort metrics | ✓✓✓ Canonical metric library (40+ defs), Redshift plan optimization | — | **3+ years** |
| **Linux** | ✓ Cron scheduling, shell environment management | ✓✓ Scripted batch automation, cross-OS environment tooling | ✓✓✓ System-level service operations, init scripting | **4+ years** |
| **Git** | ✓ GitLab personal versioning (scripts, SQL templates) | ✓✓ Team branch workflows, merge request conventions | ✓✓✓ CI/CD pipeline ownership, repo governance | **4+ years** |
| **REST API** | ✓ API client for upstream feature-store ingestion | ✓✓ 3rd-party logistics API adapter layer (3 providers) | ✓✓✓ Service-level API design, gRPC complement | **3+ years** |
| **Bash** | — | ✓ Pipeline orchestration and scheduling scripts | ✓✓ Automation, CI helper scripts | **2+ years** |
| **Docker** | — | ✓ Local analytics toolchain containerization | ✓✓ Multi-stage production image builds | **2+ years** |
| **CI/CD (GitHub Actions / GitLab CI)** | — | ✓ Lint + unit test gates on shared analytics repo | ✓✓✓ Full build → SAST scan → push → deploy pipeline | **2+ years** |
| **AWS** | — | ✓ Redshift query tuning (analyst-level warehouse access) | ✓✓ EKS node pool provisioning via Terraform | **2+ years** |
| **Datadog** | — | ✓✓ Operational KPI dashboards for regional ops team | — | **~1.5 years** |
| **Go** | — | — | ✓✓✓ Primary language; production microservice development | **6 months** |
| **Kubernetes** | — | — | ✓✓✓ Deployment manifests, HPA, Helm chart rollout | **6 months** |
| **Terraform** | — | — | ✓✓ IaC modules for compute, node pool, IAM provisioning | **6 months** |
| **gRPC** | — | — | ✓✓✓ Inter-service intake endpoints, Protocol Buffers v3 | **6 months** |
| **TLS/SSL** | — | — | ✓✓✓ mTLS via Istio, TLS 1.3 on gRPC channels | **6 months** |
| **OAuth 2.0** | — | — | ✓✓✓ Client credentials flow for pipeline source auth | **6 months** |
| **Vault (HashiCorp)** | — | — | ✓✓✓ Dynamic secret injection, engine configuration | **6 months** |
| **Istio** | — | — | ✓✓ Service mesh mTLS enforcement, canary traffic management | **6 months** |
| **Prometheus / OpenTelemetry** | — | — | ✓✓✓ Scrape endpoints, distributed trace instrumentation | **6 months** |

**ATS Depth Note:** Python, SQL, Linux, Git, and REST API establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters at the foundational level. Go, Kubernetes, Terraform, Vault, Istio, and the full DevSecOps toolchain are anchored exclusively to TikTok's production security infrastructure and substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Automated the recommendation team's daily performance digest using **Python** (pandas, SQLAlchemy) and Linux **cron** scheduling, eliminating approximately 6 manual analyst-hours per week across a 5-person team and enabling same-day visibility into click-through and conversion rate shifts after each model deployment.
- Authored and tuned complex **HiveQL / SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics (CTR, GMV lift, add-to-cart rate, novelty score), directly supplying the quantitative inputs for the recommendation algorithm team's weekly model retraining decisions.
- Built a lightweight **Python REST API** client to pull upstream feature-store payloads and join them against downstream engagement logs, reducing ad-hoc feature attribution analysis turnaround from approximately 2 days to under 4 hours.
- Standardized all analysis scripts and SQL templates under a shared **GitLab** repository with version-tagged releases, introducing reproducible re-run conventions that eliminated duplicated work across 3 team members.
- Documented 12 recurring analytical SOPs covering high-frequency report types (daily active recommendation slot performance, item-level exposure fairness audits), cutting new-analyst onboarding ramp-up from approximately 2 weeks to 4 days.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Designed and operationalized an end-to-end **Python / Apache Airflow** DAG pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's weekly KPI reporting across 8 active city markets, reducing report delivery lead time from 3 business days to under 4 hours.
- Curated a canonical **SQL** metric library of 40+ standardized definitions (DAU, GMV, order completion rate, delivery SLA, refund rate) adopted as the org-wide standard across the Mexico analytics function; cross-team metric consistency measured at 99.1% over two consecutive quarterly audits.
- Containerized the analytics team's shared Python/SQL toolchain using **Docker** (multi-service Compose stack), eliminating environment-mismatch incidents across a 6-person, 2-time-zone team (Beijing UTC+8, Mexico City UTC−6) for the entire 14-month Mexico engagement window.
- Implemented a **GitLab CI/CD** workflow on the team's shared analytics repository enforcing automated linting (flake8, sqlfluff) and pytest unit test pass gates on all merge requests; reduced production data-quality incidents from a monthly average of 4 to fewer than 1 within 60 days of rollout.
- Engineered a **Python** schema-normalization adapter layer ingesting raw feeds from 3 third-party Mexican logistics **REST APIs**, resolving field-level schema divergence across providers and supplying a unified data model to downstream **Datadog** dashboards consumed daily by a 50-person regional operations team.
- Partnered with the cloud data infrastructure team to analyze and rewrite execution plans for 5 high-frequency **AWS Redshift** dashboards, achieving an average query runtime reduction of 61% and eliminating dashboard timeout incidents that had previously blocked daily operational stand-ups.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Developed a production **Go** microservice to ingest, normalize, and route security audit log events (authentication failures, permission escalation signals, API anomaly flags) from 15+ internal platform services into the centralized detection pipeline, reducing mean time to security alert from approximately 4 minutes to under 30 seconds.
- Deployed the service to a company-managed **Kubernetes** cluster via Helm chart with Horizontal Pod Autoscaler configuration; authored **Terraform** modules for node pool provisioning and IAM service account bindings, enabling fully reproducible cluster-state management and sustaining 99.97% service uptime over the 5-month production window.
- Integrated **HashiCorp Vault** dynamic secret injection to replace hardcoded credential references in 3 legacy internal tools consumed by the audit pipeline, reducing the secret-exposure surface area by an estimated 80% as measured by internal security scanning tooling.
- Enforced **TLS 1.3** mutual authentication on all **gRPC** inter-service channels and implemented **OAuth 2.0** client credentials flow for upstream pipeline source authentication, satisfying TikTok's internal Zero Trust service-to-service security baseline requirements.
- Authored an end-to-end **GitHub Actions** CI/CD pipeline (build → SAST scan → multi-stage **Docker** image build/push to internal registry → Helm rollout to staging), reducing average deployment cycle time from approximately 45 minutes to 12 minutes while maintaining >85% unit test coverage on the Go service codebase.
- Instrumented the service with **OpenTelemetry** distributed traces and custom throughput/latency metrics; configured **Prometheus** scrape endpoints feeding a Grafana SLA dashboard adopted by the 3-member on-call security engineering rotation for real-time incident triage.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Recommendation A/B Test Metrics Automation System**

*The recommendation algorithm team ran 6–8 concurrent A/B experiments per week; metric summarization was performed manually in Excel by rotating analysts, producing a 24–48-hour reporting lag that deferred model iteration decisions and created recurring data-consistency conflicts between team members working from divergent query drafts.*

- Audited 9 recurring metric templates shared across all A/B experiment types and parameterized them into a reusable **Python** (pandas + SQLAlchemy) report generation module, reducing per-experiment metric compilation from approximately 4 hours to under 20 minutes per analyst.
- Replaced ad-hoc **SparkSQL / HiveQL** query authoring with a pre-validated query library of 11 canonical templates covering core recommendation KPIs (CTR, GMV lift, add-to-cart rate, novelty score), enforcing consistent metric definitions across simultaneous experiments and eliminating analyst-level calculation discrepancies.
- Scheduled the module as a Linux **cron** job triggered nightly following feature-store refresh cycles; the job consumed upstream metric payloads via the feature-store **REST API** and wrote structured HTML summary reports to a shared internal directory accessible by the full recommendation team.
- Versioned all scripts, SQL templates, and report configuration files in a dedicated **GitLab** project, enabling any team member to reproduce any historical experiment summary with a single parameterized command and providing a traceable audit trail for model retraining decisions.
- Delivered a net reduction of approximately 6 analyst-hours per week and compressed the A/B experiment metric review cycle from 3–5 days to same-day availability, directly accelerating the recommendation model iteration cadence.

---

### DIDI IBG · Key Project

**Mexico Food Market Cross-Region KPI Normalization and Reporting Pipeline**

*The Mexico Food analytics function operated without a unified data layer: 7 independently maintained analyst Excel models tracked overlapping KPI sets using divergent metric definitions, causing cross-team reporting conflicts and systematically missing weekly SLAs by 2+ business days during high-growth market expansion sprints.*

- Audited all 7 legacy models and consolidated 40+ overlapping metric definitions into a canonical **SQL** library governing DAU, GMV, order completion rate, delivery SLA compliance, and refund rate; the library was formally adopted as the org-wide metric standard across the Mexico analytics team within one quarter of release.
- Built a multi-DAG **Python / Apache Airflow** pipeline to replace all manual Excel workflows: upstream DAG tasks pulled raw transactional data from the **AWS Redshift** data warehouse; mid-stream transformation tasks applied the canonical SQL metric logic; downstream tasks rendered Jinja-templated reports and pushed outputs to the team's operational dashboard layer.
- Developed a **Python** schema-normalization adapter layer to resolve field-level divergence across 3 third-party Mexican logistics **REST APIs** (field mapping, type coercion, null-handling conventions), enabling reliable automated upstream ingestion and eliminating a previously recurring 2–4-hour weekly manual data reconciliation step.
- Containerized the full pipeline execution environment in **Docker** (Python 3.11, Airflow, SQLAlchemy, custom adapter package) and published the image to the team's internal container registry, ensuring bit-for-bit execution consistency across analyst workstations in Beijing and Mexico City and eliminating a class of environment-dependent data discrepancies entirely over the 14-month engagement period.
- Integrated a **GitLab CI/CD** gate on the pipeline repository enforcing flake8 linting and pytest unit tests on all SQL adapter logic before merge; reduced production data-quality incidents from a monthly average of 4 to under 1 within 60 days of deployment.
- Reduced KPI report delivery from 3 business days to under 4 hours; the pipeline subsequently served as the primary analytical foundation for go/no-go decisions on market expansion into 3 additional Mexican cities in Q1 2024.

---

### TIKTOK SECURITY · Key Project 1

**AuditStream — Security Audit Log Ingestion and Routing Service**

*Fifteen-plus internal platform services emitted security-relevant events — authentication failures, privilege escalation attempts, API anomaly signals — to isolated, schema-incompatible sinks; the resulting fragmentation created detection blind spots in the centralized security pipeline and extended mean incident triage time to approximately 4 minutes from first signal emission to alert generation.*

- Designed and implemented **AuditStream**, a **Go** microservice exposing a **gRPC** intake endpoint with Protocol Buffers v3 schema to ingest raw security events from 15+ upstream services, normalize them against a unified internal event taxonomy, and route them to the centralized detection pipeline; service sustained peak throughput of approximately 15,000 events per minute in production.
- Enforced **TLS 1.3** mutual authentication on all **gRPC** intake channels and implemented **OAuth 2.0** client credentials flow for upstream service identity verification, directly satisfying TikTok's internal Zero Trust service-to-service security baseline requirements.
- Deployed to a company-managed **Kubernetes** cluster via a versioned Helm chart with Horizontal Pod Autoscaler configuration; authored **Terraform** modules for node pool provisioning and IAM role bindings, enabling fully reproducible environment management and supporting one-command teardown and redeploy cycles for disaster recovery validation drills.
- Configured **Istio** service mesh to enforce mTLS between AuditStream and downstream consumers, with traffic management rules providing canary-deployment support for iterative Protobuf schema evolution without service interruption or upstream breaking changes.
- Instrumented with **OpenTelemetry** distributed tracing and custom event throughput/latency metrics; configured **Prometheus** scrape endpoints feeding a Grafana SLA dashboard adopted by the 3-member on-call security engineering rotation, reducing mean time to alert from approximately 4 minutes to under 30 seconds.
- Integrated **HashiCorp Vault** dynamic secret injection for all runtime credentials (gRPC mTLS certificates, downstream sink API keys), replacing hardcoded credential references in 3 legacy pipeline tools and reducing secret-exposure surface area by approximately 80% as measured by internal automated security scanning.

---

### TIKTOK SECURITY · Key Project 2

**CI/CD Security Gate Automation for Internal Platform Services**

*Internal platform service teams lacked automated security validation in their deployment pipelines; the security engineering team conducted post-deployment manual code and configuration reviews, creating a median 5–7-day remediation lag for medium-severity findings and allowing credential-exposure incidents to reach production undetected prior to quarterly review cycles.*

- Designed and authored a reusable **GitHub Actions** composite action embedding a 4-stage security gate — SAST via Semgrep rule packs, secret scanning via internal policy engine, multi-stage **Docker** image vulnerability scan, and mandatory test coverage threshold enforcement — consumable by downstream service teams with a single `uses:` reference in their existing workflow files.
- Reduced average full deployment cycle time from approximately 45 minutes to 12 minutes by parallelizing build, scan, and test stages and implementing **Docker** layer caching for multi-stage image builds, achieving a 3.75× speedup with no reduction in gate coverage scope.
- Authored **Python** and **Bash** helper scripts for automated Semgrep rule-set customization by service security classification (Tier-1 vs. Tier-2 sensitivity), enabling the security team to manage all scan policy configurations centrally in a single repository rather than maintaining per-service override files.
- Maintained >85% unit test coverage on the composite action's internal orchestration logic, validated via self-referential CI runs on each push to the action repository; produced an integration runbook adopted by 4 internal platform teams within the internship window.
- Embedded **HashiCorp Vault** token validation as a required gate step, ensuring no service image could advance past staging to production while carrying static credentials in environment variables; directly addressed the primary attack vector identified in 2 prior internal credential-exposure post-mortems.
