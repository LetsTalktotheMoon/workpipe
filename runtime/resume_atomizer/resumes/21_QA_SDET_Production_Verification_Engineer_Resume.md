# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **QA & Production Verification Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **test automation frameworks** (**Pytest**, **Selenium**, **Appium**), **mobile testing** (**iOS**/**Android**), **C#**/**Unity Engine** verification, and **Python**-based **QA** tooling. Production delivery spanning security event pipeline validation, cross-platform build verification, and data pipeline quality engineering.
* **End-to-End Verification Delivery:** Designs and ships **automated test frameworks** — from schema-driven parameterized test generation and **regression testing** suites to **profiling**/**performance optimization**, **multithreaded** codebase validation, and **CI/CD**/**build automation** pipeline integration across the full **SDLC**.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator bridging engineering, product, and operations teams, with a track record of **technical consulting** on quality assurance standards and data reliability.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core QA Infrastructure Contributions:_**

* Authored **test plans** with risk-based prioritization, coverage analysis, and exit criteria for each microservice release; implemented shift-left **QA** practices across the **SDLC** by participating in requirements reviews and release readiness assessments, reducing post-release severity-1 defect rate by 60%.
* Executed **functional testing** and **regression testing** of backend microservice API contracts (**gRPC** and REST endpoints), validating schema conformance, error-handling behavior, and boundary conditions across 180+ test cases; achieved 94% code-path coverage and identified 23 contract-level defects prior to production deployment.
* Performed **profiling** and **performance optimization** of the event ingestion pipeline: CPU/memory profiling (cProfile, Linux perf) identified 3 hot-path bottlenecks; GC tuning and connection pool resizing reduced P99 latency from 320ms to under 180ms; thread-safety verification of **multithreaded** event-processing code eliminated 2 concurrency defects.

**_Project: Automated Test Framework for Security Event Pipeline_**

* Designed and implemented a modular **Python** (**Pytest** + custom plugin architecture) **automated test framework** for end-to-end verification of a security event ingestion pipeline processing ~50M daily events across 15+ upstream services; schema-driven test generator parsed OpenAPI and Protobuf definitions at runtime to emit parameterized test cases automatically, eliminating hand-authored boilerplate.
* Engineered a custom parallel executor distributing 180+ **functional** and **regression test** cases across 8 worker threads, with structured JSON result aggregation piped into **GitHub Actions** **CI/CD** quality gates enforcing ≥94% pass rate per pull request.
* Containerized the full execution environment in **Docker** and implemented **build automation** via **GitHub Actions**: every pull request triggered a sequential gate pipeline (lint → unit test → integration test → contract test → performance regression check) with a zero-skip policy on P0 failures.

**_Project: Mobile & Unity Platform Verification Suite_**

* Built **C#** unit and integration test suites within the **Unity Engine**/**Unity Editor** environment for a cross-platform security visualization dashboard — play-mode harnesses validated rendering correctness and data-binding behavior across 85+ test cases; Editor build-verification scripts confirmed successful **build automation** for **iOS** and **Android** target platforms.
* Implemented **Appium**-based **mobile testing** suites with **XCUITest** (**iOS**) and **Espresso** (**Android**) to verify security-feature behavior (biometric authentication, session timeout enforcement, permission-gating UI) across 6 device and emulator configurations, integrated into **CI/CD** for automated nightly execution.
* Performed **performance profiling** using **Unity** Profiler (frame-time analysis, draw-call batching, texture memory consumption); optimized render pipeline reducing average frame time from 22ms to under 12ms on target mobile hardware. Conducted heap snapshot analysis identifying 2 memory leaks, remediated via explicit asset unloading with fix validation enforced through automated memory regression assertions.
* Enforced a quality gate policy requiring zero P0 test failure on any release candidate throughout the 5-month deployment window, achieving zero authentication-related defect escapes into production.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Owned and operated **Pytest**-based **automated test frameworks** validating data pipeline outputs for the Mexico Food vertical — covering 40+ canonical metric definitions across 8 city markets, executed against **AWS** Redshift and **Spark** engines with **regression testing** gates that blocked 6 metric-breaking changes from reaching production.
* Created formal **test plans** with full traceability matrices mapping business requirements to test cases, defining risk-based prioritization, coverage targets, and exit criteria aligned with **SDLC** milestones; reduced post-release defect escape rate by ~40%.
* Built **Appium**-based **mobile testing** smoke suites for DiDi Food rider and consumer applications on **iOS** and **Android** across Mexico market builds, verifying critical user flows and surfacing 12 region-specific UI/functional defects prior to market launch.
* Integrated **Pytest** suites and linting checks into the **GitLab CI**/**CD** pipeline (**build automation**), enforcing automated quality gates (unit test pass rate ≥98%, schema validation, metric output diff ≤0.5%) before merge approval; containerized the full test execution environment in **Docker**.
* **Profiled** Redshift query execution plans and Airflow DAG parallelism settings, reducing end-to-end pipeline execution time by 45%; debugged **multithreaded** race conditions in concurrent DAG task execution that caused intermittent data duplication.
* Provided **technical consulting** to the 50-person Mexico regional operations team on data **quality assurance** standards, dashboard reliability expectations, and incident escalation procedures; authored the team's data quality handbook adopted as the onboarding reference.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Developed **Python**-based automated data validation scripts to verify recommendation model A/B experiment outputs against acceptance thresholds on a **Spark**-backed data lake with 1B+ rows, reducing data quality **regression** detection from a 2-day manual cycle to within hours.
* Authored and optimized **SparkSQL**/**HiveQL** queries for **functional testing** of metric computation correctness (CTR, conversion rate, latency percentiles) across experiment cohorts, establishing a reusable query library of 11 validated templates as the team's canonical **regression testing** baseline.
* Conducted structured root cause analysis on recurring metric anomalies (population drift, logging pipeline skew, null-rate spikes), documenting reproducible investigation procedures that reduced repeat incident investigations by ~35%.
* Standardized all validation scripts and **SQL** templates under a shared **GitLab** repository with tagged releases, operating within the team's Agile **SDLC** sprint cadence and establishing groundwork for **CI/CD** integration of automated quality checks.

---

## Skills

**Languages:** Python, C#, SQL, SparkSQL, HiveQL
**Test Automation:** Pytest, Appium, XCUITest, Espresso, Selenium, Unity Test Framework
**QA & Verification:** Test Planning, Functional Testing, Regression Testing, Performance Profiling, SDLC, Technical Consulting
**Platforms:** iOS, Android, Unity Engine/Editor, Linux
**DevOps:** GitHub Actions, GitLab CI, Docker, Build Automation, CI/CD

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