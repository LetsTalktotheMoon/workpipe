# Reviewer 迭代对比

## 分数表

| Case | old_pipe | v1_current | v2_hr_recal |
| --- | --- | --- | --- |
| extra-capitalone-ai | 89.2 (fail) | 83.9 (fail) | 95.2 (pass) |
| extra-dataminr-infra | 92.8 (fail) | 84.5 (fail) | 97.4 (pass) |
| extra-healthequity-dotnet | 93.5 (pass) | 79.5 (fail) | 88.8 (pass) |
| extra-ramp-platform | 97.0 (pass) | 89.8 (fail) | 95.8 (fail) |
| extra-synechron-backend | 89.5 (fail) | 89.5 (fail) | 95.0 (pass) |
| extra-zoox-llm | 94.4 (pass) | 88.8 (fail) | 96.8 (pass) |
| same-amazon | 93.3 (pass) | 89.8 (fail) | 97.8 (pass) |
| same-aws | 94.6 (pass) | 81.5 (fail) | 94.4 (fail) |
| same-google | 79.0 (fail) | 83.4 (fail) | 92.8 (pass) |
| same-microsoft | 88.1 (fail) | 80.9 (fail) | 90.4 (pass) |

## 扣分项表

| Case | old_pipe 主要扣分 | v1_current 主要扣分 | v2_hr_recal 主要扣分 |
| --- | --- | --- | --- |
| extra-capitalone-ai | r4_rationality:high:Professional Summary | P2-001:high:Summary 第一句<br>P3E-002:critical:Experience | Temu · R&D | Jun 2021 – Feb 2022 | none |
| extra-dataminr-infra | r1_writing_standard:high:Professional Summary, sentence 3 | P2-010:high:Professional Summary 第三句<br>P3E-002:critical:Temu | Data Analyst | Jun 2021 – Feb 2022 | Shanghai | none |
| extra-healthequity-dotnet | none | P2-001:high:Professional Summary 第一句<br>P3B-001:high:Skills section<br>P3E-002:critical:Temu · Data Analyst | Jun 2021 – Feb 2022 | Shanghai | P3B-001:high:Skills section |
| extra-ramp-platform | none | P3E-002:critical:Temu | Data Analyst | Jun 2021 – Feb 2022 | P3E-010:critical:TikTok · Security | Software Engineer Intern | Jun 2025 – Dec 2025 | Bullet 2 |
| extra-synechron-backend | r1_writing_standard:high:Professional Summary | P3E-002:critical:Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai | none |
| extra-zoox-llm | none | P3C-010:high:TikTok Experience bullets<br>P3E-002:critical:Temu | Jun 2021 – Feb 2022 | P3C-010:high:TikTok · Security Experience 全段 |
| same-amazon | none | P3E-002:critical:Temu Experience, header and dates | none |
| same-aws | none | P1-051:high:## Skills<br>P2-001:high:## Professional Summary, bullet 1<br>P2-010:high:## Professional Summary, bullet 3<br>P3E-002:critical:Temu · R&D | Jun 2021 – Feb 2022 | Shanghai | P3E-010:critical:TikTok project: Security Investigation Retrieval Assistant, bullet 2 |
| same-google | r0_authenticity:critical:## Skills > Cloud | P2-001:high:Professional Summary, sentence 1<br>P3E-002:critical:Temu · Data Analyst | Jun 2021 – Feb 2022 | Shanghai | P3A-002:high:TikTok Experience, project bullet 1 |
| same-microsoft | r2_jd_fitness:high:## Skills<br>r2_jd_fitness:high:Professional Summary / TikTok experience<br>r4_rationality:high:Professional Summary 第 1 句<br>r4_rationality:high:TikTok experience | P3B-001:high:Skills<br>P3C-010:high:TikTok Experience<br>P3E-002:critical:Temu Experience | P3B-001:high:Skills; Professional Summary; TikTok Experience<br>P3C-010:high:Professional Summary; TikTok Experience |
