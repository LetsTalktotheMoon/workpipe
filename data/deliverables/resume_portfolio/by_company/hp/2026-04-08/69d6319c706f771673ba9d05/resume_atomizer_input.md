# Jingyi Zhang
404-731-1200 | jzhang3392@gatech.edu

## Professional Summary
* **Software Engineering Transition:** Software Engineer Intern and former Senior Data Analyst building **Python**, **Go**, and **SQL** systems for security, launch operations, and internal tooling.
* **Infrastructure Readiness:** Experience shipping services on **Linux** with **GitHub Actions** automation and **Prometheus** telemetry, with backend patterns transferable to development infrastructure for AI tooling.
* **Systems Judgment:** Apply the pattern recognition of a China National Certified **Go** **2-dan** player, **2022 city** champion, and **2023 city** third-place finisher to complex systems analysis and high-stakes problem solving.

## Skills
* **Programming:** Python, Go, Java, Flask, gRPC, Linux, Prometheus
* **Data:** SQL, Pandas, Hive, Spark SQL, A/B Testing, AWS Bedrock, RAG
* **Cloud:** PostgreSQL, Kafka, Docker, Kubernetes, GitHub Actions, S3

## Work Experience
### Software Engineer Intern | TikTok · Security | San Jose, USA
**Jun 2025 – Dec 2025**
* Built **Go** and **gRPC** handlers for the security evidence service, reducing median retrieval latency from **4.8 seconds** to **2.9 seconds** for investigator-facing lookups backed by **PostgreSQL**.
* Developed **Python** jobs on **Linux** to validate event payloads before ingestion into **Kafka**, cutting malformed-record retries by **31%** within a team-maintained security workflow.
* Contributed **Docker** packaging updates for **Kubernetes** deployments and added **Prometheus** metrics, shortening issue triage time from **18 minutes** to **7 minutes** in staging and production support.
* Integrated **GitHub Actions** checks into the security policy repo, raising pre-merge test coverage from **62%** to **86%** for intern-owned changes.
**_Project: Threat Knowledge Retrieval Assistant_**
> Security analysts were spending too much time searching fragmented policy notes and investigation records before escalating evidence requests.
* Built **Python** preprocessing routines that chunked investigation notes into **S3** and fed a team-maintained **RAG** index used by the threat knowledge assistant.
* Implemented **Go** adapters that called a team-maintained **AWS Bedrock** endpoint from the threat knowledge assistant, improving top-**3** answer relevance by **24%** on an internal evaluator set.
* Added **PostgreSQL** feedback logging and **Prometheus** counters for the threat knowledge assistant, giving engineers daily visibility into failed retrievals and low-confidence answers.
* Containerized local test fixtures with **Docker** and wired regression runs into **GitHub Actions**, reducing manual verification from **45 minutes** to **15 minutes** per release candidate.

### Senior Data Analyst | DiDi · IBG · Food | Beijing/Mexico
**Sep 2022 – May 2024**
> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.
* Led **Python** and **SQL** analysis for City Launch Ops, identifying dispatch and cancellation gaps that improved first-week order completion by **14%** across **6 city** launches.
* Built a **Flask** service with **Kafka** event consumers for the merchant onboarding API, cutting manual status reconciliation from **11 hours** to **3 hours** each week.
* Developed **Java** endpoints and **Docker** release configs within the merchant onboarding API, reducing rollback frequency by **29%** during launch windows.
* Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.
* Coordinated backend and ops handoffs around **Kafka** and **Flask** dependencies for the store availability service, trimming incident re-open rates by **22%** during peak meal periods.
**_Project: Launch Readiness Console_**
> City expansion teams lacked one place to verify operational dependencies before **go**-live, creating avoidable launch delays and handoff churn.
* Built **Flask** endpoints for the launch readiness console, exposing **SQL** health checks used by Mexico and Beijing ops before city **go**-live.
* Implemented **Python** validation rules that compared supply, menu, and courier readiness in the launch readiness console, reducing pre-launch checklist errors by **34%**.
* Added **Java** job handlers that published milestone changes through **Kafka** for the launch readiness console, keeping downstream notifications within **5 minutes** of status updates.
* Packaged the launch readiness console with **Docker**, enabling consistent handoff between backend engineers and regional operators during **9** launch rehearsals.

### Data Analyst | Temu · R&D | Shanghai
**Jun 2021 – Feb 2022**
* Analyzed **Hive** and **SQL** transaction tables for the promotion diagnostics queue, surfacing price-drop anomalies that recovered **8%** more eligible SKUs during weekly campaigns.
* Built **Python** and **Pandas** notebooks to trace search-to-purchase behavior in the listing quality review, shortening analyst turnaround from **2 days** to **6 hours**.
* Used **Spark SQL** to reshape clickstream data for the seller activation dashboard, improving refresh stability for **12** recurring business reports.
* Evaluated coupon experiments with **A/B Testing** methods on **Hive** extracts, helping the R&D team retire one low-performing incentive path after a **9%** lift failed to hold in holdout groups.

## Education
| Degree | Institution | Period |
| --- | --- | --- |
| M.S. Computer Science | Georgia Institute of Technology | Expected May 2026 |

## Achievements
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023)
