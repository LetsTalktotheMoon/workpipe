## MODULE 1: Professional Summary

Data and security engineer with 3+ years of cross-industry experience designing ML-driven anomaly detection, fraud intelligence, and backend security systems at hyperscale—across e-commerce recommendation infrastructure (Temu), international risk analytics (DiDi Food, Latin America), and distributed threat detection pipeline development (TikTok Security). Dual graduate enrollment in Information Management (UIUC MSIM) and Computer Science (Georgia Tech OMSCS) formalizes practitioner expertise in distributed systems, algorithm design, and applied machine learning, bridging a deep background in behavioral analytics with the systems-level rigor required for large-scale security architecture. Brings a structurally adversarial analytical lens—developed through years of modeling and operationally countering bad-actor behavioral patterns across 50M+ user populations in multi-market, high-throughput environments—directly applicable to cloud security threat modeling, anomaly detection pipeline design, and Secure-by-Default infrastructure engineering.

---

## MODULE 2: Tech Stack Snowball Distribution Strategy

### Unifying Thread
The candidate's connective tissue across all three roles is **adversarial pattern recognition in large-scale behavioral data**—first applied to data quality in recommendation systems (Temu), then to fraud and regulatory risk at international scale (DiDi), and finally formalized as security threat detection engineering (TikTok). This reframing is ATS-defensible because the core technical artifact—*a system that identifies anomalous signals in high-volume data streams and triggers a response*—is structurally identical whether the domain is e-commerce, fintech, or security.

### Snowball Accumulation Table

| Technology | Temu (2021–2022) | DiDi IBG (2022–2024) | TikTok Security (2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | Scripting, ETL automation, Airflow DAGs | ML pipelines, NLP/BERT fine-tuning, compliance automation | Test automation, CI/CD tooling | **3+ years; mastery** |
| **SQL / Hive** | Complex ad-hoc queries, A/B metric tracking | Advanced analytics, compliance reporting, data mart design | Reference only (upstream data context) | **3+ years; mastery** |
| **Big Data (Spark/Hive)** | Hive only, query-level | Spark distributed pipeline, cross-market data marts | Referenced in system design; internal equivalents | **2+ years; proficient** |
| **Anomaly Detection** | Z-score threshold rules on feature columns | Isolation Forest + ensemble models (fraud) | Real-time behavioral scoring, unsupervised clustering | **3+ years; escalating depth** |
| **Machine Learning** | Implicit in A/B test metric design | scikit-learn fraud models, BERT NLP classifier | ML feature vectors for threat behavioral analysis | **2+ years; applied proficiency** |
| **NLP** | — | BERT fine-tuning, review classification (200K labeled) | Mentioned only in behavioral fingerprint context | **1 year; functional** |
| **Automation / Tooling** | Airflow-scheduled ETL scripts | Compliance reporting templating, pipeline orchestration | CI/CD scanner integration, runbook automation | **3+ years; applied throughout** |
| **Distributed Systems** | Awareness (Hive at scale) | Spark-based distributed batch processing | Kafka event stream consumption, gRPC microservice design | **Escalating from awareness → design** |
| **Go** | — | — | Core microservice language, production components | **6 months; active contributor** |
| **C++** | — | — | Targeted refactoring of alerting module | **6 months; constrained contributor** |
| **Cloud Security** | — | — | Core domain; DLP, threat detection, Secure-by-Default | **6 months; specialist depth** |
| **Threat Detection** | — | Fraud signal detection (structural analog) | Formalized: MITRE ATT\&CK, SOC pipeline, behavioral scoring | **Escalating from analog → formalized** |
| **Incident Response** | — | — | Runbook automation, MTTE reduction, P0 escalation workflows | **6 months; operational** |
| **Vulnerability Management** | — | — | CVE scanning in CI/CD, red-team findings intake | **6 months; functional** |
| **DLP** | — | — | Enforcement middleware design, policy schema, UAT validation | **6 months; core project** |
| **Security Primitives / Frameworks** | — | — | Pattern matching, entropy analysis, token classification in DLP layer | **6 months; design-level** |
| **NLP** | — | BERT (fraud domain) | Behavioral fingerprinting signals | **1 year; applied** |
| **Large-Scale Systems Design** | — | Spark pipeline architecture (50K vendors) | 2B+ events/day, p99 < 200ms SLA, scalability validation | **Escalating from pipeline → microservice** |

### Hard Cumulative Thresholds (ATS Defense)
- **Python**: Temu (2021.6) → present = **4+ years**
- **SQL**: Temu (2021.6) → DiDi (2024.5) = **nearly 3 years active use**
- **Anomaly Detection (methodological)**: Temu (2021.6) → TikTok (2025.12) = **4+ years, three distinct implementations**
- **Machine Learning (applied)**: DiDi (2022.9) → TikTok (2025.12) = **3+ years**
- **Go / C++**: TikTok internship only—do not claim years of experience; frame as *active production contributor*

---

## MODULE 3: Resume Bullet Points

---

### Temu · Recommendation Algorithm Data Analyst · Shanghai · Jun 2021 – Feb 2022

- Queried 100M+ daily user clickstream records via Hive SQL to surface behavioral ranking signal patterns for the recommendation algorithm team, directly informing weekly feature prioritization decisions
- Automated daily ETL reporting pipeline using Python and Apache Airflow, reducing per-analyst manual data preparation time from ~4 hours to 35 minutes and eliminating ad-hoc query duplication across a 4-person data team
- Designed and tracked statistical significance metrics for 12 concurrent A/B experiments on recommendation ranking modules, delivering structured weekly reports to algorithm PMs and engineering leads
- Implemented SQL-based anomaly flag logic to detect statistical drift and null-rate degradation across 40+ recommendation feature columns in the Hive feature store, identifying 4 confirmed silent data poisoning incidents before they propagated to live model serving
- Documented feature store schemas and upstream data lineage in collaboration with the recommendation engineering team, producing the department's first standardized data dictionary and reducing new-analyst onboarding query time by an estimated 60%

---

### DiDi IBG · Food Business · Senior Data Analyst · Beijing / Mexico City · Sep 2022 – May 2024

- Led end-to-end fraud and risk analytics for DiDi Food's Latin America market, processing 5M+ daily transaction events in Python to detect merchant fraud, promotional coupon abuse, and account takeover patterns across 50K+ active vendor accounts
- Developed NLP-based fake-review classification model using fine-tuned BERT on 200K labeled samples, achieving 91% precision at production scale across 300K+ monthly user reviews and operationalizing results as a secondary risk signal in the merchant scoring pipeline
- Designed distributed batch-processing pipeline on Apache Spark to aggregate cross-market behavioral signals from heterogeneous data sources, reducing daily risk score refresh latency from 6 hours to 47 minutes and enabling same-day fraud intervention workflows
- Automated monthly regulatory compliance reporting for Mexican financial authorities (CNBV) using a parameterized Python + SQL templating framework, reducing per-cycle report generation from 12+ analyst-hours to 45 minutes and eliminating 3 prior-quarter resubmission incidents caused by manual transcription errors
- Partnered cross-functionally with Mexico City product, engineering, and legal teams to establish Hive/Spark data marts as the single source of truth for 3 business units, resolving persistent metric discrepancies that had blocked two strategic quarterly reviews
- Mentored 2 junior analysts through bi-weekly code reviews and standardized team Python conventions, reducing new-hire ramp-up time from ~3 weeks to 10 days; recognized by department lead for cross-border collaboration effectiveness across a 6-timezone working environment

---

### TikTok · Trust & Safety – Security Infrastructure · Backend Software Engineering Intern · San Jose, CA · Jun 2025 – Dec 2025

- Developed Go-based microservice components within TikTok's internal threat detection platform, consuming Kafka real-time event streams to compute per-entity behavioral anomaly scores across 2B+ daily events and producing risk-tiered signals for downstream SOC alert triage
- Refactored C++ alerting module to eliminate redundant rule evaluation passes, reducing false positive alert volume by 31% against the prior baseline in A/B shadow comparison and measurably improving SOC analyst throughput on high-fidelity signal triage
- Implemented DLP (Data Loss Prevention) enforcement middleware integrated into the content inspection API's request/response lifecycle, applying security primitives—pattern matching, entropy scoring, and token classification—to outbound payloads and reducing policy-violating data exposure events by 23% in controlled UAT against synthetic canary data
- Built automated vulnerability scanner integration (Python + shell scripting) into the team's CI/CD pipeline, detecting 18 critical dependency CVEs across 6 sprint cycles prior to deployment and contributing to team's Secure-by-Default build posture
- Supported offensive security findings intake by mapping red-team identified attack patterns to MITRE ATT\&CK TTPs, enriching incident response runbooks and reducing mean time to escalation (MTTE) for P0 security events by 40% through standardized detection-to-ticketing automation
- Collaborated with the infrastructure team on distributed storage evaluation for anomaly scoring state persistence, benchmarking Spanner-compatible schema patterns against internal ByteDance KV store options under Agile sprint constraints; findings documented in architecture decision record (ADR) for post-internship handoff

---

## MODULE 4: Key Projects

---

### TEMU · Recommendation Algorithm Data Analyst

---

**Project: Recommendation Feature Data Quality Monitoring System**

*Baseline: The 4-person data team spent 3+ hours daily manually auditing 40+ recommendation feature columns for data quality issues, with no automated alerting—creating 24-hour detection windows during which silent data degradation could corrupt live ranking model inputs without triggering any operational response.*

- Designed Python-based statistical monitoring framework computing z-score drift thresholds for 40+ feature columns in the Hive feature store, executing as scheduled Apache Airflow DAGs at hourly intervals and writing structured anomaly reports to a shared Hive monitoring table
- Authored optimized Hive SQL to compute per-feature distribution baselines (mean, standard deviation, null rate, cardinality) across 100M+ daily records, reducing per-query wall-clock time from 45 minutes to under 8 minutes via partition pruning and bucketing strategy
- Integrated anomaly flag output with a lightweight email alerting layer (Python SMTP), enabling same-day detection and escalation of 4 confirmed data quality incidents that would have propagated to live recommendation model serving under the prior manual workflow
- Reduced daily manual audit overhead by approximately 80%—from ~3 analyst-hours to ~35 minutes—freeing team capacity for upstream feature engineering collaboration with the recommendation algorithm engineers
- Delivered post-incident documentation for each of the 4 detected anomalies, establishing a root-cause taxonomy (upstream schema change, pipeline job failure, feature backfill error) that informed a subsequent data contract adoption proposal by the engineering team

---

### DIDI IBG · Senior Data Analyst

---

**Project 1: Cross-Market Merchant Fraud Intelligence Platform**

*Baseline: DiDi Food's rapid Latin America expansion surfaced significant merchant fraud behaviors—fake review inflation, promotional coupon laundering, GPS coordinate spoofing—with no automated detection system in place, creating direct GMV integrity risk and eroding platform trust in two high-growth markets with no prior data infrastructure.*

- Architected end-to-end fraud signal pipeline on Apache Spark, ingesting multi-source behavioral data (order lifecycle events, GPS trace sequences, review submission metadata, coupon redemption logs) from Hive data marts to produce daily merchant risk scores across 50K+ active vendor accounts
- Developed anomaly detection model using Isolation Forest + gradient boosting ensemble (Python/scikit-learn) trained on 18 months of historical labeled fraud cases, achieving 87% recall and 74% precision on held-out ground-truth labels provided by the manual review team
- Integrated NLP-based fake-review signal as a secondary feature by fine-tuning a multilingual BERT model on 200K manually labeled review samples, boosting model precision from 74% to 91% and reducing false referral blocks on legitimate merchants by 23%
- Deployed automated risk score output to a downstream case management system via Python API integration, enabling the Trust & Safety team to triple their daily manual review throughput without headcount increase by prioritizing highest-confidence fraud flags
- Designed and maintained a risk analytics dashboard (SQL-backed) providing daily visibility into flagging volume, precision-recall trends, and market-level fraud rate—consumed by DiDi Food's VP of Operations as the primary Latin America risk health indicator
- Validated post-deployment fraud prevention impact against a pre-/post-control group comparison, attributing an estimated $2.3M annualized reduction in promotional abuse losses to the automated flagging system across the Mexico market in the first full quarter of operation

---

**Project 2: CNBV Regulatory Compliance Reporting Automation Pipeline**

*Baseline: DiDi Food Mexico was required to file 6 standardized financial data reports to Mexico's banking regulator (CNBV) on a monthly cycle; the existing process consumed 12+ analyst-hours per cycle of manual SQL extraction, cross-referencing across 4 Hive tables, and spreadsheet formatting—with zero data validation checkpoints and a documented history of 3 resubmission events in the prior 4 quarters.*

- Built a parameterized Python + Jinja2 SQL templating framework generating all 6 CNBV report types from upstream Hive data marts, reducing per-cycle report generation time from 12+ hours to 45 minutes and eliminating all manual copy-paste operations from the compliance workflow
- Implemented multi-stage data validation checkpoints—row count reconciliation, null rate thresholds, referential integrity constraints across foreign keys, and date range completeness verification—surfacing data quality anomalies before regulatory submission and attributing zero resubmission events in the 8 months post-deployment
- Established a version-controlled SQL query repository (Git) enabling the compliance legal team to self-serve ad-hoc regulatory data queries without engineering support, reducing compliance-to-engineering ticket volume by an estimated 60% in the subsequent quarter
- Coordinated requirements with DiDi's Mexico City legal counsel and the local finance team across a 14-hour timezone differential to ensure report schema compliance with CNBV Circular 3/2012 field specifications, resolving 11 field-level ambiguities through documented clarification sessions

---

### TIKTOK · Backend Software Engineering Intern

---

**Project 1: Real-Time Behavioral Anomaly Scoring Microservice**

*Baseline: TikTok's internal threat detection platform relied on a static rule engine with no behavioral baseline modeling layer; rule-only alerts generated high false positive volume, overwhelming SOC analyst capacity during peak event periods and masking genuine account compromise signals in noise.*

- Designed and implemented a Go-based anomaly scoring microservice consuming a Kafka real-time event stream and computing per-entity behavioral risk scores across 2B+ daily user events, applying statistical baseline models (exponential moving average + standard deviation bands) to detect deviations in session cadence, action velocity, and API call patterns
- Exposed scored output to downstream SOC alerting infrastructure via gRPC interface, enabling confidence-tier filtering that reduced false positive alert volume by 31% versus the legacy rule engine in A/B shadow comparison—validated over a 3-week observation window
- Applied unsupervised clustering (k-means on behavioral feature vectors: session duration, geo-velocity, action sequence entropy) to identify coordinated inauthentic behavior patterns across 100M+ active accounts, surfacing 3 previously undetected bot network clusters for escalation to the threat intelligence team
- Collaborated with the infrastructure team on distributed storage evaluation for anomaly score state persistence and TTL management; benchmarked Spanner-compatible schema designs (partitioned by entity hash, TTL-indexed) against internal KV store options, documenting trade-offs in an architecture decision record (ADR) for post-internship engineering handoff
- Validated microservice scalability to 50K events/second with p99 end-to-end latency < 200ms through structured load testing in the staging environment, ensuring production SLA compatibility before code review submission

---

**Project 2: DLP Enforcement Layer — Content Inspection API**

*Baseline: An internal red-team audit flagged the content inspection API as a potential data exfiltration vector: outbound API responses lacked automated policy enforcement, creating a compliant-by-policy-but-unguarded-in-practice gap that could allow sensitive data (PII, credential strings, internal metadata) to surface in API consumer responses without detection.*

- Implemented DLP enforcement middleware in Go integrated into the content inspection API's request/response lifecycle, inspecting all outbound payloads against a configurable JSON policy schema before transmission and blocking or redacting policy-violating content in-line
- Designed the policy schema using layered security primitives: regex pattern matching for PII formats (SSN, email, phone), Shannon entropy analysis for high-entropy string detection (API keys, tokens), and token classification against an internal sensitive-keyword dictionary—covering 100% of data categories defined in TikTok's internal data classification policy
- Built a Python-based regression test suite with 140+ test cases covering all defined sensitive data categories and adversarial bypass edge cases, integrated into the team's CI/CD pipeline to enforce DLP policy coverage on every merge commit
- Reduced policy-violating data exposure events by 23% in controlled UAT, validated using synthetic canary data injection (known-sensitive payloads seeded into test environments); findings formally documented in the team's vulnerability management tracking system as a closed P2 remediation
- Mapped DLP enforcement design decisions to NIST SP 800-53 AC-4 (Information Flow Enforcement) controls in coordination with the security architecture team, contributing to the team's Secure-by-Default posture documentation for the content inspection service boundary

---

> **Supplemental Note — Additional Section (Suggested Placement: Below Education)**
>
> **Honors & Activities**
> - Chinese National Certified Amateur Go Player, 2nd Dan · Self-taught; no formal coaching
> - 1st Place, Shanghai Municipal Go Championship (2022); 3rd Place, Shanghai Municipal Go Championship (2023)
>
> *Placement rationale: For a Cloud Security / Threat Engineering role, the Go player credential is strategically non-trivial. Reviewers in adversarial security domains consistently respond to demonstrated comfort with zero-sum strategic reasoning, pattern recognition under uncertainty, and self-directed skill acquisition from zero to competitive—all of which the self-taught championship narrative communicates without overstatement. Keep it factual; let the reviewer draw the inference.*
