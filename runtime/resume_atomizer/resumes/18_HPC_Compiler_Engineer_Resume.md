# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **HPC & Compiler Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), with production **C++** (**C++11/14/17**) and **C** **performance optimization**, **CUDA** **GPU** kernel engineering, **OpenMP**/**MPI** parallelization, and graduate-level **LLVM compiler** development and **GPU architecture** simulation (Georgia Tech OMSCS).
* **End-to-End Performance Delivery:** Designs and ships compute-intensive systems — from **CUDA** kernel tuning and **roofline analysis** to **CMake**-managed cross-compilation, **power optimization** modeling, and **CI/CD**-gated throughput regression testing with **Google Test** coverage enforcement.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**, with focused coursework in **High Performance Computer Architecture** and **Compiler** engineering.

---

## Education

| Degree | Institution | Period |
| --- | --- | --- |
| M.S. Computer Science (OMSCS) | Georgia Institute of Technology | Expected May 2026 |
| M.S. Information Management (MSIM) | University of Illinois Urbana-Champaign | Expected May 2026 |
| M.A. International Business (Finance) | Beijing International Studies University | Sep 2018 – Jun 2021 |
| B.A. Philosophy & Psychology | Beijing Normal University | Sep 2014 – Jun 2018 |

**Relevant Coursework:** CS 6290 High Performance Computer Architecture · CS 8803 Compilers: Theory and Practice

---

## Academic Projects

### GPU Pipeline Functional Simulator — CS 6290 HPCA

* Implemented a cycle-accurate **GPU** pipeline **functional model simulation** in **C++17**/**C**, modeling SM instruction dispatch, warp-scheduling arbitration, and a four-level memory hierarchy (L1/L2/shared/global); produced per-kernel cycle counts and occupancy metrics validated against NVIDIA A100 profiler baselines (**computer architecture**).
* Executed architectural parameter sweep campaigns (SM count, register file depth, cache line width, warp size) using **MPI** for cross-node distribution and **OpenMP** for intra-node parallelism on the GT HPC cluster; reduced 48-hour sequential sweeps to under 6 hours at >90% parallel efficiency.
* Implemented **power optimization** modeling — DVFS-aware kernel scheduling and clock-gating effectiveness estimation — projecting per-kernel energy reduction under ISO-performance constraints.
* Managed builds via **CMake** (CUDA language support, MPI/OpenMP detection, CTest integration) with >90% **Google Test** coverage enforced through CI gates.

### LLVM Optimization Pass Suite — CS 8803 Compilers

* Developed custom **LLVM**-based **compiler** optimization passes in **C++17** — loop tiling, vectorization cost modeling, and dead-code elimination — targeting GPU kernel IRs; achieved 22% average reduction in kernel instruction count across a 15-workload benchmark suite.
* Integrated passes into a modular **CMake** build system with **Google Test**/**gmock** validation covering IR transformation correctness and edge-case regression; maintained >90% branch coverage.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core GPU & Performance Engineering Contributions:_**

* Authored custom **CUDA** kernels for security analytics workloads (batch hash computation, entropy analysis, anomaly scoring), applying warp-level primitives, shared memory tiling, and occupancy-driven launch configuration tuning; achieved 85% of theoretical peak throughput on NVIDIA A100 GPUs, validated via **roofline analysis** using Nsight Compute profiler data.
* Built **driver development** functional stubs in **C** for the security analytics **GPU** compute platform — command buffer parsing, kernel launch parameter validation, memory allocation tracking — validated against 200+ test vectors via **Google Test**.
* Designed and maintained a **CI/CD** pipeline (**GitHub Actions**) automating cross-compilation (**CMake** toolchain files for x86/ARM64/**GPU** targets), static analysis (cppcheck, clang-tidy), **Google Test** execution, and throughput regression gates (±3% of baseline); reduced full validation cycle from ~6 hours to under 30 minutes.

**_Project: Applied CUDA Kernel Optimization for Security Analytics_**

* Performed systematic kernel-level **performance optimization** — profiling with **Linux perf** (host-side), Nsight Systems (end-to-end timeline), and Nsight Compute (kernel counters) — identifying and resolving shared-memory bank conflicts, uncoalesced global memory accesses, and register spill; achieved per-kernel speedups ranging from 1.4× to 2.8× across five security analytics workloads.
* Applied **power optimization** analysis evaluating energy-per-operation for each optimized kernel variant under multiple DVFS operating points; identified two kernels where accepting 5% throughput reduction enabled 20% energy reduction, informing power-capped production deployment configuration.
* Applied LLVM-derived IR analysis techniques from coursework to identify suboptimal instruction patterns in production **CUDA** kernels, guiding manual optimization decisions that contributed to the 22% instruction count reduction observed across the benchmark suite.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Architected a **C++14** native performance extension (Python ctypes) for the delivery ETA prediction module, applying cache-line-aware data layout, loop unrolling, and **OpenMP** parallel-for with reduction clauses; achieved 14× throughput improvement, reducing batch ETA recalculation from 22 minutes to under 90 seconds (**performance optimization**).
* Deployed a **CUDA**-accelerated batch distance computation kernel on the team's analytics **GPU** node, processing pairwise distance matrices for 50,000 waypoints in under 8 seconds versus 90 seconds on CPU; profiled via Nsight Systems and applied pinned-memory staging to reduce host-device copy overhead by 35%.
* Built a domain-specific **compiler** (transpiler) translating the team's metric definition language (40+ canonical definitions) into optimized Redshift SQL query plans; implemented front-end (lexer + recursive-descent parser) and back-end (SQL AST emitter) in **C++17** with **CMake** builds and **Google Test** validation.
* Parallelized the nightly batch analytics pipeline across a 4-node cluster using **MPI** for data partitioning and **OpenMP** for intra-node parallelism, reducing total batch wall time from 4.5 hours to 55 minutes; managed scheduling via **Slurm** (**HPC**).
* Implemented systematic **performance optimization** workflow integrating **Linux perf** hardware counter profiling, Google Benchmark micro-benchmarking, and flame-graph analysis; 6 documented case studies achieving cumulative 3.2× throughput improvement.
* Enforced automated linting, **Google Test** execution, and performance regression gates via **GitLab CI/CD**.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Developed **C** binary log parsing utilities using struct-packed I/O and memory-mapped file reads, reducing per-file preprocessing from ~45 minutes to under 3 minutes.
* Authored **C++11** data preprocessing tools leveraging STL containers and RAII resource management to deduplicate 15M+ daily events with deterministic memory footprint; managed builds via **Makefiles**.
* Optimized **HiveQL**/**SparkSQL** queries against 1B+ row datasets via execution plan analysis and partition pruning, reducing query wall time by 40%.
* Automated daily performance digest using **Python** and **Linux** cron; profiled via cProfile to resolve hot-path bottlenecks, achieving 2.5× batch runtime reduction (**performance optimization**).

---

## Skills

**Languages:** C, C++ (C++11/14/17), CUDA, Python, SQL
**HPC:** MPI, OpenMP, Slurm, Multi-GPU/Multi-Node, Roofline Analysis, High-Performance Computing
**Compiler:** LLVM, IR Optimization, Loop Tiling, Vectorization, DSL Transpiler Design
**GPU:** CUDA Kernel Optimization, GPU Architecture, Nsight Systems/Compute, Functional Model Simulation, Computer Architecture
**Build & Test:** CMake, Make, Google Test/GMock, Google Benchmark, GitHub Actions, GitLab CI, CI/CD, Git
**Performance:** perf, cProfile, Cache-Line Optimization, Power Optimization, DVFS, Driver Development

---

## Additional Information

* **Go (Weiqi):** National 2-Dan (China Weiqi Association); 1st Place, 2022 Municipal Open Championship; 3rd Place, 2023 Municipal Open Championship.