## MODULE 1 — Professional Summary

> *3 sentences. No transition narrative. Direct value statement only.*

ML/AI engineer and applied researcher with 3+ years of production experience across high-scale consumer platforms (Temu, Didi, TikTok), currently pursuing dual graduate degrees at the University of Illinois Urbana-Champaign (MSIM) and Georgia Tech (OMSCS) with specialization in machine learning systems and distributed computing. Combines a rigorous interdisciplinary foundation in behavioral science and quantitative modeling with end-to-end ML lifecycle ownership spanning feature engineering, deep learning model development, distributed data infrastructure, and cloud-native model serving and MLOps. Demonstrated track record of translating large-scale, ambiguous behavioral signals and unstructured multilingual data into production-grade ranking, personalization, and content safety systems—delivering measurable improvements in model latency, prediction accuracy, and core business KPIs across international markets.

---

## MODULE 2 — Technology Stack Snowball Distribution Map

> *Escalation axis: ad hoc script → analytical system → production ML infrastructure.*

| Technology / Skill Cluster | **Temu** (DA, Jun 2021 – Feb 2022) | **Didi IBG** (Senior DA, Sep 2022 – May 2024) | **TikTok Safety** (SWE Intern, Jun 2025 – Dec 2025) |
|---|---|---|---|
| **Python** | Automation scripting; pandas/matplotlib for reporting | Complex ETL orchestration; ML modeling (statsmodels, PyTorch LSTM) | Production backend services; pipeline engineering; RAG orchestration |
| **SQL** (HiveSQL / SparkSQL / BigQuery) | Ad hoc event log queries | Multi-source complex joins; experiment analysis (BigQuery) | — |
| **Machine Learning** | Offline propensity scoring prototype (scikit-learn) | Production ranking feature analysis; NLP clustering | LLM fine-tuning; RAG; safety classifier evaluation |
| **Recommender Systems / Ranking** | Feature QA in recall & ranking pipeline | Dispatch ranking signal analysis & optimization | — |
| **Deep Learning / PyTorch** | — (scikit-learn only) | PyTorch LSTM (anomaly detection baseline) | LLM inference optimization; Vertex AI distributed training |
| **NLP / Hugging Face** | — | BERT sentence embeddings (multilingual-BERT) for review clustering | Fine-tuned LLM classifier; RAG retrieval; sentence-transformers |
| **LLM / Generative AI / RAG** | — | — | RAG pipeline (Vertex AI + Hugging Face); GPT-4 Synthetic Data Generation |
| **Synthetic Data Generation** | — | — | 200K-sample pipeline (GPT-4 API + rule-based augmentation) |
| **Distributed Computing / Flink / Kafka** | Kafka topic monitoring (passive QA) | Flink streaming pipeline (real-time feature refresh); Kafka ingestion | Kafka consumer throughput refactoring (Java) |
| **Data Pipelines / ETL** | Batch pipeline QA & monitoring | Python ETL pipeline (4 heterogeneous sources → BigQuery) | Kubeflow automated retraining pipeline |
| **MLOps / MLflow / Kubeflow** | — | MLflow experiment tracking; artifact management | Kubeflow Pipelines; automated drift-triggered retraining |
| **Model Serving / Model Deployment** | — | — | Docker + GKE model serving; rolling deployment |
| **Docker / Kubernetes** | — | Docker (basic containerization exposure) | Docker multi-stage builds; GKE Deployment; HPA config |
| **AWS / GCP** | — | GCP BigQuery; GCP data infrastructure | GCP Vertex AI; GKE; Cloud Monitoring; Vector Index |
| **C++ / Java** | — | — | C++ preprocessing microservice (pybind11); Java Kafka consumer refactor |
| **Model Evaluation / Model Monitoring** | Recall/precision reporting (manual) | Anomaly detection dashboards; shadow testing analysis | 12-dimension drift monitoring; KL-divergence threshold alerting |
| **scikit-learn** | Logistic regression + GBM prototype | PCA; K-means clustering | — |
| **Computer Vision** | — | — | *(Implicit: content safety scope covers visual modality signals)* |

**Snowball core (≥ 2 positions, accumulating depth):**
`Python` · `SQL` · `Machine Learning` · `Recommender Systems / Ranking` · `Distributed Data Infrastructure` · `NLP` · `GCP` · `Model Evaluation`

**Deep technology (introduced mid-career, production-grade at TikTok):**
`PyTorch` · `Hugging Face` · `LLM` · `RAG` · `MLOps / Kubeflow` · `Docker / Kubernetes` · `C++ / Java`

---

## MODULE 3 — Resume Bullet Points

---

### Temu · Recommendation Algorithm Data Analyst
**Jun 2021 – Feb 2022 | Shanghai**

> *Role calibration: Entry-level IC; business-driven analytics supporting the recommendation algorithm team. Technical scope is limited to reporting, scripting, and data pipeline QA—no independent model ownership or deployment authority.*

- Automated daily A/B test performance reports for 8 product-vertical recommendation experiments using Python (pandas, matplotlib), eliminating approximately 6 hrs/week of manual analyst reporting across the team.
- Queried multi-terabyte user behavior event logs (click, dwell time, add-to-cart, purchase) via HiveSQL and SparkSQL to extract input signals for the upstream item recall and ranking pipeline feature store, supporting feature engineering iterations by the algorithm team.
- Monitored batch ETL pipelines ingesting raw behavioral event logs from Kafka topics into the recommendation feature store; identified and escalated a schema drift issue that had introduced 14-day feature staleness in 3 item embedding dimensions, subsequently confirmed by engineering as a ranking quality regression cause.
- Built a prototype new-user LTV propensity scoring model in Python (scikit-learn: gradient boosting + logistic regression baseline) on 120K labeled user records, achieving a 9% offline lift in Day-7 retention over the existing rule-based segmentation; presented findings to the algorithm team as a cold-start strategy design reference.
- Produced weekly recall and precision measurement reports for the recommendation system, coordinating with algorithm engineers to surface cold-start item underperformance and generating targeted SQL analyses to isolate contributing feature categories.

---

### Didi IBG · Senior Data Analyst, Food Business
**Sep 2022 – May 2024 | Beijing / Mexico City**

> *Role calibration: Senior IC; end-to-end analytical ownership of international food delivery market strategy. Interfaced closely with ML engineering on feature analysis and experiment design—no independent model training or production deployment authority.*

- Diagnosed feature staleness in real-time driver supply signals feeding Didi Food's dispatch ranking model across Mexico City and Guadalajara markets; collaborated with ML engineering to implement a Flink-based 5-minute micro-batch feature refresh cycle, reducing delivery ETA prediction RMSE by **8.3%** and improving on-time delivery rate by **4.1 percentage points**.
- Engineered a Python ETL pipeline consolidating 4 heterogeneous data sources—GPS telemetry streams, order lifecycle events, restaurant POS exports, and user review text—into a unified analytical feature table (GCP BigQuery), reducing data preparation latency from ~3 hrs to **40 minutes**.
- Designed and executed pricing elasticity A/B experiments across 3 Mexico market segments using a difference-in-differences framework (Python + BigQuery + statsmodels), delivering quantitative inputs that supported a pricing strategy revision estimated at **7% GMV uplift** in Q3 2023.
- Applied NLP techniques—TF-IDF and BERT sentence embeddings (Hugging Face multilingual-BERT, Python)—to **500K+** Spanish-language restaurant reviews to derive cuisine preference clusters; collaborated with the recommendation team to incorporate cluster labels as carousel ranking features, improving restaurant carousel CTR by **11%** in targeted cohorts.
- Built an automated anomaly detection system for real-time order fulfillment KPIs using Python (statsmodels + PyTorch LSTM for seasonality modeling), reducing mean time-to-detect operational degradation events from **47 minutes to under 9 minutes**.
- Established MLflow experiment tracking for 3 consecutive dispatch ranking model iterations in partnership with ML engineers, creating standardized artifact logging and enabling a documented, clean rollback when a new model version increased P90 ETA by **6%** in shadow testing.

---

### TikTok Safety · Backend Software Engineer, Intern
**Jun 2025 – Dec 2025 | San Jose, CA**

> *Role calibration: SWE intern embedded in content safety infrastructure team. Contributions to production systems executed under senior engineer code review and staged rollout protocol.*

- Implemented a C++ preprocessing microservice for TikTok's LLM-based content policy violation classifier, applying batch tokenization and cache-aligned memory layout optimizations that reduced per-request P99 inference latency from **280ms to 193ms (31% reduction)** at 10K QPS under load testing.
- Built a RAG (Retrieval-Augmented Generation) pipeline in Python using Hugging Face sentence-transformers and GCP Vertex AI to dynamically inject relevant policy document context into the LLM safety classifier at inference time, improving nuanced policy violation recall by **14.2%** on a **50K-sample** evaluation benchmark (combined synthetic and human-labeled).
- Authored a Synthetic Data Generation pipeline (Python + GPT-4 API + rule-based augmentation) producing **200K** labeled training examples across 4 underrepresented safety violation categories, improving minority-class macro F1 by **9.7%** and reducing human annotation dependency estimated at **~$120K** annualized labeling cost.
- Containerized 3 ML model serving endpoints using Docker (multi-stage builds) and deployed via Kubernetes (GKE), configuring rolling update strategy and liveness/readiness probes that sustained **99.95% endpoint availability** over the 6-month internship.
- Designed and instrumented model monitoring dashboards (GCP Cloud Monitoring + Python) tracking distributional shift across **12 input feature dimensions** for production safety models; configured automated Kubeflow Pipeline retraining triggers activated when KL-divergence on monitored features exceeded a configurable drift threshold.
- Refactored the Java-based safety event ingestion service to resolve a Kafka consumer group partition imbalance, increasing peak message throughput from ~980K to **1.2M+ safety signals/hour** and eliminating consumer lag spikes during peak traffic windows.

---

## MODULE 4 — Key Projects

---

### ⬛ Temu (Jun 2021 – Feb 2022)

---

#### Project 1: Recommendation Feature Store Health Monitoring & Drift QA Automation

*The recommendation team had no systematic mechanism to detect feature staleness or schema inconsistencies in the batch pipelines feeding item embeddings and ranking signals into production—issues were typically surfaced only after model performance metrics visibly regressed, resulting in multi-hour ad hoc debugging cycles.*

- Mapped the end-to-end feature ingestion flow from Kafka topic producers through HiveSQL batch transformations into the recommendation feature store, identifying 11 pipeline stages where schema changes could propagate silently without alerting.
- Developed a Python (pandas + HiveSQL) feature validation script executed on each daily batch pipeline completion, cross-checking feature cardinality, null rates, and value range distributions against a rolling 7-day historical baseline snapshot.
- Detected a previously unnoticed 14-day feature staleness condition in 3 item embedding dimensions caused by an upstream schema rename; escalated to the algorithm engineering team, which confirmed the issue had coincided with a measurable dip in recommendation recall metrics during the affected window.
- Reduced schema-drift-related pipeline debugging from multi-hour ad hoc investigations to an automated daily digest report, with findings consumed by 2 algorithm engineers as a first-line data health signal; the QA pattern was subsequently adopted as a team-level standard practice.
- Documented the failure mode taxonomy (schema drift, null propagation, partition skew) in an internal runbook, establishing institutional knowledge for future pipeline debugging.

---

#### Project 2: New User LTV Propensity Scoring Prototype

*Cold-start users received identical push notification content regardless of behavioral signals available from their first session, limiting relevance of early-stage engagement interventions; the team had no quantitative model to segment new users by predicted downstream value.*

- Extracted **23 first-session behavioral features** (click sequence entropy, category dwell time, add-to-cart events, search query count) from HiveSQL queries on multi-TB raw event logs, constructing a labeled training dataset of **120K users** with 7-day purchase conversion as the ground truth label.
- Trained a gradient boosting classifier and logistic regression baseline in Python (scikit-learn), performing 5-fold cross-validated feature importance analysis to identify the top-8 signals predictive of 7-day LTV; add-to-cart event count and cross-category navigation depth ranked as the two highest-importance features.
- Achieved a **9% offline lift in Day-7 retention rate** on a 20% holdout set versus the existing rule-based segmentation baseline (AUC: 0.74 vs. 0.61); analysis surface area and model limitations clearly scoped and documented in the findings deck.
- Presented methodology and findings to the algorithm team as a cold-start strategy design reference; model was not promoted to production during the author's Temu tenure but directly informed the team's subsequent cold-start feature engineering roadmap discussion.

---

### ⬛ Didi IBG (Sep 2022 – May 2024)

---

#### Project 1: Mexico Market Dispatch Ranking Feature Staleness Remediation

*Didi Food's dispatch ranking model in Mexico exhibited degraded ETA prediction accuracy during peak demand windows—manifesting as elevated late-delivery rates and user cancellations—with no prior root cause diagnosis or attribution to a specific upstream data issue.*

- Conducted systematic feature drift analysis across **34 dispatch ranking model input features** using Python (pandas, scipy), isolating driver supply availability signals operating on a 30-minute batch refresh cycle as the primary source of staleness-induced prediction error during peak demand, where driver availability changed materially within the batch window.
- Partnered with ML engineering to design and validate a Flink streaming pipeline updating driver supply features on a **5-minute micro-batch interval**; authored Python preprocessing validation scripts and conducted 90-day historical backfill testing to confirm data quality before production instrumentation.
- Quantified model impact via a controlled shadow testing period (4 weeks, 20% production traffic): ETA RMSE improved by **8.3%** and on-time delivery rate increased by **4.1 percentage points**, providing the documented business case for engineering team prioritization of the full production rollout.
- Designed the post-launch monitoring framework—GCP BigQuery dashboards + Python alerting scripts—tracking feature freshness SLAs (p95 feature age < 6 min) and ETA accuracy trends on a weekly basis, establishing ongoing observability for the ranking team's feature health.

---

#### Project 2: Multilingual Review-Driven Cuisine Affinity Personalization Engine

*Restaurant recommendation carousels in the Mexico market were ranked primarily by historical GMV and aggregate order volume, with no user-level cuisine preference signals derived from qualitative feedback—limiting personalization depth for users with sparse order history and creating a cold-start bottleneck for restaurant carousel relevance.*

- Ingested and preprocessed **500K+** Spanish-language restaurant reviews from the operational data warehouse (GCP BigQuery), applying Python-based text normalization (lowercasing, stopword removal, accent normalization) and language-specific tokenization as preprocessing for embedding generation.
- Generated sentence-level embeddings via Hugging Face multilingual-BERT, reduced to 32-dimensional cuisine affinity vectors via PCA (scikit-learn), and applied K-means clustering with silhouette analysis to identify **12 statistically stable cuisine preference archetypes** across the Mexico user base.
- Mapped users to cuisine archetypes using their review history and delivered cluster label assignments to the recommendation engineering team as a new carousel re-ranking feature; an A/B test on a **10% traffic allocation** over 3 weeks demonstrated an **11% CTR lift** on restaurant carousels for users with ≥2 archetype signals assigned.
- Documented the full end-to-end pipeline methodology (preprocessing → embedding → clustering → label export → A/B evaluation) in an internal technical wiki, enabling the recommendation team to re-execute the clustering pipeline quarterly against updated review data without re-engagement from the data team.

---

### ⬛ TikTok Safety (Jun 2025 – Dec 2025)

---

#### Project 1: High-Throughput LLM Safety Classifier Serving Latency Optimization

*TikTok's LLM-based content policy violation classifier operated at P99 latency of ~280ms per request, exceeding the real-time content pre-screening SLA of 220ms at 10K QPS—blocking adoption of the classifier in latency-sensitive content ingestion pathways without backend infrastructure redesign.*

- Profiled the existing Python-based serving microservice under simulated 10K QPS load using cProfile and system-level perf tooling, identifying synchronous tokenization and preprocessing I/O as the primary bottlenecks accounting for **58%** of end-to-end request latency.
- Re-implemented the preprocessing module in **C++**, incorporating batch tokenization, cache-aligned memory buffers, and SIMD-optimized Unicode normalization; exposed the compiled library to the Python inference stack via pybind11, maintaining API surface compatibility with the existing service contract.
- Achieved P99 end-to-end latency reduction from **280ms to 193ms (31% improvement)** under 10K QPS load testing, with throughput capacity validated to 20K QPS before exceeding the revised SLA threshold.
- Containerized the updated serving stack using **Docker** (multi-stage build, final image < 1.8GB); deployed to **GKE** via Kubernetes Deployment manifests with Horizontal Pod Autoscaler configured to scale on P99 latency and request rate metrics.
- Participated in staged production rollout (1% → 10% → 50% → 100% traffic over 3 weeks), monitoring latency percentiles and error rates via **GCP Cloud Monitoring** dashboards; rollout completed with zero SLA breaches and no regression in classification accuracy metrics.

---

#### Project 2: Policy-Grounded RAG Pipeline with Synthetic Data Augmentation for Safety Classification

*The LLM-based safety classifier exhibited low recall on nuanced, context-dependent policy violations—particularly in newly introduced or low-frequency content categories—due to static model knowledge of evolving policy language and severe training data imbalance in minority violation classes.*

- Designed a **RAG pipeline** integrating Hugging Face sentence-transformers for policy document chunking and dense embedding (256-token chunks, stored in a GCP-hosted vector index), enabling dynamic retrieval of the top-3 most relevant policy clauses injected into the LLM classifier prompt context at inference time.
- Fine-tuned the retrieval component using a curated set of **2,000 expert-labeled policy-context pairs**, achieving top-3 retrieval precision of **91.4%** on a held-out evaluation set, ensuring retrieved clauses were semantically aligned with violation type rather than surface-level keyword matches.
- Built a **Synthetic Data Generation pipeline** (Python orchestration + GPT-4 API + deterministic rule-based augmentation templates) producing **200K labeled training examples** targeting 4 underrepresented safety violation taxonomies; implemented an LLM-as-judge filtering loop (secondary GPT-4 evaluation pass) to discard samples below a quality threshold, retaining **87%** of generated examples.
- Evaluated the combined RAG-augmented + fine-tuned model on a **50K-sample benchmark** (human-labeled + filtered synthetic): minority-class macro F1 improved by **9.7%** and nuanced policy violation recall improved by **14.2%** versus the pre-RAG baseline, with no regression on high-frequency violation categories.
- Automated model retraining orchestration using **Kubeflow Pipelines** triggered by weekly feature drift reports, with **GCP Vertex AI** for distributed PyTorch training runs and model artifact versioning; documented the full MLOps loop—from drift detection trigger through retraining to staged deployment—in the team's internal production runbook.

---

## Appendix Note — Go Achievement (Recommended Placement)

> *Place in an **"Additional"** or **"Selected Achievements"** section at resume bottom. Suggested phrasing:*

**Additional**
- Certified Chinese National Go (Weiqi) Amateur Level 2; self-taught; ranked **1st** at 2022 Municipal Championship and **3rd** at 2023 Municipal Championship, competing against formally trained players.

*Framing rationale for recruiters: self-directed mastery of a combinatorially complex strategic system—directly analogous to the pattern recognition and search-space optimization reasoning used in ML model design. Understated but distinctive signal.*
