"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function DiscrepancyCard({ d }: { d: any }) {
  const [comments, setComments] = useState<string[]>([]);
  const [tasks, setTasks] = useState<{ text: string; done: boolean; id?: string }[]>([]);
  const [commentText, setCommentText] = useState("");
  const [taskText, setTaskText] = useState("");
 
  const badgeColor =
    d.classification === "verified mismatch" ? "#e0587a" :
    d.classification === "missing information" ? "#a99cc2" : "#f0c667";

  async function postComment() {
    if (!commentText.trim()) return;
    await api.post(`/api/discrepancies/${d.id}/comments`, { text: commentText });
    setComments((c) => [...c, commentText]);
    setCommentText("");
  }
  async function postTask() {
    if (!taskText.trim()) return;
    const res = await api.post(`/api/discrepancies/${d.id}/tasks`, { text: taskText });
    setTasks((t) => [...t, { text: taskText, done: false, id: res.data.id }]);
    setTaskText("");
  }
  async function toggleTask(i: number) {
    const t = tasks[i];
    if (!t.id) return;
    await api.post(`/api/discrepancies/tasks/${t.id}/toggle`);
    setTasks((prev) => prev.map((x, idx) => (idx === i ? { ...x, done: !x.done } : x)));
  }

  return (
    <div className="bg-surface2 border border-line rounded-2xl p-4 mb-3 uiFont">
      <span className="text-xs font-bold px-3 py-1 rounded-full" style={{ background: badgeColor + "30", color: badgeColor }}>
        {d.classification}
      </span>
      <h4 className="text-lg mt-2 mb-1">{d.title}</h4>
      <p className="text-sm leading-relaxed">{d.description}</p>
      {d.sources?.length > 0 && (
        <div className="text-xs text-muted mt-2">
          Found in: {d.sources.map((s: string, i: number) => (
            <span key={i} className="bg-surface border border-line rounded px-2 py-0.5 mr-1">{s}</span>
          ))}
        </div>
      )}
      <div className="bg-surface border border-line rounded-xl p-3 mt-3">
        {comments.map((c, i) => <div key={i} className="text-sm border-b border-dashed border-line py-1">{c}</div>)}
        <div className="flex gap-2 mt-2">
          <input className="flex-1 p-2 rounded-lg bg-surface2 border border-line text-xs" placeholder="Add a comment for the team" value={commentText} onChange={(e) => setCommentText(e.target.value)} />
          <button className="text-xs px-3 rounded-lg border border-line" onClick={postComment}>Post</button>
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {tasks.map((t, i) => (
            <span key={i} className="text-xs bg-surface2 border border-line rounded-full px-3 py-1 cursor-pointer" style={{ textDecoration: t.done ? "line-through" : "none" }} onClick={() => toggleTask(i)}>
              {t.done ? "✓" : "○"} {t.text}
            </span>
          ))}
        </div>
        <div className="flex gap-2 mt-2">
          <input className="flex-1 p-2 rounded-lg bg-surface2 border border-line text-xs" placeholder="Assign a fix, e.g. Fix revenue slide by Friday" value={taskText} onChange={(e) => setTaskText(e.target.value)} />
          <button className="text-xs px-3 rounded-lg border border-line" onClick={postTask}>Add task</button>
        </div>
      </div>
    </div>
  );
}
