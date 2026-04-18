请作为 Planner，基于以下信息做流程决策：目标模式、目标 JD、Matcher Packet、Starter Resume。

返回 JSON，schema 必须包含 decision、fit_label、reuse_ratio_estimate、already_covered、missing_or_weak、risk_flags、role_seniority_guidance、planner_summary、writer_plan、direct_review_rationale。

规则：no_starter 模式下 decision 只能是 write；starter 高度贴合且 scope/真实性风险低时可以 direct_review；starter 语义相近但仍需改写时选择 write；starter 虽相似但会明显误导 summary、ownership、项目骨架或 scope 时选择 reject_starter；不要把 matcher 的相似度直接等同于可写作适配度。