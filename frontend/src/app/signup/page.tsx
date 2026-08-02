"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";

export default function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [stage, setStage] = useState("Seed");
  const [error, setError] = useState("");
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/api/auth/signup", { name, email, password, startup_stage: stage });
      setToken(res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not create your account");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-surface border border-line rounded-2xl p-8">
        <h1 className="text-2xl mb-1">Create your workspace</h1>
        <p className="uiFont text-muted text-sm mb-6">Fundraising readiness, checked before your investor does.</p>
        <form onSubmit={submit} className="uiFont space-y-4">
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Full name</label>
            <input className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" required value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Work email</label>
            <input className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Password</label>
            <input className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Funding stage</label>
            <select className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" value={stage} onChange={(e) => setStage(e.target.value)}>
              <option>Idea</option>
              <option>Seed</option>
              <option>Series A</option>
            </select>
          </div>
          {error && <p className="text-danger text-sm">{error}</p>}
          <button className="w-full p-3 rounded-lg font-bold" style={{ background: "linear-gradient(135deg,#d7a83f,#f0c667)", color: "#1a1220" }}>
            Sign up
          </button>
        </form>
        <p className="uiFont text-sm text-muted text-center mt-4">
          Already registered? <a className="text-gold2" href="/login">Log in</a>
        </p>
      </div>
    </div>
  );
}
