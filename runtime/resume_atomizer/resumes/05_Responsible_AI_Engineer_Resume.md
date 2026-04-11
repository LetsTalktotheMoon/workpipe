# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Security & Responsible AI Infrastructure Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **content provenance** pipeline design, **compliance**-native API development, and **Trust and Safety** signal engineering. Production delivery spanning **C++** low-latency services, **C2PA** standard implementation, and AI-generated content detection at global scale.
* **End-to-End Responsible AI Delivery:** Designs and ships accountable, auditable data systems — from **content watermarking** verification and provenance metadata services with defined **SLOs** to cross-jurisdiction **compliance** automation (**EU AI Act**, LFPDPPP, PIPL) and **reliability analysis** across production environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Cross-disciplinary foundation in philosophy and behavioral science applied to **Responsible AI** governance reasoning. Effective collaborator bridging security, legal, product, and infrastructure teams.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Security Infrastructure Contributions_**

* Implemented 2 **C++** microservices within TikTok's content integrity pipeline for security signal aggregation, sustaining 80K+ events/sec throughput and meeting the team's 99.9% SLA threshold under production load.
* Instrumented **SLO** dashboards for 3 Security signal APIs — defining P99 latency, error rate, and availability targets — and authored error budget policy runbooks (**reliability analysis**); services maintained 99.95% availability over the 60-day post-rollout measurement window.
* Benchmarked the platform's AI-generated content disclosure practices against **EU AI Act** Article 50 requirements and **C2PA** industry standards, producing a 12-point engineering remediation roadmap adopted by the Security compliance team.

**_Project: Content Provenance Metadata Service_**

* Designed and documented **gRPC** + **REST API** contracts for a **content provenance** metadata service consumed by 3 downstream Security classifier teams; implemented the **C++** service layer handling request deserialization, in-memory cache routing, and fallback queries, sustaining 40K+ queries/sec with P99 read latency of 12ms.
* Developed a **C2PA** 1.x manifest parsing module in **C++** extracting AI-generation assertion flags, provenance claims, and signing certificate chains from inbound media assets at ingest; benchmarked at <3ms per asset at P95 — enabling downstream **AI-generated content detection** and **content watermarking** verification at scale.
* Prototyped a **TypeScript**-based **Content Registry** tracking asset transformations (re-upload, trimming, filter application, cross-account repost) as structured provenance-chain events, with a **REST API** supporting audit log queries by asset ID or transformation type; prototype entered the platform's internal RFC design review.
* Defined and instrumented a three-**SLO** observability framework for the provenance service: P99 read latency ≤15ms, error rate <0.01%, and 99.95% rolling availability; authored on-call alerting runbooks and error budget burn rate policies.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

**_Project: Cross-Border Compliance & Data Governance_**

* Built a **Python**-based cross-border PII lineage crawler reconstructing end-to-end **data provenance** graphs for 40+ PII-containing tables, mapping each field's transit path against **LFPDPPP** (Mexico) and **PIPL** (China) **compliance** requirements and generating structured evidence packages.
* Designed and shipped a **TypeScript**-based **compliance** analytics portal consolidating 14 heterogeneous data sources via **REST API**, reducing cross-functional reporting latency from 3 days to 4 hours for a 40-person Operations, Legal, and Product stakeholder group.
* Authored dual-jurisdiction data **compliance** runbooks covering cross-border transfer legal bases, field-level retention schedules, and breach-notification SLAs under **LFPDPPP** and **PIPL**; framework extended to Brazil and Colombia operations within 12 months.

**_Project: Trust & Safety Analytics_**

* Led end-to-end quantitative modeling for DiDi Food's 4-city Mexico expansion — demand elasticity, merchant supply-demand equilibrium, driver incentive ROI — directly informing a $2.3M quarterly incentive reallocation decision.
* Engineered 12 food-safety **anomaly** features — spoilage complaint velocity, geographic outbreak clustering coefficient, merchant rating degradation slope — for the platform's **Trust & Safety** risk engine, achieving a 23% lift in fraud-flagging precision.
* Architected data-quality **SLOs** for 6 mission-critical business metrics, establishing alerting thresholds that reduced mean time to detect data incidents from 22 hours to under 4 hours (**reliability analysis**).

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Built a **Python**/pandas preprocessing pipeline validating 50M+ daily product interaction events against feature schema contracts, reducing upstream feature data error rate from 11% to 3%.
* Developed a lightweight **Python** anomaly detection script flagging CTR deviation spikes in recommendation feature feeds, enabling engineers to surface upstream pipeline failures ~36 hours earlier than the prior manual review cadence.
* Maintained a unified feature data dictionary documenting schemas, ownership, and freshness expectations for 25+ recommendation model features, adopted as canonical reference by 8+ downstream engineers.

---

## Skills

**Languages:** C++, Python, TypeScript, SQL
**Responsible AI & Compliance:** C2PA, Content Watermarking, AI-Generated Content Detection, EU AI Act, LFPDPPP, PIPL, Data Provenance, Content Registry, Responsible AI
**APIs & Infrastructure:** gRPC, REST APIs, Protobuf, SLO Design, Reliability Analysis, Observability
**Trust & Safety:** Anomaly Detection, Fraud Signal Engineering, Compliance Automation
**Data:** pandas, ETL Pipeline Design, MongoDB, MySQL

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