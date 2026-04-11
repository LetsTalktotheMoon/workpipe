# Resume Prop Document — Responsible AI Engineer

---

## MODULE 1: PROFESSIONAL SUMMARY

Seven years of progressive experience across recommendation systems analytics, cross-border platform operations, and Trust & Safety backend engineering, unified by a consistent mandate to design accountable, auditable, and compliance-native data systems at scale. Brings a structurally rare cross-disciplinary foundation — formal training in ethics and epistemology (BNU Philosophy/Psychology), quantitative risk analysis (BISU Finance), and production systems engineering (TikTok Safety Backend) — that enables rigorous reasoning about both the technical architecture and the governance implications of AI infrastructure. Targeting Responsible AI Engineering roles to apply expertise in content provenance pipeline design, compliance-aware API development, and trust signal modeling to the challenge of deploying verifiable, regulation-ready AI systems at global scale.

---

## MODULE 2: SNOWBALL TECH STACK DISTRIBUTION

### Distribution Matrix

| Technology / Capability | Temu · Jun 2021 – Feb 2022 (8 mo) | DiDi IBG · Sep 2022 – May 2024 (20 mo) | TikTok Safety Intern · Jun 2025 – Dec 2025 (6 mo) | Estimated Depth |
|---|---|---|---|---|
| **Python** | ETL scripting, pandas data cleaning | Advanced automation, PII lineage crawler, ML feature engineering | Utility scripting, data validation tooling | ~3 years · Core proficiency |
| **SQL** | Multi-table reporting queries | Complex analytical SQL, cross-region data joins | Ad-hoc data validation | ~2.5 years · Solid proficiency |
| **TypeScript** | — | Internal BI dashboard, REST API integration | Content registry prototype, observability tooling | ~2 years · Working proficiency |
| **API Design** | — | REST API consumer + schema documentation | gRPC + REST contract design and ownership | ~2 years · Design-level proficiency |
| **C++** | — | — | 2 production microservices shipped | 6 months · Functional/intern-level |
| **Reliability Analysis / SLOs** | Basic alerting threshold setup | Data quality SLO ownership for 6 metrics | Service SLO definition, error budget policy, observability dashboards | ~2 years · End-to-end ownership |
| **Trust & Safety** | — | Food safety anomaly modeling, fraud signal engineering | Core team; safety signal aggregation pipeline | ~2 years · Domain practitioner |
| **Data Provenance** | — | Cross-border PII lineage tracking (Mexico ↔ Shanghai) | Content metadata provenance service (gRPC); C2PA credential parsing | ~2 years · Architecture-level exposure |
| **Compliance** | — | LFPDPPP (Mexico) + PIPL (China) dual-jurisdiction runbooks | EU AI Act gap analysis; C2PA standard implementation | ~2 years · Policy-to-engineering translation |
| **C2PA** | — | — | C2PA 1.x manifest parsing module in C++; compliance mapping | 6 months · Implementation-level |
| **gRPC** | — | — | API contract design for provenance service; RPC interface implementation | 6 months · Contract design + service implementation |
| **Responsible AI / RAI concepts** | — | Implicit: compliance framing, trust signal integrity | Direct: AI disclosure compliance, C2PA for AI-generated media, EU AI Act analysis | 2 years cumulative signal; 6 months direct |

### Critical ATS Keyword Gap Notes

| JD Keyword | Status | Recommended Framing |
|---|---|---|
| **Stubby** | Google-proprietary RPC framework. Falsely claiming Stubby on a non-Google resume fails background verification. | Position as **gRPC-based RPC service design**. Stubby and gRPC share the same proto-based IDL; migration to Stubby is an onboarding delta, not a gap. |
| **SynthID** | Google-proprietary watermarking technology. | Analogous exposure: C2PA credential parsing and digital content watermarking research at TikTok. Direct SynthID exposure is a post-hire ramp item. |
| **Unified Provenance Service** | Google-internal architecture name. | Analogous: designed and implemented a **content provenance metadata service** at TikTok; the architectural pattern (centralized lineage store + low-latency query API) is directly transferable. |
| **Pod / Server Platform** | Kubernetes-native deployment concepts. | C++ microservices deployed in containerized staging and production environments at TikTok. Pod-level orchestration is the implementation substrate. |

---

## MODULE 3: RESUME BULLET POINTS

---

### Temu R&D · Recommendation Algorithm Data Analyst · Jun 2021 – Feb 2022 · Shanghai

- Built a Python/pandas preprocessing pipeline to validate 50M+ daily product interaction events against feature schema contracts, reducing upstream feature data error rate from 11% to 3% and eliminating weekly model refresh cycle delays caused by silent data corruption.
- Authored SQL-based A/B testing performance reports aggregating results across 6 concurrent recommendation experiments and 8+ table joins, reducing analyst team's manual reporting effort from ~9 hours to ~2.5 hours per weekly cycle.
- Developed a lightweight Python anomaly detection script to flag CTR deviation spikes in recommendation feature feeds, enabling engineers to detect upstream pipeline failures ~36 hours earlier than the prior manual review cadence.
- Instrumented logging pipelines to capture 3 new behavioral event types (add-to-cart dwell time, browse depth percentile, secondary-click rate) in coordination with recommendation engineers, increasing feature coverage for next-generation ranking model candidates by 18%.
- Maintained a unified feature data dictionary documenting schemas, ownership, and freshness expectations for 25+ recommendation model features across 3 product verticals, adopted as the team's canonical reference by 8+ downstream engineers.

---

### DiDi IBG · Senior Data Analyst, Food Business · Sep 2022 – May 2024 · Beijing / Mexico City

- Owned end-to-end quantitative analysis for DiDi Food's expansion across 4 Mexican cities, modeling demand elasticity, merchant supply-demand equilibrium, and driver incentive ROI; analytical outputs directly informed a $2.3M quarterly incentive reallocation decision.
- Designed and owned data quality SLOs for 6 mission-critical business metrics (GMV, order success rate, merchant NPS, driver earnings, refund rate, safety incident rate), establishing alerting thresholds that reduced mean time to detect data incidents from 22 hours to under 4 hours.
- Built a Python-based cross-border PII lineage crawler that reconstructed end-to-end data flow graphs for 40+ tables containing user PII, mapping each field's transit path against LFPDPPP (Mexico) and PIPL (China) compliance requirements and generating structured compliance evidence packages.
- Developed a TypeScript-based internal analytics dashboard consolidating 14 heterogeneous data sources via REST API integrations, reducing cross-functional reporting latency from 3 days to 4 hours for a 40-person stakeholder group spanning Operations, Legal, and Product.
- Collaborated with the Trust & Safety team to engineer 12 food-safety anomaly features — including spoilage complaint velocity, geographic outbreak clustering coefficient, and merchant rating degradation slope — achieving a 23% lift in fraud flagging precision when ingested by the platform's risk engine.
- Authored dual-jurisdiction data compliance runbooks covering cross-border transfer legal bases, field-level retention schedules, and breach notification SLAs under LFPDPPP and PIPL; document adopted as the IBG team's standard compliance reference for subsequent international market launches.

---

### TikTok · Backend Software Engineering Intern, Trust & Safety · Jun 2025 – Dec 2025 · San Jose, CA

- Implemented 2 C++ microservices within TikTok's content moderation pipeline handling safety signal aggregation at 80K+ events/sec, passing internal load testing benchmarks and meeting the team's 99.9% throughput SLA threshold.
- Designed and documented gRPC + REST API contracts for a content provenance metadata service consumed by 3 downstream safety classifier teams, achieving P99 read latency of 12ms under sustained staging load.
- Developed a C2PA 1.x manifest parsing module in C++ that verified creation assertions, AI-generation flags, and signing certificate chains for AI-generated media assets at ingest time; module benchmarked at < 3ms per asset at P95 and deployed to production.
- Prototyped a TypeScript-based content metadata registry tracking asset provenance across re-upload and transformation events as structured audit log entries queryable via REST API; prototype entered the platform's internal RFC design review as a candidate architecture for the content lineage initiative.
- Instrumented SLO dashboards for 3 Trust & Safety signal APIs — defining P99 latency, error rate, and availability targets — and authored error budget policy runbooks; services maintained 99.95% availability over the 60-day post-rollout measurement window.
- Conducted a compliance gap analysis benchmarking the platform's AI-generated content disclosure practices against EU AI Act Article 50 requirements and C2PA industry standards, producing a 12-point engineering remediation roadmap adopted by the Trust & Safety compliance team.

---

## MODULE 4: KEY PROJECTS

---

### TEMU — Key Project

---

**Project: Recommendation Feature Pipeline Quality Monitor**

*Data team lacked any automated pre-ingestion validation for behavioral event data, causing silent feature corruption that delayed weekly model refresh cycles and degraded recommendation quality undetected for up to 72 hours.*

- **[Baseline]** Identified that 11% of daily product interaction events entering the feature store contained schema mismatches or null-value anomalies introduced by undocumented upstream logging changes — failures that went unnoticed until model performance degraded in weekly evaluation.
- **[Action · Python]** Designed and implemented a Python/pandas validation pipeline applying configurable schema contract rules across 25+ feature columns, covering null-rate thresholds, value range bounds, and schema version compatibility checks against a centrally maintained feature registry.
- **[Action · SQL]** Built SQL-based distribution drift detection queries comparing rolling 7-day feature baselines against daily snapshots, flagging statistical outliers exceeding 2σ deviation per feature column as candidate corruption events requiring human review.
- **[Action · Reliability Analysis]** Defined alerting thresholds and freshness SLOs for each feature column (null rate < 2%, distribution drift score < 0.15, ingestion lag < 4 hours), establishing the first measurable quality contract for the team's feature inputs.
- **[Result]** Reduced feature data error rate from 11% to 3%; cut mean corruption detection lag from ~72 hours to under 8 hours. The monitoring pipeline was adopted as the team's standard pre-ingestion quality gate for all recommendation feature ingestion jobs.

---

### DIDI IBG — Key Projects

---

**Project 1: Cross-Border Data Lineage and Compliance Documentation System**

*DiDi Food's Mexico market operations generated user PII that traversed Shanghai-based data warehouses under two conflicting national data protection regimes (LFPDPPP, PIPL), with no automated lineage tracking or audit-ready compliance evidence in place.*

- **[Baseline]** As the Mexico market scaled to 4 cities, legal teams flagged a critical audit exposure: no mechanism existed to document which PII fields crossed international borders, under what legal transfer basis, or with what retention schedule — leaving the business unable to respond to regulatory inquiries with structured evidence.
- **[Action · Python · Data Provenance]** Built a Python-based ETL metadata crawler that parsed job dependency graphs and table ownership records to reconstruct end-to-end data flow paths for 40+ PII-containing tables, generating a structured data flow inventory stored as a queryable compliance registry.
- **[Action · Compliance]** Annotated each PII field's flow path against LFPDPPP international transfer conditions (Art. 36) and PIPL outbound data rules (Art. 38-39), producing field-level compliance disposition records (lawful basis, transfer mechanism, retention period) for the full inventory.
- **[Action · TypeScript · API Design]** Developed a TypeScript-based compliance registry viewer backed by a REST API, enabling Legal and Audit teams to self-serve lineage queries and generate printable evidence reports without requiring SQL access.
- **[Result]** Compliance evidence packages produced by the system cleared legal review for 2 consecutive LFPDPPP regulatory audits. The framework was extended by the same team to Brazil and Colombia operations within 12 months of initial delivery.

---

**Project 2: Food Safety Anomaly Signal Feature Engineering**

*The platform's risk engine relied on coarse static merchant flags that lagged real-world food safety incidents by 48+ hours, limiting the team's ability to proactively remove at-risk merchants before consumer harm occurred.*

- **[Baseline]** Trust & Safety team identified that existing signals (aggregate complaint count, static merchant rating) were insufficient to detect emerging food quality incidents with actionable lead time — confirmed incidents only triggered merchant review after a 48-hour accumulation window.
- **[Action · Python · SQL]** Engineered 12 time-series features from raw event data including spoilage complaint velocity (complaint count per 4-hour rolling window), geographic outbreak clustering coefficient (spatial density of co-located illness reports), and merchant rating degradation slope (7-day linear regression coefficient), computed via Python/pandas on SQL-extracted event tables.
- **[Action · Reliability Analysis · SLOs]** Defined feature-level data quality SLOs for each signal (freshness SLA < 2 hours from event time, null rate < 0.5%, schema version lock), instrumenting automated alerts to ensure consistent signal availability for the downstream risk model inference pipeline.
- **[Action · Trust & Safety]** Validated the feature set against a labeled incident dataset (n=1,400 confirmed food safety cases) using precision@K evaluation, iterating on feature formulations across 4 review cycles with the risk engineering team.
- **[Result]** Feature set integrated into the platform's risk engine achieved a 23% lift in flagging precision. Mean time-to-merchant-suspension for confirmed food safety incidents decreased from 48 hours to 11 hours following production deployment.

---

### TIKTOK SAFETY — Key Projects

---

**Project 1: Content Provenance Metadata Service**

*Safety classifier teams independently reconstructed asset origin data from disparate raw log sources, producing inconsistent provenance signals across teams, redundant compute overhead, and no defined latency SLA for provenance queries against live content.*

- **[Baseline]** Three separate safety classifier teams each maintained independent pipelines to reconstruct content origin metadata (creation timestamp, uploader identity, AI-generation flag, prior moderation history) from raw logs — resulting in divergent provenance signals for the same asset and no shared latency contract for provenance queries.
- **[Action · C++ · API Design]** Implemented the gRPC service layer in C++ for a content provenance metadata service, handling request deserialization, routing to an in-memory cache tier, and fallback queries to the persistent metadata store; service processed 40K+ queries/sec in staging load tests against a pre-populated dataset of 50M asset records.
- **[Action · TypeScript · Data Provenance]** Built a TypeScript-based content metadata registry prototype that recorded asset transformations — re-upload, trimming, filter application, cross-account repost — as structured provenance chain events, with a REST API supporting audit log queries by asset ID or transformation type.
- **[Action · SLOs · Reliability Analysis]** Defined and instrumented a three-SLO observability framework for the service: P99 read latency ≤ 15ms, error rate < 0.01%, and 99.95% rolling availability. Authored on-call alerting runbooks and error budget burn rate policies using internal observability tooling.
- **[Result]** API contract and SLO framework adopted into the team's internal RFC process. TypeScript registry prototype entered the platform's official design review as a candidate architecture for a planned content lineage initiative. Observability instrumentation was directly shipped to production as part of the team's existing service monitoring rollout.

---

**Project 2: C2PA Content Credential Integration Module**

*As EU AI Act Article 50 and C2PA industry standards increasingly mandated verifiable creation metadata for AI-generated content, the platform had no production capability to parse, validate, or store C2PA credentials at asset ingest time, creating growing compliance exposure.*

- **[Baseline]** AI-generated media ingested from third-party creation tools embedded C2PA manifests, but the platform's ingest pipeline discarded these credentials without parsing — leaving the platform unable to answer basic compliance queries ("Is this asset AI-generated?" / "Is a verified provenance chain present?") from regulators or content partners.
- **[Action · C++ · C2PA]** Implemented a C++ parsing module conforming to the C2PA 1.x manifest specification, extracting creation assertions, AI-generation claim flags, and signing certificate chains from inbound JPEG/MP4 assets at ingest time; module benchmarked at < 3ms per asset at P95 processing latency.
- **[Action · Data Provenance · Compliance]** Mapped parsed C2PA credential fields to the platform's internal content classification schema, populating `ai_generated` (bool), `provenance_chain_verified` (bool), and `manifest_issuer` (string) fields in the content metadata store, enabling downstream safety classifiers and compliance audit queries to consume structured provenance signals.
- **[Action · Responsible AI · Compliance]** Conducted a systematic compliance gap analysis benchmarking the platform's AI disclosure practices against EU AI Act Article 50 (AI-generated content labeling) and C2PA 1.x standard requirements, identifying 12 specific engineering gaps (e.g., missing re-upload credential re-signing, absent manifest expiry handling) and documenting recommended remediation owners and timelines.
- **[Result]** C2PA parsing module shipped to production and processed credentials for 10M+ assets within 6 months of deployment. Gap analysis report adopted by the Trust & Safety compliance team as the primary engineering roadmap input for the platform's EU AI Act compliance workstream.

---

> **Note to author:** The gap between Temu (Feb 2022) and DiDi (Sep 2022) — approximately 7 months — is structurally visible and will likely surface in HR screening. Recommend pre-empting with a brief cover letter line or preparing the character with a consistent, factual explanation (e.g., relocation to Beijing, personal situation, selective job search). The gap does not damage the narrative arc but should not be left unaddressed.
