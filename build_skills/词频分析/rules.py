"""JD non-tech frequency rules.

This module keeps the rule layer separate from extraction and aggregation.
The later pipeline is expected to:

1. Extract JD requirement-bearing text blocks.
2. Split them into candidate phrases.
3. Call the helpers below to normalize, classify, and group phrases.

The rule set is intentionally conservative:
- it prefers dropping uncertain phrases over misclassifying tech stack items
- it excludes any concrete tech already covered by the skills board
- it keeps phrase boundaries intact for terms like ``Full Stack`` and ``Go``
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from build_skills.taxonomy import CATEGORY_TO_SKILLS, SKILL_ALIASES, canonicalize_skill

BUCKET_GENERALIZED_TECH = "generalized_tech"
BUCKET_BUSINESS_DOMAIN = "business_domain"
BUCKET_SOFT_SKILL = "soft_skill"

BUCKETS = (
    BUCKET_GENERALIZED_TECH,
    BUCKET_BUSINESS_DOMAIN,
    BUCKET_SOFT_SKILL,
)

SECTION_INCLUDE_HEADINGS = (
    "minimum qualifications",
    "minimum qualification",
    "basic qualifications",
    "required qualifications",
    "requirements",
    "requirements and qualifications",
    "what you will need",
    "what you'll need",
    "what we need",
    "what you'll do",
    "what you will do",
    "responsibilities",
    "key responsibilities",
    "job description",
    "job descriptions",
    "preferred qualifications",
    "preferred qualification",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
)

SECTION_EXCLUDE_HEADINGS = (
    "about the job",
    "about the company",
    "about us",
    "about the team",
    "about the role",
    "about the position",
    "who we are",
    "our team",
    "why join us",
    "why you will love it here",
    "benefits",
    "perks",
    "compensation",
    "salary",
    "pay",
    "equity",
    "stock",
    "insurance",
    "health insurance",
    "dental",
    "vision",
    "retirement",
    "401k",
    "pto",
    "vacation",
    "eeo",
    "equal opportunity employer",
    "opportunity employer",
    "legal",
    "privacy",
    "location",
    "visa",
    "work authorization",
    "background check",
    "degree",
    "education",
    "bachelor",
    "master",
    "phd",
)

STOP_SINGLE_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

STOP_PHRASES = {
    "related field",
    "equivalent experience",
    "equivalent education",
    "opportunity employer",
    "equal opportunity employer",
    "benefits",
    "benefit",
    "compensation",
    "salary",
    "pay range",
    "stock options",
    "insurance",
    "health insurance",
    "dental insurance",
    "vision insurance",
    "pto",
    "paid time off",
    "retirement plan",
    "401k",
    "work authorization",
    "visa sponsorship",
    "background check",
    "about us",
    "our mission",
    "our team",
    "join us",
    "why join us",
    "company overview",
    "culture",
    "mission",
    "equal employment opportunity",
    "eeo",
}

PREFIX_WRAPPERS = (
    "experience with",
    "experience in",
    "experience working with",
    "familiarity with",
    "proficiency in",
    "ability to",
    "strong ability to",
    "ability in",
    "knowledge of",
    "working knowledge of",
    "hands-on experience with",
    "hands on experience with",
    "solid understanding of",
    "strong understanding of",
    "demonstrated experience with",
    "proven experience with",
    "background in",
    "skills in",
    "strong skills in",
)

SUFFIX_WRAPPERS = (
    "skills",
    "skill",
    "experience",
    "expertise",
    "knowledge",
    "ability",
    "proficiency",
    "background",
)

TECH_EXACT_PHRASES = {
    canonicalize_skill(skill)
    for skills in CATEGORY_TO_SKILLS.values()
    for skill in skills
}
TECH_EXACT_PHRASES.update(SKILL_ALIASES.keys())
TECH_EXACT_PHRASES.update({skill.casefold() for skill in TECH_EXACT_PHRASES})

TECH_SHORT_TOKENS = {"c", "go", "r"}

_ALIAS_LOOKUP = {key.casefold(): value for key, value in SKILL_ALIASES.items()}


@dataclass(frozen=True)
class PhraseRule:
    """A canonical title, the bucket it belongs to, and phrase variants."""

    title: str
    bucket: str
    variants: tuple[str, ...]


@dataclass(frozen=True)
class PhraseDecision:
    """Result returned by phrase classification helpers."""

    title: str
    bucket: str
    normalized_phrase: str
    matched_variant: str
    source_phrase: str


GENERALIZED_TECH_RULES: tuple[PhraseRule, ...] = (
    PhraseRule(
        title="Software Engineering",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "software engineering",
            "software engineer",
            "software developer",
            "software development",
            "software dev",
            "swe",
            "sde",
        ),
    ),
    PhraseRule(
        title="Full-Stack Development",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "full stack",
            "full-stack",
            "fullstack",
            "full stack development",
            "full stack engineer",
            "full stack developer",
            "full stack engineering",
        ),
    ),
    PhraseRule(
        title="Backend Development",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "backend development",
            "back-end development",
            "backend engineer",
            "back-end engineer",
            "backend developer",
            "back-end developer",
            "server-side development",
            "server side development",
            "server-side engineering",
        ),
    ),
    PhraseRule(
        title="Frontend Development",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "frontend development",
            "front-end development",
            "frontend engineer",
            "front-end engineer",
            "frontend developer",
            "front-end developer",
            "client-side engineering",
            "client side engineering",
        ),
    ),
    PhraseRule(
        title="Mobile Development",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "mobile development",
            "mobile engineering",
            "mobile app development",
            "android development",
            "ios development",
            "android engineer",
            "ios engineer",
        ),
    ),
    PhraseRule(
        title="Data Engineering",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "data engineering",
            "data engineer",
            "analytics engineering",
            "analytics engineer",
            "data platform engineering",
            "data pipeline engineering",
            "data infrastructure engineering",
        ),
    ),
    PhraseRule(
        title="Data Science / Analytics",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "data science",
            "data scientist",
            "analytics",
            "business analytics",
            "product analytics",
            "decision science",
            "applied analytics",
        ),
    ),
    PhraseRule(
        title="AI / ML Engineering",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "machine learning",
            "ml engineering",
            "ml engineer",
            "ai engineering",
            "ai engineer",
            "artificial intelligence",
            "applied ai",
            "generative ai engineering",
            "llm application development",
        ),
    ),
    PhraseRule(
        title="Cloud / DevOps / Infrastructure",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "cloud engineering",
            "cloud infrastructure",
            "devops",
            "site reliability engineering",
            "sre",
            "platform engineering",
            "infrastructure engineering",
            "infra engineering",
        ),
    ),
    PhraseRule(
        title="Database Systems",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "relational databases",
            "non-relational databases",
            "database systems",
            "database design",
            "database architecture",
            "database administration",
            "db administration",
            "rdbms",
            "data modeling",
        ),
    ),
    PhraseRule(
        title="API / Service Development",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "api design",
            "api development",
            "service development",
            "microservices architecture",
            "service-oriented architecture",
            "service oriented architecture",
            "service engineering",
        ),
    ),
    PhraseRule(
        title="Quality Engineering",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "software testing",
            "test automation",
            "automation testing",
            "qa engineering",
            "quality engineering",
            "test engineering",
        ),
    ),
    PhraseRule(
        title="Architecture / Systems",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "system design",
            "systems engineering",
            "technical architecture",
            "large-scale systems",
            "large scale systems",
            "distributed systems",
            "architecture",
        ),
    ),
    PhraseRule(
        title="Version Control / Workflow",
        bucket=BUCKET_GENERALIZED_TECH,
        variants=(
            "version control",
            "source control",
            "code review",
            "release management",
            "workflow automation",
        ),
    ),
)

BUSINESS_DOMAIN_RULES: tuple[PhraseRule, ...] = (
    PhraseRule("Healthcare", BUCKET_BUSINESS_DOMAIN, ("healthcare", "health care", "health tech", "health-tech")),
    PhraseRule("Life Sciences / Biotech", BUCKET_BUSINESS_DOMAIN, ("biotech", "biotechnology", "pharma", "pharmaceutical", "life sciences", "life science")),
    PhraseRule("Finance / FinTech", BUCKET_BUSINESS_DOMAIN, ("finance", "financial services", "fintech", "capital markets", "payments", "payment", "wealth management")),
    PhraseRule("Banking", BUCKET_BUSINESS_DOMAIN, ("banking", "bank", "lending", "lender", "consumer banking", "commercial banking")),
    PhraseRule("Insurance", BUCKET_BUSINESS_DOMAIN, ("insurance", "insurtech", "payer", "payer services")),
    PhraseRule("Retail / E-commerce", BUCKET_BUSINESS_DOMAIN, ("retail", "e-commerce", "ecommerce", "marketplace", "consumer goods", "commerce")),
    PhraseRule("Logistics / Supply Chain", BUCKET_BUSINESS_DOMAIN, ("logistics", "supply chain", "fulfillment", "fulfilment", "transportation", "shipping", "last mile", "warehouse")),
    PhraseRule("Manufacturing / Industrial", BUCKET_BUSINESS_DOMAIN, ("manufacturing", "industrial", "factory", "production operations", "operations technology")),
    PhraseRule("Media / Advertising", BUCKET_BUSINESS_DOMAIN, ("media", "advertising", "adtech", "marketing technology", "martech", "content platform", "publisher")),
    PhraseRule("Gaming / Entertainment", BUCKET_BUSINESS_DOMAIN, ("gaming", "game studio", "entertainment", "game platform")),
    PhraseRule("Travel / Hospitality", BUCKET_BUSINESS_DOMAIN, ("travel", "hospitality", "hotel", "airline", "lodging", "booking")),
    PhraseRule("Education / EdTech", BUCKET_BUSINESS_DOMAIN, ("education", "edtech", "learning platform", "student", "campus", "instructional")),
    PhraseRule("Public Sector / Government", BUCKET_BUSINESS_DOMAIN, ("government", "public sector", "public service", "federal", "state government", "local government", "civic")),
    PhraseRule("Energy / Utilities", BUCKET_BUSINESS_DOMAIN, ("energy", "utilities", "utility", "power grid", "renewable energy", "oil and gas")),
    PhraseRule("Telecom", BUCKET_BUSINESS_DOMAIN, ("telecom", "telecommunications", "wireless carrier", "broadband", "carrier")),
    PhraseRule("Automotive / Mobility", BUCKET_BUSINESS_DOMAIN, ("automotive", "mobility", "vehicle platform", "auto industry")),
    PhraseRule("Real Estate / PropTech", BUCKET_BUSINESS_DOMAIN, ("real estate", "proptech", "property", "housing", "rental platform")),
    PhraseRule("Security / Cybersecurity", BUCKET_BUSINESS_DOMAIN, ("cybersecurity", "security domain", "identity management", "fraud prevention", "trust and safety")),
)

SOFT_SKILL_RULES: tuple[PhraseRule, ...] = (
    PhraseRule("Communication", BUCKET_SOFT_SKILL, ("communication", "communicate", "written communication", "verbal communication", "clear communication", "articulate")),
    PhraseRule("Cross-Functional Collaboration", BUCKET_SOFT_SKILL, ("cross-functional collaboration", "cross functional collaboration", "cross-functional teamwork", "cross functional teamwork", "cross-functional partner", "cross functional partner")),
    PhraseRule("Collaboration", BUCKET_SOFT_SKILL, ("collaboration", "collaborate", "teamwork", "team player", "partner with", "cross-team collaboration")),
    PhraseRule("Problem Solving", BUCKET_SOFT_SKILL, ("problem solving", "problem-solving", "critical thinking", "analytical thinking", "troubleshooting")),
    PhraseRule("Ownership / Accountability", BUCKET_SOFT_SKILL, ("ownership", "take ownership", "accountability", "own outcomes", "initiative", "self-starter")),
    PhraseRule("Leadership", BUCKET_SOFT_SKILL, ("leadership", "lead a team", "lead the team", "influence", "influencing")),
    PhraseRule("Mentoring", BUCKET_SOFT_SKILL, ("mentoring", "mentor", "coaching", "coach others")),
    PhraseRule("Stakeholder Management", BUCKET_SOFT_SKILL, ("stakeholder management", "stakeholders", "manage stakeholders", "align stakeholders")),
    PhraseRule("Attention to Detail", BUCKET_SOFT_SKILL, ("attention to detail", "detail-oriented", "detail oriented")),
    PhraseRule("Adaptability", BUCKET_SOFT_SKILL, ("adaptability", "adaptable", "flexibility", "flexible")),
    PhraseRule("Prioritization / Time Management", BUCKET_SOFT_SKILL, ("prioritization", "prioritize", "time management", "manage priorities")),
    PhraseRule("Presentation", BUCKET_SOFT_SKILL, ("presentation", "presenting", "storytelling", "public speaking")),
    PhraseRule("Customer Focus", BUCKET_SOFT_SKILL, ("customer focus", "customer-centric", "customer centric", "user-centric", "user centric", "user empathy")),
    PhraseRule("Learning Agility", BUCKET_SOFT_SKILL, ("learning agility", "quick learner", "fast learner", "curiosity", "curious")),
)

RULES_BY_BUCKET: dict[str, tuple[PhraseRule, ...]] = {
    BUCKET_GENERALIZED_TECH: GENERALIZED_TECH_RULES,
    BUCKET_BUSINESS_DOMAIN: BUSINESS_DOMAIN_RULES,
    BUCKET_SOFT_SKILL: SOFT_SKILL_RULES,
}

ALL_RULES: tuple[PhraseRule, ...] = (
    *GENERALIZED_TECH_RULES,
    *BUSINESS_DOMAIN_RULES,
    *SOFT_SKILL_RULES,
)

_RULE_VARIANT_LOOKUP: dict[str, PhraseRule] = {}
for rule in ALL_RULES:
    for variant in rule.variants:
        _RULE_VARIANT_LOOKUP[variant.casefold()] = rule

def _build_exact_pattern(phrase: str) -> str:
    escaped = re.escape(phrase)
    if phrase in TECH_SHORT_TOKENS:
        return rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"


_TECH_ALIAS_PHRASES = sorted(
    {
        canonicalize_skill(skill)
        for skills in CATEGORY_TO_SKILLS.values()
        for skill in skills
    }
    | {alias for alias in SKILL_ALIASES}
    | {alias.casefold() for alias in SKILL_ALIASES},
    key=lambda item: (-len(item), item),
)

_TECH_EXACT_PATTERNS = tuple((phrase, re.compile(_build_exact_pattern(phrase), flags=re.I if phrase not in TECH_SHORT_TOKENS else 0)) for phrase in _TECH_ALIAS_PHRASES)


def _build_variant_pattern(variant: str) -> re.Pattern[str]:
    text = variant.strip().casefold()
    if not text:
        raise ValueError("variant must not be empty")
    if text in TECH_SHORT_TOKENS:
        return re.compile(_build_exact_pattern(text), flags=0 if text in {"c"} else re.I)

    tokens = [re.escape(token) for token in re.split(r"[\s\-_/]+", text) if token]
    if not tokens:
        return re.compile(_build_exact_pattern(text), flags=re.I)
    joined = r"[\s\-_/]+".join(tokens)
    return re.compile(rf"(?<![A-Za-z0-9]){joined}(?![A-Za-z0-9])", flags=re.I)


_RULE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    rule.title: tuple(_build_variant_pattern(variant) for variant in rule.variants)
    for rule in ALL_RULES
}


def _strip_prefix_wrappers(text: str) -> str:
    lowered = text.casefold()
    for prefix in PREFIX_WRAPPERS:
        if lowered.startswith(prefix):
            return text[len(prefix) :].strip(" ,:;-")
    return text


def _strip_suffix_wrappers(text: str) -> str:
    lowered = text.casefold()
    for suffix in SUFFIX_WRAPPERS:
        if lowered.endswith(f" {suffix}"):
            return text[: -len(suffix)].strip(" ,:;-")
    return text


def normalize_phrase(raw_phrase: str) -> str:
    """Normalize a candidate phrase without changing its semantic meaning."""

    if raw_phrase is None:
        return ""

    text = str(raw_phrase).replace("\u00a0", " ").strip()
    if not text:
        return ""

    text = re.sub(r"^[\s\-\*\u2022]+", "", text)
    text = re.sub(r"[\s\-\*\u2022]+$", "", text)
    text = text.replace("—", "-").replace("–", "-").replace("／", "/")
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" ,;:()[]{}")

    if not text:
        return ""

    text = _strip_prefix_wrappers(text)
    text = _strip_suffix_wrappers(text)
    text = re.sub(r"^(?:the|an|a|and|or)\s+", "", text, flags=re.I)
    text = re.sub(r"\s+(?:the|an|a|and|or)$", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ,;:()[]{}")


def normalize_for_matching(raw_phrase: str) -> str:
    """Lower-case matching form used by the rules engine."""

    return normalize_phrase(raw_phrase).casefold()


def is_noise_phrase(raw_phrase: str) -> bool:
    """Return True for pure boilerplate or useless fragments."""

    phrase = normalize_for_matching(raw_phrase)
    if not phrase:
        return True
    if phrase in STOP_SINGLE_WORDS:
        return True
    if phrase in STOP_PHRASES:
        return True

    if len(phrase) <= 2 and phrase not in TECH_SHORT_TOKENS:
        return True

    for stop in STOP_PHRASES:
        if stop in phrase:
            return True
    return False


def is_requirement_heading(raw_heading: str) -> bool:
    """True when the heading should be used as JD requirement input."""

    heading = normalize_for_matching(raw_heading)
    if not heading:
        return False
    if any(excluded == heading or excluded in heading for excluded in SECTION_EXCLUDE_HEADINGS):
        return False
    return any(include == heading or include in heading for include in SECTION_INCLUDE_HEADINGS)


def is_excluded_heading(raw_heading: str) -> bool:
    heading = normalize_for_matching(raw_heading)
    if not heading:
        return True
    return any(excluded == heading or excluded in heading for excluded in SECTION_EXCLUDE_HEADINGS)


def _tech_pattern_hits(text: str) -> list[str]:
    lowered = text.casefold()
    hits: list[str] = []
    for phrase, pattern in _TECH_EXACT_PATTERNS:
        if pattern.search(lowered):
            hits.append(phrase)
    return hits


def _matches_any_rule(normalized_phrase: str, rules: tuple[PhraseRule, ...]) -> bool:
    for rule in rules:
        for pattern in _RULE_PATTERNS[rule.title]:
            if pattern.search(normalized_phrase):
                return True
    return False


def is_specific_tech_phrase(raw_phrase: str) -> bool:
    """True if the phrase is already covered by the skills board."""

    phrase = normalize_phrase(raw_phrase)
    if not phrase:
        return False

    lowered = phrase.casefold()
    if _matches_any_rule(lowered, GENERALIZED_TECH_RULES):
        return False

    if lowered in TECH_EXACT_PHRASES:
        return True

    if any(token in TECH_SHORT_TOKENS for token in re.findall(r"[A-Za-z][A-Za-z0-9#+.]*/?[A-Za-z0-9#+.]*", phrase)):
        # standalone C / Go / R tokens need to be protected against ordinary words
        for token in re.findall(r"(?<![A-Za-z0-9])(C\+\+|C#|C|Go|R)(?![A-Za-z0-9])", phrase):
            if token.casefold() in TECH_SHORT_TOKENS or token in {"C", "C++", "C#"}:
                return True

    return bool(_tech_pattern_hits(phrase))


def _match_rule(normalized_phrase: str) -> tuple[PhraseRule, str] | None:
    for rule in ALL_RULES:
        for variant, pattern in zip(rule.variants, _RULE_PATTERNS[rule.title], strict=True):
            if pattern.search(normalized_phrase):
                return rule, variant
    return None


def classify_phrase(raw_phrase: str) -> PhraseDecision | None:
    """Classify a candidate phrase into one of the three buckets.

    Returns ``None`` when the phrase should be dropped.
    """

    normalized = normalize_phrase(raw_phrase)
    if not normalized:
        return None
    if is_noise_phrase(normalized):
        return None
    if is_specific_tech_phrase(normalized):
        return None

    matched = _match_rule(normalize_for_matching(normalized))
    if not matched:
        return None

    rule, variant = matched
    return PhraseDecision(
        title=rule.title,
        bucket=rule.bucket,
        normalized_phrase=normalized,
        matched_variant=variant,
        source_phrase=str(raw_phrase),
    )


def canonicalize_phrase(raw_phrase: str) -> str | None:
    """Return the merged title for a phrase, or ``None`` when dropped."""

    decision = classify_phrase(raw_phrase)
    return decision.title if decision else None


def canonicalize_variants(raw_text: str) -> list[str]:
    """Split a slash/comma separated text blob into semantic variants.

    The caller should still run :func:`classify_phrase` on each item.
    Concrete tech stack terms are filtered out before this function is useful
    in the pipeline.
    """

    text = normalize_phrase(raw_text)
    if not text:
        return []

    protected: dict[str, str] = {}
    protected_text = text
    for index, phrase in enumerate(_TECH_ALIAS_PHRASES):
        if not phrase:
            continue
        pattern = re.compile(_build_exact_pattern(phrase), flags=re.I)

        def _repl(match: re.Match[str], *, _i: int = index) -> str:
            token = f"__TECH_{_i}__"
            protected[token] = match.group(0)
            return token

        protected_text = pattern.sub(_repl, protected_text)

    parts = re.split(r"\s*(?:/|;|\||\n|\band\b|\bor\b|\+)\s*", protected_text, flags=re.I)
    variants: list[str] = []
    for part in parts:
        candidate = part.strip(" ,;:")
        if not candidate:
            continue
        for token, original in protected.items():
            candidate = candidate.replace(token, original)
        candidate = normalize_phrase(candidate)
        if candidate:
            variants.append(candidate)
    return variants


def group_phrases(phrases: Iterable[str]) -> dict[str, dict[str, object]]:
    """Group accepted phrases by merged title.

    Returns a structure ready for later frequency aggregation:

    ``{title: {"bucket": ..., "variants": [...], "count": 0}}``
    """

    grouped: dict[str, dict[str, object]] = {}
    for raw_phrase in phrases:
        decision = classify_phrase(raw_phrase)
        if decision is None:
            continue
        bucket = grouped.setdefault(
            decision.title,
            {"bucket": decision.bucket, "variants": [], "count": 0},
        )
        variants: list[str] = bucket["variants"]  # type: ignore[assignment]
        if decision.source_phrase not in variants:
            variants.append(decision.source_phrase)
        bucket["count"] = int(bucket["count"]) + 1
    return grouped


def rule_index() -> dict[str, PhraseRule]:
    """Expose the canonical rule table for downstream aggregation."""

    return {rule.title: rule for rule in ALL_RULES}


__all__ = [
    "ALL_RULES",
    "BUCKETS",
    "BUCKET_BUSINESS_DOMAIN",
    "BUCKET_GENERALIZED_TECH",
    "BUCKET_SOFT_SKILL",
    "BUSINESS_DOMAIN_RULES",
    "GENERALIZED_TECH_RULES",
    "PhraseDecision",
    "PhraseRule",
    "RULES_BY_BUCKET",
    "SECTION_EXCLUDE_HEADINGS",
    "SECTION_INCLUDE_HEADINGS",
    "SOFT_SKILL_RULES",
    "STOP_PHRASES",
    "STOP_SINGLE_WORDS",
    "TECH_EXACT_PHRASES",
    "canonicalize_phrase",
    "canonicalize_variants",
    "classify_phrase",
    "group_phrases",
    "is_excluded_heading",
    "is_noise_phrase",
    "is_requirement_heading",
    "is_specific_tech_phrase",
    "normalize_for_matching",
    "normalize_phrase",
    "rule_index",
]
