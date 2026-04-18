"""Canonical skill normalization and recategorization rules."""

from __future__ import annotations

from collections import defaultdict

CATEGORY_ORDER = [
    "Programming Languages",
    "Backend & APIs",
    "Frontend & UI",
    "Data & Analytics",
    "AI / ML",
    "Cloud / DevOps / Infrastructure",
    "Databases / Storage / Streaming",
    "Architecture / Systems",
    "Quality & Workflow",
]

SKILL_ALIASES = {
    "REST": "REST APIs",
    "RESTful": "REST APIs",
    "API": "APIs",
    "Api": "APIs",
    "REST APIs": "REST APIs",
    "RESTful APIs": "REST APIs",
    "Restful Apis": "REST APIs",
    "Pytest": "pytest",
    "pytest": "pytest",
    "Junit": "JUnit",
    "JUnit": "JUnit",
    "Gitlab Ci": "GitLab CI",
    "GitLab CI": "GitLab CI",
    "Html": "HTML",
    "Html5": "HTML5",
    "HTML5": "HTML5",
    "Css": "CSS",
    "CSS": "CSS",
    "Css3": "CSS3",
    "Php": "PHP",
    "Power Bi": "Power BI",
    "DBT": "dbt",
    "Google Cloud": "GCP",
    "Apache Airflow": "Airflow",
    "Apache Flink": "Flink",
    "Dynamodb": "DynamoDB",
    "Db2": "DB2",
    "Ssms": "SSMS",
    "Openai Api": "OpenAI API",
    "Genai": "Generative AI",
    "Mlops": "MLOps",
    "K8S": "Kubernetes",
    "Embedded": "Embedded Systems",
    "Embedded Systems": "Embedded Systems",
    "Selenium Webdriver": "Selenium",
    "C#/.Net": ".NET / C#",
    "Vb.Net": "VB.NET",
    "Java 17": "Java",
    "React 16+": "React",
    "Vector Embeddings": "Embeddings",
    "Langchain": "LangChain",
    "Android Sdk": "Android SDK",
    "Matlab": "MATLAB",
    "Golang": "Go",
    "Typescript": "TypeScript",
    "Natural Language Processing": "NLP",
    "Large Language Models": "LLM",
    "Large language models (LLMs)": "LLM",
    "Large Language Models (LLMs)": "LLM",
    "REST web services": "REST APIs",
    "Data structures": "Data Structures",
    "Distributed systems": "Distributed Systems",
    "Relational databases": "Relational Databases",
    "NoSQL databases": "NoSQL",
    "Object-oriented programming": "Object-Oriented Programming",
    "Programming languages - C": "C",
    "Programming languages - C++": "C++",
    "Programming languages - C#": "C#",
    "Programming languages - Java": "Java",
    "Programming languages - JavaScript": "JavaScript",
    "Programming languages - Python": "Python",
    "anomaly detection": "Anomaly Detection",
    "time-series analysis": "Time Series Analysis",
}

_ALIAS_LOOKUP = {key.casefold(): value for key, value in SKILL_ALIASES.items()}

CATEGORY_TO_SKILLS = {
    "Programming Languages": {
        "C",
        "Python",
        "Go",
        "Java",
        "JavaScript",
        "TypeScript",
        "Scala",
        "C++",
        "C#",
        "R",
        "PHP",
        "Rust",
        "Ruby",
        "Kotlin",
        "Swift",
        "MATLAB",
        "VB.NET",
    },
    "Backend & APIs": {
        "APIs",
        "Web Development",
        "Backend Development",
        "Full-Stack Development",
        "Flask",
        "FastAPI",
        "Rails",
        "Spring",
        "Spring Boot",
        "ASP.NET",
        "ASP.NET MVC",
        ".NET",
        ".NET / C#",
        "Node.js",
        "Express",
        "NestJS",
        "Django",
        "GraphQL",
        "gRPC",
        "REST APIs",
        "Microservices",
    },
    "Frontend & UI": {
        "React",
        "Angular",
        "Vue",
        "HTML",
        "HTML5",
        "CSS",
        "CSS3",
        "Next.js",
        "Tailwind",
        "Vite",
        "Webpack",
        "Android SDK",
        "Jetpack Compose",
        "Material Design",
    },
    "Data & Analytics": {
        "Data Science",
        "SQL",
        "Pandas",
        "Spark SQL",
        "Hive",
        "ETL",
        "A/B Testing",
        "Airflow",
        "Jupyter",
        "Spark",
        "Tableau",
        "Data Pipelines",
        "Matplotlib",
        "Snowflake",
        "Databricks",
        "BigQuery",
        "NumPy",
        "Power BI",
        "dbt",
        "Hadoop",
        "Experiment Design",
        "Forecasting",
        "Looker",
        "KPI Measurement",
        "Dashboard Automation",
        "Anomaly Detection",
        "Time Series Analysis",
    },
    "AI / ML": {
        "RAG",
        "AWS Bedrock",
        "LLM",
        "scikit-learn",
        "Machine Learning",
        "PyTorch",
        "TensorFlow",
        "Deep Learning",
        "Generative AI",
        "NLP",
        "Model Deployment",
        "ML Infrastructure",
        "Prompt Engineering",
        "Computer Vision",
        "OpenAI",
        "Azure OpenAI",
        "OpenAI API",
        "Embeddings",
        "Context Engineering",
        "Retrieval Evaluation",
        "LLM Application Development",
        "Keras",
        "LangChain",
        "MLOps",
    },
    "Cloud / DevOps / Infrastructure": {
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "CI/CD",
        "GitHub Actions",
        "GitLab CI",
        "Jenkins",
        "Terraform",
        "ECS",
        "Linux",
        "Shell",
        "Bash",
        "Prometheus",
        "Ansible",
    },
    "Databases / Storage / Streaming": {
        "Relational Databases",
        "PostgreSQL",
        "MySQL",
        "Redis",
        "MongoDB",
        "NoSQL",
        "Cassandra",
        "Kafka",
        "S3",
        "DynamoDB",
        "Elasticsearch",
        "Redshift",
        "DB2",
        "SSMS",
        "Flink",
        "Azure Blob Storage",
    },
    "Architecture / Systems": {
        "Object-Oriented Programming",
        "Algorithms",
        "Data Structures",
        "Distributed Systems",
        "System Design",
        "Networking",
        "Network Protocol",
        "Large-Scale Systems",
        "Embedded Systems",
    },
    "Quality & Workflow": {
        "Version Control",
        "Software Testing",
        "Git",
        "Scrum",
        "Agile",
        "Jira",
        "Unit Testing",
        "TDD",
        "pytest",
        "JUnit",
        "Code Review",
        "Playwright",
        "Software Test Engineering",
        "Design Review",
        "Selenium",
        "Jest",
        "Cypress",
        "Visual Studio",
    },
}

_SKILL_TO_CATEGORY = {}
for category, skills in CATEGORY_TO_SKILLS.items():
    for skill in skills:
        if skill in _SKILL_TO_CATEGORY:
            raise ValueError(f"Duplicate canonical skill in taxonomy: {skill}")
        _SKILL_TO_CATEGORY[skill] = category


def clean_skill_name(raw_skill: str) -> str:
    return " ".join(raw_skill.replace("\u00a0", " ").split())


def canonicalize_skill(raw_skill: str) -> str:
    cleaned = clean_skill_name(raw_skill)
    return _ALIAS_LOOKUP.get(cleaned.casefold(), cleaned)


def categorize_skill(canonical_skill: str) -> str:
    category = _SKILL_TO_CATEGORY.get(canonical_skill)
    if category is not None:
        return category

    lowered = canonical_skill.casefold()
    if "openai" in lowered or "llm" in lowered or "embedding" in lowered:
        return "AI / ML"
    if lowered.endswith("api") or lowered.endswith("apis"):
        return "Backend & APIs"
    if lowered.endswith("sql"):
        return "Data & Analytics"
    return "Quality & Workflow"


def unknown_skills(skills: set[str]) -> set[str]:
    unknown = set()
    for skill in skills:
        category = _SKILL_TO_CATEGORY.get(skill)
        if category is None and categorize_skill(skill) == "Quality & Workflow" and skill not in CATEGORY_TO_SKILLS["Quality & Workflow"]:
            unknown.add(skill)
    return unknown


def taxonomy_snapshot() -> dict[str, object]:
    alias_groups: dict[str, list[str]] = defaultdict(list)
    for alias, canonical in SKILL_ALIASES.items():
        alias_groups[canonical].append(alias)

    return {
        "category_order": CATEGORY_ORDER,
        "skill_aliases": dict(sorted(SKILL_ALIASES.items())),
        "category_to_skills": {
            category: sorted(skills) for category, skills in CATEGORY_TO_SKILLS.items()
        },
        "alias_groups": {
            canonical: sorted(aliases) for canonical, aliases in sorted(alias_groups.items())
        },
    }
