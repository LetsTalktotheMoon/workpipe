# PLACEHOLDER

PLACEHOLDER

---

## Professional Summary

* **Sensor Data & Signal Processing Engineer:** 3+ years of technical experience across high-scale platforms (**ByteDance/TikTok**, **DiDi**, **Temu**), specializing in **sensor fusion** pipeline architecture, **DSP**-based signal conditioning, **computer vision**/**image processing**, and **C**/**C++** performance-critical data processing on resource-constrained platforms.
* **End-to-End Sensor Pipeline Delivery:** Designs and ships production sensor data systems — from GPS/IMU **sensor fusion** via Kalman filtering and real-time **video processing** to **Python**/**C++** pipeline optimization, **simulation** harness development, and **CI/CD**-gated **regression testing** across **ARM64**, **x86**, and **Linux**/**Android OS** environments.
* **Collaboration & Impact:** National 2-Dan Go (Weiqi) competitor with a discipline for systematic thinking. Pursuing concurrent M.S. degrees at **Georgia Tech (OMSCS)** and **UIUC**, targeting sensor software roles spanning logistics, automotive, and IoT product lines.

---

## Work Experience

### Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA

**Jun 2025 – Dec 2025**

**_Core Sensor & Signal Processing Contributions:_**

* Built a real-time **video processing** pipeline for a hardware-side security monitoring module, performing frame-level edge detection, optical flow computation, and object bounding-box extraction using hand-optimized **C++** with **ARM64** NEON SIMD intrinsics; sustained 28 fps throughput at 720p with frame-to-output latency under 35ms (**image processing**).
* Optimized on-device **AI/ML** inference via TensorFlow Lite INT8 quantization on an **ARM64** target platform, reducing model size 4× and inference latency 62% for real-time anomaly classification.
* Authored a **CI/CD** pipeline (**GitHub Actions**) automating cross-compilation for **ARM64** and **x86** targets, static analysis, unit test execution, and **regression testing** against sensor data **simulation** harnesses — reducing validation cycle time from ~4 hours to under 25 minutes.
* Developed **Python** test orchestration scripts and sensor data **simulation** harnesses for offline **regression testing**; authored **TCL** automation scripts integrating **EDA** tool flows to validate test fixture signal integrity across 3 board revisions.
* Diagnosed sensor data pipeline stability issues via **ADB** logcat/systrace for **Android OS** HAL-level sensor service stack validation and **Linux** perf profiling; isolated and resolved a scheduling bug causing sporadic 150ms sampling jitter (**debugging**).

**_Project: Security Monitoring Sensor Fusion Prototype_**

* Developed an extended Kalman filter (**sensor fusion**) combining IMU inertial measurements and stereo camera visual odometry to produce 6-DOF pose estimates at 100 Hz update rate, achieving <5 cm position estimation error in controlled test environments.
* Implemented **C**/**C++** sensor interface modules for IMU and camera data acquisition on an **ARM64** development board running **embedded Linux**, achieving stable 200 Hz IMU sampling and 30 fps camera frame capture.
* Containerized the full build and **simulation** environment (**Python**, **C++** toolchain, **OpenCV**) in **Docker**, enabling cross-platform reproducibility across **ARM64** and **x86** targets.

### Senior Data Analyst | DiDi IBG · Food Business | Beijing / Mexico City

**Sep 2022 – May 2024**

* Designed and deployed a multi-**sensor** GPS + accelerometer telemetry **fusion** pipeline using a complementary Kalman filter, improving real-time delivery fleet positioning from ±25m to ±8m and reducing false-positive delivery alerts by 31% across 8 Mexican city markets.
* Implemented **DSP**-based signal conditioning (exponential moving average, median filtering) on raw accelerometer time-series data to suppress vehicle vibration noise, improving delivery event detection accuracy from 79% to 94%.
* Engineered a **C++** native extension (via **Python** ctypes) replacing a pure-Python Haversine distance matrix computation across 50,000+ daily GPS waypoints, achieving 14× throughput improvement and reducing batch ETA recalculation from 22 minutes to under 90 seconds.
* Built a **Python**/**OpenCV** proof-of-delivery **image** verification pipeline performing edge detection, blur scoring, and template matching; processed ~8,000 delivery photos per day at 96.1% classification agreement rate (**computer vision**).
* Containerized the full analytics and **simulation** environment in **Docker**, enabling cross-platform build reproducibility across **ARM64** edge-node targets and **x86** analyst workstations.
* Integrated a **GitLab CI/CD** pipeline enforcing automated linting, unit tests, and **regression testing** gates; reduced production data-quality incidents from 4/month to fewer than 1 within 60 days.

### Machine Learning Data Analyst | Temu · R&D · Recommendation Infra | Shanghai

**Jun 2021 – Feb 2022**

* Developed a **C** utility to parse binary log dumps (~200 MB/day) into structured CSV for downstream **SQL** ingestion, reducing per-file preprocessing time from ~45 minutes to under 3 minutes.
* Built a **Python**/**OpenCV** image feature extraction pipeline to score item thumbnail quality (resolution, sharpness, color histogram variance), flagging 12% of images as below-threshold; targeted re-shoots improved category-level CTR by 2.3% (**computer vision**).
* Authored and tuned **HiveQL**/**SparkSQL** queries against 1B+ row event datasets to extract A/B test cohort metrics, supplying quantitative inputs for weekly model retraining decisions.
* Standardized all analysis scripts, **SQL** templates, and binary parsing utilities under a shared **GitLab** repository with version-tagged releases (**Git**).

---

## Skills

**Languages:** C, C++, Python, TCL, SQL
**Sensors & DSP:** Sensor Fusion, Kalman Filter, DSP (Signal Conditioning), Computer Vision (OpenCV), Image/Video Processing, AI/ML
**Platforms:** ARM64, x86, Android OS, Linux, Embedded Linux
**Debugging & Validation:** ADB, EDA, Simulation, Regression Testing, Debugging
**DevOps:** GitHub Actions, GitLab CI, Docker, CI/CD, Git

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