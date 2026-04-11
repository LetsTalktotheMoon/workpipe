## Professional Summary
* **Backend Systems Fit:** Software engineer candidate with **3+ years** of experience across **Rust**, **TypeScript**, **Go**, **Python**, **C++**, **Java**, and **SQL**, building backend services, internal tools, and operator-facing platforms for production environments.
* **Distributed Systems Scope:** Delivered **Microservices**, **REST** and **gRPC** APIs, **Kafka** pipelines, **AWS** services, and **Linux** validation workflows for telemetry processing, release safety, and high-volume operational tooling with clear ownership boundaries.
* **Systems Judgment:** Brings cross-functional decision-making experience from platform and data-intensive teams, with working exposure to **CI/CD**, Code Review, and tradeoff analysis across reliability, speed, and operational risk.

## Skills
* **Programming:** Java, C++, Go, Rust, Python, TypeScript, REST, gRPC, Linux
* **Data:** SQL, Hive, Spark SQL, Pandas, ETL, Airflow, A/B Testing, Jupyter, AWS Bedrock, RAG
* **Cloud:** Kafka, AWS, S3, Docker, Kubernetes, PostgreSQL, MySQL, Redis, GitHub Actions, Microservices, CI/CD

## Experience
### Software Engineer Intern | TikTok · Security
*Jun 2025 – Dec 2025 | San Jose, USA*

* Owned an intern-scoped backend surface for security-agent telemetry validation and ingestion, building a **Go** and **gRPC** path in a **Kubernetes** service that checked events before policy actions entered quarantine, reducing false-positive quarantine events by **18%**.
* Built **Java** and **C++** ingestion adapters and a **Rust** parser for signed-agent event payloads, normalizing firmware and process-signing records into **Kafka** and cutting triage preparation time from **42 minutes** to **19 minutes** for incident responders.
* Developed **Python** regression checks against **PostgreSQL** audit tables in **Docker** and **Linux** environments, then wired the owned schema and API contract suite into **GitHub Actions**-based **CI/CD**, raising permission-rule regression coverage by **31%**.
* Improved merge-to-staging safety for the owned service boundary by validating schema and API changes before release, shortening merge-to-staging time by **22%** while reducing rollback risk on security-policy updates.

**Project: Security Knowledge Retrieval Console**
> Separate side project supporting analyst lookup across fragmented investigation playbooks.
* Built a **Go** query endpoint that called a team-maintained **RAG** retriever over **gRPC**, surfacing ranked remediation steps for on-call analysts.
* Implemented a **Java** fallback path that pulled authoritative snippets from **S3** on **AWS** when retriever confidence was low, reducing empty-result cases by **24%**.
* Added a lightweight **TypeScript** console flow for retrieval feedback capture and replay hooks, helping analysts validate ranked results with fewer manual handoffs.
* Wrote **Python** evaluation scripts against **PostgreSQL** feedback logs to compare **AWS Bedrock** prompt templates, improving citation hit rate by **17%** in controlled team tests.

### Senior Data Analyst | DiDi · IBG · Food
*Sep 2022 – May 2024 | Beijing/Mexico*
> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.

* Led weekly Design Review for courier dispatch tooling, translating growth requirements into **Java** **Microservices** and **REST** APIs used by operations teams in **20+ cities** across multiple markets.
* Drove a **Python**, **SQL**, and **ETL** service that consumed **Kafka** events and loaded **MySQL** metrics tables, reducing order-status data lag from **27 minutes** to **9 minutes** for marketplace dashboards.
* Coordinated rollout of **Docker** services with **Redis** caching for restaurant availability rules, lowering peak-time API latency by **33%** on the internal platform.
* Established lightweight Code Review checklists for API schema changes and null-handling paths, cutting production rollback incidents by **21%** over two quarters.
* Represented analytics in backend planning by mapping experiment definitions into **REST** contracts and **SQL** audit queries, improving cross-market release traceability for **8** launch workflows.

**Project: Dispatch Control API Module**
> Backend control layer replacing spreadsheet-based coordination for city-level dispatch exception handling.
* Designed and shipped a **Java** **Microservices** module that exposed courier ETA override controls through **REST** endpoints, replacing spreadsheet-based coordination for city operations.
* Implemented **Kafka** consumers and **MySQL** write paths for assignment events, increasing same-day root-cause coverage from **61%** to **79%** in the internal ops console.
* Added service-side validation and partnered on **TypeScript** operator-facing workflows for dispatch exception handling, improving release readiness for regional rollouts.
* Facilitated Design Review and follow-up Code Review on failure handling and retry logic, helping the service sustain promo-week load without emergency rollback.

### Data Analyst | Temu · R&D
*Jun 2021 – Feb 2022 | Shanghai*

* Built **SQL** and **Hive** analyses in **Jupyter** to track merchant funnel leakage, identifying checkout defects that lifted completed orders by **7.8%** after fix rollout.
* Automated **Airflow** jobs that refreshed **Pandas** datasets from **Spark SQL** aggregates each morning, reducing manual reporting time from **3 hours** to **45 minutes**.
* Evaluated search-ranking changes with **A/B Testing** and **Python** notebooks, improving click-to-order conversion by **5.4%** on the monitored cohort.
* Produced weekly exception views by reconciling **Hive** and **Spark SQL** outputs, improving metric consistency for R&D reviews and giving engineers cleaner handoff inputs.

## Education
### M.S. Computer Science | Georgia Institute of Technology
*Expected May 2026*

## Achievements
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).