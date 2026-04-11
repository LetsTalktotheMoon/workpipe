# Jingyi Zhang
404-731-1200 | jzhang3392@gatech.edu

## Professional Summary
* **Backend Systems Transition:** Software engineer transitioning from data analytics into backend engineering with hands-on delivery in **SQL**, **ETL**, and **Distributed Systems** across security, commerce, and food delivery environments.
* **Production Decision Infrastructure:** Built and supported services and data workflows in **Go**, **Python**, **Java**, **MySQL**, and **Snowflake** that turned operational signals into faster investigations and cross-market decisions.
* **Systems Judgment:** Apply the pattern recognition of a China National Certified **Go** **2-dan** player, **2022 city** champion, and **2023 city** third-place finisher to complex systems analysis and high-stakes problem solving.

## Skills
* **Programming:** Python, Go, Java, Snowflake, gRPC, Distributed Systems, Flask
* **Data:** SQL, Hive, ETL, Pandas, Spark SQL
* **Cloud:** MySQL, PostgreSQL, Kafka, Docker, Kubernetes, Redis

## Work Experience
### Software Engineer Intern | TikTok · Security | San Jose, USA
**Jun 2025 – Dec 2025**
* Built **Go** and **gRPC** handlers in the security evidence service, extending a team-maintained **Distributed Systems** workflow that joined alerts from **Kafka** with investigator requests and cut evidence assembly time from **18 minutes** to **7 minutes**.
* Developed **Python** checks for **ETL** jobs loading event summaries into **Snowflake**, reducing daily reconciliation exceptions by **38%** within a team-maintained analytics dataset.
* Containerized **PostgreSQL**-backed review components with **Docker** and validated deploy behavior in **Kubernetes**, shortening local-to-staging verification from **2 days** to **6 hours**.
* Implemented query tracing around **Kafka** consumers and **gRPC** calls, helping the team isolate hot partitions in a **Distributed Systems** path supporting **24**/**7** security investigations.
**_Project: Security Investigation Retrieval Workspace_**
> Investigators were switching across multiple internal tools to collect evidence, slowing case triage and increasing lookup gaps.
* Built a **Go** adapter that pulled normalized case events from **Kafka** and exposed ranked evidence over **gRPC**, giving analysts a single entry point for multi-source lookup.
* Wrote **Python** transformation logic to stage investigator labels into **Snowflake** and **PostgreSQL** tables used for retrieval quality checks.
* Packaged the service with **Docker** and ran test deployments in **Kubernetes**, improving release confidence for the team-maintained security evidence service.
* Added **ETL** validation rules for missing entity links, reducing empty-result lookups by **29%** on an internal evaluation set.

### Senior Data Analyst | DiDi · IBG · Food | Beijing/Mexico
**Sep 2022 – May 2024**
> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.
* Led **SQL** and **Python** analyses for City Launch Ops, converting weekly demand, supply, and fulfillment signals into market actions that improved launch-month order conversion by **14%** across **6** LATAM cities.
* Coordinated **ETL** jobs and **MySQL** data models behind the merchant onboarding service, cutting issue-resolution turnaround from **3 days** to **1 day** for regional ops.
* Built **Flask** APIs and **Kafka** consumers for dispatch exception tooling, replacing spreadsheet handoffs and reducing duplicate case creation by **31%**.
* Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.
* Partnered with backend engineers on **Java** services running in **Docker**, adding **Redis** caching for a pricing rule service and lowering repeated read load by **27%**.
**_Project: Merchant Fulfillment Control Center_**
> Regional operators lacked one consistent operating view for fulfillment exceptions, causing delayed action across Beijing and Mexico teams.
* Built **Java** modules for a merchant fulfillment control center within a **Distributed Systems** rollout path, merging city-level SLA events from **Kafka** with operator actions stored in **MySQL**.
* Added **Flask** admin endpoints for manual replay and audit lookup, reducing escalation handling from **45 minutes** to **12 minutes**.
* Reworked upstream **ETL** logic and validation **SQL** to align fulfillment states across Beijing and Mexico operating views.
* Shipped the service in **Docker** for regional testing, helping product and ops retire **4** legacy spreadsheets in one launch cycle.

### Data Analyst | Temu · R&D | Shanghai
**Jun 2021 – Feb 2022**
* Built **SQL** and **Hive** analyses for merchant onboarding, identifying form-drop patterns that improved completion rate by **11%** after rule updates.
* Used **Python** and **Pandas** to standardize weekly category reports for the R&D planning team, reducing manual refresh time from **6 hours** to **90 minutes**.
* Wrote **Spark SQL** jobs to compare promotion cohorts across search ranking experiments, giving PMs next-day readouts instead of waiting **2 days** for ad hoc pulls.
* Prepared anomaly slices in **Pandas** and **SQL** for the coupon abuse review, helping investigators recover **17%** more valid cases on an internal labeled set.

## Education
| Degree | Institution | Period |
| --- | --- | --- |
| M.S. Computer Science | Georgia Institute of Technology | Expected May 2026 |

## Achievements
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023)
