"""
JD数据模型 - 解析后的岗位需求Profile。
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# 技术栈关键词库 - 用于从JD文本中提取技术栈
TECH_KEYWORDS = {
    # 编程语言
    "python", "java", "javascript", "typescript", "c#", "c++", "go", "golang",
    "rust", "ruby", "swift", "kotlin", "scala", "php", "r", "matlab",
    "hiveql", "shell", "bash",
    # 前端
    "react", "vue", "angular", "next.js", "node.js", "html", "css",
    "tailwind", "webpack", "vite",
    # 后端框架
    "django", "flask", "fastapi", "spring", "spring boot", "express",
    ".net", "asp.net", "rails", "gin", "fiber",
    # 数据库
    "sql", "postgresql", "postgres", "mysql", "mongodb", "redis",
    "cassandra", "dynamodb", "bigquery", "snowflake", "elasticsearch",
    "nosql", "sqlite",
    # 数据/ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spark", "apache spark", "hadoop", "airflow", "apache airflow",
    "kafka", "apache kafka", "flink", "apache flink", "dbt",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data pipeline", "data pipelines", "etl",
    "ml infrastructure", "model deployment",
    "generative ai", "gen ai", "llm",
    # 云/基础设施
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform",
    "ci/cd", "jenkins", "github actions", "gitlab ci",
    # API/协议
    "rest", "restful", "graphql", "grpc", "protobuf", "websocket",
    # 工具
    "git", "linux", "tableau", "power bi", "jupyter", "databricks",
    "jira", "confluence",
    # 方法论/概念
    "agile", "scrum", "tdd", "test-driven development",
    "microservices", "distributed systems",
    "data structures", "algorithms",
    "large-scale systems", "system design",
    "network protocol", "networking",
    "embedded", "embedded systems",
    "code review", "design review",
    "software test engineering",
}

# 领域关键词
DOMAIN_KEYWORDS = {
    "recommendation": ["recommendation", "recommender", "personalization"],
    "ads": ["advertising", "ad tech", "adtech", "ads platform"],
    "search": ["search engine", "information retrieval", "search ranking"],
    "fintech": ["fintech", "financial technology", "payment", "lending", "credit"],
    "healthcare": ["healthcare", "health care", "medical", "clinical"],
    "ecommerce": ["e-commerce", "ecommerce", "marketplace", "retail"],
    "security": ["cybersecurity", "cyber security", "infosec", "security engineering"],
    "transportation": ["transportation", "logistics", "ride sharing", "delivery"],
    "ai_ml": ["artificial intelligence", "machine learning", "deep learning", "llm", "generative ai"],
}


@dataclass
class JDProfile:
    """从原始JD文本解析出的结构化profile"""
    # 基本信息
    jd_id: str = ""
    company: str = ""
    title: str = ""
    raw_text: str = ""

    # 分类维度
    role_type: str = ""              # swe_backend, data_analyst, tech_pm, mle, etc.
    business_domain: str = ""        # recommendation, ads, search, fintech, etc.
    seniority: str = ""              # ng, entry, senior

    # 技术要求 (hard requirements)
    tech_required: List[str] = field(default_factory=list)      # 必须有的技术栈
    tech_preferred: List[str] = field(default_factory=list)     # Nice to have
    tech_or_groups: List[List[str]] = field(default_factory=list)  # "Python or Java"这种

    # 软性要求 (non-tech requirements)
    soft_required: List[str] = field(default_factory=list)      # 必须的软技能/经验
    soft_preferred: List[str] = field(default_factory=list)     # Nice to have软要求

    # 团队/业务方向
    team_direction: str = ""         # 团队做什么业务

    # 业务要求
    responsibilities: List[str] = field(default_factory=list)
    qualifications_required: List[str] = field(default_factory=list)
    qualifications_preferred: List[str] = field(default_factory=list)

    # 职级信号
    yoe_range: str = ""              # "0", "1-3", "3-5"
    leadership_required: bool = False
    team_size_signal: Optional[int] = None

    @classmethod
    def from_text(cls, raw_text: str, jd_id: str = "", company: str = "") -> "JDProfile":
        """
        从原始JD文本解析 - 增强版。
        支持两种格式：
        1. 结构化markdown (## Metadata / ## Required Qualifications)
        2. 纯文本JD (Google/Amazon风格 - Minimum qualifications / Preferred qualifications)
        """
        profile = cls(jd_id=jd_id, company=company, raw_text=raw_text)
        text_lower = raw_text.lower()

        # ── 提取title ──
        for line in raw_text.strip().split("\n"):
            line = line.strip().lstrip("#").strip()
            if line and len(line) > 5 and not line.startswith("**"):
                profile.title = line
                break

        # ── 分段提取：Minimum qualifications vs Preferred qualifications ──
        # 支持Google/Amazon风格的JD分段
        req_text, pref_text, about_text = cls._split_sections(raw_text)

        # ── 提取YOE（综合所有段落中的YOE信号） ──
        yoe_matches = re.findall(
            r'(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:non-internship\s+)?(?:professional\s+)?'
            r'(?:experience|exp|software\s+development)',
            text_lower
        )
        yoe_nums = [float(m) for m in yoe_matches] if yoe_matches else []
        yoe_min = min(yoe_nums) if yoe_nums else -1
        yoe_max = max(yoe_nums) if yoe_nums else -1
        if yoe_nums:
            profile.yoe_range = f"{yoe_min:.0f}" if yoe_min == yoe_max else f"{yoe_min:.0f}-{yoe_max:.0f}"

        # ── 职级推断（综合YOE和关键词） ──
        has_new_grad = "new grad" in text_lower
        has_entry_level = "entry level" in text_lower or "entry-level" in text_lower
        # "Senior" in title is a seniority signal; "senior" in body text (e.g. "senior management") is not
        title_lower = profile.title.lower() if profile.title else ""
        has_senior_title = "senior" in title_lower or "sr." in title_lower or "sde-ii" in title_lower.replace(" ", "")
        has_lead_title = "lead" in title_lower or "principal" in title_lower or "staff" in title_lower

        # 关键判断逻辑：以最低YOE要求为基准
        if has_lead_title or has_senior_title or yoe_min >= 5:
            profile.seniority = "senior"
        elif has_new_grad and yoe_min <= 1:
            profile.seniority = "ng"
        elif has_entry_level and yoe_min <= 1:
            profile.seniority = "ng"
        elif yoe_min >= 3:
            profile.seniority = "senior"
        elif yoe_min >= 1:
            profile.seniority = "entry"
        elif has_new_grad:
            profile.seniority = "ng"
        else:
            profile.seniority = "entry"

        # ── 角色类型推断（title + 正文关键词综合） ──
        profile.role_type = cls._infer_role_type(title_lower, text_lower)

        # ── 技术栈提取（基于段落区分required/preferred） ──
        profile.tech_required, profile.tech_preferred = cls._extract_tech_stack(
            raw_text, req_text, pref_text
        )

        # 如果qualifications中没提取到任何tech，从全文body补充提取（如Amazon风格JD）
        if not profile.tech_required and not profile.tech_preferred:
            body_tech_req, body_tech_pref = cls._extract_tech_stack(
                raw_text, raw_text, ""
            )
            profile.tech_required = body_tech_req
            profile.tech_preferred = body_tech_pref

        # ── 软性要求提取 ──
        profile.soft_required, profile.soft_preferred = cls._extract_soft_requirements(
            req_text, pref_text
        )

        # ── 检测 "X or Y" 模式 ──
        or_patterns = re.findall(r'(\w+(?:\.\w+)?)\s+or\s+(\w+(?:\.\w+)?)', text_lower)
        for a, b in or_patterns:
            if a.lower() in TECH_KEYWORDS and b.lower() in TECH_KEYWORDS:
                a_cap = cls._capitalize_tech(a)
                b_cap = cls._capitalize_tech(b)
                profile.tech_or_groups.append([a_cap, b_cap])

        # ── 领域推断 ──
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                profile.business_domain = domain
                break

        # ── 团队方向提取 ──
        profile.team_direction = cls._extract_team_direction(about_text, raw_text)

        # ── 领导力信号 ──
        leadership_signals = [
            "lead a team", "manage a team", "leadership", "team lead",
            "mentorship", "mentor", "drive technical", "lead cross-team",
        ]
        profile.leadership_required = any(s in text_lower for s in leadership_signals)

        # ── 提取职责和要求列表 ──
        profile.responsibilities = cls._extract_bullet_list(raw_text, [
            "Responsibilities", "In This Role You Will", "Key job responsibilities",
            "What you'll do", "A day in the life",
        ])
        profile.qualifications_required = cls._extract_bullet_list(raw_text, [
            "Minimum qualifications", "Basic Qualifications", "Required Qualifications",
            "Requirements", "Must have",
        ])
        profile.qualifications_preferred = cls._extract_bullet_list(raw_text, [
            "Preferred qualifications", "Preferred Qualifications", "Nice to Have",
            "Bonus", "Plus",
        ])

        return profile

    @classmethod
    def _split_sections(cls, raw_text: str) -> Tuple[str, str, str]:
        """将JD文本分割为 required/preferred/about 三个区域"""
        text_lower = raw_text.lower()

        # 定义各段的标志
        req_markers = [
            "minimum qualifications", "basic qualifications",
            "required qualifications", "requirements:", "must have:",
        ]
        pref_markers = [
            "preferred qualifications", "nice to have",
            "bonus:", "plus:", "preferred:",
        ]
        about_markers = [
            "about the job", "about the team", "about the role",
            "description", "about the position",
        ]

        # 构建分段索引（支持同一marker出现多次，如两个"About the job"段落）
        sections = []
        for marker in req_markers:
            for m in re.finditer(re.escape(marker), text_lower):
                sections.append((m.start(), "required", marker))
        for marker in pref_markers:
            for m in re.finditer(re.escape(marker), text_lower):
                sections.append((m.start(), "preferred", marker))
        for marker in about_markers:
            for m in re.finditer(re.escape(marker), text_lower):
                sections.append((m.start(), "about", marker))

        sections.sort(key=lambda x: x[0])

        req_text = ""
        pref_text = ""
        about_text = ""

        for i, (start, section_type, _) in enumerate(sections):
            end = sections[i + 1][0] if i + 1 < len(sections) else len(raw_text)
            chunk = raw_text[start:end]
            if section_type == "required":
                req_text += " " + chunk
            elif section_type == "preferred":
                pref_text += " " + chunk
            elif section_type == "about":
                about_text += " " + chunk

        # 如果没有分段，整个文本视为required
        if not req_text and not pref_text:
            req_text = raw_text

        return req_text, pref_text, about_text

    @classmethod
    def _infer_role_type(cls, title_lower: str, text_lower: str) -> str:
        """从title和全文推断角色类型"""
        # 优先从title推断
        if "backend" in title_lower or "back-end" in title_lower:
            return "swe_backend"
        elif "frontend" in title_lower or "front-end" in title_lower:
            return "swe_frontend"
        elif "full stack" in title_lower or "fullstack" in title_lower:
            return "swe_fullstack"
        elif "data scientist" in title_lower:
            return "data_scientist"
        elif "data analyst" in title_lower:
            return "data_analyst"
        elif "data engineer" in title_lower:
            return "data_engineer"
        elif any(kw in title_lower for kw in ["machine learning", "ml engineer", "ai engineer", "ai/ml"]):
            return "mle"
        elif "product manager" in title_lower or "technical program" in title_lower:
            return "tech_pm"
        elif "devops" in title_lower or "sre" in title_lower:
            return "swe_devops"

        # 从正文推断
        if "ai/ml" in text_lower or "ml infrastructure" in text_lower:
            return "mle"
        elif "full-stack" in text_lower[:500] or "full stack" in text_lower[:500]:
            return "swe_fullstack"

        # 默认
        if "software" in title_lower or "developer" in title_lower or "sde" in title_lower:
            return "swe_backend"
        return "swe_backend"

    @classmethod
    def _extract_team_direction(cls, about_text: str, raw_text: str) -> str:
        """从About段落提取团队业务方向"""
        source = about_text if about_text else raw_text
        # 去掉段落header行（如 "About the job", "Description" 等）
        lines = source.strip().split("\n")
        body_lines = []
        for line in lines:
            stripped = line.strip().lstrip("#").strip()
            lower = stripped.lower()
            if lower in ("about the job", "about the team", "about the role",
                         "about the position", "description", ""):
                continue
            if lower.startswith("note:"):
                continue
            body_lines.append(stripped)
        body = " ".join(body_lines)
        # 取第一段有意义的句子
        sentences = re.split(r'[.!?]\s', body)
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 30]
        if meaningful:
            return meaningful[0][:200]
        return ""

    @classmethod
    def _extract_soft_requirements(cls, req_text: str, pref_text: str) -> Tuple[List[str], List[str]]:
        """提取非技术类软性要求"""
        soft_req = []
        soft_pref = []

        soft_patterns = [
            r"(?:experience|familiarity)\s+(?:with|in)\s+(.+?)(?:\.|$)",
            r"(?:ability|strong\s+ability)\s+to\s+(.+?)(?:\.|$)",
        ]

        # 从required中提取非技术条目
        for line in req_text.split("\n"):
            line = line.strip().lstrip("-•* ")
            if not line or len(line) < 10:
                continue
            # 如果该行不含任何TECH_KEYWORDS，视为软性要求
            line_lower = line.lower()
            has_tech = any(tech in line_lower for tech in TECH_KEYWORDS if len(tech) > 2)
            if not has_tech and any(kw in line_lower for kw in [
                "experience", "degree", "bachelor", "master", "phd",
                "ability", "communication", "leadership", "mentor",
            ]):
                soft_req.append(line)

        for line in pref_text.split("\n"):
            line = line.strip().lstrip("-•* ")
            if not line or len(line) < 10:
                continue
            line_lower = line.lower()
            has_tech = any(tech in line_lower for tech in TECH_KEYWORDS if len(tech) > 2)
            if not has_tech and any(kw in line_lower for kw in [
                "experience", "degree", "bachelor", "master", "phd",
                "ability", "communication",
            ]):
                soft_pref.append(line)

        return soft_req, soft_pref

    @classmethod
    def _extract_tech_stack(cls, raw_text: str,
                            req_text: str = "", pref_text: str = "") -> Tuple[List[str], List[str]]:
        """从JD文本中提取required和preferred技术栈"""
        found_required = []
        found_preferred = []

        # 先尝试从 "Tech Stack:" 行提取（结构化markdown格式）
        tech_line_match = re.search(r'Tech Stack:\s*(.+)', raw_text, re.IGNORECASE)
        if tech_line_match:
            tech_items = [t.strip() for t in tech_line_match.group(1).split(",")]
            found_required = tech_items[:6]
            found_preferred = tech_items[6:]
            if found_required:
                return found_required, found_preferred

        # 如果没有预分段的文本，用整个raw_text作为required
        if not req_text:
            req_text = raw_text
        req_lower = req_text.lower()
        pref_lower = pref_text.lower() if pref_text else ""

        # 容易产生误匹配的关键词：只在qualifications段落中匹配（不从body提取）
        # 这些词作为普通英语词太常见（如scalable→scala, swift→swift）
        AMBIGUOUS_TECH = {"scala", "swift", "ruby", "r", "c", "go", "code review", "design review"}

        # 判断是否为body fallback模式（qualifications无tech时用全文提取）
        is_body_fallback = (req_text == raw_text and not pref_text)

        # 短关键词（<=4字符）用word boundary匹配，避免substring误匹配（如gin匹配Engineering）
        for tech in TECH_KEYWORDS:
            # 在body fallback模式下跳过歧义词（scala/swift/go等普通英语词）
            if is_body_fallback and tech in AMBIGUOUS_TECH:
                continue

            if len(tech) <= 4:
                # 短关键词需要word boundary
                if tech in ("r", "c"):
                    pattern = r'\b' + re.escape(tech.upper()) + r'\b'
                    if re.search(pattern, req_text):
                        found_required.append(tech.upper())
                    elif pref_text and re.search(pattern, pref_text):
                        found_preferred.append(tech.upper())
                elif tech == "c++":
                    # C++ 的 ++ 不是word boundary友好的，直接用substring
                    if "c++" in req_lower:
                        found_required.append("C++")
                    elif "c++" in pref_lower:
                        found_preferred.append("C++")
                else:
                    pattern = r'\b' + re.escape(tech) + r'\b'
                    if re.search(pattern, req_lower):
                        found_required.append(cls._capitalize_tech(tech))
                    elif re.search(pattern, pref_lower):
                        found_preferred.append(cls._capitalize_tech(tech))
            else:
                if tech in req_lower:
                    found_required.append(cls._capitalize_tech(tech))
                elif tech in pref_lower:
                    found_preferred.append(cls._capitalize_tech(tech))

        # 去重（含同义词合并）
        SYNONYMS = {
            "gen ai": "Generative AI",
            "generative ai": "Generative AI",
            "golang": "Go",
            "postgres": "PostgreSQL",
            "apache kafka": "Kafka",
            "apache spark": "Spark",
            "data pipeline": "Data Pipelines",
            "test-driven development": "TDD",
        }
        seen = set()
        deduped_req = []
        for t in found_required:
            canonical = SYNONYMS.get(t.lower(), t)
            if canonical.lower() not in seen:
                seen.add(canonical.lower())
                deduped_req.append(canonical)
        deduped_pref = []
        for t in found_preferred:
            canonical = SYNONYMS.get(t.lower(), t)
            if canonical.lower() not in seen:
                seen.add(canonical.lower())
                deduped_pref.append(canonical)

        return deduped_req, deduped_pref

    @staticmethod
    def _capitalize_tech(tech: str) -> str:
        """标准化技术名称大小写"""
        special_cases = {
            "python": "Python", "java": "Java", "javascript": "JavaScript",
            "typescript": "TypeScript", "c#": "C#", "c++": "C++",
            "go": "Go", "golang": "Go", "rust": "Rust", "ruby": "Ruby",
            "kotlin": "Kotlin", "scala": "Scala", "swift": "Swift",
            "react": "React", "vue": "Vue", "angular": "Angular",
            "node.js": "Node.js", "next.js": "Next.js",
            "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
            "spring": "Spring", "spring boot": "Spring Boot",
            ".net": ".NET", "asp.net": "ASP.NET",
            "sql": "SQL", "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
            "mysql": "MySQL", "mongodb": "MongoDB", "redis": "Redis",
            "bigquery": "BigQuery", "snowflake": "Snowflake",
            "nosql": "NoSQL", "elasticsearch": "Elasticsearch",
            "aws": "AWS", "gcp": "GCP", "azure": "Azure",
            "docker": "Docker", "kubernetes": "Kubernetes",
            "terraform": "Terraform", "kafka": "Kafka",
            "apache kafka": "Apache Kafka", "apache spark": "Apache Spark",
            "spark": "Spark", "airflow": "Airflow",
            "git": "Git", "linux": "Linux", "tableau": "Tableau",
            "dbt": "DBT", "grpc": "gRPC", "graphql": "GraphQL",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "ci/cd": "CI/CD", "agile": "Agile", "scrum": "Scrum",
            "restful": "RESTful", "rest": "REST",
            "microservices": "Microservices",
            "distributed systems": "Distributed Systems",
            "data pipelines": "Data Pipelines",
            "data pipeline": "Data Pipelines",
            "etl": "ETL", "nlp": "NLP",
            "pandas": "Pandas", "numpy": "NumPy",
            "scikit-learn": "scikit-learn",
            "tensorflow": "TensorFlow", "pytorch": "PyTorch",
            "tdd": "TDD", "test-driven development": "TDD",
            "generative ai": "Generative AI", "gen ai": "Gen AI", "llm": "LLM",
            "ml infrastructure": "ML Infrastructure", "model deployment": "Model Deployment",
            "network protocol": "Network Protocol", "networking": "Networking",
            "embedded": "Embedded", "embedded systems": "Embedded Systems",
            "code review": "Code Review", "design review": "Design Review",
            "software test engineering": "Software Test Engineering",
            "data structures": "Data Structures", "algorithms": "Algorithms",
            "large-scale systems": "Large-Scale Systems", "system design": "System Design",
            "computer vision": "Computer Vision",
            "hiveql": "HiveQL", "shell": "Shell", "bash": "Bash",
        }
        return special_cases.get(tech.lower(), tech.title())

    @classmethod
    def _extract_bullet_list(cls, text: str, headers: List[str]) -> List[str]:
        """从文本中提取某个section的bullet points，支持多种header名"""
        for header in headers:
            # 支持多种格式：
            # "## Header\n- item" (markdown)
            # "Header:\n item" / "Header\n\n item" (plain text)
            pattern = rf'(?:^|\n)\s*(?:#+\s*)?{re.escape(header)}[:\s]*\n((?:\s*[-•*]\s*.+\n?)+)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                section = match.group(1)
                items = re.findall(r'[-•*]\s*(.+)', section)
                return [item.strip() for item in items if item.strip()]

            # 尝试无bullet格式（Google风格：每行一个条目，缩进或空行分隔）
            esc_header = re.escape(header)
            pattern2 = rf'(?:^|\n)\s*(?:#+\s*)?{esc_header}[:\s]*\n((?:[ \t]+.+\n?)+)'
            match2 = re.search(pattern2, text, re.IGNORECASE | re.MULTILINE)
            if match2:
                section = match2.group(1)
                items = [line.strip() for line in section.split("\n") if line.strip()]
                return items

        return []

    # 向后兼容旧的调用
    @classmethod
    def _extract_section(cls, text: str, header: str) -> List[str]:
        """向后兼容"""
        return cls._extract_bullet_list(text, [header])
