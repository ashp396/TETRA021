"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getToken, clearToken } from "@/lib/api";
import DocumentUpload from "@/components/DocumentUpload";
import ScoreCard from "@/components/ScoreCard";
import DiscrepancyCard from "@/components/DiscrepancyCard";
import PennyPal from "@/components/PennyPal";
import TeamPanel from "@/components/TeamPanel";

type Tab = "workspace" | "analysis" | "discrepancies" | "followups" | "versions" | "report" | "team";

function VersionsTab({ docs }: { docs: any[] }) {
  const [docId, setDocId] = useState("");
  const [newText, setNewText] = useState("");
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function compare() {
    if (!docId || !newText.trim()) return;
    setBusy(true);
    try {
      const res = await api.post("/api/versions/compare", { document_id: docId, new_text: newText });
      setResult(res.data);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="uiFont">
      <h1 className="text-2xl mb-1">Document Version Tracking</h1>
      <p className="text-muted text-sm mb-5">Pick a document already in your workspace, paste the newer version, and see what changed.</p>
      <div className="bg-surface border border-line rounded-2xl p-5">
        <select className="w-full p-3 rounded-lg bg-surface2 border border-line mb-3" value={docId} onChange={(e) => setDocId(e.target.value)}>
          <option value="">Choose a document</option>
          {docs.map((d) => <option key={d.id} value={d.id}>{d.name} (v{d.version_number})</option>)}
        </select>
        <textarea className="w-full p-3 rounded-lg bg-surface2 border border-line text-sm" rows={8} placeholder="Paste the newer version of this document" value={newText} onChange={(e) => setNewText(e.target.value)} />
        <button className="mt-3 px-4 py-2 rounded-lg font-bold" style={{ background: "#d7a83f", color: "#1a1220" }} disabled={busy} onClick={compare}>
          {busy ? "Comparing…" : "Compare versions"}
        </button>
      </div>
      {result && (
        <div className="bg-surface border border-line rounded-2xl p-5 mt-4">
          <h3 className="mb-2">What changed</h3>
          {(result.changes || []).map((c: string, i: number) => (
            <div key={i} className="p-3 pl-4 mb-2 rounded-r-xl bg-surface2" style={{ borderLeft: "3px solid #d7a83f" }}>{c}</div>
          ))}
          <p className="text-muted mt-2">{result.improvementNote}</p>
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("workspace");
  const [docs, setDocs] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [me, setMe] = useState<any>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    if (!getToken()) { router.replace("/login"); return; }
    loadAll();
  }, []);

  async function loadAll() {
    try {
      const [meRes, docsRes, analysisRes] = await Promise.all([
        api.get("/api/auth/me"),
        api.get("/api/documents"),
        api.get("/api/analysis/latest"),
      ]);
      setMe(meRes.data);
      setDocs(docsRes.data);
      setAnalysis(analysisRes.data);
    } catch (e) {
      router.replace("/login");
    }
  }

  async function refreshDocs() {
    const res = await api.get("/api/documents");
    setDocs(res.data);
  }

  async function runAnalysis() {
    if (docs.length < 2) {
      setError("Add at least two documents (for example a pitch deck and financial statements) before running a check.");
      return;
    }
    setAnalyzing(true); setError("");
    try {
      const res = await api.post("/api/analysis/run");
      setAnalysis(res.data);
      setTab("analysis");
    } catch (e: any) {
      setError(e?.response?.data?.detail || "The check could not complete.");
    }
    setAnalyzing(false);
  }

  async function downloadReport() {
    const res = await api.get("/api/report/pdf", { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "finvestor_readiness_report.pdf";
    a.click();
  }

  function logout() {
    clearToken();
    router.replace("/login");
  }

  const navItems: { key: Tab; label: string; badge?: number }[] = [
    { key: "workspace", label: "Document Workspace" },
    { key: "analysis", label: "Readiness Score" },
    { key: "discrepancies", label: "Discrepancy Report", badge: analysis?.discrepancies?.length },
    { key: "followups", label: "Investor Follow Ups" },
    { key: "versions", label: "Version Tracking" },
    { key: "report", label: "Export Report" },
    { key: "team", label: "Team" },
  ];

  return (
    <div className={theme === "dark" ? "" : ""} data-theme={theme}>
      <div className="flex items-center justify-between px-6 py-3 border-b border-line bg-surface sticky top-0 z-40">
        <div className="text-2xl uiFont">Finvestor</div>
        <div className="flex items-center gap-3 uiFont text-sm">
          <button className="px-3 py-2 rounded-lg border border-line" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
          <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold" style={{ background: "linear-gradient(135deg,#c1447e,#d7a83f)", color: "#1a1220" }}>
            {me?.name?.[0]?.toUpperCase() || "?"}
          </div>
          <button className="px-3 py-2 rounded-lg border border-line" onClick={logout}>Log out</button>
        </div>
      </div>

      <div className="grid md:grid-cols-[220px_1fr] min-h-[calc(100vh-57px)]">
        <div className="border-r border-line bg-surface p-3 uiFont hidden md:block">
          {navItems.map((it) => (
            <div
              key={it.key}
              className="flex items-center gap-2 p-3 rounded-lg text-sm mb-1 cursor-pointer"
              style={tab === it.key ? { background: "#2a1f40" } : { color: "#a99cc2" }}
              onClick={() => setTab(it.key)}
            >
              {it.label}
              {!!it.badge && <span className="ml-auto text-xs bg-mulberry text-white rounded-full px-2">{it.badge}</span>}
            </div>
          ))}
        </div>

        <div className="p-6">
          {tab === "workspace" && (
            <div className="uiFont">
              <h1 className="text-2xl mb-1">Document Workspace</h1>
              <p className="text-muted text-sm mb-5">Add every document you would send an investor.</p>
              <DocumentUpload onAdded={refreshDocs} />
              <div className="bg-surface border border-line rounded-2xl p-5 mt-5">
                <h3 className="mb-3">Documents in this round ({docs.length})</h3>
                {docs.map((d) => (
                  <div key={d.id} className="flex justify-between items-center p-3 border border-line rounded-xl mb-2 bg-surface2">
                    <div>
                      <div className="font-semibold text-sm">{d.name}</div>
                      <div className="text-xs text-muted">{d.doc_type}</div>
                    </div>
                  </div>
                ))}
              </div>
              {error && <p className="text-danger text-sm mt-3">{error}</p>}
              <button
                className="mt-5 px-4 py-3 rounded-lg font-bold disabled:opacity-50"
                style={{ background: "linear-gradient(135deg,#d7a83f,#f0c667)", color: "#1a1220" }}
                disabled={analyzing}
                onClick={runAnalysis}
              >
                {analyzing ? "Checking documents…" : "Run readiness check"}
              </button>
            </div>
          )}

          {tab === "analysis" && (
            <div className="uiFont">
              <h1 className="text-2xl mb-1">Investor Readiness Score</h1>
              <p className="text-muted text-sm mb-5">350 to 850, across six categories. Not a valuation, not investment advice.</p>
              {!analysis && <p className="text-muted">Run the readiness check from the Document Workspace tab first.</p>}
              <ScoreCard analysis={analysis} />
            </div>
          )}

          {tab === "discrepancies" && (
            <div className="uiFont">
              <h1 className="text-2xl mb-1">Discrepancy Report</h1>
              <p className="text-muted text-sm mb-5">Every item is linked to the source documents it was found in.</p>
              {(analysis?.discrepancies || []).map((d: any) => <DiscrepancyCard key={d.id} d={d} />)}
              {!analysis && <p className="text-muted">No report yet.</p>}
            </div>
          )}

          {tab === "followups" && (
            <div className="uiFont">
              <h1 className="text-2xl mb-1">Investor Follow Up Questions</h1>
              <p className="text-muted text-sm mb-5">Rehearse these before the real meeting.</p>
              {(analysis?.follow_ups || []).map((q: string, i: number) => (
                <div key={i} className="p-3 pl-4 mb-2 rounded-r-xl bg-surface2" style={{ borderLeft: "3px solid #d7a83f" }}>{q}</div>
              ))}
            </div>
          )}

          {tab === "versions" && <VersionsTab docs={docs} />}

          {tab === "report" && (
            <div className="uiFont">
              <h1 className="text-2xl mb-1">Export Report</h1>
              <p className="text-muted text-sm mb-5">A one page fundraising readiness summary.</p>
              <button
                className="px-4 py-3 rounded-lg font-bold"
                style={{ background: "linear-gradient(135deg,#d7a83f,#f0c667)", color: "#1a1220" }}
                onClick={downloadReport}
                disabled={!analysis}
              >
                Download PDF report
              </button>
            </div>
          )}
          {tab === "team" && <TeamPanel />}
        </div>
      </div>
      <PennyPal />
    </div>
  );
}
