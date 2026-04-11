# Company Subseed Index

## Amazon

* `max_mainline_directions`: `2`
* `notes`: Keep Amazon on two stable mainlines: platform/distributed systems and AI/ads/LLM. Robotics stays explicitly out-of-mainline.

### Amazon Platform / Distributed Systems

* `subseed_id`: `amazon_platform_mainline`
* `kind/status`: `mainline` / `active`
* `primary_seed_id`: `seed_amazon_management_plane_anchor_candidate`
* `seed_ids`: `seed_amazon_management_plane_anchor_candidate, seed_codex_amazon_sde`
* `derived_count`: `27`

### Amazon AI / Ads / LLM

* `subseed_id`: `amazon_ai_ads_mainline`
* `kind/status`: `mainline` / `active`
* `primary_seed_id`: `seed_amazon_agi_ml_anchor`
* `seed_ids`: `seed_amazon_agi_ml_anchor, seed_amazon_conversational_ads_backend`
* `derived_count`: `42`

### Outliers

- `69d05887cfdc6132f943a843` | Robotics - Software Development Engineer | generated `True` | Rust/robotics/hardware-adjacent scope should be generated separately and not folded into the Amazon mainline.
- `69d00c2ccdb525785fba6b0b` | Robotics - Software Development Engineer | generated `True` | Duplicate robotics posting; keep marked as outlier even if generated.

## Google

* `max_mainline_directions`: `2`
* `notes`: Google is now split into product-facing AI/application work and cloud/infra work. Global Network Edge remains an explicit outlier until proven otherwise.

### Google Product / AI Application

* `subseed_id`: `google_product_ai_mainline`
* `kind/status`: `mainline` / `active`
* `primary_seed_id`: `seed_google_geo_aiml_anchor`
* `seed_ids`: `seed_google_geo_aiml_anchor, seed_codex_google_aiml, seed_codex_google_fullstack`
* `derived_count`: `40`

### Google Cloud / Infra

* `subseed_id`: `google_cloud_infra_mainline`
* `kind/status`: `mainline` / `active`
* `primary_seed_id`: `seed_google_cloud_infra_anchor_candidate`
* `seed_ids`: `seed_google_cloud_infra_anchor_candidate`
* `derived_count`: `43`

### Outliers

- `69d01348cfdc6132f943818e` | Software Engineer, Global Network Edge | generated `False` | SDN/network-edge/hardware-abstraction scope is still outside the proven Google mainlines.

## JPMorganChase

* `max_mainline_directions`: `2`
* `notes`: Keep JPMC on one active data/mlops mainline and at most one second enterprise-apps direction if ROI proves out. Explicitly mark management, Salesforce, and VP modeling/compliance as outliers.

### JPMC Data Platform / MLOps

* `subseed_id`: `jpmc_data_mlops_mainline`
* `kind/status`: `mainline` / `active`
* `primary_seed_id`: `seed_jpmc_data_mlops_anchor`
* `seed_ids`: `seed_jpmc_data_mlops_anchor`
* `derived_count`: `41`

### JPMC Internal Apps / Fullstack

* `subseed_id`: `jpmc_enterprise_apps_pending`
* `kind/status`: `mainline` / `planned`
* `primary_seed_id`: ``
* `seed_ids`: ``
* `derived_count`: `0`

### Outliers

- `69d05041cfdc6132f943a6a2` | Process Improvement Manager | generated `False` | Management/process-improvement route should not dilute the software/data mainline.
- `69625bd025e18715077f4272` | Salesforce Software Engineer III | generated `False` | Salesforce-specific application line is outside the current JPMC mainline and should stay explicitly separated.
- `6995f86ce0bddb6acac45e39` | Compliance - Applied AI/ML Lead - Vice President | generated `False` | VP compliance/applied-modeling leadership is an explicit outlier, not a company-mainline extension.
- `6925bda627bf2f41a2c401d5` | Business Modeling - Applied AI Modeling Lead (VP) | generated `False` | VP applied-modeling leadership is an explicit outlier, not a company-mainline extension.
- `697b738f1136d179eeeef5ea` | Security Engineer III - Java/Python AWS | generated `True` | Security-specific Java/Python/AWS route is currently outside the proven JPMC mainline.
- `69ce9e1a891d7b11cfcca544` | Software Engineer III - C/C++ Programming | generated `False` | C/C++ and shell-heavy systems work sits outside the proven JPMC data/mlops and internal-apps directions.

