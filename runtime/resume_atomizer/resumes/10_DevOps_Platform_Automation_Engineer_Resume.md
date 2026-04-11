# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **DevOps & Platform Automation Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **CI/CD** pipeline design, **Kubernetes**/**Helm** orchestration, **Terraform**-managed **Infrastructure as Code**, and **DevSecOps** toolchain integration. Production delivery spanning security audit log infrastructure, cross-border data pipeline **automation**, and cloud-native deployment workflows.
* **End-to-End Platform Delivery:** Builds and ships automated infrastructure — from **GitHub Actions** multi-stage security gates and **Docker** containerized deployments to **HashiCorp Vault** secret management, **Istio** service mesh configuration, and **Prometheus**/**OpenTelemetry** observability instrumentation across **AWS** and **Linux** environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator bridging platform, security, and operations teams to deliver measurable gains in engineering velocity and system **reliability**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core DevOps & Infrastructure Contributions:_**

* Owned the team's end-to-end **GitHub Actions** **CI/CD** pipeline (build → SAST scan → multi-stage **Docker** image build/push → **Helm** rollout to staging); cut average deployment cycle from ~45 min to 12 min while maintaining >85% unit test coverage on the **Go** service codebase.
* Designed a reusable **GitHub Actions** composite action embedding a 4-stage **DevSecOps** gate — SAST via Semgrep, secret scanning, **Docker** image vulnerability scan, and test coverage threshold enforcement — adopted by 4 internal platform teams, extending consistent security gate coverage across the organization.
* Replaced hardcoded credential references in 3 legacy pipeline tools with **HashiCorp Vault** dynamic secret injection, reducing secret-exposure surface area by ~80% and satisfying the Security Platform's Zero Trust remediation mandate (**Security**).
* Enforced **TLS** 1.3 mutual authentication on all **gRPC** inter-service channels and implemented **OAuth 2.0** client credentials flow for upstream pipeline source authentication, meeting the internal Zero Trust service-to-service baseline.

**_Project: Security Audit Log Ingestion & Routing Service_**

* Developed a production **Go** microservice ingesting security audit events — authentication failures, privilege escalation attempts, API anomaly flags — from 15+ internal services via a **gRPC** endpoint backed by **Protocol Buffers** v3 schema; reduced mean time to security alert from ~4 min to under 30 sec.
* Deployed to a company-managed **Kubernetes** cluster via versioned **Helm** chart with HPA configured to scale between 2 and 8 replicas; authored **Terraform** modules for node pool provisioning and IAM service-account bindings, achieving fully reproducible cluster-state management and 99.97% service uptime across the 5-month production window.
* Configured **Istio** service mesh to enforce **mTLS** between the ingestion service and all downstream consumers, with canary-weight routing for iterative schema evolution enabling version rollout without upstream breaking changes.
* Instrumented the service with **OpenTelemetry** distributed traces and custom **Prometheus** throughput/latency metrics; co-designed a **Grafana** SLA dashboard adopted by the 3-person on-call rotation for real-time incident triage.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and operationalized an end-to-end **Python**/**Apache Airflow** DAG pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's weekly KPI reporting across 8 city markets; cut report delivery lead time from 3 business days to under 4 hours (**automation**).
* Designed and rolled out a **GitLab CI/CD** workflow enforcing automated linting and pytest unit-test gates on all merge requests to the shared analytics repository; reduced production data-quality incidents from a monthly average of 4 to fewer than 1 within 60 days.
* Containerized the analytics team's shared **Python**/**SQL** toolchain using **Docker** (multi-service Compose stack), eliminating environment-mismatch incidents across a 6-person, 2-timezone team for the full 14-month Mexico engagement.
* Engineered a **Python** schema-normalization adapter layer ingesting raw feeds from 3 third-party Mexican logistics **REST APIs**, delivering a unified data model to downstream **Datadog** dashboards consumed daily by a 50-person regional operations team.
* Partnered with the cloud data infrastructure team to rewrite execution plans for 5 high-frequency **AWS Redshift** dashboards; achieved 61% average query runtime reduction, eliminating dashboard timeout incidents that had blocked daily operational stand-ups.
* Established a canonical **SQL** metric library of 40+ standardized KPI definitions adopted as the org-wide standard; cross-team metric consistency validated at 99.1% across two consecutive quarterly audits.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Automated the recommendation team's daily performance digest using **Python** (pandas, SQLAlchemy) and **Linux** cron scheduling; eliminated ~6 manual analyst-hours per week across a 5-person team (**automation**).
* Authored and tuned complex **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics, directly supplying quantitative inputs for the algorithm team's weekly model retraining cycle.
* Built a lightweight **Python** **REST API** client to pull upstream feature-store payloads and join them against downstream engagement logs; reduced ad-hoc feature attribution analysis turnaround from ~2 days to under 4 hours.
* Consolidated all analysis scripts and **SQL** templates under a shared **GitLab** repository with version-tagged releases, introducing reproducible re-run conventions that eliminated duplicated work across 3 team members (**Git**).

---

## Skills

**Languages:** Go, Python, Bash, SQL, HiveQL
**DevOps & IaC:** Docker, Kubernetes, Helm, Terraform (Infrastructure as Code), Git, GitHub Actions, GitLab CI, Automation
**Security:** HashiCorp Vault, TLS 1.3/mTLS, OAuth 2.0, Istio, DevSecOps, SAST (Semgrep)
**Networking & APIs:** TCP/IP, gRPC (Protocol Buffers), REST APIs
**Observability:** Prometheus, OpenTelemetry, Datadog, Grafana
**Cloud & Platform:** AWS (EKS, Redshift, S3), Linux, Apache Airflow

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