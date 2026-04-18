## 输出格式

请严格按以下 JSON 格式输出（不要有任何额外文字）：

```json
{
  "scores": {
    "r0_authenticity": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": [
        {"severity": "<critical|high|medium|low>", "field": "<具体位置>", "issue": "<问题描述>", "fix": "<具体修改建议>"}
      ]
    },
    "r1_writing_standard": {
      "score": <0-10>,
      "weight": 0.15,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r2_jd_fitness": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r3_overqualification": {
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r4_rationality": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r5_logic": {
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r6_competitiveness": {
      "score": <0-10>,
      "weight": 0.05,
      "verdict": "<pass|fail>",
      "findings": []
    }
  },
  "weighted_score": <0-100, 保留1位小数>,
  "overall_verdict": "<pass|fail>",
  "critical_count": <整数>,
  "high_count": <整数>,
  "needs_revision": <true|false>,
  "revision_priority": [
    "<最优先修改事项1（一句话）>",
    "<最优先修改事项2（一句话）>"
  ],
  "revision_instructions": "<如果 needs_revision=true，给出完整修改指令（具体到每处修改）；否则为空字符串>"
}
```

评分指南：
- 9.5-10: 完美，无问题
- 9.0-9.4: 优秀，仅有 low 级别建议
- 8.0-8.9: 良好，有 medium 问题需优化
- 7.0-7.9: 有 high 问题，必须修改
- < 7.0: 有 critical 问题，FAIL

额外校准：
- 发现若仅为格式润色、分类命名、轻微措辞重复，不应轻易打到 8.5 以下
- 若 0 critical 且 0 high，并且 JD 必须技术完整覆盖、转岗叙事自洽，则综合分应优先落在 93+，除非存在会显著影响 HR 信任的中等级结构问题
- revision_priority 应优先列出“最小但最高杠杆”的 1-2 个改动，而不是笼统要求整份简历重写

综合加权分 = sum(score_i * weight_i) * 10

若当前处于 rewrite 审查模式，revision_priority 和 revision_instructions 必须体现“可重写到 pass 的最高杠杆改法”。只有当你判断该 JD 与候选人背景天然不适配、继续重写也难以自洽时，才应给出明确 reject 信号。

只输出 JSON，不要其他内容。