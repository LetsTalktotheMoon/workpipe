# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Generalist Software Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery in **Java**, **Python**, **C++**, and **Go** spanning backend **web services**, **distributed systems**, data pipeline automation, and **cloud-native** development on **AWS**.
* **End-to-End Engineering Delivery:** Owns features through the complete SDLC — from **Object-Oriented Design**, **RESTful**/**gRPC** API development, and **SQL** **database** schema design to **Docker**/**Kubernetes** containerization, **CI/CD** pipeline automation, and **Agile/Scrum** sprint delivery. Strong foundation in **data structures**, **algorithms**, and **multi-threaded** systems.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**. Effective cross-functional collaborator with strong **ownership** and growth mindset.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Backend Engineering Contributions:_**

* Implemented **RESTful** and **gRPC** API endpoints in **Java** (**Spring Boot**) within the **Security** Platform microservice architecture, enabling downstream enforcement pipelines to query and update policy metadata at 50M+ daily events with P99 latency under 45ms (**web services**).
* Developed a **Kafka** consumer service in **Python** subscribing to 4 upstream **security** event topics, applying configurable rule-based filtering with bloom-filter deduplication and persisting structured records to **PostgreSQL**; achieved end-to-end latency under 200ms at production load.
* Built a **multi-threaded** **C++** log-processing utility using POSIX threads on **Linux** to parse and index 2TB+ of daily audit logs, enabling sub-second historical lookups for on-call incident triage; reduced mean investigation time by 35%.
* Containerized three microservices with **Docker** and authored **Kubernetes** manifests on **AWS** ECS/EC2, supporting horizontal auto-scaling; P99 service latency reduced 18% under 3× baseline simulation.
* Contributed to **CI/CD** pipeline automation via **GitHub Actions**, implementing integration test gates and zero-downtime canary deployments that compressed update cycles from two weeks to two days.
* Participated in 5 Design Reviews and 30+ Code Reviews within **Agile/Scrum** sprint ceremonies; contributed interface proposals for a shared rate-limiting library adopted across 4 sub-teams (**ownership**).

**_Project: Unified Data Compliance Control Plane_**

* Designed and implemented a bidirectional schema translation engine in **Go** using the visitor pattern to achieve lossless conversion across 6 gateway formats; completed migration of 1.2M+ legacy schema entries with zero-downtime parallel rollout (**distributed systems**).
* Implemented a distributed compliance workflow state machine in **Go** managing 10+ state transitions with **MongoDB** optimistic locking for concurrent-write atomicity; reduced approval cycle from 7 days to 2 days at 5× throughput.
* Deployed the platform on **Kubernetes** with **gRPC** + **RESTful** dual-protocol services, JWT authentication, **Kafka** event streaming, and **Redis** caching; replaced 3 legacy systems across GDPR- and CCPA-regulated data flows (**security**, **cloud services**).

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Owned end-to-end analytical coverage for DiDi Food's Mexico operations; designed a normalized **PostgreSQL** reporting schema tracking order-funnel KPIs across 12 city-level markets as the authoritative data source (**databases**, **SQL**).
* Built **Python** ETL pipelines consuming **RESTful API** endpoints from third-party logistics providers, normalizing heterogeneous JSON payloads into a unified warehouse schema on a 30-minute automated refresh cycle; eliminated a 48-hour manual export process.
* Developed a **Python** anomaly detection module monitoring 9 operational KPIs with configurable alert thresholds; automated notifications reduced median P1 incident response time from 47 minutes to under 9 minutes.
* Performed latency root-cause analysis on the **C++** dispatch engine by profiling hot paths in collaboration with the engineering team; findings contributed to a 12% reduction in median dispatch latency.
* Collaborated across Beijing HQ and Mexico City in bi-weekly **Agile/Scrum** review cycles, translating regional constraints into quantified KPI targets; all work managed via **Git** branching workflows with peer code review.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Extracted and aggregated product-level behavioral data from **MySQL** **databases** via parameterized **SQL** queries, generating weekly algorithm performance dashboards and eliminating ~4 hours of manual compilation per cycle.
* Developed **Python** automation scripts to batch-process 500K+ daily raw user event logs with rule-based deduplication and feature normalization; reduced pre-processing error rates from ~15% to under 3%.
* Designed a lightweight **Python** class hierarchy encapsulating extraction, transformation, and validation logic into reusable **OOD** modules, enabling the team to onboard new experiment pipelines without rewriting boilerplate.
* Maintained all pipeline scripts under **Git** version control with documented commit history, establishing the team's first reproducible codebase for experiment data preparation.

---

## Skills

**Languages:** Java, Python, C++, Go, C#, JavaScript, SQL
**Backend:** Spring Boot, RESTful APIs, gRPC, Protobuf, Kafka, Redis, PostgreSQL, MongoDB, MySQL
**Cloud & DevOps:** AWS (ECS, EC2, S3), Docker, Kubernetes, GitHub Actions, CI/CD, Git
**Engineering Practices:** Object-Oriented Design, Data Structures & Algorithms, Distributed Systems, Agile/Scrum
**Systems:** Linux, Multi-threaded Programming (POSIX), Operating Systems, Networking, Security, Databases

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