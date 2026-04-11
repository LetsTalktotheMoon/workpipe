from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from runtime.automation.text_utils import normalize_token

from .models import JobDocument, RequirementUnit, StructuredJob, SurfaceElement
from .taxonomy import DEFAULT_TAXONOMY, Taxonomy


CONSTRAINT_WEIGHTS = {
    "must_have": 1.0,
    "strong_preference": 0.78,
    "preferred": 0.5,
    "background": 0.24,
}

SECTION_CONTENT_HINT = {
    "core_skills": "tech_stack",
    "must_have_quals": "tech_stack",
    "preferred_quals": "tech_stack",
    "core_responsibilities": "responsibility",
    "job_summary": "domain",
    "metadata": "constraint",
    "title": "responsibility",
}

PARENT_PATTERN_ALIASES = {
    "TECH_MAINSTREAM_PROGRAMMING_LANGUAGE": (
        "mainstream programming language",
        "modern programming language",
        "major programming language",
        "one programming language",
    ),
}

AT_LEAST_K_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
}


def _split_field(value: str) -> list[str]:
    if not value:
        return []
    coarse_parts = re.split(r"\n|; ", value)
    sentence_starters = (
        "experience",
        "knowledge",
        "ability",
        "bachelor",
        "master",
        "phd",
        "proven",
        "strong",
        "excellent",
        "understanding",
        "familiarity",
        "hands-on",
        "proficient",
        "skilled",
        "build",
        "design",
        "develop",
        "write",
        "contribute",
    )
    parts: list[str] = []
    for coarse in coarse_parts:
        chunk = coarse.strip(" -")
        if not chunk:
            continue
        current = ""
        for segment in chunk.split(","):
            piece = segment.strip()
            if not piece:
                continue
            lowered = piece.lower()
            starts_sentence = lowered.startswith(sentence_starters) or re.match(r"^(?:[A-Z][a-z]+(?:\s+[a-z]+){1,}|[0-9]+\+?\s+years?)", piece)
            if current and starts_sentence and len(piece.split()) >= 3:
                parts.append(current.strip(" -"))
                current = piece
            else:
                current = f"{current}, {piece}".strip(", ")
        if current:
            parts.append(current.strip(" -"))
    return [part for part in parts if part]


def _text_blocks(document: JobDocument) -> list[tuple[str, str, str]]:
    row = document.row
    blocks: list[tuple[str, str, str]] = []

    title = str(document.title or "").strip()
    if title:
        blocks.append((title, "title", "strong_preference"))

    summary = str(row.get("job_summary", "") or "").strip()
    if summary:
        blocks.append((summary, "job_summary", "background"))

    for item in _split_field(str(row.get("core_skills", "") or "")):
        blocks.append((item, "core_skills", "strong_preference"))
    for item in _split_field(str(row.get("must_have_quals", "") or "")):
        blocks.append((item, "must_have_quals", "must_have"))
    for item in _split_field(str(row.get("preferred_quals", "") or "")):
        blocks.append((item, "preferred_quals", "preferred"))
    for item in _split_field(str(row.get("core_responsibilities", "") or "")):
        blocks.append((item, "core_responsibilities", "background"))

    work_model = str(row.get("work_model", "") or "").strip()
    if work_model:
        blocks.append((work_model, "metadata", "background"))
    job_location = str(row.get("job_location", "") or "").strip()
    if job_location:
        blocks.append((job_location, "metadata", "background"))

    return blocks


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("/", " / ").replace("(", " ").replace(")", " ")
    lowered = re.sub(r"[^a-z0-9+#.\-/\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _find_alias_matches(text: str, taxonomy: Taxonomy) -> list[str]:
    ordered_hits = _find_alias_hits(text, taxonomy)
    return [canonical_id for _, _, canonical_id, _ in ordered_hits]


def _find_alias_hits(text: str, taxonomy: Taxonomy) -> list[tuple[int, int, str, str]]:
    normalized = _normalize_text(text)
    hits: list[tuple[int, int, str, str]] = []
    seen: set[tuple[str, int, int]] = set()
    for pattern, canonical_id in taxonomy.compiled_alias_patterns:
        for match in pattern.finditer(normalized):
            key = (canonical_id, match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            definition = taxonomy.get(canonical_id)
            if definition is None:
                continue
            hits.append((match.start(), match.end(), canonical_id, definition.content_type))
    hits.sort(key=lambda item: (item[0], item[1] - item[0]))
    deduped: list[tuple[int, int, str, str]] = []
    seen_canonical: set[str] = set()
    for start, end, canonical_id, content_type in hits:
        if canonical_id in seen_canonical:
            continue
        seen_canonical.add(canonical_id)
        deduped.append((start, end, canonical_id, content_type))
    return deduped


def _detect_experience_bucket(text: str) -> list[str]:
    years = [int(item) for item in re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", text.lower())]
    if not years:
        months = [int(item) for item in re.findall(r"(\d+)\+?\s*months?", text.lower())]
        if months:
            return ["EXP_YOE_0_2"]
        return []
    floor = min(years)
    if floor >= 5:
        return ["EXP_YOE_5_PLUS"]
    if floor >= 3:
        return ["EXP_YOE_3_5"]
    return ["EXP_YOE_0_2"]


def _experience_bucket_from_text(text: str) -> str | None:
    buckets = _detect_experience_bucket(text)
    return buckets[0] if buckets else None


def _detect_metadata_constraints(document: JobDocument) -> list[str]:
    row = document.row
    matches: list[str] = []
    work_model = str(row.get("work_model", "") or "").lower()
    if "remote" in work_model:
        matches.append("CONSTRAINT_REMOTE")
    elif "hybrid" in work_model:
        matches.append("CONSTRAINT_HYBRID")
    elif "site" in work_model or "office" in work_model or "on-site" in work_model or "onsite" in work_model:
        matches.append("CONSTRAINT_ONSITE")
    return matches


def _infer_logic_type(text: str, members: list[str], taxonomy: Taxonomy) -> tuple[str, int | None]:
    normalized = _normalize_text(text)
    if _extract_at_least_k(text) is not None and len(members) >= 2:
        return "AT_LEAST_K", _extract_at_least_k(text)
    if " or " in normalized and len(members) >= 2:
        return "OR", None
    if (" and " in normalized or " plus " in normalized) and len(members) >= 2:
        return "AND", None
    if len(members) == 1:
        member = members[0]
        if taxonomy.children_of(member):
            for alias in PARENT_PATTERN_ALIASES.get(member, ()):
                if alias in normalized:
                    return "PARENT_ANY_CHILD", None
    return "SINGLE", None


def _hierarchy_level(members: Iterable[str], taxonomy: Taxonomy) -> str:
    items = list(members)
    if not items:
        return "unknown"
    has_parent = any(taxonomy.children_of(item) for item in items)
    has_child = any(taxonomy.get(item) and taxonomy.get(item).parent_id for item in items)
    if has_parent and has_child:
        return "mixed"
    if has_parent:
        return "parent"
    if has_child:
        return "child"
    return "flat"


def _guess_content_type(section: str, members: Iterable[str], taxonomy: Taxonomy) -> str:
    counter: Counter[str] = Counter()
    for member in members:
        definition = taxonomy.get(member)
        if definition is not None:
            counter[definition.content_type] += 1
    if counter:
        return counter.most_common(1)[0][0]
    return SECTION_CONTENT_HINT.get(section, "other")


def _unit_weight(
    *,
    constraint_type: str,
    content_type: str,
    section: str,
    logic_type: str,
) -> float:
    base = CONSTRAINT_WEIGHTS[constraint_type]
    content_bonus = {
        "tech_stack": 0.12,
        "domain": 0.09,
        "responsibility": 0.08,
        "constraint": 0.06,
        "experience": 0.1,
    }.get(content_type, 0.03)
    section_bonus = {
        "core_skills": 0.08,
        "must_have_quals": 0.1,
        "preferred_quals": 0.04,
        "title": 0.05,
        "core_responsibilities": 0.02,
    }.get(section, 0.0)
    logic_bonus = 0.04 if logic_type in {"OR", "AND", "AT_LEAST_K", "PARENT_ANY_CHILD"} else 0.0
    return round(min(base + content_bonus + section_bonus + logic_bonus, 1.35), 3)


def _member_weight(member: str, taxonomy: Taxonomy) -> float:
    definition = taxonomy.get(member)
    if definition is None:
        return 1.0
    if definition.content_type == "experience":
        return 1.08
    if taxonomy.children_of(member):
        return 0.82
    if definition.parent_id:
        return 1.04
    return 1.0


def _surface_confidence(members: list[str]) -> float:
    if not members:
        return 0.12
    return min(0.55 + 0.1 * len(members), 0.96)


def _role_family(document: JobDocument) -> str:
    title = f"{document.title} {document.row.get('taxonomy_v3', '')}".lower()
    if "machine learning" in title or "applied scientist" in title or "ai engineer" in title:
        return "ai_ml_swe"
    if "data scientist" in title:
        return "data_science"
    if "data engineer" in title:
        return "data_platform"
    if "frontend" in title:
        return "frontend"
    if "full stack" in title or "full-stack" in title:
        return "fullstack"
    if "backend" in title or "java developer" in title or "python developer" in title:
        return "backend_generalist"
    if "platform" in title or "infrastructure" in title or "devops" in title or "site reliability" in title or "sre" in title:
        return "platform"
    if "security" in title:
        return "security"
    if "mobile" in title or "ios" in title or "android" in title:
        return "mobile"
    if "embedded" in title:
        return "embedded"
    if "manager" in title:
        return "manager"
    if "solutions" in title or "architect" in title:
        return "solutions"
    if "qa" in title or "sdet" in title:
        return "qa"
    return "generalist"


def _seniority(document: JobDocument) -> str:
    seniority = str(document.row.get("job_seniority", "") or "").lower()
    title = document.title.lower()
    years_raw = str(document.row.get("min_years_experience", "") or "").strip()
    try:
        years = float(years_raw) if years_raw else None
    except ValueError:
        years = None

    if "staff" in title or "principal" in title or "lead" in title:
        return "lead"
    if "senior" in seniority or title.startswith("senior ") or title.startswith("sr.") or (years is not None and years >= 5):
        return "senior"
    if "new grad" in seniority or "entry" in seniority or (years is not None and years <= 1):
        return "entry"
    if "mid" in seniority or (years is not None and years >= 2):
        return "mid_senior"
    return "mid"


def _business_domains(document: JobDocument, members: Iterable[str], taxonomy: Taxonomy) -> list[str]:
    domains: list[str] = []
    for member in members:
        definition = taxonomy.get(member)
        if definition is not None and definition.content_type == "domain":
            domains.append(member)

    text = " ".join(
        str(document.row.get(column, "") or "")
        for column in ("job_title", "job_nlp_title", "job_summary", "must_have_quals", "preferred_quals")
    )
    normalized_text = normalize_token(text)
    for canonical_id, definition in taxonomy.definitions.items():
        if definition.content_type != "domain":
            continue
        if normalize_token(definition.canonical_name) in normalized_text:
            domains.append(canonical_id)
            continue
        if any(normalize_token(alias) in normalized_text for alias in definition.aliases):
            domains.append(canonical_id)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in domains:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _pattern_signature(units: list[RequirementUnit]) -> str:
    parts = []
    for unit in sorted(
        units,
        key=lambda item: (
            item.constraint_type,
            item.content_type,
            item.logic_type,
            ",".join(item.members),
            item.display_name,
        ),
    ):
        member_sig = "|".join(sorted(unit.members)) or "SURFACE_ONLY"
        parts.append(
            f"{unit.constraint_type}:{unit.content_type}:{unit.logic_type}:{member_sig}"
        )
    return " || ".join(parts)


def _recall_keys(units: list[RequirementUnit]) -> list[str]:
    ranked = sorted(units, key=lambda item: (item.unit_weight, len(item.members)), reverse=True)
    keys: list[str] = []
    seen: set[str] = set()
    anchor_members: list[str] = []
    for unit in ranked:
        if unit.members:
            if len(unit.members) == 1:
                key = unit.members[0]
            else:
                key = f"{unit.logic_type}({','.join(sorted(unit.members))})"
            if key not in seen:
                seen.add(key)
                keys.append(key)
            if unit.constraint_type in {"must_have", "strong_preference"}:
                for member in unit.members:
                    if member not in anchor_members:
                        anchor_members.append(member)
        if len(keys) >= 6:
            break
    if len(anchor_members) >= 2:
        combo = f"{anchor_members[0]}+{anchor_members[1]}"
        if combo not in seen:
            keys.append(combo)
    return keys[:6]


def _new_unit(
    *,
    job_id: str,
    block_index: int,
    local_index: int,
    text: str,
    section: str,
    constraint_type: str,
    members: list[str],
    logic_type: str,
    min_match_count: int | None,
    taxonomy: Taxonomy,
) -> RequirementUnit:
    content_type = _guess_content_type(section, members, taxonomy)
    hierarchy_level = _hierarchy_level(members, taxonomy)
    weight = _unit_weight(
        constraint_type=constraint_type,
        content_type=content_type,
        section=section,
        logic_type=logic_type,
    )
    return RequirementUnit(
        unit_id=f"{job_id}::ru::{block_index}.{local_index}",
        content_type=content_type,
        constraint_type=constraint_type,
        logic_type=logic_type,
        hierarchy_level=hierarchy_level,
        unit_weight=weight,
        members=list(members),
        display_name=text,
        source_section=section,
        member_weights={member: _member_weight(member, taxonomy) for member in members},
        source_evidence=[text],
        min_match_count=min_match_count,
    )


def _connector_between(text: str, left_end: int, right_start: int) -> str:
    between = text[left_end:right_start]
    if " and / or " in between or " and/or " in between:
        return "OR"
    if " or " in between:
        return "OR"
    if " and " in between or " plus " in between:
        return "AND"
    return ""


def _group_hits_by_connector(
    normalized_text: str,
    hits: list[tuple[int, int, str, str]],
) -> list[tuple[str, list[str]]]:
    grouped: list[tuple[str, list[str]]] = []
    i = 0
    while i < len(hits):
        start, end, canonical_id, content_type = hits[i]
        members = [canonical_id]
        logic_type = ""
        j = i + 1
        last_end = end
        while j < len(hits):
            next_start, next_end, next_canonical, next_type = hits[j]
            if next_type != content_type:
                break
            if content_type == "experience":
                break
            connector = _connector_between(normalized_text, last_end, next_start)
            if not connector:
                break
            if not logic_type:
                logic_type = connector
            if connector != logic_type:
                break
            members.append(next_canonical)
            last_end = next_end
            j += 1
        if logic_type and len(members) >= 2:
            grouped.append((logic_type, members))
            i = j
        else:
            i += 1
    return grouped


def _group_inline_list_units(
    normalized_text: str,
    hits: list[tuple[int, int, str, str]],
    consumed: set[str],
) -> list[tuple[str, list[str]]]:
    grouped: list[tuple[str, list[str]]] = []
    logic_candidates = []
    if " or " in normalized_text:
        logic_candidates.append("OR")
    if " and " in normalized_text or " plus " in normalized_text:
        logic_candidates.append("AND")
    for logic_type in logic_candidates:
        by_type: dict[str, list[tuple[int, int, str]]] = {}
        for start, end, canonical_id, content_type in hits:
            if canonical_id in consumed or content_type == "experience":
                continue
            by_type.setdefault(content_type, []).append((start, end, canonical_id))
        for content_type, members in by_type.items():
            if len(members) < 2:
                continue
            members = sorted(members, key=lambda item: item[0])
            window_text = normalized_text[members[0][0]:members[-1][1]]
            if logic_type == "OR" and " or " not in window_text:
                continue
            if logic_type == "AND" and " and " not in window_text and " plus " not in window_text:
                continue
            if len(window_text) > 140:
                continue
            grouped.append((logic_type, [canonical_id for _, _, canonical_id in members]))
    return grouped


def _build_units_for_block(
    *,
    job_id: str,
    block_index: int,
    text: str,
    section: str,
    constraint_type: str,
    taxonomy: Taxonomy,
) -> list[RequirementUnit]:
    normalized = _normalize_text(text)
    hits = _find_alias_hits(text, taxonomy)
    experience_bucket = _experience_bucket_from_text(text)
    units: list[RequirementUnit] = []
    consumed: set[str] = set()
    local_index = 1

    for logic_type, members in _group_hits_by_connector(normalized, hits):
        units.append(
            _new_unit(
                job_id=job_id,
                block_index=block_index,
                local_index=local_index,
                text=text,
                section=section,
                constraint_type=constraint_type,
                members=members,
                logic_type=logic_type,
                min_match_count=None,
                taxonomy=taxonomy,
            )
        )
        consumed.update(members)
        local_index += 1

    for logic_type, members in _group_inline_list_units(normalized, hits, consumed):
        units.append(
            _new_unit(
                job_id=job_id,
                block_index=block_index,
                local_index=local_index,
                text=text,
                section=section,
                constraint_type=constraint_type,
                members=members,
                logic_type=logic_type,
                min_match_count=None,
                taxonomy=taxonomy,
            )
        )
        consumed.update(members)
        local_index += 1

    at_least_k = _extract_at_least_k(text)
    if at_least_k is not None:
        remaining_hits = [(canonical_id, content_type) for _, _, canonical_id, content_type in hits if canonical_id not in consumed]
        grouped_by_type: dict[str, list[str]] = {}
        for canonical_id, content_type in remaining_hits:
            grouped_by_type.setdefault(content_type, []).append(canonical_id)
        best_members: list[str] = []
        for content_type, members in grouped_by_type.items():
            if content_type == "experience":
                continue
            if len(members) > len(best_members):
                best_members = members
        if len(best_members) >= 2:
            units.append(
                _new_unit(
                    job_id=job_id,
                    block_index=block_index,
                    local_index=local_index,
                    text=text,
                    section=section,
                    constraint_type=constraint_type,
                    members=best_members,
                    logic_type="AT_LEAST_K",
                    min_match_count=at_least_k,
                    taxonomy=taxonomy,
                )
            )
            consumed.update(best_members)
            local_index += 1

    for _, _, canonical_id, _ in hits:
        if canonical_id in consumed:
            continue
        if taxonomy.children_of(canonical_id):
            logic_type, min_match_count = _infer_logic_type(text, [canonical_id], taxonomy)
        else:
            logic_type, min_match_count = ("SINGLE", None)
        units.append(
            _new_unit(
                job_id=job_id,
                block_index=block_index,
                local_index=local_index,
                text=text,
                section=section,
                constraint_type=constraint_type,
                members=[canonical_id],
                logic_type=logic_type,
                min_match_count=min_match_count,
                taxonomy=taxonomy,
            )
        )
        consumed.add(canonical_id)
        local_index += 1

    if experience_bucket is not None:
        units.append(
            _new_unit(
                job_id=job_id,
                block_index=block_index,
                local_index=local_index,
                text=text,
                section=section,
                constraint_type=constraint_type,
                members=[experience_bucket],
                logic_type="SINGLE",
                min_match_count=None,
                taxonomy=taxonomy,
            )
        )

    deduped: list[RequirementUnit] = []
    seen_signatures: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for unit in units:
        signature = (
            unit.source_section,
            unit.constraint_type,
            unit.logic_type,
            tuple(sorted(unit.members)),
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        deduped.append(unit)
    return deduped


def _extract_at_least_k(text: str) -> int | None:
    normalized = _normalize_text(text)
    direct = re.search(r"\bat least (\d+)\b", normalized)
    if direct is not None:
        return int(direct.group(1))
    word_direct = re.search(r"\bat least (one|two|three|four)\b", normalized)
    if word_direct is not None:
        return AT_LEAST_K_NUMBER_WORDS[word_direct.group(1)]
    of_pattern = re.search(r"\b(\d+)\s+of (?:the following|these|those)\b", normalized)
    if of_pattern is not None:
        return int(of_pattern.group(1))
    word_of_pattern = re.search(r"\b(one|two|three|four)\s+of (?:the following|these|those)\b", normalized)
    if word_of_pattern is not None:
        return AT_LEAST_K_NUMBER_WORDS[word_of_pattern.group(1)]
    plus_pattern = re.search(r"\b(\d+)\+\s+of (?:the following|these|those)\b", normalized)
    if plus_pattern is not None:
        return int(plus_pattern.group(1))
    return None


def build_structured_job(
    document: JobDocument,
    *,
    taxonomy: Taxonomy = DEFAULT_TAXONOMY,
) -> StructuredJob:
    surface_elements: list[SurfaceElement] = []
    requirement_units: list[RequirementUnit] = []
    all_members: list[str] = []
    pending_surface_texts: list[str] = []

    metadata_constraints = _detect_metadata_constraints(document)
    if metadata_constraints:
        all_members.extend(metadata_constraints)

    for index, (text, section, constraint_type) in enumerate(_text_blocks(document), start=1):
        members = _find_alias_matches(text, taxonomy)
        experience_bucket = _experience_bucket_from_text(text)
        if experience_bucket and experience_bucket not in members:
            members.append(experience_bucket)

        deduped_members: list[str] = []
        seen_members: set[str] = set()
        for member in members:
            if member not in seen_members:
                seen_members.add(member)
                deduped_members.append(member)
        members = deduped_members

        content_type = _guess_content_type(section, members, taxonomy)
        surface_elements.append(
            SurfaceElement(
                text=text,
                source_section=section,
                constraint_type=constraint_type,
                type_hint=content_type,
                canonical_ids=list(members),
                confidence=_surface_confidence(members),
            )
        )

        if members:
            requirement_units.extend(
                _build_units_for_block(
                    job_id=document.job_id,
                    block_index=index,
                    text=text,
                    section=section,
                    constraint_type=constraint_type,
                    taxonomy=taxonomy,
                )
            )
            all_members.extend(members)
        else:
            if section != "metadata":
                pending_surface_texts.append(text)

    canonical_elements: list[str] = []
    seen_exact: set[str] = set()
    for member in all_members:
        if member not in seen_exact:
            seen_exact.add(member)
            canonical_elements.append(member)

    expanded_elements: list[str] = list(canonical_elements)
    for member in list(canonical_elements):
        for ancestor in taxonomy.ancestors_of(member):
            if ancestor not in expanded_elements:
                expanded_elements.append(ancestor)

    business_domains = _business_domains(document, canonical_elements, taxonomy)
    role_family = _role_family(document)
    seniority = _seniority(document)
    pattern_signature = _pattern_signature(requirement_units)
    recall_keys = _recall_keys(requirement_units)

    return StructuredJob(
        job_id=document.job_id,
        company_name=document.company_name,
        title=document.title,
        source_kind=document.source_kind,
        raw_text=document.raw_text,
        role_family=role_family,
        seniority=seniority,
        business_domains=business_domains,
        canonical_elements=canonical_elements,
        expanded_elements=expanded_elements,
        surface_elements=surface_elements,
        requirement_units=requirement_units,
        pattern_signature=pattern_signature,
        recall_keys=recall_keys,
        pending_surface_texts=pending_surface_texts,
        metadata={
            **document.metadata,
            "canonical_element_count": len(canonical_elements),
            "requirement_unit_count": len(requirement_units),
        },
    )
