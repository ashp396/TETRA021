"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function TeamPanel() {
  const [members, setMembers] = useState<any[]>([]);
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
 
  async function load() {
    const res = await api.get("/api/workspaces/members");
    setMembers(res.data);
  }
  useEffect(() => { load(); }, []);

  async function invite() {
    if (!email.trim()) return;
    setMessage("");
    try {
      const res = await api.post("/api/workspaces/invite", { email });
      setMessage(res.data.message);
      setEmail("");
      load();
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || "Could not add that co founder");
    }
  }

  return (
    <div className="uiFont">
      <h1 className="text-2xl mb-1">Team</h1>
      <p className="text-muted text-sm mb-5">
        Co founders you add here get lasting access to this same workspace: the same documents, score,
        discrepancy threads and tasks, whenever they log in. It is shared access, not a live session,
        so nobody needs to be online at the same time.
      </p>
      <div className="bg-surface border border-line rounded-2xl p-5 mb-5">
        <h3 className="mb-3">Add a co founder</h3>
        <p className="text-xs text-muted mb-2">They need a Finvestor account already; ask them to sign up first if they do not have one.</p>
        <div className="flex gap-2">
          <input className="flex-1 p-3 rounded-lg bg-surface2 border border-line" placeholder="cofounder@company.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          <button className="px-4 py-2 rounded-lg font-bold" style={{ background: "#d7a83f", color: "#1a1220" }} onClick={invite}>Add</button>
        </div>
        {message && <p className="text-sm text-muted mt-2">{message}</p>}
      </div>
      <div className="bg-surface border border-line rounded-2xl p-5">
        <h3 className="mb-3">Who has access</h3>
        {members.map((m, i) => (
          <div key={i} className="flex justify-between items-center p-3 border border-line rounded-xl mb-2 bg-surface2 text-sm">
            <div>
              <div className="font-semibold">{m.name}</div>
              <div className="text-xs text-muted">{m.email}</div>
            </div>
            <span className="text-xs text-muted uppercase">{m.role}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
