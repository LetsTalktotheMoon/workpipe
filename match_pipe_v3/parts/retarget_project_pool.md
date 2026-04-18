## 经验公司项目池（硬约束）
- 单篇简历最多保留 2 个项目。
- 项目只能从下面的公司主池里选，不允许发明新项目或把同一项目改写成完全不同的业务逻辑。
- 同一项目可以换强调角度，但 team / domain / scope ceiling / ownership ceiling 不可越界。

### TikTok / ByteDance
- 公司池上限: 2
- 说明: Internship company. Keep scope explicitly team-contributed and avoid multiplying independent project universes.
- `tiktok_security_retrieval_console`
  时间: 2025-06 -> 2025-09
  团队: Security Investigation Tooling
  业务域: Security knowledge retrieval and analyst tooling
  目标: Reduce manual context gathering for policy and incident investigations through retrieval-assisted internal tooling.
  scope ceiling: Feature delivery inside a team-maintained retrieval assistant, evaluator, or analyst console; not end-to-end ownership of a standalone platform.
  ownership ceiling: Implement handlers, evaluators, ingestion utilities, replay hooks, lightweight UI surfaces, and deployment checks for a bounded intern-owned slice.
  allowed tech surface: Go, Python, Java, JavaScript, TypeScript, PostgreSQL, Kafka, gRPC, REST, Docker, Kubernetes, AWS, S3, AWS Bedrock, RAG, LLM
  allowed role lenses: backend, data, swe, mle, analyst
  scope note: 需要
  notes: Use for retrieval assistant, policy search, evaluation, or analyst-console variants. The business logic stays anchored in security knowledge retrieval.
- `tiktok_security_release_hardening`
  时间: 2025-10 -> 2025-12
  团队: Security Platform Release and Replay
  业务域: Security telemetry replay, release safety, and validation
  目标: Improve release confidence and replay fidelity for security event-processing and retrieval-adjacent services.
  scope ceiling: Tooling and reliability work around existing services, replay sandboxes, CI gates, and device/parser validation; not ownership of the core product roadmap.
  ownership ceiling: Implement parsers, replay fixtures, CI/CD gates, deployment automation, Linux validation harnesses, and bounded reliability fixes with teammate guidance.
  allowed tech surface: Go, Python, Java, C++, Linux, Kafka, PostgreSQL, Docker, Kubernetes, GitHub Actions, CI/CD, Model Deployment, Network Protocol, Embedded
  allowed role lenses: backend, platform, swe, data
  scope note: 需要
  notes: Use for replay sandbox, release hardening, device-feed validation, or regression-gating variants without changing the underlying security-platform context.

### DiDi Food
- 公司池上限: 4
- 说明: Longer tenure allows multiple sequential projects, but their time windows must not overlap or read like unrelated parallel careers.
- `didi_merchant_incident_workbench`
  时间: 2022-09 -> 2023-03
  团队: Merchant Support and Exception Operations
  业务域: Merchant incident triage, support routing, and exception handling
  目标: Replace spreadsheet-heavy merchant support workflows with auditable services and operator tooling.
  scope ceiling: Cross-functional delivery of internal support tooling, routing APIs, and dashboards used by regional operations; not sole ownership of the full merchant platform.
  ownership ceiling: Translate analyst requirements, build validation scripts and service slices, coordinate release checks, and ship operator-facing views with backend/frontend partners.
  allowed tech surface: Java, Python, Flask, REST, SQL, MySQL, Redis, Kafka, Airflow, Docker, React, TypeScript, Jira
  allowed role lenses: analyst, backend, fullstack, pm, swe
  scope note: 通常不需要
  notes: Use for merchant incident console, exception workbench, refund-resolution workflow, or issue-routing variants.
- `didi_pricing_rules_migration`
  时间: 2023-04 -> 2023-09
  团队: Pricing and Promotion Infrastructure
  业务域: Pricing, dispatch rules, and promotion eligibility services
  目标: Move frequently changed pricing and dispatch logic from analyst-managed processes into release-managed backend services.
  scope ceiling: Service migration, rule validation, release-readiness checks, and ops tooling for pricing/dispatch workflows; not ownership of company-wide pricing strategy.
  ownership ceiling: Build backfills, rule validators, microservice modules, data parity checks, and rollout coordination with backend and ops partners.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Microservices, Docker, Git, Jira
  allowed role lenses: analyst, backend, data, pm, swe
  scope note: 通常不需要
  notes: Use for merchant offer rules, pricing rules migration, dispatch rules service, or rule-evaluation service variants.
- `didi_supply_eta_service`
  时间: 2023-10 -> 2024-02
  团队: Supply Planning and Dispatch Analytics
  业务域: Courier ETA, supply-demand planning, and anomaly monitoring
  目标: Improve city-level planning speed and operational visibility through reusable ETA and supply monitoring services.
  scope ceiling: Internal feature services and planning workflows for ops teams, backed by ETL and event-driven updates; not a standalone customer-facing product.
  ownership ceiling: Build feature pipelines, anomaly checks, service adapters, cached reads, and planning diagnostics with partner engineering teams.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Flask, Docker, ETL
  allowed role lenses: analyst, backend, data, pm, swe
  scope note: 通常不需要
  notes: Use for courier ETA feature service, capacity planning service, merchant supply exception monitoring, or outage diagnostics.
- `didi_campaign_ops_console`
  时间: 2024-03 -> 2024-05
  团队: Promotion Operations and Experimentation
  业务域: Campaign launch tooling, experimentation, and promotion audits
  目标: Give operators a shared console to configure, launch, and audit promotion campaigns with fewer errors.
  scope ceiling: Internal launch-console and experimentation workflows tied to existing backend services and data refresh jobs; not ownership of company-wide growth product strategy.
  ownership ceiling: Build validation logic, console flows, sync jobs, audit tables, and release coordination with product/frontend/backend partners.
  allowed tech surface: Java, Python, TypeScript, JavaScript, Flask, REST, SQL, Redis, Kafka, Airflow, ETL, Docker
  allowed role lenses: analyst, fullstack, pm, backend, swe
  scope note: 通常不需要
  notes: Use for campaign operations console, regional promotion console, or experiment-setup workflow variants.

### Temu R&D
- 公司池上限: 2
- 说明: Shorter tenure. Keep Temu scoped to analytics and experimentation support rather than turning it into a large standalone engineering program.
- `temu_checkout_funnel_diagnostics`
  时间: 2021-06 -> 2021-10
  团队: Growth and Funnel Analytics
  业务域: Checkout funnel, assortment, and conversion diagnostics
  目标: Identify conversion friction and prioritize product fixes through repeatable diagnostics and experiment readouts.
  scope ceiling: Analytics workflows, readouts, and lightweight modeling for product and R&D reviews; not ownership of the core product roadmap.
  ownership ceiling: Build SQL/Hive/Spark analyses, notebooks, and experiment slices that inform product decisions and monitoring.
  allowed tech surface: SQL, Hive, Spark SQL, Python, Pandas, A/B Testing, scikit-learn
  allowed role lenses: analyst, data, pm
  scope note: 通常不需要
  notes: Use for checkout funnel, conversion diagnostics, retention slices, or experiment-readout variants.
- `temu_promo_reporting_automation`
  时间: 2021-11 -> 2022-02
  团队: Merchant and Promotion Analytics
  业务域: Merchant reporting, promotion monitoring, and recurring analytics automation
  目标: Reduce repetitive reporting and improve visibility for merchant performance and promotion operations.
  scope ceiling: Recurring analytics automation, anomaly checks, and lightweight modeling; not full-stack product development.
  ownership ceiling: Automate reports, reconcile datasets, build monitoring tables, and provide decision support for experiments and merchant reviews.
  allowed tech surface: Python, Pandas, SQL, Hive, Spark SQL, Airflow, A/B Testing, scikit-learn
  allowed role lenses: analyst, data, pm
  scope note: 通常不需要
  notes: Use for reporting automation, merchant quality reviews, promotion monitoring, or cohort-analysis variants.