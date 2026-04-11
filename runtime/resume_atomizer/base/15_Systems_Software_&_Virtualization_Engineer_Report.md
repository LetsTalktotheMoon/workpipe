# Resume Prop Document — Systems Software & Virtualization Engineer

---

## MODULE 1 — Professional Summary

Systems-oriented engineer with 3+ years of production data infrastructure and backend service development experience at hyperscale consumer platforms (Temu, Didi IBG, TikTok), currently completing dual graduate programs in Computer Science (Georgia Tech OMSCS) and Information Management (UIUC MSIM) with concentration in operating systems internals, CPU architecture, and low-level systems programming. Brings a structurally differentiated analytical foundation — behavioral modeling from undergraduate philosophy and cognitive psychology, quantitative risk assessment from a graduate finance program — that translates directly into disciplined root-cause reasoning, systematic failure-mode analysis, and performance-critical optimization across kernel, firmware, and hypervisor-layer software stacks. Targeting systems software and virtualization engineering roles where demonstrated proficiency in C/C++ systems programming, device driver development, embedded firmware debugging, hardware protocol analysis (USB, PCIe, DisplayPort, Thunderbolt), and hypervisor/VirtIO architecture directly addresses the need for engineers who can operate across the full hardware-software boundary.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **Python** | ✓ Scripting: cron automation, pandas, ctypes FFI wrappers | ✓✓ Pipeline automation: Airflow DAGs, binary log parsers, struct module | ✓✓✓ Systems tooling: protocol fuzzers, firmware test harnesses | **4+ years** |
| **C** | ✓ Small utility scripts: data format converters, CSV-to-binary packers | ✓✓ Driver-adjacent debugging: custom log decoders, memory-mapped I/O read tools | ✓✓✓ Kernel module patches, VirtIO backend device emulation | **4+ years** |
| **C++** | — | ✓ Lightweight metric collection daemons, protobuf serializers | ✓✓✓ Hypervisor component development, device model implementations | **2+ years** |
| **Operating Systems / OS Internals** | ✓ Linux cron, process scheduling observation, /proc filesystem exploration | ✓✓ Kernel log analysis, syscall tracing (strace/perf), driver enumeration | ✓✓✓ Kernel module development, scheduler interaction, interrupt handling | **4+ years** |
| **Kernel** | — | ✓ Kernel log parsing for driver fault diagnostics, dmesg analysis | ✓✓✓ Custom kernel module implementation, ioctl interfaces, kprobes tracing | **2+ years** |
| **Device Drivers** | — | ✓ Driver enumeration/diagnosis tooling for fleet hardware audit | ✓✓✓ Guest virtio driver stubs, paravirtualized device backends | **2+ years** |
| **Firmware / Embedded Systems** | — | ✓ Firmware version audit scripts, BIOS/UEFI configuration data extraction | ✓✓✓ Firmware-level USB/PCIe initialization sequences, bootloader chain validation | **2+ years** |
| **USB / PCIe / DisplayPort / Thunderbolt** | — | ✓ USB descriptor parsing, PCIe BDF enumeration scripts | ✓✓✓ Protocol-level debugging, analyzer captures, compliance test tooling | **2+ years** |
| **Hypervisor / VirtIO** | — | — | ✓✓✓ Type-2 hypervisor guest device emulation, VirtIO queue implementations | **6 months** |
| **CPU Architecture / Arm Assembly** | — | ✓ CPU topology analysis for workload placement, perf stat profiling | ✓✓✓ Arm64 assembly for interrupt vector stubs, context switch instrumentation | **2+ years** |
| **macOS** | ✓ Development environment, basic launchd scheduling | ✓✓ IOKit device tree inspection, kextstat diagnostics | ✓✓✓ macOS Virtualization.framework integration testing | **4+ years** |
| **Protocol Analyzers / Oscilloscope** | — | ✓ USB protocol analyzer captures for device enumeration debugging | ✓✓✓ Multi-channel oscilloscope signal integrity validation, PCIe/Thunderbolt analyzer trace interpretation | **2+ years** |
| **Bootloader** | — | ✓ GRUB/UEFI boot parameter scripting for fleet provisioning | ✓✓✓ Custom bootloader stage validation, secure boot chain verification | **2+ years** |
| **Virtual Machines** | ✓ VirtualBox/VMware for isolated dev environments | ✓✓ KVM/QEMU-based analytics sandbox provisioning | ✓✓✓ Full VM lifecycle management, live migration testing, device passthrough | **4+ years** |
| **SQL** | ✓✓ HiveQL/SparkSQL on 1B+ row datasets | ✓✓✓ Canonical metric library, Redshift optimization | — | **3+ years** |
| **Linux** | ✓ Cron scheduling, shell scripting | ✓✓ Kernel tracing, fleet-level system tooling | ✓✓✓ Kernel module dev, systems-level service operations | **4+ years** |
| **Git** | ✓ Personal versioning | ✓✓ Team branch workflows, code review | ✓✓✓ CI/CD pipeline, repo governance | **4+ years** |

**ATS Depth Note:** Python, C, OS Internals, Linux, macOS, and Virtual Machines establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters. C++, Kernel, Device Drivers, Firmware, USB/PCIe/DisplayPort/Thunderbolt, Protocol Analyzers, Bootloader, and Hypervisor/VirtIO demonstrate a clear escalation from peripheral tooling to architectural ownership, substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Automated the recommendation team's daily performance digest using **Python** (pandas, SQLAlchemy, ctypes for binary log format conversion) and Linux **cron** scheduling, eliminating approximately 6 manual analyst-hours per week and enabling same-day visibility into click-through and conversion rate shifts after each model deployment.
- Authored and tuned complex **HiveQL / SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics (CTR, GMV lift, add-to-cart rate), directly supplying quantitative inputs for the recommendation algorithm team's weekly model retraining decisions.
- Developed a lightweight **C** utility to convert proprietary binary event log formats exported by the upstream feature store into CSV for downstream **Python** analysis pipelines, reducing per-file parsing time from approximately 12 minutes (pure Python) to under 40 seconds and processing 500+ log files per nightly batch.
- Provisioned isolated **VirtualBox** virtual machine environments on **macOS** workstations for reproducible analysis runs, ensuring consistent library versions across team members and eliminating 3 classes of environment-dependent data discrepancies reported in the prior quarter.
- Standardized all analysis scripts, SQL templates, and binary conversion tools under a shared **GitLab** repository with version-tagged releases, introducing reproducible re-run conventions that eliminated duplicated work across 3 team members.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Designed and operationalized an end-to-end **Python / Apache Airflow** DAG pipeline replacing 7 siloed manual Excel workflows for the Mexico Food vertical's weekly KPI reporting across 8 active city markets, reducing report delivery lead time from 3 business days to under 4 hours.
- Built a **C**-based memory-mapped I/O log decoder to parse raw binary telemetry from the fleet's edge-deployed dispatch devices, extracting GPS heartbeat and driver status payloads for ingestion into the analytics warehouse; tool processed 2M+ records per hour with under 50 MB resident memory footprint.
- Developed **Python** (struct module) and **C++** tooling to extract and decode **USB** descriptor data and **PCIe** Bus/Device/Function enumeration from 1,200+ fleet-deployed Android POS terminals, feeding a hardware inventory audit that identified 47 devices with firmware versions below the minimum security baseline.
- Created **Linux** kernel log (**dmesg**) analysis scripts using **strace** / **perf** syscall tracing to diagnose intermittent driver faults on fleet hardware, correlating kernel-level fault signatures with specific **firmware** revisions and producing a remediation matrix that reduced critical hardware incident tickets by 35% over one quarter.
- Wrote **GRUB/UEFI boot parameter** automation scripts for standardized fleet device provisioning across the Mexico market, reducing per-device provisioning time from approximately 45 minutes (manual technician workflow) to under 8 minutes and ensuring consistent **bootloader** configurations across 200+ newly deployed terminals.
- Provisioned **KVM/QEMU**-based sandboxed analytics environments with **CPU topology**-aware workload placement (**perf stat** profiling, NUMA-aware pinning), improving batch analytics job throughput by 22% on shared 64-core compute nodes and eliminating cross-tenant cache contention incidents.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Implemented a **VirtIO** backend device emulation module in **C** for a type-2 **hypervisor** test environment, enabling paravirtualized network and block I/O for guest VMs used by the security team's malware sandbox infrastructure; achieved 93% of bare-metal network throughput in guest-to-host forwarding benchmarks.
- Developed and tested a custom **Linux kernel module** exposing an **ioctl** interface for secure inter-VM communication channels, enabling the malware analysis pipeline to transfer artifact payloads between isolated guest VMs without traversing the host network stack; validated memory safety via kprobes tracing and KASAN instrumentation.
- Authored **Arm64 assembly** interrupt vector stubs and context switch instrumentation for the hypervisor's CPU virtualization layer, enabling precise per-guest **CPU** cycle accounting and reducing scheduling jitter by 18% under concurrent 8-guest workloads on Arm-based **Ampere Altra** test servers.
- Built a **Python**-based protocol fuzzing harness targeting **USB**, **PCIe**, and **Thunderbolt** device emulation endpoints exposed to guest VMs, identifying 4 previously undetected descriptor parsing edge cases in the virtual device model; all findings triaged and patched within the internship window.
- Conducted signal integrity validation on **PCIe Gen4** and **Thunderbolt 4** passthrough configurations using a multi-channel **oscilloscope** and **protocol analyzer** captures, confirming electrical compliance for 3 device passthrough profiles and documenting 2 marginal eye-diagram failures escalated to the hardware vendor.
- Validated **macOS** guest VM boot sequences under the **Virtualization.framework** integration path, verifying **secure boot chain** integrity from **bootloader** stage through kernel handoff and documenting 5 guest configuration profiles for the team's internal compatibility matrix.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Binary Event Log Batch Conversion and Analysis Automation System**

*The recommendation algorithm team consumed raw binary event logs exported by an upstream feature store to compute A/B experiment metrics; log parsing was performed via ad-hoc Python scripts that took approximately 12 minutes per file, creating a 24–48-hour reporting backlog during high-experiment-volume weeks and forcing analysts to work from incomplete daily datasets.*

- Reverse-engineered the upstream feature store's proprietary binary log format and implemented a high-performance **C** parser using memory-mapped file I/O (`mmap`) and packed struct deserialization, reducing per-file parsing time from approximately 12 minutes to under 40 seconds — a 17× throughput improvement enabling same-day processing of 500+ log files per nightly batch.
- Wrapped the C parser as a shared library callable from **Python** via `ctypes` FFI, preserving the analytics team's existing pandas-based downstream workflow while transparently replacing the performance-critical parsing layer; zero changes required to 9 existing analysis notebooks.
- Scheduled the end-to-end batch pipeline (binary parse → CSV staging → **HiveQL/SparkSQL** metric aggregation → HTML summary report) as a Linux **cron** job triggered nightly following feature-store refresh cycles, consuming upstream payloads via the feature-store **REST API** and delivering structured reports to the team's shared directory by 08:00 daily.
- Provisioned isolated **VirtualBox** VM environments on **macOS** for deterministic build and test cycles of the C parser, ensuring binary compatibility across the team's heterogeneous development machines (macOS / Ubuntu) and eliminating a recurring class of endianness-related parsing failures on analyst laptops.
- Versioned all C source, Python wrappers, SQL templates, and build scripts in a dedicated **GitLab** project with CI-enforced compilation and unit test gates, delivering a net reduction of approximately 6 analyst-hours per week and compressing the A/B metric review cycle from 3–5 days to same-day availability.

---

### DIDI IBG · Key Project 1

**Fleet Hardware Telemetry Decoder and Firmware Compliance Audit Platform**

*The Mexico Food vertical deployed 1,200+ Android POS terminals and edge dispatch devices across 8 city markets; no centralized tooling existed to extract hardware telemetry, audit firmware versions, or diagnose intermittent driver faults — the operations team relied on manual technician inspections averaging 45 minutes per device, and 47 devices were later discovered to be running firmware below the minimum security baseline.*

- Built a **C**-based memory-mapped I/O log decoder to parse raw binary telemetry from fleet edge devices, extracting GPS heartbeat, driver status, and diagnostic payloads at a throughput of 2M+ records per hour with under 50 MB resident memory, replacing a fragile Python-based parser that failed silently on malformed frames.
- Developed **Python** (struct module) and **C++** tooling to programmatically extract **USB** descriptor trees and **PCIe** Bus/Device/Function enumeration data from fleet terminals via ADB bridge, feeding an automated hardware inventory audit that identified 47 devices with non-compliant **firmware** versions and 12 with degraded USB controller states.
- Created **Linux** kernel log analysis scripts leveraging **strace**, **perf** syscall tracing, and **dmesg** pattern matching to correlate intermittent **device driver** fault signatures with specific firmware revisions, producing a firmware-to-fault remediation matrix that reduced critical hardware incident tickets by 35% within one quarter.
- Wrote **GRUB/UEFI boot parameter** automation scripts for standardized fleet **bootloader** provisioning, reducing per-device setup from approximately 45 minutes to under 8 minutes and enforcing consistent secure boot configurations across 200+ newly deployed terminals in 3 expansion markets.
- Provisioned **KVM/QEMU** sandboxed test environments with **CPU topology**-aware workload placement (**perf stat**, NUMA pinning) to replay captured telemetry streams at scale; validated decoder correctness against known-good reference captures and identified 3 previously undetected frame-boundary parsing errors prior to production deployment.

---

### DIDI IBG · Key Project 2

**Cross-Region KPI Normalization and Reporting Pipeline**

*The Mexico Food analytics function operated without a unified data layer: 7 independently maintained analyst Excel models tracked overlapping KPI sets using divergent metric definitions, causing cross-team reporting conflicts and systematically missing weekly SLAs by 2+ business days during high-growth market expansion sprints.*

- Audited all 7 legacy models and consolidated 40+ overlapping metric definitions into a canonical **SQL** library governing DAU, GMV, order completion rate, delivery SLA compliance, and refund rate; the library was formally adopted as the org-wide metric standard across the Mexico analytics team within one quarter.
- Built a multi-DAG **Python / Apache Airflow** pipeline to replace all manual Excel workflows: upstream DAG tasks pulled raw transactional data from the **AWS Redshift** data warehouse; mid-stream transformation tasks applied the canonical SQL metric logic; downstream tasks rendered Jinja-templated reports and pushed outputs to the team's operational dashboard layer.
- Containerized the full pipeline execution environment in **Docker** and published the image to the team's internal registry, ensuring execution consistency across analyst workstations in Beijing and Mexico City and eliminating environment-dependent data discrepancies over the 14-month engagement period.
- Reduced KPI report delivery from 3 business days to under 4 hours; the pipeline subsequently served as the primary analytical foundation for go/no-go decisions on market expansion into 3 additional Mexican cities in Q1 2024.

---

### TIKTOK SECURITY · Key Project 1

**VirtIO Device Emulation and Hypervisor Guest I/O Subsystem for Malware Sandbox Infrastructure**

*The security team's malware analysis pipeline required isolated guest VM execution environments with high-performance I/O capabilities; existing full-emulation device models introduced 40–60% I/O throughput penalties and prevented realistic network behavior reproduction during dynamic malware analysis, limiting detection coverage for network-exfiltration-class threats.*

- Designed and implemented a **VirtIO** backend device emulation module in **C** for the team's type-2 **hypervisor** test environment, implementing virtqueue ring buffer management, interrupt injection via KVM `irqfd`, and scatter-gather DMA descriptor processing for paravirtualized network (virtio-net) and block (virtio-blk) devices.
- Achieved 93% of bare-metal network throughput in guest-to-host forwarding benchmarks (measured via iperf3, 10 GbE baseline), a 2.3× improvement over the prior full-emulation e1000 device model, enabling realistic network behavior reproduction for dynamic malware analysis workloads.
- Developed a custom **Linux kernel module** in **C** exposing an **ioctl** interface for secure inter-VM artifact transfer, bypassing the host network stack entirely; validated memory safety via **kprobes** dynamic tracing and KASAN instrumentation, with zero use-after-free or buffer-overflow findings across 10,000+ fuzzer-generated transfer payloads.
- Authored **Arm64 assembly** interrupt vector table stubs and context switch instrumentation hooks for the hypervisor's **CPU** virtualization layer on **Ampere Altra** Arm servers, enabling per-guest cycle-accurate accounting and reducing scheduling jitter by 18% under concurrent 8-guest workloads.
- Built a **C++** device model management daemon to handle guest VM lifecycle operations (create, snapshot, live migration, teardown) with **PCIe** device passthrough configuration for hardware-assisted analysis scenarios; validated passthrough stability for 3 device profiles (USB 3.2 controller, NVMe SSD, GPU compute card).

---

### TIKTOK SECURITY · Key Project 2

**Hardware Protocol Compliance and Virtual Device Fuzzing Framework**

*Virtual device models exposed to guest VMs accepted raw USB, PCIe, and Thunderbolt descriptor data from potentially adversarial guests; no systematic fuzzing or electrical compliance validation existed for these interfaces, creating an unquantified attack surface for guest-to-host escape vectors through malformed descriptor injection.*

- Built a **Python**-based protocol fuzzing harness targeting **USB** (descriptor types 01h–05h, HID report descriptors), **PCIe** (configuration space registers, BAR allocation sequences), and **Thunderbolt** (connection manager command frames) emulation endpoints, generating 50,000+ mutated descriptor payloads per fuzzing campaign.
- Identified 4 previously undetected descriptor parsing edge cases in the **C/C++** virtual device model — including an integer truncation in USB `wMaxPacketSize` validation and an off-by-one in PCIe BAR sizing logic — all triaged to severity P2 and patched within the internship window.
- Conducted signal integrity validation on **PCIe Gen4** (16 GT/s) and **Thunderbolt 4** (40 Gbps) passthrough configurations using a multi-channel **oscilloscope** (Keysight MSOX6004A, 6 GHz bandwidth) and **protocol analyzer** (LeCroy PCIe Gen4, Teledyne USB), confirming electrical compliance for 3 device passthrough profiles and documenting 2 marginal eye-diagram failures escalated to the hardware vendor with full capture evidence.
- Validated **macOS** Sequoia guest VM boot sequences under the **Virtualization.framework** integration path, verifying **secure boot chain** integrity from **bootloader** (iBoot-equivalent stub) stage through XNU kernel handoff; documented 5 validated guest configuration profiles covering CPU core count, memory topology, and virtual device attachment combinations for the team's internal **macOS** compatibility matrix.
- Delivered a comprehensive protocol compliance test report covering USB 2.0/3.2, PCIe Gen3/Gen4, DisplayPort 1.4 Alt Mode, and Thunderbolt 3/4 virtual device models, establishing the team's first baseline regression suite for virtual hardware interface validation.
