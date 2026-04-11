from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import re

from .models import CanonicalDefinition


def _definition(
    canonical_id: str,
    canonical_name: str,
    content_type: str,
    *aliases: str,
    parent_id: str | None = None,
) -> CanonicalDefinition:
    return CanonicalDefinition(
        canonical_id=canonical_id,
        canonical_name=canonical_name,
        content_type=content_type,
        aliases=tuple(alias.lower() for alias in aliases if alias),
        parent_id=parent_id,
    )


CANONICAL_DEFINITIONS: tuple[CanonicalDefinition, ...] = (
    _definition(
        "TECH_MAINSTREAM_PROGRAMMING_LANGUAGE",
        "Mainstream Programming Language",
        "tech_stack",
        "mainstream programming language",
        "modern programming language",
        "one programming language",
        "one major programming language",
        "at least one programming language",
    ),
    _definition("TECH_PYTHON", "Python", "tech_stack", "python", "py", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_JAVA", "Java", "tech_stack", "java", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_CPP", "C++", "tech_stack", "c++", "c / c++", "c/c++", "modern c++", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_CSHARP", "C#", "tech_stack", "c#", "c sharp", "c-sharp", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_GO", "Go", "tech_stack", "go", "golang", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_JAVASCRIPT", "JavaScript", "tech_stack", "javascript", "js", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_TYPESCRIPT", "TypeScript", "tech_stack", "typescript", "ts", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_KOTLIN", "Kotlin", "tech_stack", "kotlin", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_RUST", "Rust", "tech_stack", "rust", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_SCALA", "Scala", "tech_stack", "scala", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_RUBY", "Ruby", "tech_stack", "ruby", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition(
        "TECH_BACKEND_FRAMEWORK",
        "Backend Framework",
        "tech_stack",
        "backend framework",
        "backend frameworks",
        "server framework",
    ),
    _definition("TECH_DJANGO", "Django", "tech_stack", "django", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_FLASK", "Flask", "tech_stack", "flask", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_FASTAPI", "FastAPI", "tech_stack", "fastapi", "fast api", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_SPRING", "Spring", "tech_stack", "spring", "spring boot", "springboot", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_EXPRESS", "Express", "tech_stack", "express", "express.js", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_NESTJS", "NestJS", "tech_stack", "nestjs", "nest js", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition("TECH_NODEJS", "Node.js", "tech_stack", "node.js", "nodejs", "node", parent_id="TECH_BACKEND_FRAMEWORK"),
    _definition(
        "TECH_FRONTEND_FRAMEWORK",
        "Frontend Framework",
        "tech_stack",
        "frontend framework",
        "frontend frameworks",
        "web framework",
    ),
    _definition("TECH_REACT", "React", "tech_stack", "react", "react.js", "reactjs", parent_id="TECH_FRONTEND_FRAMEWORK"),
    _definition("TECH_NEXTJS", "Next.js", "tech_stack", "next.js", "nextjs", parent_id="TECH_FRONTEND_FRAMEWORK"),
    _definition("TECH_ANGULAR", "Angular", "tech_stack", "angular", parent_id="TECH_FRONTEND_FRAMEWORK"),
    _definition("TECH_VUE", "Vue", "tech_stack", "vue", "vue.js", "vuejs", parent_id="TECH_FRONTEND_FRAMEWORK"),
    _definition(
        "TECH_DATABASE",
        "Database",
        "tech_stack",
        "database",
        "databases",
        "sql or nosql",
    ),
    _definition("TECH_POSTGRESQL", "PostgreSQL", "tech_stack", "postgresql", "postgres", parent_id="TECH_DATABASE"),
    _definition("TECH_MYSQL", "MySQL", "tech_stack", "mysql", parent_id="TECH_DATABASE"),
    _definition("TECH_SQL", "SQL", "tech_stack", "sql", parent_id="TECH_DATABASE"),
    _definition("TECH_DYNAMODB", "DynamoDB", "tech_stack", "dynamodb", parent_id="TECH_DATABASE"),
    _definition("TECH_MONGODB", "MongoDB", "tech_stack", "mongodb", parent_id="TECH_DATABASE"),
    _definition("TECH_REDIS", "Redis", "tech_stack", "redis", parent_id="TECH_DATABASE"),
    _definition("TECH_SNOWFLAKE", "Snowflake", "tech_stack", "snowflake", parent_id="TECH_DATABASE"),
    _definition("TECH_BIGQUERY", "BigQuery", "tech_stack", "bigquery", parent_id="TECH_DATABASE"),
    _definition(
        "TECH_CLOUD_PLATFORM",
        "Cloud Platform",
        "tech_stack",
        "cloud platform",
        "cloud infrastructure",
    ),
    _definition("TECH_AWS", "AWS", "tech_stack", "aws", "amazon web services", parent_id="TECH_CLOUD_PLATFORM"),
    _definition("TECH_GCP", "GCP", "tech_stack", "gcp", "google cloud", parent_id="TECH_CLOUD_PLATFORM"),
    _definition("TECH_AZURE", "Azure", "tech_stack", "azure", parent_id="TECH_CLOUD_PLATFORM"),
    _definition("TECH_S3", "S3", "tech_stack", "s3", parent_id="TECH_AWS"),
    _definition("TECH_LAMBDA", "Lambda", "tech_stack", "lambda", "aws lambda", parent_id="TECH_AWS"),
    _definition(
        "TECH_INFRA_PLATFORM",
        "Infrastructure Platform",
        "tech_stack",
        "platform infrastructure",
        "infrastructure",
        "distributed systems",
    ),
    _definition("TECH_DOCKER", "Docker", "tech_stack", "docker", "containerization", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_KUBERNETES", "Kubernetes", "tech_stack", "kubernetes", "k8s", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_TERRAFORM", "Terraform", "tech_stack", "terraform", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_CICD", "CI/CD", "tech_stack", "ci/cd", "cicd", "continuous integration", "continuous delivery", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_LINUX", "Linux", "tech_stack", "linux", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_GRAFANA", "Grafana", "tech_stack", "grafana", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_MICROSERVICES", "Microservices", "tech_stack", "microservices", "microservices architecture", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_DISTRIBUTED_SYSTEMS", "Distributed Systems", "tech_stack", "distributed systems", "large-scale systems", "system design", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_NETWORKING", "Networking", "tech_stack", "networking", "network systems", "network software", parent_id="TECH_INFRA_PLATFORM"),
    _definition("TECH_CONTROL_PLANE", "Control Plane", "tech_stack", "control plane", parent_id="TECH_NETWORKING"),
    _definition(
        "TECH_AI_ML",
        "AI/ML Stack",
        "tech_stack",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "ml framework",
        "deep learning framework",
    ),
    _definition("TECH_PYTORCH", "PyTorch", "tech_stack", "pytorch", parent_id="TECH_AI_ML"),
    _definition("TECH_TENSORFLOW", "TensorFlow", "tech_stack", "tensorflow", parent_id="TECH_AI_ML"),
    _definition("TECH_PANDAS", "Pandas", "tech_stack", "pandas", parent_id="TECH_AI_ML"),
    _definition("TECH_NUMPY", "NumPy", "tech_stack", "numpy", parent_id="TECH_AI_ML"),
    _definition("TECH_R", "R", "tech_stack", " r ", parent_id="TECH_AI_ML"),
    _definition("TECH_LLM", "LLM", "tech_stack", "llm", "large language model", "large language models", parent_id="TECH_AI_ML"),
    _definition("TECH_GENAI", "Generative AI", "tech_stack", "genai", "generative ai", parent_id="TECH_AI_ML"),
    _definition("TECH_RAG", "RAG", "tech_stack", "rag", "retrieval augmented generation", "retrieval-augmented generation", parent_id="TECH_AI_ML"),
    _definition("TECH_LANGCHAIN", "LangChain", "tech_stack", "langchain", parent_id="TECH_AI_ML"),
    _definition("TECH_AIRFLOW", "Airflow", "tech_stack", "airflow", "apache airflow"),
    _definition("TECH_KAFKA", "Kafka", "tech_stack", "kafka", "apache kafka"),
    _definition("TECH_SPARK", "Spark", "tech_stack", "spark", "apache spark", "pyspark"),
    _definition("TECH_HADOOP", "Hadoop", "tech_stack", "hadoop"),
    _definition("TECH_HIVE", "Hive", "tech_stack", "hive", "apache hive"),
    _definition("TECH_DBT", "dbt", "tech_stack", "dbt"),
    _definition("TECH_DATABRICKS", "Databricks", "tech_stack", "databricks"),
    _definition("TECH_TABLEAU", "Tableau", "tech_stack", "tableau"),
    _definition("TECH_POWER_BI", "Power BI", "tech_stack", "power bi"),
    _definition("TECH_LOOKER", "Looker", "tech_stack", "looker"),
    _definition("TECH_PYTEST", "pytest", "tech_stack", "pytest"),
    _definition("TECH_PLAYWRIGHT", "Playwright", "tech_stack", "playwright"),
    _definition("TECH_JEST", "Jest", "tech_stack", "jest"),
    _definition("TECH_SELENIUM", "Selenium", "tech_stack", "selenium"),
    _definition("TECH_C", "C", "tech_stack", " c ", parent_id="TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"),
    _definition("TECH_REST_API", "REST API", "tech_stack", "rest api", "restful api", "restful apis", "api development"),
    _definition("TECH_API", "API", "tech_stack", "apis", "api"),
    _definition("TECH_GRAPHQL", "GraphQL", "tech_stack", "graphql"),
    _definition("TECH_GRPC", "gRPC", "tech_stack", "grpc"),
    _definition(
        "RESP_BACKEND_DEVELOPMENT",
        "Backend Development",
        "responsibility",
        "backend development",
        "backend services",
        "server-side development",
        "software engineer ii (backend)",
        "backend",
    ),
    _definition(
        "RESP_SOFTWARE_DEVELOPMENT",
        "Software Development",
        "responsibility",
        "software development",
        "software engineering",
    ),
    _definition(
        "RESP_FRONTEND_DEVELOPMENT",
        "Frontend Development",
        "responsibility",
        "frontend development",
        "frontend engineering",
        "frontend",
        "web applications",
    ),
    _definition(
        "RESP_FULLSTACK_DEVELOPMENT",
        "Full-Stack Development",
        "responsibility",
        "full stack",
        "full-stack",
        "full stack development",
    ),
    _definition(
        "RESP_API_DEVELOPMENT",
        "API Development",
        "responsibility",
        "api design",
        "api development",
        "api lifecycle management",
        "scalable api",
    ),
    _definition(
        "RESP_TEST_AUTOMATION",
        "Test Automation",
        "responsibility",
        "automated test",
        "testing methodologies",
        "test automation",
        "tdd",
        "quality standards",
    ),
    _definition(
        "RESP_CODE_REVIEW",
        "Code Review",
        "responsibility",
        "code review",
        "design review",
    ),
    _definition(
        "RESP_SYSTEM_DESIGN",
        "System Design",
        "responsibility",
        "system design",
        "software design",
        "architecture",
    ),
    _definition(
        "RESP_PLATFORM_BUILDING",
        "Platform Building",
        "responsibility",
        "platform building",
        "shared services",
        "core services",
        "platform engineering",
    ),
    _definition(
        "RESP_ML_MODEL_DEPLOYMENT",
        "Model Deployment",
        "responsibility",
        "model deployment",
        "on-target deployment",
        "ml platform",
    ),
    _definition(
        "RESP_MOBILE_DEVELOPMENT",
        "Mobile Development",
        "responsibility",
        "mobile applications",
        "mobile development",
        "android programming",
        "ios",
        "android",
    ),
    _definition(
        "RESP_CROSS_FUNCTIONAL_COLLABORATION",
        "Cross-Functional Collaboration",
        "responsibility",
        "cross functional",
        "cross-functional",
        "collaborate with",
        "partner with",
        "stakeholders",
    ),
    _definition("DOMAIN_PAYMENTS", "Payments", "domain", "payments", "payment processing", "billing", "invoice"),
    _definition("DOMAIN_FINTECH", "Fintech", "domain", "fintech", "financial technology", "merchant"),
    _definition("DOMAIN_SECURITY", "Security", "domain", "security", "cybersecurity", "cyber security", "privacy"),
    _definition("DOMAIN_RECOMMENDATION", "Recommendation", "domain", "recommendation", "recommender", "personalization", "ranking"),
    _definition("DOMAIN_SEARCH", "Search", "domain", "search", "information retrieval", "retrieval"),
    _definition("DOMAIN_ADS", "Ads", "domain", "ads", "adtech", "advertising"),
    _definition("DOMAIN_AD_MEASUREMENT", "Ad Measurement", "domain", "measurement science", "ad measurement", "marketing measurement"),
    _definition("DOMAIN_ECOMMERCE", "Ecommerce", "domain", "e-commerce", "ecommerce", "marketplace", "retail"),
    _definition("DOMAIN_HEALTHCARE", "Healthcare", "domain", "healthcare", "health care", "medical", "clinical"),
    _definition("DOMAIN_CLOUD_INFRA", "Cloud Infrastructure", "domain", "cloud infrastructure", "cloud networking", "cloud systems"),
    _definition("DOMAIN_DATA_PLATFORM", "Data Platform", "domain", "data platform", "data warehouse", "etl platform", "data infrastructure"),
    _definition("DOMAIN_ML_PLATFORM", "ML Platform", "domain", "ml platform", "mlops", "model optimization"),
    _definition("DOMAIN_DATA_SCIENCE", "Data Science", "domain", "data science"),
    _definition("DOMAIN_NETWORKING", "Networking", "domain", "networking", "network control plane", "network infrastructure"),
    _definition("DOMAIN_FRAUD_RISK", "Fraud / Risk", "domain", "abuse prevention", "fraud", "risk", "trust and safety"),
    _definition("DOMAIN_DATABASE_ENGINES", "Database Engines", "domain", "distributed sql", "dsql", "aurora dsql", "query processing", "database internals"),
    _definition("DOMAIN_AGENT_SYSTEMS", "Agent Systems", "domain", "agentcore", "agent systems", "multi-agent workflows", "agentic workflows"),
    _definition("DOMAIN_HR_SYSTEMS", "HR Systems", "domain", "workforce solutions", "employee onboarding", "hr systems", "human resources systems"),
    _definition("DOMAIN_SPACE_SYSTEMS", "Space Systems", "domain", "space infrastructure", "satellite operations", "space missions"),
    _definition("DOMAIN_ENERGY_SYSTEMS", "Energy Systems", "domain", "electric utility grid", "utility industry", "energy team"),
    _definition("CONSTRAINT_BACHELORS", "Bachelor's Degree", "constraint", "bachelor's degree", "bachelors degree", "bs degree"),
    _definition("CONSTRAINT_MASTERS", "Master's Degree", "constraint", "master's degree", "masters degree", "ms degree"),
    _definition("CONSTRAINT_COMPUTER_SCIENCE", "Computer Science", "constraint", "computer science"),
    _definition("CONSTRAINT_STATISTICS", "Statistics", "constraint", "statistics"),
    _definition("CONSTRAINT_MATHEMATICS", "Mathematics", "constraint", "mathematics"),
    _definition("CONSTRAINT_ENGINEERING_FIELD", "Engineering Field", "constraint", "engineering", "related field"),
    _definition("CONSTRAINT_WORK_AUTH", "Work Authorization", "constraint", "work authorization", "work auth", "authorized to work"),
    _definition("CONSTRAINT_REMOTE", "Remote Work", "constraint", "remote", "remote work"),
    _definition("CONSTRAINT_HYBRID", "Hybrid Work", "constraint", "hybrid"),
    _definition("CONSTRAINT_ONSITE", "Onsite Work", "constraint", "onsite", "on-site"),
    _definition("EXP_YOE_0_2", "0-2 Years Experience", "experience", "0-2 years", "1 year", "2 years"),
    _definition("EXP_YOE_3_5", "3-5 Years Experience", "experience", "3 years", "4 years", "5 years", "3-5 years"),
    _definition("EXP_YOE_5_PLUS", "5+ Years Experience", "experience", "5+ years", "6+ years", "7+ years", "8+ years"),
)


@dataclass(frozen=True)
class Taxonomy:
    definitions: dict[str, CanonicalDefinition]
    alias_index: dict[str, str]
    children_index: dict[str, tuple[str, ...]]
    descendants_index: dict[str, tuple[str, ...]]
    compiled_alias_patterns: tuple[tuple[re.Pattern[str], str], ...]

    def get(self, canonical_id: str) -> CanonicalDefinition | None:
        return self.definitions.get(canonical_id)

    def children_of(self, canonical_id: str) -> tuple[str, ...]:
        return self.children_index.get(canonical_id, ())

    def descendants_of(self, canonical_id: str) -> tuple[str, ...]:
        return self.descendants_index.get(canonical_id, ())

    def ancestors_of(self, canonical_id: str) -> tuple[str, ...]:
        current = self.definitions.get(canonical_id)
        ancestors: list[str] = []
        while current is not None and current.parent_id:
            ancestors.append(current.parent_id)
            current = self.definitions.get(current.parent_id)
        return tuple(ancestors)


def _build_descendants(
    definitions: dict[str, CanonicalDefinition],
    children_index: dict[str, tuple[str, ...]],
) -> dict[str, tuple[str, ...]]:
    memo: dict[str, tuple[str, ...]] = {}

    def visit(node_id: str) -> tuple[str, ...]:
        if node_id in memo:
            return memo[node_id]
        descendants: list[str] = []
        for child_id in children_index.get(node_id, ()):
            descendants.append(child_id)
            descendants.extend(visit(child_id))
        deduped: list[str] = []
        seen: set[str] = set()
        for item in descendants:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        memo[node_id] = tuple(deduped)
        return memo[node_id]

    for canonical_id in definitions:
        visit(canonical_id)
    return memo


def build_taxonomy() -> Taxonomy:
    definitions = {item.canonical_id: item for item in CANONICAL_DEFINITIONS}
    alias_index: dict[str, str] = {}
    children_map: dict[str, list[str]] = defaultdict(list)
    for item in CANONICAL_DEFINITIONS:
        alias_index[item.canonical_name.lower()] = item.canonical_id
        for alias in item.aliases:
            alias_index[alias] = item.canonical_id
        if item.parent_id:
            children_map[item.parent_id].append(item.canonical_id)
    children_index = {key: tuple(value) for key, value in children_map.items()}
    descendants_index = _build_descendants(definitions, children_index)
    compiled_alias_patterns = tuple(
        (
            re.compile(rf"(?<![a-z0-9+#]){re.escape(alias)}(?![a-z0-9+#])"),
            canonical_id,
        )
        for alias, canonical_id in sorted(alias_index.items(), key=lambda item: len(item[0]), reverse=True)
        if alias
    )
    return Taxonomy(
        definitions=definitions,
        alias_index=alias_index,
        children_index=children_index,
        descendants_index=descendants_index,
        compiled_alias_patterns=compiled_alias_patterns,
    )


DEFAULT_TAXONOMY = build_taxonomy()
