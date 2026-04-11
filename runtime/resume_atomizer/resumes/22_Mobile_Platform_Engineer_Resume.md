# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Mobile-Facing Backend & SDK Engineer:** 3+ years of technical experience across high-traffic platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with direct involvement in **Android SDK** backend services, on-device **performance optimization**, and **mobile event instrumentation** at scale.
* **End-to-End Delivery Across the Mobile Stack:** Builds and optimizes **Kotlin**/**Java** services that power **Android** client experiences — from low-latency **REST API** design and **Protocol Buffer** serialization to on-device **memory management** profiling and **Mobile CI/CD** pipeline automation via **Gradle** and **Jenkins**.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator bridging backend, **Android** client, product, and data teams in **Agile** sprint environments.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

*The Security Infra team owns both the server-side policy engine and the on-device Android Security SDK distributed to 500K+ concurrent sessions.*

**_Project: Android Security SDK — Backend Services & API Optimization_**

* Developed and maintained **Kotlin**-based backend microservices powering the **Android** Security SDK, structuring service-layer contracts to mirror the client's **MVVM** separation of concerns and preserve API compatibility across SDK versions.
* Optimized three high-frequency **REST API** endpoints serving the **Android SDK** client, reducing P99 latency from 340ms to 118ms through **Protocol Buffer** payload compression, connection pool tuning, and **Redis**-backed result caching — bringing all three endpoints within the 150ms SLA for the first time.
* Implemented memory-efficient batch ingestion logic in **Java** to handle concurrent security event streams from 500K+ simultaneous **Android** sessions, reducing GC pause frequency by 41% under sustained load-test conditions.
* Integrated **Jetpack**-compatible **Protocol Buffer** serialization schemas into the backend response layer, enabling the **Android SDK** team to adopt **Room**-persisted local caching without breaking existing API contracts.

**_Project: Android Security SDK — On-Device Performance & CI/CD_**

* Profiled the Security SDK's on-device threat detection module using **Android Studio** **Memory Profiler**, identifying and resolving 2 Context-reference memory leaks responsible for ANR events on devices with ≤2GB RAM.
* Authored **Gradle** build configurations and added automated unit test coverage (87% line coverage) to two previously untested service modules, integrated into the team's **Mobile CI/CD** pipeline via **Jenkins**.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

**_Mobile Event Instrumentation & Analytics_**

* Led mobile event instrumentation design with the Mexico City product and **Android** engineering teams, defining a 40+ event taxonomy spanning app launch, order acceptance, route navigation, and earnings review flows; the resulting **Android SDK** tracking schema was adopted as the canonical spec across 3 Latin America markets.
* Wrote **SQL**-based post-release data quality validation queries to audit incoming **Android** event streams against the defined schema, identifying 3 structural mismatches that would have invalidated 2 months of A/B test results; lifted event coverage of critical user flows from 34% to 89% within 2 sprint cycles.

**_Data Engineering & Operations_**

* Owned end-to-end analytics for the Latin America food delivery vertical, maintaining **SQL** reporting pipelines that processed 500K+ daily order records across a distributed multi-region data warehouse.
* Engineered a **Java**-based batch automation tool to reconcile driver payout discrepancies across 6 currency regions, replacing a 16-FTE-hour weekly manual process with 99.2% first-pass accuracy.
* Consumed and documented **RESTful APIs** from the backend engineering team to integrate real-time delivery ETA signals into operational dashboards, enabling ops managers to surface SLA breach risks 20 minutes earlier.
* Optimized 30+ cross-regional **SQL** queries through index tuning and partition pruning, reducing average execution time from 8 minutes to under 90 seconds.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Partnered with recommendation engineers to define behavioral event schemas for mobile click tracking, mapping tap depth, scroll velocity, and session duration to feature variables consumed by the upstream ranking model.
* Built a **Python** automation script consuming the internal data lake's **REST APIs** to replace a manual daily log extraction process, cutting analyst reporting time from 4 hours to 45 minutes per day.
* Maintained a **SQL** query library in **Git** for cross-team reuse, standardizing version-controlled definitions for 20+ recurring business metrics.

---

## Skills

**Languages:** Kotlin, Java, Python, SQL
**Mobile & Android:** Android SDK, Android Studio, Memory Profiler, Jetpack (DataStore, Room), MVVM
**APIs & Serialization:** RESTful APIs, Protocol Buffers, JSON
**Infrastructure & DevOps:** Redis, Docker, Kubernetes, Jenkins, Gradle, Mobile CI/CD, Git
**Performance:** Latency Profiling, GC Tuning, Memory Management, Load Testing

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