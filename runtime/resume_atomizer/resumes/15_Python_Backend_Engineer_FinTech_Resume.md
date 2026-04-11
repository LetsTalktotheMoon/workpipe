# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Python Backend Engineer (FinTech):** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery in **Python backend development**, **RESTful API** architecture, **identity** and **authentication** services, **payment** settlement systems, and **transaction processing** pipelines.
* **End-to-End FinTech Delivery:** Designs and ships **security**-critical **backend** systems — from **OAuth 2.0**/**JWT** token lifecycle management and **RBAC**/**ABAC** **authorization** to cross-border **payment** reconciliation, **PCI-DSS** compliance automation, and **API development** with **Agile** **SDLC** delivery discipline.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Graduate foundation in quantitative finance directly applicable to **fintech** domain reasoning. Effective cross-functional collaborator bridging engineering, operations, and compliance teams.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Backend & Identity Engineering Contributions:_**

* Developed and maintained production **Python** (Django/FastAPI) **backend** microservices on the Security Platform, implementing gRPC inter-service communication, async task queues (Celery/Redis), and distributed task scheduling for **security** event processing pipelines handling 500K+ daily **authentication** and **authorization** events.
* Owned the full **SDLC** lifecycle for 3 **backend** services: authored design documents, led code review sessions, managed GitHub Actions CI/CD pipelines (build, lint, unit/integration test, canary deployment), maintained on-call rotation; achieved 99.95% service availability across the 6-month tenure.
* Enforced OWASP Top 10 compliance across all owned services via automated dependency vulnerability scanning, static analysis, and penetration test remediation tracking; contributed to **security** incident response tooling reducing mean time to containment for credential-related incidents by 35%.

**_Project: Centralized Identity & Authorization Service_**

* Developed and owned the **Python** (FastAPI/Django) centralized **identity services** module — user provisioning, credential rotation, MFA enforcement, and SSO federation (SAML 2.0/OIDC) — processing 200K daily identity verification requests at P99 latency under 120ms; deployed via blue-green release on AWS ECS with zero downtime (**authentication**).
* Built a **JWT**/**OAuth 2.0** token lifecycle management service with **RBAC**/**ABAC** policy engine integration, enforcing fine-grained **authorization** decisions across 12 downstream platform services; implemented token revocation, refresh rotation, and session management with Redis-backed distributed session store.
* Designed PostgreSQL schema for identity and session data stores with Alembic migration management, audit logging, and soft-delete patterns for credential lifecycle traceability; aligned data retention policies to SOC 2 Type II requirements.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

**_Payment & Transaction Systems:_**

* Engineered a cross-border **payment** settlement reconciliation system in **Python** integrating 3 regional **payment** processors (Conekta, MercadoPago, Didi Pay), automating multi-currency FX rate application, double-entry **transaction** ledger validation, and chargeback classification; reduced monthly settlement resolution from 5 analyst-days to under 8 hours at 99.7% automated accuracy (**transaction processing**).
* Built a real-time delivery **transaction** lifecycle management system consuming Kafka event streams (order creation, driver assignment, pickup, **payment** capture, settlement), tracking 50,000+ daily delivery **transactions** and surfacing anomaly alerts (stuck orders, duplicate charges, settlement mismatches) to the operations dashboard.
* Automated **PCI-DSS** scoping assistance scripts and TLS certificate rotation for **payment**-adjacent services using HashiCorp Vault for secrets management, ensuring compliance with regional **security** and data residency requirements across China and Mexico jurisdictions (**fintech**).

**_Backend API & Operations:_**

* Designed and deployed a FastAPI-based internal operations **API**, providing versioned **RESTful** endpoints with OpenAPI specification, pagination, rate limiting, and **OAuth 2.0** integration for third-party logistics provider data exchange — serving as the central data contract layer for 5 downstream services across 8 Mexican city markets (**API development**).
* Architected an **RBAC**-based **authorization** layer for the internal analytics tooling suite, enforcing role-scoped data access controls across Beijing and Mexico City teams; integrated driver identity verification workflows (KYC document upload) into the delivery onboarding pipeline, processing ~2,000 monthly verifications.
* Containerized the full environment in Docker, managed deployment via GitLab CI/CD with automated testing gates, and established **Scrum** ceremonies across a cross-functional Beijing/Mexico City team of 8 using JIRA-based backlog management (**Agile**).

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Developed **Python** (pandas, NumPy, SQLAlchemy) automation scripts to extract, transform, and load daily e-commerce **transaction** event data (~1.2B rows/month), eliminating ~6 manual analyst-hours per week.
* Built a lightweight Flask-based internal **API** serving pre-computed analytics dashboards, implementing API key **authentication** and input sanitization to gate access to sensitive revenue and conversion data; reduced ad-hoc data request tickets by ~40% (**API development**).
* Authored and tuned HiveQL/SparkSQL queries against 1B+ row event datasets to compute **transaction**-level metrics (GMV, conversion rate, refund rate, **payment** failure rate) segmented by A/B test cohort.
* Implemented **Python** scripts automating daily e-commerce **transaction** analytics — **payment** failure rate tracking, refund pattern analysis, and category-level GMV aggregation — providing standardized reporting to finance and BI teams.

---

## Skills

**Languages:** Python, SQL, HiveQL, SparkSQL
**Backend:** Django, FastAPI, Flask, Celery, gRPC, RESTful APIs, OpenAPI
**FinTech:** Payment Processing, Transaction Orchestration, Settlement Reconciliation, PCI-DSS
**Identity & Security:** OAuth 2.0, JWT, SAML 2.0, OIDC, MFA, RBAC/ABAC, OWASP, HashiCorp Vault
**Infrastructure:** AWS (ECS, RDS, S3), Docker, Kafka, RabbitMQ, Redis, PostgreSQL
**DevOps & SDLC:** GitHub Actions, GitLab CI, Agile/Scrum, JIRA, Git

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