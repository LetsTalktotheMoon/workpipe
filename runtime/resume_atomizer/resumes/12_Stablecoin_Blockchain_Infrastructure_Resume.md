# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Stablecoin & Blockchain Infrastructure Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production delivery spanning **stablecoin** mint/redeem pipeline design, **blockchain** node operations, **wallet infrastructure**, **payment rails** integration (SPEI, SWIFT), and cross-border **treasury management** in **regulated environments**.
* **End-to-End FinTech Infrastructure Delivery:** Designs and ships cloud-native financial systems on **AWS**/**GCP**/**Azure** — from HSM-backed transaction signing and proof-of-reserve attestation to **Terraform**-managed **Infrastructure as Code**, **distributed systems** architecture, and real-time settlement reconciliation across multi-currency, multi-jurisdiction environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Graduate foundation in international **fintech** and quantitative finance directly applied to protocol-level trust architecture and regulatory compliance reasoning. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Blockchain & Security Infrastructure Contributions:_**

* Deployed and hardened **blockchain** node infrastructure (Geth, Erigon) across 3 availability zones on **Kubernetes** (EKS/GKE) with Helm-managed deployments, network-isolation policies, mempool anomaly monitoring dashboards (Prometheus/Grafana), and health-check sidecars — sustaining 99.97% RPC endpoint availability with zero-trust network segmentation over 90 days.
* Designed and authored a CI/CD pipeline (GitHub Actions) automating Solidity compilation, Slither/Mythril static security analysis with zero-critical-finding enforcement, Hardhat unit and integration tests (98% line coverage gate), staged testnet deployment, and production gating requiring multi-sig approval.
* Instrumented API endpoint and transaction-field security policy classification across multi-jurisdiction payment gateway topologies, building the data-ingestion backbone consumed by an internal **distributed** compliance scoring platform processing 2M+ daily field-level policy evaluations across **regulated** cross-border data flows.

**_Project: Stablecoin Mint/Redeem Pipeline & Proof-of-Reserve Attestation_**

* Designed and implemented a **stablecoin** mint/redeem pipeline on **GCP** + **AWS** multi-cloud infrastructure — HSM-backed (CloudHSM) ECDSA transaction signing, GKE-hosted fiat on-ramp webhook ingestion, on-chain ERC-20 mint execution, and reserve ledger reconciliation — validating end-to-end mint latency of <8 seconds on Ethereum L1 testnet.
* Built Go backend services for a **wallet infrastructure** platform: HD wallet derivation (BIP-32/44), hot/cold wallet segregation with configurable signing thresholds, and a transaction signing service distributing ECDSA key shares across 3 geographically isolated HSM clusters via multi-party computation — achieving <200ms signing latency at sustained 500 TPS.
* Built an automated proof-of-reserve attestation pipeline in Python: hourly on-chain ERC-20 supply queries against archive nodes, cross-referenced against off-chain bank API reserve balances via mTLS-authenticated connections, with Merkle tree inclusion proofs and cryptographically signed attestation reports — detecting simulated reserve deviations within <60 seconds.
* Authored **Terraform** IaC modules managing the full deployment topology: GKE/EKS clusters, VPC peering, CloudHSM provisioning, KMS envelope encryption for **wallet** seed material, IAM policies, and Sentinel policy-as-code rules (**Infrastructure as Code**).

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

**_Payment Rails & Treasury:_**

* Designed and deployed a cross-border **payment** settlement pipeline integrating Mexico's **SPEI** real-time **payment rail** and SWIFT messaging for USD/MXN **treasury** flows, processing ~$2.4M in daily driver payout settlements across 8 city-markets with exactly-once delivery guarantee via Kafka event sourcing and Redis-backed distributed locking (**payment rails**).
* Built a **treasury management** reporting system (Python/Airflow) computing daily MXN/USD/CNY exposure positions, automated FX hedging analytics, and settlement netting optimization that reduced inter-entity transfer volume by 22%.
* Developed an internal **wallet** balance reconciliation suite for DiDi's multi-currency driver payout wallets, performing automated end-of-day balance assertions against the payment gateway settlement ledger; reduced weekly unresolved reconciliation exceptions from 34 to fewer than 5.

**_Compliance & Infrastructure:_**

* Integrated KYC/AML pipeline feeds into the settlement reconciliation workflow, automating flagging of driver payout transactions against OFAC/SAT watchlists and generating SOX-compliant audit trail exports for quarterly CNBV regulatory filings (**regulated environments**).
* Provisioned and managed **AWS** multi-region infrastructure via **Terraform** modules: Redshift clusters, S3 data lake partitions, IAM cross-account roles, and KMS encryption-at-rest policies for PII datasets — ensuring compliance with Mexico's CNBV financial data residency requirements (**Infrastructure as Code**).
* Conducted a **blockchain**-based delivery receipt timestamping proof-of-concept (Hyperledger Fabric), evaluating immutable audit trail feasibility; delivered a technical feasibility report with cost-benefit analysis to the VP of Engineering that informed the 2024 technology roadmap.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Built a Python data extraction and reconciliation pipeline cross-validating daily GMV figures between the recommendation engine event log and the **payment** settlement ledger — identifying a recurring ¥120K/day discrepancy from timezone-boundary double-counting that had persisted undetected for 3 months (**fintech**).
* Authored HiveQL/SparkSQL queries against 1B+ row transaction datasets to extract **payment** funnel conversion metrics (Alipay, WeChat Pay) segmented by recommendation cohort, supplying inputs for weekly A/B evaluation.
* Developed PII access audit trails compliant with China's PIPL, collaborating with legal and compliance to ensure recommendation-to-payment data joins adhered to **regulated environment** data minimization requirements.
* Automated daily performance digest and **payment** conversion reporting via Python cron jobs ingesting S3-hosted data lake partitions, eliminating ~6 manual analyst-hours per week.

---

## Skills

**Blockchain & Stablecoin:** Stablecoin Architecture, ERC-20, Solidity, Geth/Erigon, Smart Contract CI/CD, Proof-of-Reserve
**Cryptography & Security:** HSM (CloudHSM), MPC, ECDSA/EdDSA, KMS, Merkle Proofs
**Infrastructure:** Terraform (IaC), Kubernetes (EKS/GKE), Helm, Docker, AWS, GCP, Azure
**Distributed Systems:** gRPC, Protobuf, Kafka, Redis, MongoDB, Microservices, OpenTelemetry
**Financial Systems:** Payment Rails (SPEI, SWIFT), Treasury Management, Wallet Infrastructure, KYC/AML, Regulated Environments
**Languages:** Go, Python, Solidity, SQL (HiveQL/SparkSQL)

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