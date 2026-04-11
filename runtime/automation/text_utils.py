"""
Text normalization helpers shared by sheet routing modules.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Iterable, Sequence


SKILL_SYNONYMS = {
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "nextjs": "next.js",
    "golang": "go",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "ms sql": "sql",
    "sql server": "sql",
    "nosql": "nosql",
    "py": "python",
    "pyton": "python",
    "c sharp": "c#",
    "c-sharp": "c#",
    "dotnet": ".net",
    "asp.net": ".net",
    "sparksql": "spark",
    "apache spark": "spark",
    "pyspark": "spark",
    "apache airflow": "airflow",
    "airflow": "airflow",
    "apache kafka": "kafka",
    "ci cd": "ci/cd",
    "ci / cd": "ci/cd",
    "github action": "github actions",
    "github actions": "github actions",
    "git hub actions": "github actions",
    "k8s": "kubernetes",
    "kuberenetes": "kubernetes",
    "gcp": "gcp",
    "google cloud": "gcp",
    "amazon web services": "aws",
    "bedrock": "aws bedrock",
    "azure openai service": "azure openai",
    "azure ai search": "azure ai search",
    "openai": "openai",
    "llms": "llm",
    "large language models": "llm",
    "large language model": "llm",
    "genai": "genai",
    "generative ai": "genai",
    "rag": "rag",
    "retrieval augmented generation": "rag",
    "retrieval-augmented generation": "rag",
    "langchain": "langchain",
    "langgraph": "langgraph",
    "crewai": "crewai",
    "vector databases": "vector database",
    "vector database": "vector database",
    "pinecone": "pinecone",
    "weaviate": "weaviate",
    "chromadb": "chromadb",
    "faiss": "faiss",
    "semantic search": "semantic search",
    "embeddings": "embeddings",
    "agents": "ai agents",
    "ai agent": "ai agents",
    "ai agents": "ai agents",
    "prompt engineering": "prompt engineering",
    "context engineering": "context engineering",
    "text-to-sql": "text-to-sql",
    "function calling": "function calling",
    "observability": "observability",
    "mlops": "mlops",
    "docker": "docker",
    "terraform": "terraform",
    "fast api": "fastapi",
    "springboot": "spring boot",
    "grpc": "grpc",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest": "rest api",
    "apis": "api",
    "api": "api",
    "pytest": "pytest",
    "jest": "jest",
    "selenium": "selenium",
    "cypress": "cypress",
    "playwright": "playwright",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "numpy": "numpy",
    "pandas": "pandas",
    "dbt": "dbt",
    "databricks": "databricks",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
    "redshift": "redshift",
    "hiveql": "hive",
    "slurm": "slurm",
    "lsf": "lsf",
    "hpc": "hpc",
    "bioinformatics": "bioinformatics",
    "unreal engine": "unreal engine",
    "perforce": "perforce",
}


DOMAIN_TERMS = {
    "ads",
    "ai",
    "analytics",
    "automation",
    "backend",
    "billing",
    "biotech",
    "blockchain",
    "bioinformatics",
    "clinical",
    "cloud",
    "compliance",
    "consumer",
    "content",
    "creative",
    "data",
    "developer-tools",
    "devops",
    "distributed-systems",
    "enterprise",
    "experimentation",
    "fintech",
    "frontend",
    "gaming",
    "genai",
    "growth",
    "hardware",
    "healthcare",
    "infrastructure",
    "integration",
    "internal-tools",
    "legal-tech",
    "medical-device",
    "ml-platform",
    "mobile",
    "observability",
    "payments",
    "platform",
    "privacy",
    "productivity",
    "qa",
    "recommendation",
    "research",
    "robotics",
    "risk",
    "search",
    "security",
    "systems",
    "testing",
    "web",
}


DOMAIN_PATTERNS = {
    "ads": (r"\bads?\b", r"advertis", r"adtech"),
    "ai": (r"\bartificial intelligence\b", r"\bai\b"),
    "analytics": (r"analytic", r"insight"),
    "automation": (r"automation", r"orchestration"),
    "backend": (r"backend", r"server-side", r"api"),
    "billing": (r"billing", r"invoice", r"subscription"),
    "biotech": (r"genomic", r"sequenc", r"assay", r"biotech", r"life[- ]science"),
    "blockchain": (r"blockchain", r"stablecoin", r"crypto"),
    "bioinformatics": (r"bioinformatics", r"biomedical", r"clinical"),
    "cloud": (r"\baws\b", r"\bazure\b", r"\bgcp\b", r"cloud"),
    "compliance": (r"compliance", r"governance", r"policy"),
    "content": (r"content", r"creator", r"media"),
    "creative": (r"creative", r"studio", r"asset workflow", r"unreal"),
    "data": (r"data", r"etl", r"warehouse"),
    "developer-tools": (r"developer", r"workflow", r"tooling"),
    "devops": (r"devops", r"ci/cd", r"release"),
    "distributed-systems": (r"distributed", r"microservices", r"event-driven"),
    "enterprise": (r"enterprise", r"saas", r"b2b"),
    "experimentation": (r"experimentation", r"a/b", r"ab test"),
    "fintech": (r"fintech", r"payments?", r"lending", r"credit", r"bank"),
    "frontend": (r"frontend", r"ui", r"design systems?", r"react", r"vue", r"angular"),
    "gaming": (r"game", r"gaming", r"halo", r"studio"),
    "genai": (r"llm", r"rag", r"prompt engineering", r"langchain", r"langgraph", r"agent"),
    "growth": (r"growth", r"acquisition", r"funnel"),
    "hardware": (r"hardware", r"firmware", r"silicon", r"board[- ]level"),
    "healthcare": (r"health", r"clinical", r"medical"),
    "infrastructure": (r"infrastructure", r"platform", r"sre", r"reliability"),
    "integration": (r"integration", r"third-party", r"partner"),
    "internal-tools": (r"internal", r"workflow", r"developer productivity"),
    "legal-tech": (r"legal", r"contract", r"document review", r"case review", r"matter management"),
    "medical-device": (r"implant", r"medical device", r"surgical", r"device software"),
    "ml-platform": (r"mlops", r"model deployment", r"ml platform"),
    "mobile": (r"mobile", r"ios", r"android", r"swift", r"kotlin"),
    "observability": (r"observability", r"monitoring", r"telemetry"),
    "payments": (r"payment", r"card", r"merchant"),
    "platform": (r"platform", r"shared services", r"core services"),
    "privacy": (r"privacy", r"ph[i1]", r"sensitive data"),
    "productivity": (r"productivity", r"workflow", r"authoring"),
    "qa": (r"\bqa\b", r"sdet", r"test automation"),
    "recommendation": (r"recommendation", r"ranking", r"relevance", r"personalization"),
    "research": (r"research", r"applied scientist", r"research engineer"),
    "robotics": (r"robot", r"robotic", r"manipulation", r"autonomy"),
    "risk": (r"fraud", r"risk", r"trust"),
    "search": (r"search", r"retrieval", r"discovery"),
    "security": (r"security", r"threat", r"auth", r"secure"),
    "systems": (r"systems", r"compiler", r"virtualization", r"kernel"),
    "testing": (r"testing", r"quality", r"validation"),
    "web": (r"web", r"browser", r"website"),
}


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def normalize_token(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[()|]+", " ", text)
    text = text.replace("&", " and ")
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"[^a-z0-9.+#/ -]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return SKILL_SYNONYMS.get(text, text)


def canonicalize_skill(text: str) -> str:
    token = normalize_token(text)
    return SKILL_SYNONYMS.get(token, token)


def split_delimited_list(text: str) -> list[str]:
    if not text:
        return []
    text = text.replace("\u2022", ",").replace("|", ",").replace("•", ",")
    parts = re.split(r"[,;\n]+", text)
    values = []
    for part in parts:
        token = canonicalize_skill(part)
        if not token or len(token) < 2:
            continue
        values.append(token)
    return values


def build_skill_vocabulary(iterables: Sequence[Iterable[str]]) -> set[str]:
    vocab: set[str] = set()
    for iterable in iterables:
        for item in iterable:
            token = canonicalize_skill(item)
            if token:
                vocab.add(token)
    vocab.update(SKILL_SYNONYMS.values())
    return vocab


def prepare_skill_tokens(vocabulary: Iterable[str]) -> tuple[str, ...]:
    if isinstance(vocabulary, tuple):
        return vocabulary
    normalized = sorted(
        {
            token
            for skill in vocabulary
            for token in [canonicalize_skill(skill)]
            if token and len(token) >= 2
        },
        key=lambda item: (-len(item), item),
    )
    return tuple(normalized)


def extract_known_skills(text: str, vocabulary: Iterable[str] | tuple[str, ...]) -> set[str]:
    haystack = normalize_token(text)
    if not haystack:
        return set()
    tokens = prepare_skill_tokens(vocabulary)
    if not tokens:
        return set()
    pattern = _compiled_skill_pattern(tokens)
    return {canonicalize_skill(match.group(0)) for match in pattern.finditer(haystack)}


@lru_cache(maxsize=32)
def _compiled_skill_pattern(tokens: tuple[str, ...]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(token) for token in tokens)
    return re.compile(r"(?<![a-z0-9])(?:" + alternation + r")(?![a-z0-9])")


def extract_domain_terms(text: str) -> set[str]:
    haystack = normalize_token(text)
    terms = set()
    for term, patterns in DOMAIN_PATTERNS.items():
        if any(re.search(pattern, haystack) for pattern in patterns):
            terms.add(term)
    return terms


def normalized_overlap(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = {normalize_token(item) for item in left if normalize_token(item)}
    right_set = {normalize_token(item) for item in right if normalize_token(item)}
    if not left_set:
        return 1.0
    return len(left_set & right_set) / len(left_set)
