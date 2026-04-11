# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Production ML/AI Engineer:** 3+ years of technical experience across high-scale consumer platforms (**TikTok**, **DiDi**, **Temu**), with end-to-end ownership spanning **feature engineering**, **deep learning** model development, **NLP**/**LLM** systems, **recommender system** infrastructure, and cloud-native **model serving** and **MLOps**.
* **Research-to-Production Delivery:** Ships ML systems from prototype to production — from **C++** inference optimization and **RAG** pipeline development to **distributed** data processing on **GCP**, with rigorous **model evaluation** and staged rollout discipline.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Effective cross-functional collaborator bridging data science, ML engineering, product, and operations teams in **Agile** environments to deliver measurable **business impact**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core ML Infrastructure Contributions_**

* Refactored the **Java**-based security event ingestion service to resolve a **Kafka** consumer group partition imbalance, increasing peak throughput from ~980K to 1.2M+ signals/hour.
* Containerized ML **model serving** endpoints using **Docker** (multi-stage builds) and deployed via **Kubernetes** (**GKE**) with HPA and liveness/readiness probes, sustaining 99.95% availability over the 6-month internship.
* Instrumented **Kubeflow** Pipeline retraining triggers monitoring distributional shift across 12 input feature dimensions, activated when KL-divergence exceeded a configurable drift threshold.

**_Project: LLM Security Threat Classifier — Inference Optimization & RAG_**

* Implemented a **C++** preprocessing module for the Security Platform's **LLM**-based threat classifier, applying batch tokenization and cache-aligned memory layout optimizations; exposed to the **Python** inference stack via **pybind11**, reducing per-request P99 latency from 280ms to 193ms (31% reduction) at 10K QPS with zero changes to downstream callers.
* Built a **RAG** pipeline in **Python** using **Hugging Face** sentence-transformers and **GCP Vertex AI**, dynamically injecting relevant threat intelligence context into the **LLM** at inference time; improved security threat detection recall by 14.2% on a 50K-sample evaluation benchmark.
* Authored a **Synthetic Data Generation** pipeline (**Python** + GPT-4 API + rule-based augmentation) producing 200K labeled training examples across 4 underrepresented threat categories, improving minority-class macro F1 by 9.7% and reducing estimated annotation cost by ~$120K annually.
* Executed staged production rollout (1% → 10% → 50% → 100% traffic over 3 weeks), monitoring latency percentiles and classification accuracy via **GCP Cloud Monitoring** dashboards; rollout completed with zero SLA breaches.

**_Project: Enterprise AI Compliance Platform — Multi-Model Orchestration & MLOps_**

* Architected a unified **LLM** multi-model routing layer in **Python** integrating GPT-4, Claude-3, and open-source models via **Hugging Face** with automatic provider failover and cost-tier dispatch; achieved 99.9% call availability at <3s P99 response time across 20K+ daily inference requests.
* Built a dual-layer validation framework: a deterministic rule engine covering 80% of policy violations at <50ms, combined with **LLM** semantic analysis for ambiguous edge cases; reduced compliance ticket rejection rate from 52% to 9%.
* Instrumented end-to-end **MLOps** observability via **GCP Cloud Monitoring** and **MLflow**, tracking per-provider **LLM** response drift and annotation agreement rates across weekly cohorts; configured automated alerts triggering **model evaluation** workflows when validation metrics dropped below threshold.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Diagnosed feature staleness in real-time driver supply signals feeding DiDi Food's dispatch **ranking** model; collaborated with ML engineering to implement a **Flink**-based 5-minute micro-batch feature refresh cycle, reducing delivery ETA prediction RMSE by 8.3% (**feature engineering**).
* Applied **NLP** techniques — TF-IDF and **BERT** sentence embeddings (**Hugging Face**, **Python**) — to 500K+ Spanish-language restaurant reviews to derive cuisine preference clusters; cluster labels incorporated as **ranking** features improved restaurant carousel CTR by 11% in targeted cohorts.
* Built an automated anomaly detection system using **PyTorch** LSTM for seasonality modeling, reducing mean time-to-detect operational degradation from 47 minutes to under 9 minutes.
* Engineered a **Python** ETL pipeline consolidating 4 heterogeneous data sources into a unified analytical feature table (**GCP BigQuery**), reducing **data pipeline** preparation latency from ~3 hours to 40 minutes.
* Established **MLflow** experiment tracking for 3 dispatch **ranking** model iterations, enabling documented rollback when a model version increased P90 ETA by 6% in shadow testing (**model evaluation**).
* Designed and executed pricing elasticity A/B experiments across 3 Mexico market segments using difference-in-differences (**Python** + **BigQuery**), delivering inputs that supported a 7% GMV uplift (**business impact**).

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Queried multi-terabyte user behavior event logs via **HiveSQL** and **SparkSQL** to extract input signals for the **recommender system** feature store, supporting **feature engineering** iterations for the ranking pipeline.
* Built a prototype new-user LTV propensity scoring model in **Python** (**scikit-learn**: gradient boosting + logistic regression baseline) on 120K labeled records, achieving 9% offline lift in Day-7 retention over rule-based segmentation; presented as a cold-start strategy reference to the algorithm team (**research-to-production**).
* Monitored batch ETL pipelines ingesting events from **Kafka** into the recommendation feature store; identified a schema drift issue causing 14-day feature staleness in 3 item embedding dimensions, confirmed by engineering as a **ranking** quality regression cause.
* Automated daily A/B test performance reports for 8 **recommendation** experiments using **Python** (pandas, matplotlib), eliminating ~6 hours/week of manual reporting.

---

## Skills

**Languages:** Python, C++, Java, SQL, HiveSQL, SparkSQL
**ML & AI:** PyTorch, scikit-learn, Hugging Face, Deep Learning, LLM, RAG, Generative AI, Synthetic Data Generation, NLP/BERT, Recommender Systems, Ranking/Personalization, Model Serving, Model Evaluation
**MLOps & Infra:** Kubeflow, MLflow, Vertex AI, GCP Cloud Monitoring, Docker, Kubernetes (GKE), Data Pipelines, Distributed Computing
**Data & Streaming:** BigQuery, Kafka, Flink, Hive, Spark, pandas
**Cloud:** GCP (Vertex AI, BigQuery, GKE, Cloud Monitoring), AWS

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