"""
Deterministic Investor Readiness Score engine.

The score itself is computed with fixed arithmetic rules, not by asking a
language model to guess a number. The LLM is only used earlier in the
pipeline to extract structured metrics and discrepancy candidates from raw
text; once those structured numbers exist, every calculation below is plain
arithmetic so the result is reproducible and explainable.

Score range: 350 to 850, following the same band convention used for
Indian credit and readiness benchmarks so founders can anchor to a familiar
scale.
"""

from typing import Dict, List

CATEGORY_WEIGHTS: Dict[str, float] = {
    "Financial Health": 0.25,
    "Pitch Consistency": 0.20,
    "Cap Table Clarity": 0.15,
    "Team Readiness": 0.15,
    "Market Validation": 0.15,
    "DD Preparedness": 0.10,
}

SCORE_FLOOR = 350
SCORE_CEILING = 850
SCORE_RANGE = SCORE_CEILING - SCORE_FLOOR


def percent_difference(a: float, b: float) -> float:
    """Symmetric percent difference between two figures, guarding against zero."""
    base = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / base * 100


def financial_health_score(revenue_figures: List[float], margin_figures: List[float],
                            cash_runway_months: float) -> float:
    """
    0-100. Penalised by the spread between the highest and lowest revenue
    figure quoted across documents, the spread in margin figures, and
    rewarded by a healthier cash runway.
    """
    score = 100.0
    if len(revenue_figures) >= 2:
        spread = percent_difference(max(revenue_figures), min(revenue_figures))
        score -= min(spread, 60)
    if len(margin_figures) >= 2:
        margin_spread = max(margin_figures) - min(margin_figures)
        score -= min(margin_spread, 25)
    if cash_runway_months < 6:
        score -= 15
    elif cash_runway_months < 12:
        score -= 5
    return max(0.0, min(100.0, score))


def pitch_consistency_score(claim_mismatches: int, total_claims_checked: int) -> float:
    """0-100. Share of pitch deck claims that are corroborated by the other documents."""
    if total_claims_checked == 0:
        return 50.0
    corroborated = total_claims_checked - claim_mismatches
    return max(0.0, min(100.0, (corroborated / total_claims_checked) * 100))


def cap_table_score(has_esop_line: bool, ownership_sums_to_100: bool,
                     missing_round_history: int) -> float:
    score = 100.0
    if not has_esop_line:
        score -= 20
    if not ownership_sums_to_100:
        score -= 30
    score -= min(missing_round_history * 10, 30)
    return max(0.0, min(100.0, score))


def team_readiness_score(founders_with_linkedin: int, total_founders: int,
                          key_roles_filled: int, key_roles_total: int) -> float:
    if total_founders == 0 or key_roles_total == 0:
        return 50.0
    identity_component = (founders_with_linkedin / total_founders) * 50
    role_component = (key_roles_filled / key_roles_total) * 50
    return round(identity_component + role_component, 2)


def market_validation_score(tam_stated: bool, tam_source_cited: bool,
                             customer_count_mismatch_percent: float) -> float:
    score = 60.0
    if tam_stated:
        score += 15
    if tam_source_cited:
        score += 15
    score -= min(customer_count_mismatch_percent, 40) * 0.5
    return max(0.0, min(100.0, score))


def dd_prep_score(documents_present: int, documents_expected: int = 5) -> float:
    """0-100. Purely a completeness ratio of the five expected document types."""
    return round((documents_present / documents_expected) * 100, 2)


def compute_readiness_score(category_scores: Dict[str, float]) -> int:
    """
    Weighted sum of the six category scores (each already 0-100), mapped
    onto the 350-850 band. This is the only place the final number is
    produced, so the mapping is auditable end to end.
    """
    weighted_fraction = 0.0
    for category, weight in CATEGORY_WEIGHTS.items():
        weighted_fraction += (category_scores.get(category, 0.0) / 100.0) * weight
    return round(SCORE_FLOOR + weighted_fraction * SCORE_RANGE)


def score_band(score: int) -> str:
    if score >= 750:
        return "Strong"
    if score >= 650:
        return "Ready"
    if score >= 550:
        return "Needs Work"
    return "Early Stage"


def classify_finding(is_confirmed_in_two_sources: bool, has_supporting_number: bool) -> str:
    """
    Returns one of: 'verified_mismatch', 'unresolved_inconsistency', 'missing_information'.
    A finding is a verified mismatch only when two independent documents each
    give a concrete figure and those figures disagree beyond a tolerance.
    """
    if not has_supporting_number:
        return "missing_information"
    if is_confirmed_in_two_sources:
        return "verified_mismatch"
    return "unresolved_inconsistency"
