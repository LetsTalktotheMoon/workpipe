# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Low-Level Systems & Virtualization Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), delivering production-grade **C**/**C++** systems programming, **hypervisor** backend development (**VirtIO**, **KVM/QEMU**), **device driver** debugging, **kernel** module development, and hardware protocol analysis (**USB**, **PCIe**, **DisplayPort**, **Thunderbolt**).
* **End-to-End Systems Delivery:** Designs and ships performance-critical software across the full hardware-software boundary — from **Arm64 assembly** context switch instrumentation and **bootloader** validation to **firmware** diagnostics, virtual device **fuzzing**, and **protocol analyzer**/**oscilloscope**-based signal integrity verification.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**, concentrating on **operating systems** internals and **CPU architecture**.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Systems Engineering Contributions:_**

* Built a **Python** protocol fuzzing harness targeting **USB**, **PCIe**, and **Thunderbolt** virtual device emulation endpoints, generating 50,000+ mutated descriptors per campaign and surfacing 4 previously undetected parsing edge cases across the **C**/**C++** device model — all triaged to severity P2 and patched within the internship window.
* Conducted signal integrity validation on **PCIe** Gen4 (16 GT/s) and **Thunderbolt** 4 (40 Gbps) passthrough configurations using a multi-channel **oscilloscope** and **protocol analyzer** captures; confirmed electrical compliance for 3 device profiles and escalated 2 marginal eye-diagram failures with full waveform documentation to the hardware vendor.
* Validated **macOS** Sequoia guest **VM** boot sequences under the **Virtualization.framework** integration path, verifying **secure boot chain** integrity from **bootloader** stage through XNU **kernel** handoff and producing 5 validated guest configuration profiles.

**_Project: VirtIO Paravirtualized I/O Backend for Malware Sandbox_**

* Implemented a **VirtIO** backend device emulation module in **C** for the team's type-2 **hypervisor**, covering virtqueue ring buffer management, interrupt injection, and scatter-gather DMA descriptor processing for virtio-net and virtio-blk devices; guest-to-host forwarding reached 93% of bare-metal throughput on 10 GbE links — a 2.3× improvement over the prior full-emulation model.
* Developed a custom **Linux kernel module** in **C** exposing an ioctl interface for secure inter-**VM** artifact transfer between isolated guest VMs, bypassing the host network stack entirely and eliminating all cross-sandbox network exposure vectors.
* Authored **Arm64 assembly** interrupt vector table stubs and context switch instrumentation for the **hypervisor**'s **CPU** virtualization layer on Ampere Altra servers, enabling per-guest cycle-accurate accounting and reducing scheduling jitter by 18% under concurrent 8-guest workloads.
* Built a **C++** device model management daemon to orchestrate **VM** lifecycle operations (create, snapshot, live migration, teardown) with **PCIe** device passthrough configuration; confirmed passthrough stability across 3 device profiles under 72-hour continuous soak testing.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Built a **C**-based memory-mapped I/O log decoder to parse raw binary telemetry from fleet-deployed dispatch devices, extracting GPS heartbeat and driver status payloads for warehouse ingestion; processed 2M+ records per hour at under 50 MB resident memory footprint.
* Developed **Python** and **C++** tooling to extract and decode **USB** descriptor data and **PCIe** Bus/Device/Function enumeration from 1,200+ fleet-deployed Android POS terminals, feeding a hardware inventory audit that identified 47 devices running **firmware** versions below the minimum security baseline.
* Authored **Linux** **kernel** log (dmesg) analysis scripts using strace/perf syscall tracing to diagnose intermittent **device driver** faults on fleet hardware, correlating kernel-level fault signatures with specific **firmware** revisions; reduced critical hardware incident tickets by 35%.
* Wrote **GRUB/UEFI bootloader** parameter automation scripts for standardized fleet device provisioning across the Mexico market, compressing per-device provisioning time from ~45 minutes to under 8 minutes across 200+ terminals.
* Provisioned **KVM/QEMU**-based sandboxed analytics environments with **CPU** topology-aware workload placement (perf stat profiling, NUMA-aware pinning), improving batch analytics job throughput by 22% on shared 64-core compute nodes.
* Designed and operationalized a **Python**/**Apache Airflow** pipeline replacing 7 siloed manual workflows for Mexico Food's weekly KPI reporting across 8 city markets; reduced report delivery from 3 business days to under 4 hours.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Developed a **C** utility to convert proprietary binary event log formats exported by the upstream feature store into CSV for downstream **Python** analysis pipelines, reducing per-file parsing time from ~12 minutes (pure Python) to under 40 seconds.
* Automated the recommendation team's daily performance digest using **Python** (pandas, SQLAlchemy, ctypes for binary log parsing) and **Linux** cron scheduling, eliminating ~6 manual analyst-hours per week.
* Authored and tuned **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics, supplying quantitative inputs for weekly model retraining decisions.
* Provisioned isolated **VirtualBox** **virtual machine** environments on **macOS** workstations for reproducible analysis runs, standardizing library versions and eliminating 3 classes of environment-dependent data discrepancies.

---

## Skills

**Languages:** C, C++, Python, Arm64 Assembly, SQL
**Systems:** Linux Kernel Modules, VirtIO, Hypervisor Development, Device Drivers, Bootloader/UEFI, Operating Systems
**Hardware Protocols:** USB, PCIe, DisplayPort, Thunderbolt, Protocol Analyzers, Oscilloscope
**Virtualization:** KVM/QEMU, VirtualBox, macOS Virtualization.framework, VM Lifecycle Management, CPU Architecture
**Platforms:** Linux, macOS, ARM64, x86

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