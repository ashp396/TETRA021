"use client";
import { useRef, useState } from "react";
import { api } from "@/lib/api";

const DOC_TYPES = ["Pitch deck", "Financial statements", "Monthly MIS", "Projections", "Cap table", "Other"];

export default function DocumentUpload({ onAdded }: { onAdded: () => void }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [docType, setDocType] = useState("Pitch deck");
  const [busy, setBusy] = useState(false);
  const [pasteName, setPasteName] = useState("");
  const [pasteText, setPasteText] = useState("");
  const [showPaste, setShowPaste] = useState(false);

  async function handleFiles(files: FileList | null) {
    if (!files || !files.length) return;
    setBusy(true);
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("file", file);
      form.append("doc_type", docType);
      try {
        await api.post("/api/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
      } catch (e) {
        console.error("upload failed", e);
      }
    }
    setBusy(false);
    onAdded();
  }

  async function submitPaste() {
    if (!pasteText.trim()) return;
    const form = new FormData();
    form.append("name", pasteName || `Pasted ${docType}`);
    form.append("doc_type", docType);
    form.append("text", pasteText);
    await api.post("/api/documents/paste", form);
    setPasteText("");
    setPasteName("");
    setShowPaste(false);
    onAdded();
  }

  return (
    <div className="bg-surface border border-line rounded-2xl p-5 uiFont">
      <div className="flex gap-2 flex-wrap mb-3">
        {DOC_TYPES.map((t) => (
          <button
            key={t}
            className="text-xs px-3 py-1 rounded-lg border"
            style={{ borderColor: docType === t ? "#d7a83f" : "#3a2c54", color: docType === t ? "#f2ecf9" : "#a99cc2" }}
            onClick={() => setDocType(t)}
          >
            {t}
          </button>
        ))}
      </div>
      <div
        className="border-2 border-dashed border-line rounded-2xl p-8 text-center text-muted cursor-pointer"
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
      >
        {busy ? "Reading files…" : `Drop a file here, or click to upload as "${docType}" (pdf, docx, pptx, xlsx, csv, txt)`}
      </div>
      <input ref={fileRef} type="file" multiple className="hidden" onChange={(e) => handleFiles(e.target.files)} />
      <div className="mt-3">
        {!showPaste ? (
          <button className="text-xs text-muted underline" onClick={() => setShowPaste(true)}>Or paste text instead</button>
        ) : (
          <div className="space-y-2">
            <input className="w-full p-2 rounded-lg bg-surface2 border border-line text-sm" placeholder="Label" value={pasteName} onChange={(e) => setPasteName(e.target.value)} />
            <textarea className="w-full p-2 rounded-lg bg-surface2 border border-line text-sm" rows={5} placeholder="Paste document text" value={pasteText} onChange={(e) => setPasteText(e.target.value)} />
            <div className="flex gap-2">
              <button className="text-xs px-3 py-2 rounded-lg" style={{ background: "#d7a83f", color: "#1a1220" }} onClick={submitPaste}>Add document</button>
              <button className="text-xs px-3 py-2 rounded-lg border border-line" onClick={() => setShowPaste(false)}>Cancel</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
