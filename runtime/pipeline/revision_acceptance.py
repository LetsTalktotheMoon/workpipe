"""
Revision adoption rules shared by main and retarget orchestrators.
"""
from __future__ import annotations


def should_adopt_revision(
    *,
    score_before: float,
    critical_before: int,
    high_before: int,
    score_after: float,
    critical_after: int,
    high_after: int,
    passed_after: bool,
    tolerance: float = 0.3,
) -> bool:
    if critical_after > critical_before or high_after > high_before:
        return False

    if score_after > score_before:
        return True

    severity_improved = critical_after < critical_before or high_after < high_before
    if severity_improved and score_after >= score_before - tolerance:
        return True

    if passed_after and critical_after == critical_before and high_after == high_before:
        return True

    return False
