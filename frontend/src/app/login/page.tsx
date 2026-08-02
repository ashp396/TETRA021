"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/api/auth/login", { email, password });
      setToken(res.data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not log in");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-surface border border-line rounded-2xl p-8">
        <h1 className="text-2xl mb-1">Welcome back</h1>
        <p className="uiFont text-muted text-sm mb-6">Log in to your Finvestor workspace.</p>
        <form onSubmit={submit} className="uiFont space-y-4">
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Email</label>
            <input className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs text-muted mb-1 uppercase tracking-wide">Password</label>
            <input className="w-full p-3 rounded-lg bg-surface2 border border-line text-text" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          {error && <p className="text-danger text-sm">{error}</p>}
          <button className="w-full p-3 rounded-lg font-bold" style={{ background: "linear-gradient(135deg,#d7a83f,#f0c667)", color: "#1a1220" }}>
            Log in
          </button>
        </form>
        <p className="uiFont text-sm text-muted text-center mt-4">
          New here? <a className="text-gold2" href="/signup">Create an account</a>
        </p>
      </div>
    </div>
  );
}
