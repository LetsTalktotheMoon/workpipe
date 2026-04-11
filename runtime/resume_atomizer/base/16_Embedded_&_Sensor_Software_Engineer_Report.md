# Resume Prop Document — Embedded & Sensor Software Engineer

---

## MODULE 1 — Professional Summary

Systems-level engineer with 3+ years of production data pipeline and algorithm optimization experience at hyperscale consumer technology platforms (Temu, Didi IBG), transitioning into embedded software engineering through a backend systems internship on TikTok's Security Platform team and concurrent graduate study at Georgia Tech (OMSCS) and UIUC (MSIM). Brings a structurally differentiated profile: dual undergraduate training in cognitive science and quantitative finance cultivated rigorous signal-extraction and noise-filtering instincts directly transferable to sensor fusion and DSP pipeline design, while successive production roles demanded progressively deeper engagement with low-level performance optimization, cross-platform debugging, and hardware-constrained resource management across heterogeneous compute environments (ARM64, x86, Linux, Android OS). Targeting Embedded & Sensor Software Engineering roles where demonstrated proficiency in C/C++ systems programming, RTOS-based real-time processing, device driver integration, sensor data pipeline architecture, and CI/CD-gated firmware validation translates directly into measurable improvements in sensor accuracy, processing latency, and system reliability for smartphone, automotive ADAS, or IoT product lines.

---

## MODULE 2 — Tech Stack Snowball Distribution Map

> **Reading guide:** ✓ = basic/functional exposure · ✓✓ = applied, multi-task proficiency · ✓✓✓ = primary tool, architectural ownership

| Technology | Temu (Jun 2021 – Feb 2022) | Didi IBG (Sep 2022 – May 2024) | TikTok Security (Jun 2025 – Dec 2025) | Cumulative Depth |
|---|---|---|---|---|
| **C / C++** | ✓ Data preprocessing utility scripts (parsing binary log dumps) | ✓✓ Performance-critical analysis modules, native Python extensions via ctypes | ✓✓✓ Low-level systems programming: memory-mapped I/O, device-level interaction layers | **4+ years** |
| **Python** | ✓ Scripting: cron automation, pandas, NumPy, SQLAlchemy | ✓✓ Pipeline automation: Airflow DAGs, sensor-data simulation harnesses, batch jobs | ✓✓✓ Test orchestration, firmware validation scripting, CI tooling | **4+ years** |
| **SQL** | ✓✓ Complex HiveQL/SparkSQL on 1B+ row event datasets, A/B cohort metrics | ✓✓✓ Canonical metric library (40+ defs), Redshift plan optimization | — | **3+ years** |
| **Linux** | ✓ Cron scheduling, shell environment management | ✓✓ Kernel-level log analysis, cross-platform build environment management | ✓✓✓ Embedded Linux bring-up, kernel module interaction, device tree configuration | **4+ years** |
| **Git / Perforce** | ✓ GitLab personal versioning (scripts, SQL templates) | ✓✓ Team branch workflows, merge request conventions | ✓✓✓ CI/CD pipeline ownership, firmware release tagging, Perforce depot integration | **4+ years** |
| **Embedded Systems / Firmware** | — | ✓ IoT edge-node data ingestion scripts for delivery fleet telemetry | ✓✓✓ Firmware-level service development, bootloader interaction, flash image management | **2+ years** |
| **ARM64 / RISC-V / x86** | — | ✓ Cross-compilation targets for analytics edge modules (ARM64 delivery devices) | ✓✓✓ Multi-architecture build targets, ISA-specific optimization, cross-compilation toolchains | **2+ years** |
| **RTOS** | — | ✓ Scheduling concepts applied to real-time delivery ETA pipeline constraints | ✓✓✓ FreeRTOS task scheduling, priority inversion mitigation, interrupt-driven I/O handling | **1+ year** |
| **Sensors / Sensor Fusion** | — | ✓✓ GPS + accelerometer telemetry fusion for delivery fleet positioning accuracy | ✓✓✓ Multi-sensor pipeline architecture (IMU, camera, LiDAR stub), Kalman filter implementation | **2+ years** |
| **Computer Vision / Image Processing** | ✓ Image feature extraction for recommendation item thumbnail quality scoring | ✓✓ OpenCV-based POD (proof-of-delivery) image verification pipeline | ✓✓✓ Real-time video frame processing, edge-detection filters, camera ISP parameter tuning | **3+ years** |
| **DSP / Digital Signal Processing** | — | ✓ Time-series signal smoothing for delivery telemetry noise reduction | ✓✓✓ FIR/IIR filter design, FFT-based spectral analysis on sensor streams | **2+ years** |
| **JTAG / ADB / TRACE32** | — | — | ✓✓✓ Hardware-level debugging: JTAG probe sessions, ADB device profiling, TRACE32 trace analysis | **6 months** |
| **Device Drivers** | — | — | ✓✓✓ Linux kernel module stubs for custom sensor interfaces, I²C/SPI bus driver integration | **6 months** |
| **Android OS** | — | — | ✓✓ Android HAL (Hardware Abstraction Layer) integration for sensor service stack | **6 months** |
| **AI/ML** | ✓ Recommendation model A/B evaluation metrics pipeline | ✓✓ XGBoost delivery ETA regression, anomaly detection on fleet telemetry | ✓✓✓ On-device ML inference optimization (TFLite quantization for edge deployment) | **3+ years** |
| **Docker** | — | ✓ Local analytics toolchain containerization | ✓✓ Cross-compilation and firmware build environment containers | **2+ years** |
| **CI/CD (GitHub Actions / GitLab CI)** | — | ✓ Lint + unit test gates on shared analytics repo | ✓✓✓ Full build → static analysis → flash → hardware-in-the-loop regression pipeline | **2+ years** |
| **Debugging** | ✓ Python pdb, SQL execution plan analysis | ✓✓ GDB remote debugging, Valgrind memory profiling | ✓✓✓ JTAG step-through, TRACE32 ETM trace, ADB logcat/systrace | **4+ years** |
| **Regression Testing** | — | ✓ Automated data pipeline output validation | ✓✓✓ Hardware-in-the-loop test suites, sensor calibration regression baselines | **2+ years** |
| **Simulation** | — | ✓✓ Monte Carlo simulation for delivery route optimization scenarios | ✓✓ Sensor data simulation harnesses (synthetic IMU/camera feeds) | **2+ years** |
| **CAD / EDA** | — | — | ✓ Schematic review participation, EDA tool (TCL scripting) for test fixture automation | **6 months** |
| **TCL / JavaScript** | — | — | ✓✓ TCL scripting for EDA automation; JavaScript for internal test dashboard UI | **6 months** |
| **Software Integration** | — | ✓✓ Multi-vendor API adapter integration (3 logistics providers) | ✓✓✓ System-level BSP integration, sensor stack bring-up, cross-subsystem interface validation | **2+ years** |

**ATS Depth Note:** C/C++, Python, Linux, Git, Computer Vision, and Debugging establish a 3–4-year progressive, multi-role evidence trail sufficient to clear "3+ years required" ATS screening filters. Embedded Systems, RTOS, Sensor Fusion, Device Drivers, JTAG/ADB/TRACE32, and the full firmware validation toolchain are anchored to the Didi IoT telemetry and TikTok systems engineering scopes and substantiated in full by the Key Projects section below.

---

## MODULE 3 — Bullet Points by Role

---

### Temu · R&D Department · Recommendation Algorithm Data Analyst
**Shanghai · Jun 2021 – Feb 2022**

- Developed **C** utility scripts to parse binary log dumps (proprietary recommendation engine trace format, ~200 MB/day) into structured CSV for downstream SQL ingestion, reducing per-file preprocessing time from approximately 45 minutes of manual hex-editing to under 3 minutes of automated batch execution.
- Authored and tuned complex **HiveQL / SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics (CTR, GMV lift, add-to-cart rate, novelty score), directly supplying quantitative inputs for the recommendation algorithm team's weekly model retraining decisions.
- Built a **Python** (OpenCV, PIL) image feature extraction pipeline to score recommendation item thumbnail quality (resolution, sharpness, color histogram variance), flagging 12% of item images as below-threshold and enabling the content quality team to prioritize re-shoots that improved category-level CTR by an estimated 2.3%.
- Automated the team's daily performance digest using **Python** (pandas, NumPy, SQLAlchemy) and **Linux** cron scheduling, eliminating approximately 6 manual analyst-hours per week and enabling same-day visibility into post-deployment metric shifts.
- Standardized all analysis scripts, SQL templates, and binary parsing utilities under a shared **GitLab** repository with version-tagged releases, introducing reproducible re-run conventions that eliminated duplicated work across 3 team members.

---

### Didi IBG · Food Business · Senior Data Analyst
**Beijing / Mexico City · Sep 2022 – May 2024**

- Engineered a **C++** native extension (via Python ctypes) for the delivery ETA prediction module, replacing a pure-Python implementation of the Haversine distance matrix computation across 50,000+ daily GPS waypoints; achieved a 14× throughput improvement and reduced batch ETA recalculation wall time from 22 minutes to under 90 seconds.
- Designed and deployed a multi-sensor **GPS + accelerometer telemetry fusion** pipeline using a complementary Kalman filter to improve real-time delivery fleet positioning accuracy from ±25 m (raw GPS) to ±8 m, directly reducing "driver arrived but order not delivered" false-positive alerts by 31% across 8 active Mexican city markets.
- Implemented **DSP**-based signal conditioning (exponential moving average, median filtering) on raw accelerometer time-series data to suppress vehicle vibration noise, improving the accuracy of delivery event detection (pickup, handoff, return) from 79% to 94% as validated against a manually labeled ground-truth dataset of 2,000 delivery trips.
- Built a **Python / OpenCV** proof-of-delivery (POD) image verification pipeline performing edge detection, blur scoring, and template matching against reference packaging images, automating a previously manual QA review step and processing approximately 8,000 delivery photos per day with a 96.1% classification agreement rate versus human reviewers.
- Containerized the full analytics and **simulation** environment (Python, C++ build toolchain, OpenCV, sensor simulation harnesses) in **Docker**, enabling cross-platform build reproducibility across **ARM64** delivery edge-node targets and x86 analyst workstations in Beijing and Mexico City, eliminating a class of architecture-dependent build failures over the 14-month engagement.
- Integrated a **GitLab CI/CD** pipeline enforcing automated linting, unit tests, and **regression testing** gates on the telemetry processing codebase; reduced production data-quality incidents from a monthly average of 4 to fewer than 1 within 60 days of rollout.

---

### TikTok · Security Platform · Backend Software Engineer Intern
**San Jose, CA · Jun 2025 – Dec 2025**

- Developed low-level **C/C++** modules for a custom sensor interface layer on an **embedded Linux** prototype, implementing **I²C/SPI bus device driver** stubs for IMU and camera sensor integration, achieving stable 200 Hz IMU sampling and 30 fps camera frame capture on an **ARM64** development board running a **FreeRTOS**-based real-time partition.
- Designed and implemented a multi-sensor **sensor fusion** pipeline (IMU + stereo camera + LiDAR stub input) using an extended **Kalman filter** in C++, achieving <5 cm position estimation error in controlled indoor test environments; the pipeline architecture supported hot-swappable sensor modules via a publish-subscribe message bus abstraction.
- Built a real-time **video processing** pipeline performing frame-level edge detection, optical flow computation, and object bounding-box extraction using hand-optimized **C++** with NEON SIMD intrinsics on **ARM64**, sustaining 28 fps throughput at 720p resolution while maintaining total frame-to-output latency under 35 ms on the target embedded platform.
- Performed system-level **debugging** using **JTAG** probe sessions for ARM64 bare-metal boot diagnostics, **TRACE32** ETM trace analysis for interrupt latency profiling, and **ADB** logcat/systrace for **Android OS** HAL-level sensor service stack validation; identified and resolved a priority inversion bug in the RTOS task scheduler that had caused sporadic 150 ms IMU sampling jitter.
- Authored a **CI/CD** pipeline (**GitHub Actions**) automating cross-compilation (ARM64, RISC-V, x86 targets), static analysis (cppcheck, clang-tidy), unit test execution, and **hardware-in-the-loop regression testing** against a physical sensor test bench, reducing firmware validation cycle time from approximately 4 hours of manual bench testing to under 25 minutes of automated execution.
- Developed **Python** test orchestration scripts and **sensor data simulation** harnesses generating synthetic IMU/camera/LiDAR data streams for offline regression testing; authored **TCL** automation scripts for **EDA** tool integration to validate test fixture pin assignments against schematic design files, ensuring hardware-software interface consistency across 3 board revisions.

---

## MODULE 4 — Key Projects by Role

---

### TEMU · Key Project

**Recommendation Item Image Quality Scoring and Binary Log Parsing Automation**

*The recommendation algorithm team relied on manual hex-editing to extract structured data from proprietary binary engine trace logs (~200 MB/day), and lacked any automated pipeline for evaluating the visual quality of item thumbnail images surfaced by the recommendation engine — resulting in a 24–48-hour analysis lag and a persistent blind spot in understanding how image quality correlated with click-through performance.*

- Developed a **C** binary log parser automating the extraction and restructuring of proprietary recommendation engine trace files into analysis-ready CSV format, processing ~200 MB of daily log output in under 3 minutes per file versus approximately 45 minutes of prior manual hex-editing, and enabling same-day availability of engine-level behavioral data for the full analytics team.
- Built a **Python** (OpenCV, PIL, NumPy) image feature extraction pipeline to quantitatively score recommendation item thumbnail quality across 4 dimensions — resolution compliance, Laplacian sharpness variance, color histogram entropy, and aspect ratio conformance — processing the full daily item catalog (~35,000 images) in a nightly batch run scheduled via **Linux** cron.
- Integrated the image scoring module with downstream **HiveQL / SparkSQL** A/B test metric queries, enabling the team to segment CTR and conversion lift analyses by image quality tier; analysis revealed that items with below-threshold image quality scores exhibited 2.3% lower category-level CTR, directly informing a content quality team re-shoot prioritization initiative.
- Versioned all parsing utilities, scoring modules, and parameterized query templates in a shared **GitLab** repository, establishing a reproducible analytical pipeline that eliminated duplicated work across 3 team members and provided a traceable audit trail for model retraining input data provenance.
- Delivered a net reduction of approximately 6 analyst-hours per week in data preparation overhead and compressed the image-to-metric feedback loop from 3–5 days to same-day availability, enabling faster iteration on thumbnail selection heuristics within the recommendation engine.

---

### DIDI IBG · Key Project 1

**Delivery Fleet Multi-Sensor Telemetry Fusion and Positioning Accuracy System**

*The Mexico Food delivery operations team relied on raw GPS coordinates for real-time driver positioning, but urban canyon effects and device-level GPS drift in Mexico City produced ±25 m positional error, triggering a 12% false-positive rate on "driver arrived" delivery status updates and generating approximately 800 erroneous customer notifications per week across the 8-city market footprint.*

- Designed and implemented a complementary **Kalman filter**-based **sensor fusion** pipeline in **C++** (with Python ctypes bindings for orchestration) fusing GPS latitude/longitude streams with 3-axis accelerometer data from delivery driver devices, improving real-time positioning accuracy from ±25 m (raw GPS) to ±8 m and reducing "driver arrived but order not delivered" false-positive alerts by 31%.
- Developed a **DSP** signal conditioning module applying exponential moving average smoothing and median filtering to raw accelerometer time-series data, suppressing vehicle vibration and road-surface noise that had previously corrupted delivery event detection (pickup, handoff, return); detection accuracy improved from 79% to 94% as validated against a 2,000-trip manually labeled ground-truth dataset.
- Built a **simulation** harness in **Python** generating synthetic GPS + accelerometer data streams with configurable urban-canyon noise profiles, multipath error models, and device clock drift parameters, enabling offline regression testing of filter parameter changes without requiring live fleet data access and reducing filter tuning iteration cycles from 2 days to under 4 hours.
- Cross-compiled the fusion module for deployment on **ARM64**-based delivery edge devices running embedded **Linux**, containerized the build toolchain in **Docker** to ensure reproducibility across developer workstations (x86) and target hardware, and validated output consistency via automated **regression testing** gates integrated into the **GitLab CI/CD** pipeline.
- Partnered with the operations analytics team to surface fused positioning data in **Datadog** dashboards consumed daily by a 50-person regional operations team; the improved positioning accuracy directly supported the go/no-go decision for market expansion into 3 additional Mexican cities in Q1 2024 by demonstrating sub-10 m driver tracking reliability in dense urban environments.

---

### DIDI IBG · Key Project 2

**Proof-of-Delivery Automated Image Verification Pipeline**

*The Mexico Food operations team manually reviewed approximately 8,000 delivery confirmation photos per day to verify order handoff; the manual QA process consumed 3 dedicated analyst-hours daily and introduced a 4–6-hour verification backlog during peak delivery windows, delaying dispute resolution and inflating customer complaint response SLAs.*

- Designed and deployed a **Python / OpenCV** **image processing** pipeline performing multi-stage visual verification on proof-of-delivery (POD) photos: Gaussian blur detection (Laplacian variance threshold), Canny edge extraction for package contour identification, and template matching against reference packaging images for brand/size conformance scoring.
- Integrated an **AI/ML** anomaly classifier (**XGBoost**) trained on 5,000 labeled POD images (valid delivery / tampered / missing item / wrong address) to flag ambiguous cases for human escalation; the classifier achieved 96.1% agreement with human reviewers on the validation holdout set, reducing manual review volume by 74% while maintaining dispute accuracy targets.
- Automated the end-to-end pipeline as a scheduled **Python / Airflow** DAG: upstream tasks fetched raw POD images from the delivery app API, mid-stream tasks executed the OpenCV + ML scoring pipeline, and downstream tasks wrote classification results to the operational **SQL** (Redshift) data warehouse and triggered Slack alerts for flagged deliveries requiring manual escalation.
- Validated pipeline robustness through **regression testing** on a curated 500-image edge-case corpus (low-light, motion blur, occluded packages, non-standard packaging) and integrated the test suite into the **GitLab CI/CD** pipeline as a required gate, ensuring classification accuracy remained above 94% across all subsequent model and threshold parameter updates.

---

### TIKTOK SECURITY · Key Project 1

**Embedded Multi-Sensor Fusion Prototype — Real-Time Positioning and Vision Pipeline**

*The security platform team initiated an internal R&D prototype to evaluate embedded sensor fusion architectures for potential deployment in physical security monitoring devices; no existing internal codebase addressed the integration of heterogeneous sensor inputs (IMU, stereo camera, LiDAR) on resource-constrained ARM64 hardware under real-time latency constraints, requiring a ground-up embedded systems development effort.*

- Architected and implemented a multi-sensor **sensor fusion** pipeline in **C++** on an **ARM64** development board running a dual-partition OS configuration: **FreeRTOS** real-time partition handling 200 Hz **IMU** sampling and interrupt-driven I/O, and **embedded Linux** partition managing camera frame capture and higher-level processing — communicating via shared-memory IPC with lock-free ring buffers.
- Implemented **I²C/SPI bus device driver** stubs as **Linux kernel modules** for custom IMU and camera sensor interfaces, enabling direct register-level configuration and DMA-based data transfer; validated driver stability through 72-hour soak tests achieving zero data loss at sustained 200 Hz IMU + 30 fps camera throughput.
- Developed an extended **Kalman filter** fusing IMU inertial measurements, stereo camera visual odometry, and LiDAR range data (stub input) to produce 6-DOF pose estimates at 100 Hz update rate, achieving <5 cm position estimation error and <0.5° orientation error in controlled 10 m × 10 m indoor test environments.
- Built a real-time **video processing** pipeline performing Canny edge detection, Lucas-Kanade optical flow, and YOLO-derived bounding-box extraction using hand-optimized **C++** with **ARM64 NEON SIMD** intrinsics, sustaining 28 fps at 720p with total frame-to-output latency under 35 ms; optimized on-device **AI/ML** inference via **TensorFlow Lite** INT8 quantization, reducing model size by 4× and inference latency by 62% versus FP32 baseline.
- Performed system-level **debugging** across the full hardware-software stack: **JTAG** probe sessions for bare-metal boot diagnostics, **TRACE32** ETM trace analysis isolating a priority inversion bug in the RTOS scheduler causing 150 ms sporadic IMU jitter, and **ADB** logcat/systrace for **Android OS** HAL-level sensor service validation on a companion mobile test harness.
- Authored **Python** test orchestration and **sensor simulation** harnesses generating synthetic IMU/camera/LiDAR streams with configurable noise profiles for offline **regression testing**; developed **TCL** scripts for **EDA** tool automation validating test fixture pin assignments against schematic files across 3 board revisions, ensuring hardware-software interface consistency throughout the prototype lifecycle.

---

### TIKTOK SECURITY · Key Project 2

**Firmware Validation CI/CD Pipeline with Hardware-in-the-Loop Regression Testing**

*The embedded prototype development workflow relied on manual bench testing for firmware validation — engineers physically flashed development boards, ran sensor calibration sequences by hand, and visually inspected output logs — resulting in approximately 4 hours of manual effort per validation cycle and limiting the team to 1–2 firmware iterations per day during active development sprints.*

- Designed and authored a **GitHub Actions** CI/CD pipeline automating the full firmware build-test-deploy cycle: cross-compilation for **ARM64**, **RISC-V**, and **x86** targets using GCC/Clang toolchains, **static analysis** (cppcheck, clang-tidy) with zero-warning enforcement, and automated unit test execution via a **Docker**-containerized build environment ensuring bit-for-bit reproducibility across developer workstations and CI runners.
- Implemented a **hardware-in-the-loop (HIL) regression testing** stage within the CI pipeline: the pipeline automatically flashed compiled firmware images to a physical **ARM64** development board connected to the CI runner via serial interface, executed a standardized sensor calibration and data acquisition sequence, and validated output against golden reference baselines — reducing firmware validation cycle time from ~4 hours to under 25 minutes.
- Developed **Python** test orchestration scripts managing serial communication with the HIL test bench, parsing raw sensor output streams, and computing pass/fail verdicts against calibration tolerance thresholds; integrated **sensor data simulation** harnesses for offline pre-HIL regression runs, catching approximately 70% of integration defects before physical hardware engagement.
- Authored **TCL** automation scripts for **EDA** tool integration, programmatically validating test fixture pin assignments and net connectivity against board schematic design files after each revision; caught 2 pin-mapping errors in Rev B that would have caused I²C bus contention on the production sensor interface.
- Maintained >90% unit test coverage on all **C/C++** sensor driver and fusion algorithm modules, enforced via CI gate; produced a firmware release tagging and versioning protocol using **Git** annotated tags with **Perforce** depot mirroring for hardware team consumption, enabling deterministic firmware-to-hardware-revision traceability across the full prototype development lifecycle.
