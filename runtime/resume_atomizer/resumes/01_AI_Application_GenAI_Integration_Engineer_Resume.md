# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **AI Application & Backend Engineer:** 3+ years of technical experience across high-traffic platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production-grade delivery of **RAG** pipelines, **LLM**-based content classification systems, **AI Agent** workflows, and **Python**/**Java** microservices on **AWS**.
* **End-to-End GenAI Delivery:** Designs and ships enterprise AI systems spanning **Prompt Engineering**, **LangChain**/**LangGraph** orchestration, vector-store retrieval, structured **confidence scoring**, and multi-model routing — integrated into **Spring Boot** services with **CI/CD** automation and **observability** instrumentation.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator translating complex **business requirements** from product, compliance, and stakeholder teams into auditable AI architectures in **Agile** environments.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Project: Policy-Aware Content Classification — RAG Pipeline & AI Agent_**

* Designed and implemented a **Python** **RAG** pipeline using **LangChain** and **Pinecone** vector store, ingesting 200+ internal policy documents with a 512-token sliding-window chunking strategy and per-chunk metadata tagging; achieved an 18% improvement in classification **confidence scores** over the keyword-matching baseline across 4 violation **taxonomy** categories.
* Engineered structured **Prompt Engineering** templates with **Pydantic**-validated JSON output schemas enforcing deterministic **LLM** output — each inference call returns a typed violation classification, calibrated **confidence score**, supporting policy references, and recommended action, eliminating free-text response drift.
* Built a **LangGraph**-based multi-step **AI Agent** workflow routing low-confidence results (< 0.72 threshold) through a secondary cross-taxonomy retrieval step, reducing manual review escalation rate by 12% on a 3,000-case pilot validation set.
* Integrated the RAG classification service as a **REST** endpoint within the **Spring Boot** policy management microservice; P95 end-to-end latency maintained below 300ms under load testing at 500 RPS.

**_Project: Crystal AI (CAI) — Enterprise Privacy Compliance AI Agent Platform_**

* Designed and implemented the AutoDraft field annotation pipeline using **Python** and structured **LLM** inference (DeepSeek R1 primary, GPT-4 fallback) with **Pydantic**-validated JSON output schemas, reducing per-API annotation time from 4–8 days to under 15 minutes for APIs with 1,000+ fields.
* Engineered a dual-layer PreCheck validation engine combining a deterministic rule engine (fast-path covering 80% of common violations) with **LLM** semantic analysis for ambiguous edge cases, reducing compliance ticket rejection rate from >50% to <10% — validated on a 30,000-ticket historical dataset.
* Architected a Sync/Async dual-mode Hooks middleware for **AI Agent** execution control: synchronous hooks intercept tool calls before execution to enforce real-time compliance checks, enabling declarative permission policies and audit logging without modifying agent business logic.
* Built a unified multi-model **LLM** routing layer integrating DeepSeek R1, GPT-4, Claude-3, and OpenRouter with cost-tiered automatic failover, exposed as a **REST API** and instrumented with **OpenTelemetry** distributed tracing (**observability**) to maintain P99 inference latency SLOs across providers.
* Implemented a protocol-agnostic agent deployment layer — the same codebase serves **MCP** (IDE integration), HTTP **REST**, WebSocket streaming, and Lark Bot without protocol-specific modifications — deployed on **Kubernetes** with **Docker**, reducing protocol onboarding overhead by 90%.

**_Infrastructure & Frontend Contributions_**

* Developed **Java**/**Spring Boot** microservices for the policy management API, implementing 6 **REST** endpoints and integrating with upstream **Kafka** event queues for asynchronous policy update propagation.
* Instrumented classification microservices with **OpenTelemetry** and **Datadog** SLO dashboards (**telemetry**), reducing mean incident detection latency from ~45 minutes to under 8 minutes.
* Containerized services with **Docker** and deployed on **AWS EKS** via **Kubernetes** manifests; automated build and release through **GitHub Actions** + **ArgoCD** **CI/CD** pipelines, compressing deployment cycles from 2 days to under 30 minutes.
* Built the internal developer tool portal frontend using **React**, **TypeScript**, and **Next.js**, delivering a responsive version dashboard and binary download hub for the security engineering team.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Led end-to-end data strategy for DiDi Food's Mexico market launch across 5 cities, defining a 47-metric KPI framework adopted as the cross-market reporting standard across 4 international Food markets (**business requirements translation**).
* Engineered **Python** ETL pipelines consolidating 3 internal platforms via **REST API** and batch extraction, reducing monthly reconciliation time from 72 hours to 4 hours.
* Developed incremental **Kafka** event consumers in **Python** to capture real-time order lifecycle events, powering operational dashboards with same-day merchant fulfillment visibility.
* Constructed multi-table **SQL** analytical queries joining order, merchant, and geo data across 6 tables; collaborated cross-functionally with product, engineering, and local operations teams across two time zones (**cross-functional collaboration**).
* Partnered with BI and finance stakeholders to establish data governance standards, resolving 3 conflicting KPI definitions that had caused persistent discrepancies in HQ vs. local reporting (**privacy & compliance**).

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Maintained **Hive**/**Spark SQL** batch jobs processing 50M+ daily user interaction events to generate offline feature datasets consumed by the recommendation model training pipeline.
* Automated weekly experiment summary reporting via **Python** (pandas), eliminating ~6 hours of manual consolidation per analyst per cycle.
* Partnered with algorithm engineers to define 8 standardized offline evaluation metrics for cold-start recommendation quality, supporting a controlled experiment that yielded a 3.2% CTR lift.

---

## Skills

**Languages:** Python, Java, Go, SQL, HiveQL
**AI & GenAI:** LLM, RAG, LangChain, LangGraph, AI Agents, Prompt Engineering, Pydantic, Pinecone, Confidence Scoring, Taxonomy Matching
**Frameworks & Tools:** Spring Boot, FastAPI, React, Next.js, Kafka, OpenTelemetry, Datadog, MCP
**Cloud & Infrastructure:** AWS (EKS, S3), Docker, Kubernetes, ArgoCD, GitHub Actions, CI/CD
**Data:** SQL, MongoDB, HiveQL, Spark SQL, pandas

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