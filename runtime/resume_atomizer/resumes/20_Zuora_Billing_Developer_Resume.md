# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Revenue Operations & Billing Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery spanning enterprise **SaaS** **billing** architectures (**Zuora Billing**/**Orders**, **Salesforce CPQ**, **NetSuite** ERP integration), **Mulesoft** middleware orchestration, and **RevPro** ASC 606 **revenue** recognition automation.
* **End-to-End Quote-to-Cash Delivery:** Designs and ships across the full **Quote-to-Cash** and **Record to Report** pipeline — from **Salesforce CPQ** pricing configuration and **Zuora Orders API** integration to multi-currency settlement reconciliation, **Order-to-Revenue** lifecycle tracking, and **SaaS Subscription** billing exception handling.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Graduate foundation in international finance directly applicable to multi-entity revenue recognition and cross-border billing domain reasoning. Effective cross-functional collaborator bridging engineering, finance, and compliance teams.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Billing Infrastructure Contributions:_**

* Configured **Salesforce CPQ** pricing rule sets, multi-tier seat-count discount schedules, and guided selling flows for 3 security product families, implementing co-term proration calculation logic for mid-contract additions and evergreen renewal flags synchronized with **Zuora** subscription auto-renewal settings.
* Validated **RevPro** ASC 606 **revenue** recognition rule outputs for hybrid **SaaS Subscription** + usage-based billing models, cross-referencing automated SSP waterfall allocations against **Zuora Billing** invoice data to verify end-to-end billing pipeline correctness.
* Built and executed integration test suites validating the **Zuora Billing** invoice run → **Zuora Revenue** recognition schedule → **NetSuite** GL journal posting flow across 15 subscription lifecycle scenarios; identified and resolved 6 edge-case payload mapping failures pre-launch, contributing to 99.4% straight-through processing across 300+ monthly events.

**_Project: Quote-to-Cash Integration Pipeline_**

* Implemented a **Mulesoft**-based integration flow connecting **Salesforce CPQ** quote approval events to **Zuora Orders API** v2 order creation endpoints, mapping CPQ quote line items to Zuora rate plan charge parameters (billing frequency, contract term, product catalog IDs); achieved 95% straight-through processing rate, reducing **order** entry cycle time from 2 business days to under 15 minutes (**Quote-to-Cash**).
* Built the downstream **Zuora Billing** → **Zuora Revenue** recognition schedule → **NetSuite** GL journal posting path: billing run completion events triggered automated **revenue** recognition schedule generation; recognized **revenue** entries transformed by **Mulesoft** batch sync into **NetSuite** GL accounts via field-mapped staging (**Order-to-Revenue**).
* Designed **Mulesoft** resilience patterns — dead-letter queue routing, configurable exponential backoff retry, and circuit-breaker logic isolating **NetSuite** concurrent user lock conflicts — reducing unprocessed journal entry backlog at month-end close from 120+ items to fewer than 5.
* Authored a 15-scenario regression test harness covering the full **Quote-to-Cash** → **Order-to-Revenue** data flow (new order, co-term addition, mid-term upgrade, downgrade, cancellation-with-refund, evergreen renewal) plus 3 failure-injection scenarios.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

**_Revenue Recognition & Record to Report:_**

* Developed **Zuora Revenue** rule configurations for multi-element **SaaS Subscription** arrangements — flat-fee vendor access, usage-based API tiers, and milestone-based onboarding — producing automated **revenue** allocation waterfalls conforming to ASC 606; all 12 arrangement types validated clean across two consecutive SOX audit cycles (**RevPro**).
* Built the automated **Record to Report** period-close pipeline: **Zuora Revenue** recognized journal entries validated against **Zuora Billing** invoice totals, transformed into **NetSuite**-compatible import format via Python field-mapping scripts, and batch-uploaded to **NetSuite** GL accounts; automated trial balance reconciliation flagged variances within 30 minutes of period close across 3 LATAM legal entities.
* Implemented **RevPro** SSP waterfall logic with automated fair value determination, reducing per-arrangement SSP analysis from 6 analyst-hours to under 20 minutes and eliminating subjective judgment variance that had triggered prior audit findings.

**_Project: Billing Reconciliation & Operations:_**

* Architected a multi-currency billing reconciliation engine in Python consuming **Zuora Billing** invoice exports (MXN, USD, BRL) cross-referenced against **NetSuite** intercompany journal entries, automating FX translation variance detection and reducing month-end close discrepancies by 62% across 3 LATAM legal entities.
* Designed **Zuora Orders** action workflow sequences (Create, Suspend, Resume, Cancel) for DiDi's internal **SaaS** vendor license management system, orchestrating mid-term subscription amendments for 200+ enterprise accounts and surfacing $180K in previously unrecognized deferred **revenue** (**Order-to-Revenue**).
* Developed **Mulesoft** Anypoint integration monitoring dashboards and connector troubleshooting runbooks for **Salesforce**-to-billing sync flows, reducing mean-time-to-resolution for failed **order** sync events from 6 hours to under 45 minutes.
* Designed and operationalized a Python/Apache Airflow DAG pipeline integrating **Zuora Billing** invoice data, **NetSuite** GL journal entries, and **Salesforce** opportunity records; reduced report delivery from 3 business days to under 4 hours.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Automated the recommendation team's daily pricing experiment digest using Python, reconciling **Zuora Billing** subscription plan catalog exports against internal A/B experiment cohorts to validate rate plan charge accuracy across 12 active pricing tiers; eliminated ~6 manual analyst-hours per week.
* Authored and tuned HiveQL/SparkSQL queries against 1B+ row transaction datasets to extract **SaaS Subscription** cohort metrics (MRR, trial-to-paid conversion rate, churn by rate plan), supplying inputs to weekly pricing adjustment decisions.
* Developed a Python script using the **Zuora Orders API** (REST) to programmatically create and validate test subscription **orders** in the staging catalog, enabling QA verification of billing run outputs against expected invoice line items for 8 promotional bundle configurations.
* Extracted **Salesforce** CRM opportunity and lead-source data via SOQL report queries, mapping conversion funnels to subscription activation rates and surfacing a 14% attribution gap between marketing-reported leads and actual **Quote-to-Cash** order records.

---

## Skills

**Revenue Systems:** Zuora Billing, Zuora Orders, Orders API, Zuora Revenue, Salesforce CPQ, RevPro (ASC 606)
**ERP & Finance:** NetSuite, Record to Report, Order-to-Revenue, Multi-Currency Settlement
**Integration:** Mulesoft Anypoint, REST APIs, Middleware Orchestration, Dead-Letter Queue Patterns
**Languages:** Python, SQL, HiveQL, SparkSQL
**SaaS & Billing:** SaaS Subscription Lifecycle, Quote-to-Cash, Usage-Based Metering, MRR/ARR Analytics
**DevOps:** Git, GitLab CI/CD, Docker, Apache Airflow

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