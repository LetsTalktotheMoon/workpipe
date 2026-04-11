# Resume Prop Document — Zuora Billing Developer / Quote-to-Cash Engineer

---

## MODULE 1 — Professional Summary

Revenue operations and subscription billing engineer with 3+ years of progressive experience building data pipelines, financial reconciliation workflows, and backend automation across hyperscale consumer platforms (Temu, Didi IBG, TikTok), currently completing dual graduate programs in Computer Science (Georgia Tech OMSCS) and Information Management (UIUC MSIM) with concentration in enterprise systems integration, distributed transactions, and SaaS billing architecture. Brings a structurally differentiated analytical foundation — behavioral modeling and formal logic from undergraduate philosophy and cognitive psychology, quantitative financial modeling and international settlement frameworks from a graduate International Business–Finance program — that translates directly into rigorous Order-to-Revenue lifecycle design, multi-entity revenue recognition rule implementation, and subscription billing exception-handling logic across Zuora, Salesforce CPQ, NetSuite, and RevPro environments. Targeting Zuora Billing Developer and Quote-to-Cash engineering roles where demonstrated proficiency in Zuora Billing, Zuora Orders, Orders API, Zuora Revenue, Salesforce CPQ, NetSuite ERP integration, RevPro ASC 606 automation, and Mulesoft middleware orchestration directly addresses the need for engineers who can operate across the full Quote-to-Cash and Record-to-Report pipeline.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | ✓ Scripting: cron automation, pandas, CSV reconciliation scripts | ✓✓ Pipeline automation: Airflow DAGs, API-driven billing data extraction, reconciliation engines | ✓✓✓ Systems integration: Mulesoft dataweave prototyping, Zuora REST API test harnesses, revenue waterfall generators | **4+ years** |
| **SQL** | ✓✓ HiveQL/SparkSQL on 1B+ row transaction datasets | ✓✓✓ Canonical metric library, Redshift financial reporting, multi-currency settlement queries | ✓✓ Zuora Revenue reporting queries, NetSuite Saved Searches, journal entry reconciliation | **4+ years** |
| **Zuora Billing** | ✓ Subscription plan catalog data extraction, rate plan charge analysis for pricing experiments | ✓✓ Multi-currency billing run configuration, invoice template customization, payment gateway reconciliation | ✓✓✓ Complex billing rule engine configuration, usage-based metering integration, billing preview automation | **4+ years** |
| **Zuora Orders / Orders API** | ✓ Basic order creation scripting via REST API for test catalog entries | ✓✓ Order action orchestration (Create/Update/Suspend/Resume), order metrics pipeline for churn analysis | ✓✓✓ Orders API v2 migration, complex order-level amendment cascading, evergreen subscription lifecycle management | **4+ years** |
| **Salesforce** | ✓ Basic CRM data pull for recommendation funnel analysis, report builder | ✓✓ Salesforce-to-warehouse ETL integration, opportunity-to-order mapping, custom object design for regional ops | ✓✓✓ Salesforce CPQ-to-Zuora order handoff architecture, approval workflow configuration, trigger-based automation | **4+ years** |
| **Salesforce CPQ** | — | ✓ Quote template configuration for regional pricing tiers, basic product bundle structures | ✓✓✓ Advanced CPQ pricing rule engine, multi-dimensional discount schedules, contract amendment flows, guided selling configuration | **2+ years** |
| **NetSuite** | — | ✓✓ NetSuite GL mapping for multi-entity financial close, intercompany journal entries, Saved Searches for AR aging | ✓✓✓ NetSuite ERP integration architecture, SuiteScript custom record automation, revenue arrangement sync from Zuora Revenue | **2+ years** |
| **RevPro** | — | ✓ RevPro data feed validation, ASC 606 allocation rule familiarization, manual SSP analysis uploads | ✓✓✓ RevPro ASC 606 revenue recognition automation, stand-alone selling price waterfall configuration, contract modification handling | **2+ years** |
| **Mulesoft** | — | ✓ Mulesoft Anypoint monitoring for existing billing integration flows, basic connector troubleshooting | ✓✓✓ Mulesoft integration architecture: Zuora-to-NetSuite middleware, Salesforce CPQ event-driven triggers, error handling and dead-letter queue design | **2+ years** |
| **Zuora Revenue** | — | ✓✓ Zuora Revenue journal entry generation, revenue recognition schedule validation, period-close checklist execution | ✓✓✓ Zuora Revenue rule configuration for hybrid SaaS/usage models, multi-element arrangement allocation, automated fair value waterfall | **2+ years** |
| **Quote-to-Cash** | ✓ Downstream consumer of pricing data; exposure to order-to-fulfillment data flows | ✓✓ End-to-end Q2C process mapping for Didi's SaaS vendor management and internal subscription licensing | ✓✓✓ Full Q2C lifecycle ownership: CPQ quote → Zuora order → billing → revenue recognition → NetSuite GL posting | **4+ years** |
| **Order-to-Revenue** | — | ✓✓ O2R data lineage documentation for cross-border settlement workflows, revenue leakage audit | ✓✓✓ O2R pipeline architecture: order ingestion → billing event → revenue scheduling → journal entry → ERP close | **2+ years** |
| **SaaS Subscription** | ✓ Subscription analytics: cohort retention, MRR/ARR computation from raw transaction logs | ✓✓ SaaS subscription lifecycle management tooling: trial-to-paid conversion, mid-term upgrade/downgrade waterfall | ✓✓✓ Complex SaaS subscription modeling: multi-tier usage + flat-fee hybrids, evergreen renewals, co-termed amendments | **4+ years** |
| **Record to Report** | — | ✓✓ R2R process support: sub-ledger reconciliation, intercompany elimination entries, period-close task automation | ✓✓✓ R2R architecture ownership: automated journal entry generation, trial balance reconciliation, audit-trail compliance | **2+ years** |
| **Git** | ✓ Personal versioning | ✓✓ Team branch workflows, code review | ✓✓✓ CI/CD pipeline for integration deployments, repo governance | **4+ years** |

**ATS Depth Note:** Python, SQL, Zuora Billing, Zuora Orders/Orders API, Salesforce, Quote-to-Cash, and SaaS Subscription establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters. Salesforce CPQ, NetSuite, RevPro, Mulesoft, Zuora Revenue, Order-to-Revenue, and Record to Report demonstrate a clear escalation from peripheral data consumption to full architectural ownership, substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Automated the recommendation team's daily pricing experiment digest using **Python** (pandas, SQLAlchemy) and Linux **cron** scheduling, reconciling **Zuora Billing** subscription plan catalog exports against internal A/B experiment cohorts to validate rate plan charge accuracy across 12 active pricing tiers; eliminated approximately 6 manual analyst-hours per week.
- Authored and tuned complex **HiveQL / SparkSQL** queries against 1B+ row transaction datasets to extract **SaaS Subscription** cohort metrics (MRR, trial-to-paid conversion rate, subscription churn by rate plan), directly supplying quantitative inputs to the product team's weekly pricing adjustment decisions.
- Developed a **Python** script leveraging the **Zuora Orders API** (REST) to programmatically create and validate test subscription orders in the staging catalog, enabling the QA team to verify billing run outputs against expected invoice line items for 8 promotional bundle configurations before launch.
- Extracted **Salesforce** CRM opportunity and lead-source data via SOQL report builder queries, mapping downstream conversion funnels to subscription activation rates and surfacing a 14% attribution gap between marketing-reported leads and actual **Quote-to-Cash** order records.
- Standardized all reconciliation scripts, SQL templates, and API test harnesses under a shared **GitLab** repository with version-tagged releases, introducing reproducible re-run conventions that eliminated duplicated work across 3 team members.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Designed and operationalized an end-to-end **Python / Apache Airflow** DAG pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's vendor subscription billing and settlement reporting, integrating **Zuora Billing** invoice data, **NetSuite** GL journal entries, and **Salesforce** opportunity records to reduce report delivery lead time from 3 business days to under 4 hours.
- Built a multi-currency billing reconciliation engine in **Python** that consumed **Zuora Billing** invoice exports (MXN, USD, BRL) and cross-referenced them against **NetSuite** intercompany journal entries, automating the detection of FX translation variances and reducing month-end close discrepancies by 62% across 3 LATAM legal entities.
- Configured **Zuora Orders** action workflows (Create, Suspend, Resume, Cancel) for Didi's internal SaaS vendor license management system, orchestrating mid-term subscription amendments for 200+ driver-partner enterprise accounts and producing automated **Order-to-Revenue** data lineage reports that identified $180K in previously unrecognized deferred revenue.
- Developed **Mulesoft** Anypoint monitoring dashboards and basic connector troubleshooting runbooks for the existing **Salesforce**-to-billing integration flows, reducing mean-time-to-resolution for failed order sync events from 6 hours to under 45 minutes and preventing an estimated 30+ invoice generation delays per quarter.
- Authored **Zuora Revenue** journal entry generation scripts and validated monthly revenue recognition schedules against **RevPro** ASC 606 stand-alone selling price allocation outputs, supporting the finance team's quarterly close process and eliminating 2 recurring manual reconciliation steps from the **Record to Report** checklist.
- Created **NetSuite** Saved Searches for AR aging analysis and intercompany elimination entries, enabling the regional controller to execute **Record to Report** period-close tasks 40% faster and producing audit-ready sub-ledger reconciliation packages for 4 consecutive quarters without restatement.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Architected and implemented a **Mulesoft**-based middleware integration layer connecting **Salesforce CPQ** quote approval events to **Zuora Orders API** v2 order creation endpoints, enabling fully automated quote-to-order handoff for TikTok's internal SaaS procurement platform; reduced manual order entry cycle time from 2 business days to under 15 minutes for 95% of standard quote configurations.
- Designed and configured **Salesforce CPQ** advanced pricing rules, multi-dimensional discount schedules, and guided selling flows for 4 product families across the security platform's internal tooling subscription catalog, supporting contract amendment workflows that handled mid-term upgrades, co-termed additions, and evergreen renewals without billing disruption.
- Built an end-to-end **Quote-to-Cash** automation pipeline spanning CPQ quote generation → **Zuora Orders** subscription creation → **Zuora Billing** invoice run → **Zuora Revenue** recognition schedule → **NetSuite** GL journal posting, processing 300+ subscription lifecycle events per month with a 99.4% straight-through processing rate.
- Configured **RevPro** ASC 606 revenue recognition rules for hybrid SaaS subscription + usage-based billing models, implementing stand-alone selling price waterfall allocation logic and contract modification handling for multi-element arrangements; automated fair value determination reduced manual SSP analysis effort by 80%.
- Developed **Zuora Revenue** rule configurations for complex multi-element **SaaS Subscription** arrangements combining flat-fee platform access, usage-based API metering, and professional services milestones, producing automated revenue allocation waterfalls that passed SOX audit review with zero adjustments.
- Designed **Mulesoft** error handling, dead-letter queue, and retry patterns for the **Order-to-Revenue** integration pipeline, implementing circuit-breaker logic for Zuora-to-NetSuite sync failures and reducing unprocessed journal entry backlog from 120+ items per month-end close to fewer than 5.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Subscription Catalog Reconciliation and Pricing Experiment Validation System**

*The recommendation algorithm team ran 8–12 concurrent pricing experiments per sprint cycle, each requiring manual cross-referencing of Zuora Billing rate plan charge data against internal A/B test cohort definitions; reconciliation was performed via ad-hoc spreadsheets, taking 3–5 analyst-hours per experiment and producing inconsistent results that delayed weekly pricing committee decisions by 1–2 business days.*

- Developed a **Python** (pandas, SQLAlchemy) reconciliation engine that programmatically extracted **Zuora Billing** subscription plan catalog data — rate plan charges, pricing tiers, discount percentages, and currency configurations — and cross-referenced them against internal experiment cohort definitions stored in HiveQL tables, automating a previously manual 3–5-hour-per-experiment validation process down to a 12-minute scheduled batch run.
- Authored complex **HiveQL / SparkSQL** queries against 1B+ row event datasets to compute **SaaS Subscription** cohort metrics (MRR by rate plan, trial-to-paid conversion by pricing tier, subscription churn segmented by promotional bundle), delivering a canonical metrics layer that replaced 4 ad-hoc analyst spreadsheets with a single auditable source of truth.
- Built a **Python** API test harness using the **Zuora Orders API** (REST) to programmatically create, modify, and cancel test subscription orders in the staging environment, validating billing preview outputs against expected invoice line items for all 12 active pricing tiers; the harness caught 3 rate plan misconfiguration errors before production deployment in Q4 2021.
- Mapped **Salesforce** CRM opportunity data to downstream **Quote-to-Cash** subscription activation records via SOQL extraction and Python join logic, surfacing a 14% attribution gap between marketing-reported qualified leads and actual activated subscriptions — a finding that triggered a cross-functional audit of the lead-to-order handoff process.
- Scheduled the full reconciliation pipeline as a Linux **cron** job with alerting via webhook, delivering daily pricing experiment status reports to the product team's Slack channel by 08:00 and compressing the overall pricing committee review cycle from 3–5 days to same-day availability.

---

### DIDI IBG · Key Project 1

**Multi-Currency Billing Reconciliation and Cross-Border Settlement Automation Platform**

*The Mexico Food vertical operated across 3 LATAM legal entities (Mexico, Brazil, Colombia) with transactions denominated in MXN, USD, and BRL; month-end close required manual reconciliation of Zuora Billing invoice data against NetSuite intercompany journal entries — a 4-day process performed by 2 FP&A analysts using pivot tables, frequently producing FX translation variances that required post-close adjustments in 3 of the prior 4 quarters.*

- Built a multi-currency billing reconciliation engine in **Python** (pandas, requests) that consumed **Zuora Billing** invoice line-item exports via the Billing REST API, cross-referenced them against **NetSuite** intercompany journal entries retrieved via SuiteTalk (RESTlet), and automatically flagged FX translation variances exceeding a configurable $50 materiality threshold; reduced month-end close discrepancies by 62% across 3 LATAM legal entities.
- Configured **Zuora Orders** action workflows (Create, Suspend, Resume, Cancel) for Didi's internal SaaS vendor license management system servicing 200+ driver-partner enterprise accounts, implementing mid-term amendment orchestration logic that correctly cascaded rate plan changes through billing, revenue recognition, and GL posting layers — surfacing $180K in previously unrecognized deferred revenue during the initial remediation cycle.
- Developed **Zuora Revenue** journal entry generation scripts that automated monthly revenue recognition schedule production, validating outputs against **RevPro** ASC 606 stand-alone selling price allocation rules and eliminating 2 recurring manual reconciliation steps from the **Record to Report** period-close checklist; the finance team achieved 4 consecutive clean quarterly closes without restatement.
- Created **NetSuite** Saved Searches and SuiteAnalytics workbooks for AR aging analysis, intercompany elimination entries, and sub-ledger-to-GL reconciliation, enabling the regional controller to execute **Record to Report** close tasks 40% faster and producing audit-ready documentation packages that passed external audit review without exceptions.
- Operationalized the reconciliation pipeline as an **Airflow** DAG with parameterized legal entity and currency inputs, scheduling automated runs at T+1 following each billing run and pushing exception reports to the finance team's Jira board; reduced FP&A manual effort from 4 analyst-days to under 3 hours per monthly close cycle.

---

### DIDI IBG · Key Project 2

**Salesforce-to-Billing Integration Monitoring and Order Sync Reliability Improvement**

*The existing Mulesoft-based integration between Salesforce CRM and the Zuora Billing platform experienced an average of 30+ failed order sync events per quarter, each requiring manual investigation averaging 6 hours; root causes were undocumented, and the operations team lacked visibility into sync failure patterns, leading to cascading invoice generation delays affecting vendor payment SLAs.*

- Developed **Mulesoft** Anypoint monitoring dashboards tracking end-to-end **Salesforce**-to-**Zuora Billing** order sync event latency, success/failure rates, and error categorization, providing the first systematic visibility into integration health and enabling proactive incident response before invoice generation deadlines.
- Authored integration troubleshooting runbooks documenting the 8 most common **Mulesoft** connector failure modes (OAuth token expiry, Zuora API rate limiting, Salesforce field mapping mismatches, NetSuite concurrent user locks), reducing mean-time-to-resolution from 6 hours to under 45 minutes per incident.
- Implemented automated alerting on the **Mulesoft** integration layer that detected **Orders API** sync failures within 5 minutes of occurrence and routed categorized incident tickets to the appropriate resolution queue, preventing an estimated 30+ downstream invoice generation delays per quarter.
- Mapped the end-to-end **Order-to-Revenue** data lineage from **Salesforce** opportunity close through **Zuora Orders** creation, billing run execution, **Zuora Revenue** recognition, and **NetSuite** GL posting, producing a canonical process flow document adopted by both the engineering and finance teams as the authoritative reference for cross-functional incident triage.

---

### TIKTOK SECURITY · Key Project 1

**End-to-End Quote-to-Cash Automation Pipeline for Internal SaaS Procurement Platform**

*TikTok's security platform managed 300+ internal SaaS tool subscriptions through a manual procurement workflow: security engineers submitted quote requests via email, procurement analysts manually keyed orders into Zuora, and finance teams reconciled invoices against purchase orders in spreadsheets — the process averaged 2 business days per order, suffered a 12% error rate in billing configurations, and produced $45K in quarterly revenue recognition timing differences due to inconsistent GL posting.*

- Architected a **Mulesoft**-based middleware integration layer connecting **Salesforce CPQ** quote approval workflows to **Zuora Orders API** v2 order creation endpoints, implementing event-driven triggers on CPQ quote status changes that automatically generated corresponding Zuora subscription orders with correct rate plan, billing frequency, and contract term parameters; achieved 95% straight-through processing for standard quote configurations, reducing order entry cycle time from 2 business days to under 15 minutes.
- Designed and configured **Salesforce CPQ** advanced pricing rules for 4 product families (endpoint protection, SIEM, vulnerability scanning, identity management), implementing multi-dimensional discount schedules based on seat count tiers and contract duration, guided selling flows for non-technical requesters, and contract amendment workflows handling mid-term upgrades, co-termed additions, and evergreen renewals without billing disruption.
- Built the downstream **Zuora Billing** → **Zuora Revenue** → **NetSuite** GL integration path: billing run outputs triggered automated **Zuora Revenue** recognition schedule generation; recognized revenue journal entries were transformed and posted to **NetSuite** GL accounts via **Mulesoft** batch sync, achieving a 99.4% straight-through processing rate across 300+ subscription lifecycle events per month.
- Configured **RevPro** ASC 606 revenue recognition rules for hybrid **SaaS Subscription** models combining flat-fee platform access with usage-based API call metering, implementing stand-alone selling price waterfall allocation for multi-element arrangements and contract modification handling for mid-term scope changes; automated fair value determination reduced manual SSP analysis from 8 analyst-hours per arrangement to under 15 minutes.
- Designed **Mulesoft** error handling, dead-letter queue, and circuit-breaker patterns for the full **Order-to-Revenue** pipeline, implementing configurable retry policies with exponential backoff for transient Zuora API failures and NetSuite concurrent user lock conflicts; reduced unprocessed journal entry backlog from 120+ items per month-end close to fewer than 5, eliminating the primary root cause of quarterly revenue recognition timing differences.

---

### TIKTOK SECURITY · Key Project 2

**Zuora Revenue Multi-Element Allocation and Record-to-Report Automation Framework**

*The security platform's subscription catalog included 12 multi-element SaaS arrangements combining platform licenses, usage-based API metering, and professional services milestones; revenue allocation was performed manually by the finance team using spreadsheet-based SSP analysis, averaging 8 hours per arrangement and producing allocation outputs that required adjustment in 3 of the prior 4 SOX audit cycles due to inconsistent fair value methodology application.*

- Developed **Zuora Revenue** rule configurations for complex multi-element **SaaS Subscription** arrangements — flat-fee platform access, usage-based API call tiers, and milestone-based professional services deliverables — producing automated revenue allocation waterfalls conforming to ASC 606 multi-element arrangement guidance; all 12 arrangement types passed SOX audit review with zero allocation adjustments.
- Implemented **RevPro** stand-alone selling price waterfall logic with automated fair value determination using the adjusted market assessment, expected cost plus margin, and residual approaches in priority sequence, reducing per-arrangement SSP analysis from 8 analyst-hours to under 15 minutes and eliminating the subjective judgment variance that triggered prior audit findings.
- Built an automated **Record to Report** period-close pipeline: **Zuora Revenue** recognized revenue journal entries were validated against **Zuora Billing** invoice totals, transformed into **NetSuite**-compatible CSV import format via **Python** transformation scripts, and batch-uploaded to NetSuite GL accounts; automated trial balance reconciliation scripts flagged variances exceeding $100 within 30 minutes of period close.
- Authored **Python** test harnesses for regression-testing the full **Quote-to-Cash** → **Order-to-Revenue** → **Record to Report** data flow across 15 representative subscription lifecycle scenarios (new order, mid-term upgrade, downgrade, co-term, cancellation with refund, evergreen renewal, usage true-up), executing automated end-to-end validation after each Zuora or NetSuite configuration change.
- Delivered comprehensive **Record to Report** process documentation covering journal entry mapping rules, intercompany elimination logic, sub-ledger reconciliation procedures, and audit trail requirements, establishing the security platform finance team's first fully documented and repeatable period-close playbook adopted across 3 consecutive quarterly close cycles.
