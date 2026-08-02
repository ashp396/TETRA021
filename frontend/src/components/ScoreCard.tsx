"use client";

const CATEGORIES = [
  { key: "pitch", label: "Pitch Narrative" },
  { key: "financials", label: "Financial Statements" },
  { key: "capTable", label: "Cap Table" },
  { key: "team", label: "Team Credibility" },
  { key: "market", label: "Market Sizing" },
  { key: "ddPrep", label: "DD Preparedness" },
  { key: "regHygiene", label: "Regulatory & Disclosure Hygiene" },
];

export default function ScoreCard({ analysis }: { analysis: any }) {
  if (!analysis) return null;
  const score = analysis.composite_score;
  const pct = (score - 350) / (850 - 350);
  const circ = 2 * Math.PI * 70;
  const offset = circ * (1 - pct);

  return (
    <div className="grid md:grid-cols-2 gap-5 uiFont">
      <div className="bg-surface border border-line rounded-2xl p-5 text-center">
        <h3 className="mb-3">Composite score</h3>
        <div className="relative w-44 h-44 mx-auto">
          <svg width="170" height="170" viewBox="0 0 170 170">
            <circle cx="85" cy="85" r="70" fill="none" stroke="#2a1f40" strokeWidth="12" />
            <circle
              cx="85" cy="85" r="70" fill="none" stroke="url(#g1)" strokeWidth="12" strokeLinecap="round"
              strokeDasharray={circ} strokeDashoffset={offset} transform="rotate(-90 85 85)"
            />
            <defs>
              <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#c1447e" />
                <stop offset="100%" stopColor="#d7a83f" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-4xl font-bold">{score}</div>
            <div className="text-xs text-muted uppercase tracking-wide">of 850</div>
          </div>
        </div>
      </div>
      <div className="bg-surface border border-line rounded-2xl p-5">
        <h3 className="mb-3">Category breakdown</h3>
        {CATEGORIES.map((c) => (
          <div key={c.key} className="mb-3">
            <div className="flex justify-between text-sm mb-1">
              <span>{c.label}</span>
              <span>{analysis.category_scores?.[c.key] ?? 0}/100</span>
            </div>
            <div className="h-2 rounded bg-surface2 overflow-hidden">
              <div className="h-full rounded" style={{ width: `${analysis.category_scores?.[c.key] ?? 0}%`, background: "linear-gradient(90deg,#c1447e,#d7a83f)" }} />
            </div>
            {analysis.category_notes?.[c.key] && <div className="text-xs text-muted mt-1">{analysis.category_notes[c.key]}</div>}
          </div>
        ))}
      </div>
      <div className="bg-surface border border-line rounded-2xl p-5 md:col-span-2">
        <h3 className="mb-2">Readiness summary</h3>
        <p className="leading-relaxed">{analysis.summary}</p>
        {analysis.regulatory_disclaimer && (
          <p className="text-xs text-muted mt-4 leading-relaxed border-t border-line pt-3">{analysis.regulatory_disclaimer}</p>
        )}
      </div>
    </div>
  );
}
