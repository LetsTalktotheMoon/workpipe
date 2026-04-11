## Professional Summary
* **Backend Transition:** Software engineer transitioning from analytics to backend development with hands-on delivery in **Java**, **Go**, and **C++** across security, food operations, and marketplace systems.
* **Distributed Systems Scope:** Built and extended reliability-focused services using **Kafka**, **PostgreSQL**, and **AWS**, with senior-level operating exposure at DiDi and production engineering contributions within a team-maintained service at TikTok.
* **Strategic Pattern Recognition:** Apply the pattern recognition of a China National Certified **Go** **2-dan** player, **2022 city** champion, and **2023 city** third-place finisher to complex systems analysis and high-stakes problem solving.

## Skills
* **Programming:** Java, C++, Go, Python, Embedded, gRPC, Flask
* **Cloud:** PostgreSQL, Kafka, Redis, Docker, Kubernetes, AWS, AWS Bedrock, SQL, Spark SQL

## Experience
### Software Engineer Intern | TikTok · Security
*Jun 2025 – Dec 2025 | San Jose, USA*

* Built **Go** handlers and **gRPC** contracts for security evidence service, reducing analyst retrieval time from **18 minutes** to **7 minutes** within a team-maintained service backed by **PostgreSQL**.
* Implemented **Java** ingestion workers consuming **Kafka** events for policy incident index, cutting duplicate evidence records by **34%** during weekly replay tests.
* Contributed **Docker** packaging and **Kubernetes** readiness probes for security evidence service, lowering failed staging deployments from **6** to **2** per month.
* Integrated a team-maintained **AWS Bedrock** retrieval endpoint into security evidence service so investigators could search prior cases in natural language, improving top-**5** evidence recall by **27%** on an internal benchmark.
* Developed a lightweight **Embedded** **C++** parser used by a Linux-side evidence collector, trimming host CPU overhead by **19%** in controlled lab runs.

**Project: Security Evidence Retrieval Assistant**
> Investigators needed faster access to comparable prior cases without manually stitching together logs, tags, and analyst notes.
* Built **Go** ranking logic on top of **PostgreSQL** metadata and **AWS Bedrock** embeddings for case retrieval assistant, raising first-query resolution by **24%** on an internal dataset.
* Added **gRPC** adapters between **Java** ingestion services and the assistant so evidence tags from **Kafka** streams were searchable within **5 seconds** of arrival.
* Containerized evaluation jobs with **Docker** and ran smoke suites on **Kubernetes**, keeping release verification under **12 minutes** for scoped intern changes.
* Tuned the **Embedded** **C++** tokenizer used by the collector-side preprocessor, reducing malformed payloads by **21%** before records entered the team-maintained retrieval flow.

### Senior Data Analyst | DiDi · IBG · Food
*Sep 2022 – May 2024 | Beijing/Mexico*
> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.

* Led development of **Java** services behind City Launch Ops, replacing manual spreadsheet routing with service-backed decision rules and reducing launch configuration turnaround from **3 days** to **9 hours**.
* Built **Python** and **SQL** quality checks for merchant supply monitor, surfacing broken assortment feeds **2 days** earlier and cutting false-positive alerts by **31%**.
* Coordinated **Kafka** event contracts and **Redis** caching for order readiness API, lowering p95 response time from **420** ms to **250** ms during lunch peaks in **20+ cities** across multiple markets.
* Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.
* Extended a **Flask** admin surface that exposed rule diagnostics from an **Embedded** **C++** scoring library, cutting incident triage time from **45 minutes** to **18 minutes** for launch-day issues.

**Project: Multi-City Launch Decision Service**
> New-market launches depended on fragmented checks across assortment, courier coverage, and subsidy rules, creating avoidable delays and inconsistent operator decisions.
* Designed a **Java** rule-execution layer for City Launch Ops that standardized market-launch checks across menu quality, courier coverage, and subsidy guardrails, reducing duplicate manual reviews by **38%**.
* Implemented **Kafka** consumers and **Redis** snapshots so launch-state changes propagated to downstream tools within **90 seconds** instead of hourly refreshes.
* Wrote **SQL** backfills and **Python** replay scripts to validate rollout behavior over **12 months** of historical launches before production cutover.
* Integrated an **Embedded** **C++** heuristics module through a **Flask** diagnostics endpoint, giving operators explainable reasons for blocked launches and reducing escalation loops by **26%**.

### Data Analyst | Temu · R&D
*Jun 2021 – Feb 2022 | Shanghai*

* Built **SQL** and **Spark SQL** analyses for assortment anomaly service, identifying category-level stock mismatches that reduced out-of-stock exposure by **14%** on pilot categories.
* Created **Python** validation scripts for merchant onboarding datasets, cutting weekly cleanup time from **6 hours** to **2 hours** for the R&D team.
* Developed a small **Flask** review tool for promotion exception queue, letting analysts inspect rule hits in one place and shortening case resolution by **29%**.
* Automated recurring **SQL** metric checks for seller quality monitor, catching schema drift before report generation on **11** straight weekly cycles.

## Education
### M.S. Computer Science | Georgia Institute of Technology
*Expected May 2026*

## Achievements
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).