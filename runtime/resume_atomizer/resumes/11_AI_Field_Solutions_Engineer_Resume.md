# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **AI Field & Solutions Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery spanning **Python**/**JavaScript** **SDK** development, **LLM** application deployment, **API** design and integration, **Kubernetes**/**Helm**-based infrastructure orchestration, and **customer-facing** technical engagement in enterprise and **public-sector** environments.
* **End-to-End Solutions Delivery:** Bridges complex AI systems with non-technical stakeholders — from **pre/post-sales** discovery workshops and POC delivery to **technical documentation** (solution architecture guides, integration playbooks), **DevSecOps** pipeline implementation, and **Ansible**-automated environment provisioning across **data pipeline** and compliance platforms.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**. Applies **TS/SCI-eligible** operational discipline to compress customer onboarding time and POC delivery cycles.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Solutions & Developer Experience Contributions:_**

* Developed and maintained **Python** and **JavaScript SDKs** for the security platform's threat intelligence **API** — client libraries, OAuth 2.0/mTLS authentication wrappers, retry/backoff logic, structured logging, and an interactive React **API** playground enabling live request execution and boilerplate code generation; reduced external team first-successful-API-call time from ~2 hours to under 10 minutes.
* Architected a gRPC + REST dual-protocol **API** gateway for the security signal ingestion pipeline, authoring OpenAPI 3.1 specifications with automated contract testing in GitHub Actions CI; served 6 internal consumer teams with zero breaking-change incidents across 3 release cycles, compressing average integration onboarding from 3 weeks to under 5 days.
* Produced **customer-facing** solution architecture documentation and compliance mapping white papers for FedRAMP-aligned and **public-sector** pre-qualification reviews; delivered live technical demos and **pre/post-sales** discovery workshops to 4 prospective enterprise clients, driving 2 successful POC engagements valued at $400K+ combined pipeline.
* Authored **Ansible** roles and playbooks for production environment provisioning: CIS-benchmarked Linux hardening, HashiCorp Vault secrets rotation, TLS certificate lifecycle management, and audit logging configuration; reduced new environment setup from ~2 days to under 45 minutes.

**_Project: LLM-Driven Privacy Compliance Platform & Agent SDK_**

* Designed and implemented a composable Agent **SDK** in Go with a Hooks architecture enabling synchronous tool-call interception for permission enforcement, asynchronous audit logging, and fine-grained per-tool access controls — standardized as the internal agent development foundation for the privacy compliance platform (**LLMs**).
* Built a multi-model **LLM** routing layer (DeepSeek R1, GPT-4, Claude-3, OpenRouter) with unified **API** abstraction and automatic provider failover, maintaining 99.9%+ availability across a 30-day production window despite two upstream provider outages with zero client-visible interruption.
* Engineered a dual-mode annotation **API** — synchronous for single-field response, asynchronous serverless-dispatched for bulk processing — automating privacy label assignment across 12 taxonomy categories; achieved 89% agreement rate with expert reviewers, compressing per-endpoint annotation cycle from 3.5 days to under 4 hours.
* Delivered a Model Context Protocol (MCP) server with one-click IDE installation, exposing compliance tools directly in the developer workflow; authored **customer-facing** **technical documentation** (architecture guides, MCP integration playbooks, **API** reference) and delivered platform walkthroughs to legal, product, and security leadership (**pre/post-sales engineering**).

**_Infrastructure & DevSecOps:_**

* Operated production **Kubernetes** (GKE) multi-namespace cluster infrastructure for **LLM**-powered compliance services via custom **Helm** charts with ArgoCD-driven GitOps deployment; implemented rolling updates, pod disruption budgets, and HPA to sustain sub-200ms P95 latency under 3× peak traffic, achieving 99.95% availability.
* Built a full **DevSecOps** CI/CD pipeline in GitHub Actions integrating SAST (Semgrep), DAST (OWASP ZAP), container image scanning (Trivy), SBOM generation, and policy-as-code enforcement (OPA/Gatekeeper); blocked 23 policy-violating deployments in the first quarter.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and deployed a multi-stage **data pipeline** (Airflow-orchestrated) processing 2M+ daily delivery events across 8 Mexican city markets, integrating real-time Kafka streaming and batch ETL; maintained a canonical SQL (Redshift) metric library covering 40+ KPI definitions.
* Architected and maintained a **Python** **SDK** abstracting 3 third-party logistics vendor **APIs** into a unified internal interface — standardized error handling, retry logic, and rate limiting — reducing partner integration onboarding from 4 weeks to under 10 days per new provider.
* Built a cross-datacenter **Ansible** playbook suite synchronizing configuration between Beijing development and Mexico City production environments; containerized the analytics stack in Docker and integrated Trivy container scanning into GitLab CI/CD, catching 14 high/critical CVEs within 30 days (**DevSecOps**).
* Prototyped an **LLM**-based delivery exception auto-classification module (OpenAI API + prompt engineering) routing free-text driver notes into 12 predefined categories; achieved 82% classification agreement with human reviewers, establishing the business case for production deployment.
* Conducted direct **customer-facing** technical engagement with 3 logistics vendor engineering teams in bilingual (EN/ZH ↔ ES) sessions — led **API** integration troubleshooting, authored **technical documentation** (integration guides, data dictionary), and delivered analytics product demos to 50+ cross-functional personnel.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Authored HiveQL/SparkSQL queries against 1B+ row user-event datasets to extract A/B test cohort metrics, delivering quantitative inputs for the algorithm team's weekly model retraining and monthly stakeholder review decks.
* Built **Python** automation scripts generating the team's daily performance digest, eliminating ~6 manual analyst-hours per week via Linux cron-scheduled batch execution.
* Developed a lightweight **JavaScript** widget layer for the team's internal Metabase dashboard, adding drill-down interactivity for CTR trend visualization and enabling non-technical PMs to self-serve on experiment results.
* Authored onboarding **technical documentation** (runbooks, query cookbook, **API** field glossary) that reduced new analyst ramp-up from ~3 weeks to under 1 week.

---

## Skills

**Languages:** Python, JavaScript, Go, SQL
**APIs & SDKs:** REST, gRPC, OpenAPI 3.1, SDK Development, API Gateway Design, MCP
**AI/ML:** LLM Deployment, RAG Pipelines, Prompt Engineering, Agent SDK Design, Multi-Model Orchestration
**Infrastructure:** Kubernetes, Helm, Ansible, Docker, AWS, GCP, Terraform, ArgoCD
**DevSecOps:** SAST/DAST, Trivy, OPA/Gatekeeper, SBOM, GitHub Actions, GitLab CI
**Data:** Kafka, Airflow, MongoDB, Redis, Redshift, HiveQL, SparkSQL
**Customer-Facing:** Pre/Post-Sales Engineering, Technical Documentation, POC Delivery, Solution Architecture, Public Sector

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