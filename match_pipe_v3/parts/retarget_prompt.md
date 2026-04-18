你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

目标：尽可能少改动，在保留 seed 叙事骨架、结构质量和可信 scope 的前提下，让简历对齐目标 JD。

路由模式: retarget

## Retarget 原则
1. 这是在现有 seed 上微调，不是从零重写
2. 总改动预算控制在约 35%
3. 优先保留已成熟的 summary phrasing、经历骨架、项目结构和量化风格
4. 先改 Summary、Skills、最相关经历与对应项目，再考虑其余段落
5. 所有不可变字段（公司/部门/职称/时间/地点）必须完全不变
6. 经历顺序必须保持 {experience_order}
7. 必须把 JD 必需技术写到正文里有真实使用出处，不能只堆在 SKILLS
8. 不要为了补技术而把 scope 夸大；intern/junior 一律保持 team-contributed framing
9. 若 route_mode = reuse，默认只做轻改；若 route_mode = retarget，可做中等幅度改动，但仍不得改写候选人的核心职业叙事
10. 如果目标 JD 带有行业语境（如 fintech / healthcare / security / devops），优先通过 summary 和项目业务 framing 对齐，而不是凭空新增不可信 ownership
11. 如果进入同公司一致性模式，优先复用现有 team/domain/project 骨架；把变化理解为“同项目换一种表述”，而不是“换了一套完全不同的工作内容”
12. 保留合法的 DiDi senior scope，不要把它机械压缩成 generic collaboration phrasing；是否把该 scope 提到 summary/bullet，由目标 JD 决定
13. 如果目标 JD 属于自动驾驶 / physical AI / robotics / spatial-sensor systems 等陌生行业，优先在 Summary 或项目 baseline 中写“transferable infrastructure / pipeline / reliability patterns”，不要假装已有 perception、planning、simulation 或 robotics 本体 ownership

## 目标 JD 关键信息
- Role type: {role_type}
- Seniority: {seniority}
- Must-have tech: {tech_required}
- Preferred tech: {tech_preferred}
- 当前路由识别的主要缺口: {missing_required}