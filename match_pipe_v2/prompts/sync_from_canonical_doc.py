"""Sync edits from CANONICAL_PROMPT_DOCUMENT.md back to data/*.yaml files."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DOC = ROOT / "CANONICAL_PROMPT_DOCUMENT.md"
DATA_DIR = ROOT / "data"


def str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_representer)


def parse_sentences(text: str) -> dict[str, str]:
    """Extract <!-- SENTENCE: key --> ... <!-- END_SENTENCE: key --> blocks."""
    pattern = re.compile(
        r"<!--\s*SENTENCE:\s*(\S+)\s*-->\n(.*?)(?:\n)?<!--\s*END_SENTENCE:\s*\1\s*-->",
        re.DOTALL,
    )
    sentences: dict[str, str] = {}
    for m in pattern.finditer(text):
        key = m.group(1)
        content = m.group(2)
        sentences[key] = content
    return sentences


def parse_domains(text: str) -> dict[str, dict[str, dict]]:
    """Extract DOMAIN -> ATOM -> SUB_ATOM -> content hierarchy."""
    domains: dict[str, dict[str, dict]] = {}

    # Find all DOMAIN blocks
    domain_pattern = re.compile(r"<!--\s*DOMAIN:\s*(\S+)\s*-->")
    end_domain_pattern = re.compile(r"<!--\s*END_DOMAIN:\s*(\S+)\s*-->")

    for dm in domain_pattern.finditer(text):
        domain_name = dm.group(1)
        start = dm.end()

        # Find matching END_DOMAIN
        end_match = None
        for em in end_domain_pattern.finditer(text, start):
            if em.group(1) == domain_name:
                end_match = em
                break

        if not end_match:
            raise ValueError(f"Missing END_DOMAIN for {domain_name}")

        domain_text = text[start:end_match.start()]
        domains[domain_name] = parse_atoms(domain_text)

    return domains


def parse_atoms(text: str) -> dict[str, dict]:
    """Parse ATOM blocks within a domain."""
    atoms: dict[str, dict] = {}
    atom_pattern = re.compile(r"<!--\s*ATOM:\s*(\S+)\s*-->")
    end_atom_pattern = re.compile(r"<!--\s*END_ATOM:\s*(\S+)\s*-->")

    pos = 0
    while True:
        am = atom_pattern.search(text, pos)
        if not am:
            break
        atom_name = am.group(1)
        start = am.end()

        # Find matching END_ATOM (must be after this atom and not nested in sub-atom)
        depth = 1
        scan_pos = start
        end_pos = None
        while True:
            next_start = atom_pattern.search(text, scan_pos)
            next_end = end_atom_pattern.search(text, scan_pos)

            if not next_end:
                break

            if next_start and next_start.start() < next_end.start():
                depth += 1
                scan_pos = next_start.end()
            else:
                depth -= 1
                if depth == 0 and next_end.group(1) == atom_name:
                    end_pos = next_end.start()
                    break
                scan_pos = next_end.end()

        if end_pos is None:
            raise ValueError(f"Missing END_ATOM for {atom_name}")

        atom_text = text[start:end_pos]
        atoms[atom_name] = parse_sub_atoms(atom_text)
        pos = end_pos + len(f"<!-- END_ATOM: {atom_name} -->")

    return atoms


def parse_sub_atoms(text: str) -> dict[str, dict | str | list]:
    """Parse SUB_ATOM blocks within an atom."""
    items: dict[str, dict | str | list] = {}

    sub_atom_pattern = re.compile(r"<!--\s*SUB_ATOM:\s*(\S+)\s*-->")
    end_sub_atom_pattern = re.compile(r"<!--\s*END_SUB_ATOM:\s*(\S+)\s*-->")
    inline_sub_atom_pattern = re.compile(r"<!--\s*SUB_ATOM:\s*(\S+)\s*-->\s*(.*?)\s*<!--\s*END_SUB_ATOM:\s*\1\s*-->")

    pos = 0
    while True:
        # Try inline first
        inline = inline_sub_atom_pattern.search(text, pos)
        next_block = sub_atom_pattern.search(text, pos)

        if inline and (not next_block or inline.start() < next_block.start()):
            key = inline.group(1)
            value = inline.group(2).strip()
            items[key] = maybe_split_list(value)
            pos = inline.end()
            continue

        if not next_block:
            break

        key = next_block.group(1)
        start = next_block.end()

        # Find matching END_SUB_ATOM
        end_match = None
        for em in end_sub_atom_pattern.finditer(text, start):
            if em.group(1) == key:
                end_match = em
                break

        if not end_match:
            raise ValueError(f"Missing END_SUB_ATOM for {key}")

        content = text[start:end_match.start()].strip("\n")
        if "<!-- SUB_SUB_ATOM:" in content:
            items[key] = parse_sub_sub_atoms(content)
        else:
            items[key] = maybe_split_list(content)
        pos = end_match.end()

    # If no SUB_ATOMs found, treat the entire atom text as a scalar value
    if not items and text.strip():
        return text.strip("\n")

    return items


def parse_sub_sub_atoms(text: str) -> dict[str, str | list]:
    """Parse SUB_SUB_ATOM blocks within a SUB_ATOM."""
    items: dict[str, str | list] = {}
    inline = re.compile(r"<!--\s*SUB_SUB_ATOM:\s*(\S+)\s*-->\s*(.*?)\s*<!--\s*END_SUB_SUB_ATOM:\s*\1\s*-->")
    block_start = re.compile(r"<!--\s*SUB_SUB_ATOM:\s*(\S+)\s*-->")
    block_end = re.compile(r"<!--\s*END_SUB_SUB_ATOM:\s*(\S+)\s*-->")

    pos = 0
    while True:
        # Try inline first
        il = inline.search(text, pos)
        nxt = block_start.search(text, pos)

        if il and (not nxt or il.start() < nxt.start()):
            key = il.group(1)
            value = il.group(2).strip()
            items[key] = maybe_split_list(value)
            pos = il.end()
            continue

        if not nxt:
            break

        key = nxt.group(1)
        start = nxt.end()

        end_match = None
        for em in block_end.finditer(text, start):
            if em.group(1) == key:
                end_match = em
                break

        if not end_match:
            raise ValueError(f"Missing END_SUB_SUB_ATOM for {key}")

        content = text[start:end_match.start()].strip("\n")
        lines = content.split("\n")
        # Remove the first line if it's empty (newline right after start tag)
        if lines and not lines[0].strip():
            lines = lines[1:]
        # Remove the last line if it's pure whitespace (indentation before end tag)
        if lines and not lines[-1].strip():
            lines = lines[:-1]
        content = "\n".join(lines).rstrip(" ")
        items[key] = maybe_split_list(content)
        pos = end_match.end()

    return items


def maybe_split_list(text: str) -> str | list[str]:
    """If text consists entirely of markdown list items, return as list."""
    lines = text.split("\n")
    list_items = []
    current_item = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # A list item starts with - or * at the beginning of line (possibly indented)
        if re.match(r"^\s*[-*]\s", line):
            if current_item:
                list_items.append(current_item)
            current_item = line
        elif current_item and line.startswith("  "):
            # Continuation of previous list item
            current_item += "\n" + line
        else:
            # Mixed content - not a pure list
            return text

    if current_item:
        list_items.append(current_item)

    if len(list_items) >= 1 and all(
        re.match(r"^\s*[-*]\s", item) for item in list_items
    ):
        return list_items
    return text


def rebuild_data_files() -> tuple[int, int]:
    if not DOC.exists():
        raise FileNotFoundError(f"Canonical document not found: {DOC}")

    doc_text = DOC.read_text(encoding="utf-8")

    sentences = parse_sentences(doc_text)
    domains = parse_domains(doc_text)

    # Write sentences.yaml
    sentences_path = DATA_DIR / "sentences.yaml"
    with sentences_path.open("w", encoding="utf-8") as f:
        yaml.dump(sentences, f, allow_unicode=True, sort_keys=False)
    print(f"[WRITTEN] sentences.yaml ({len(sentences)} entries)")

    # Write domain data files
    updated = 0
    for domain_name, atoms in domains.items():
        data_file = DATA_DIR / f"{domain_name}.yaml"
        with data_file.open("w", encoding="utf-8") as f:
            yaml.dump(atoms, f, allow_unicode=True, sort_keys=False)
        print(f"[WRITTEN] {data_file.name}")
        updated += 1

    return len(sentences), updated


def main() -> None:
    sentence_count, domain_count = rebuild_data_files()
    print(f"\nSync complete. {sentence_count} sentence(s), {domain_count} domain file(s) updated.")


if __name__ == "__main__":
    main()
