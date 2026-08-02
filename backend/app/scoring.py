"""The readiness scoring engine.

Cross document verification and discrepancy detection are retrieval
driven: for each metric area (revenue, margins, growth, customers, cash,
ownership, and standard Indian private fundraising disclosure hygiene) we
retrieve the most relevant chunks from every uploaded document using
Postgres full text search (see app.search_index), then ask the model to
compare them and cite which document each figure came from. This keeps
the score explainable and grounded instead of a black box number, and
stops the model from inventing figures that are not actually in the
documents.

A note on "SEBI guidelines": SEBI's direct rulebook (ICDR, LODR, PIT
regulations) governs listed companies, IPOs, and SEBI registered
Alternative Investment Funds. A private seed or Series A round by an
unlisted startup is mostly governed by the Companies Act, 2013 instead,
in particular Section 42 on private placement (a cap of 200 investors
per financial year, and requirements like a PAS-4 offer letter and a
valuation report from a registered valuer), plus ordinary disclosure
hygiene that SEBI registered AIFs commonly expect from the startups they
fund (arm's length related party transactions, a cap table consistent
with the round terms, valuation support for the round). This tool checks
documents for that general hygiene and flags gaps in it; it does not
perform a legal or regulatory compliance review, and nothing it produces
should be treated as legal advice. A company secretary or securities
lawyer should sign off on actual compliance.
"""
from sqlalchemy.orm import Session
from app.search_index import retrieve_all_grouped
from app.llm import chat_json

CATEGORIES = [
    {"key": "pitch", "label": "Pitch Narrative", "weight": 0.18},
    {"key": "financials", "label": "Financial Statements", "weight": 0.22},
    {"key": "capTable", "label": "Cap Table", "weight": 0.16},
    {"key": "team", "label": "Team Credibility", "weight": 0.12},
    {"key": "market", "label": "Market Sizing", "weight": 0.12},
    {"key": "ddPrep", "label": "DD Preparedness", "weight": 0.10},
    {"key": "regHygiene", "label": "Regulatory & Disclosure Hygiene", "weight": 0.10},
]

STAGE_BENCHMARKS = {
    "Idea": {"min": 350, "target": 520},
    "Seed": {"min": 520, "target": 650},
    "Series A": {"min": 650, "target": 780},
}

METRIC_QUERIES = [
    "revenue and monthly recurring revenue figures",
    "gross margin and unit economics",
    "user growth and customer count",
    "cash balance and runway",
    "founder ownership and equity percentages, cap table",
    "market size, TAM SAM SOM claims",
    "team background, founder experience, hiring plan",
    "projections and forward looking assumptions",
    "private placement offer letter, PAS-4, valuation report, Section 42",
    "related party transactions, founder linked vendors, arm's length",
]

SYSTEM_PROMPT = (
    "You are a rigorous fundraising due diligence analyst for Indian startups. "
    "You only state what the provided document excerpts actually support, and you "
    "always name which document an excerpt came from. You never invent numbers. "
    "Treat amounts as Indian Rupees unless a document clearly states another "
    "currency. When reconciling figures, 1 lakh = 100000 and 1 crore = 10000000. "
    "For the regHygiene category, check only for ordinary disclosure hygiene that "
    "Indian private placements and SEBI registered AIF investors commonly expect: "
    "a private placement offer letter or board resolution, a valuation report or "
    "basis for the round price, a cap table consistent with the amounts raised, "
    "and any related party or founder linked transactions being flagged rather than "
    "buried. Do not claim to assess formal SEBI or Companies Act compliance, and say "
    "so explicitly if evidence for this category is thin. You do not value the "
    "company and you do not give an investment recommendation. Respond with valid "
    "JSON only, no prose, no markdown fences."
)

REGULATORY_DISCLAIMER = (
    "Finvestor checks for common Indian private fundraising disclosure hygiene "
    "(private placement paperwork, valuation support, related party flags). It "
    "does not perform a legal or regulatory compliance review, and it is not a "
    "substitute for sign off by a company secretary or securities lawyer. SEBI's "
    "own rulebook mainly governs listed companies, IPOs, and SEBI registered "
    "investment funds; a private round is chiefly governed by the Companies Act, "
    "2013, including the private placement limits in Section 42."
)

def compute_composite_score(category_scores: dict) -> int:
    weighted = 0.0
    for cat in CATEGORIES:
        v = max(0, min(100, category_scores.get(cat["key"], 0)))
        weighted += v * cat["weight"]
    score = round(350 + (weighted / 100) * (850 - 350))
    return max(350, min(850, score))

def build_evidence_block(db: Session, workspace_id: str) -> tuple[str, set]:
    hits = retrieve_all_grouped(db, workspace_id, METRIC_QUERIES, top_k_each=6)
    lines = [f"[{h['document_name']} | {h['doc_type']}] {h['text']}" for h in hits]
    known_types = {h["doc_type"] for h in hits}
    return "\n\n".join(lines), known_types

def run_full_analysis(db: Session, workspace_id: str, doc_names: list[str]) -> dict:
    evidence, known_types = build_evidence_block(db, workspace_id)
    expected = {"Pitch deck", "Financial statements", "Monthly MIS", "Projections", "Cap table"}
    gaps = expected - known_types
    gap_note = f"\n\nNote: no evidence was retrieved for these expected document types: {', '.join(gaps)}." if gaps else ""

    user_prompt = f"""Below are retrieved excerpts from the fundraising documents in this
workspace (retrieved because they are the passages most relevant to revenue,
margins, growth, cash, ownership, market sizing, team, projections, and
private placement / related party disclosure hygiene).

Documents present in this workspace: {', '.join(doc_names)}

Produce a JSON object with exactly this shape:
{{
 "categoryScores": {{"pitch":0-100,"financials":0-100,"capTable":0-100,"team":0-100,"market":0-100,"ddPrep":0-100,"regHygiene":0-100}},
 "categoryNotes": {{"pitch":"one sentence","financials":"one sentence","capTable":"one sentence","team":"one sentence","market":"one sentence","ddPrep":"one sentence","regHygiene":"one sentence"}},
 "discrepancies": [
   {{"title":"short title","category":"pitch|financials|capTable|team|market|ddPrep|regHygiene","classification":"verified mismatch|unresolved inconsistency|missing information","description":"what is inconsistent and why","sources":["Document name 1","Document name 2"],"severity":"high|medium|low"}}
 ],
 "followUpQuestions": ["question an investor would likely ask, phrased directly"],
 "summary": "a compact one paragraph fundraising readiness summary, plain language"
}}

Classification rules:
- verified mismatch: two or more excerpts state different numbers or facts for the same thing.
- unresolved inconsistency: something looks off, such as a sudden change in assumptions or an unsupported claim, without a clear factual contradiction.
- missing information: something an investor would expect is absent from the retrieved evidence.

List at least 4 discrepancies where the evidence gives any basis for them, and at least 5 follow up questions.

EVIDENCE:
{evidence}{gap_note}
"""
    parsed = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2400)
    parsed["compositeScore"] = compute_composite_score(parsed.get("categoryScores", {}))
    parsed["regulatoryDisclaimer"] = REGULATORY_DISCLAIMER
    return parsed

def compare_versions(old_text: str, new_text: str) -> dict:
    prompt = f"""Compare version A and version B of the same fundraising document.
Respond with JSON only:
{{"changes":["short bullet describing a real change"], "improvementNote":"one sentence on whether clarity or consistency improved"}}
Only note real differences, not rewording with the same meaning.

VERSION A:
{old_text[:6000]}

VERSION B:
{new_text[:6000]}
"""
    return chat_json(
        "You compare document versions precisely and respond with JSON only, no prose.",
        prompt,
        max_tokens=800,
    )
