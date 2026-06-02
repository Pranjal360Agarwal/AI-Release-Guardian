"use client";

import { useState } from "react";
import { GitPullRequest, MessageSquarePlus, ShieldAlert, TestTube2 } from "lucide-react";
import { postComment } from "@/lib/api";
import { AnalysisReport } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";

function riskColor(level: string) {
  if (level === "High") return "text-rose";
  if (level === "Medium") return "text-amber";
  return "text-teal";
}

export function ReportView({ report }: { report: AnalysisReport }) {
  const [commentState, setCommentState] = useState<string>("");

  async function onPostComment() {
    setCommentState("Posting...");
    try {
      await postComment(report.id);
      setCommentState("Posted to GitHub.");
    } catch (error) {
      setCommentState(error instanceof Error ? error.message : "Failed to post comment.");
    }
  }

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-5 px-4 py-6">
      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-teal">
              <GitPullRequest size={18} />
              {report.pr.owner}/{report.pr.repo} #{report.pr.number}
            </div>
            <h1 className="text-2xl font-bold text-ink">{report.pr.title}</h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-600">{report.summary}</p>
          </div>
          <button
            onClick={onPostComment}
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md border border-line px-3 font-semibold"
          >
            <MessageSquarePlus size={17} />
            Post GitHub Comment
          </button>
        </div>
        {commentState ? <p className="mt-3 text-sm text-slate-600">{commentState}</p> : null}
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Risk Score</p>
          <p className={`mt-2 text-4xl font-bold ${riskColor(report.risk_level)}`}>{report.risk_score}</p>
          <p className="font-semibold">{report.risk_level} risk</p>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Files Changed</p>
          <p className="mt-2 text-3xl font-bold">{report.pr.files_changed}</p>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Lines Changed</p>
          <p className="mt-2 text-3xl font-bold">{report.pr.additions + report.pr.deletions}</p>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Issues Found</p>
          <p className="mt-2 text-3xl font-bold">{report.issues.length}</p>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <div className="mb-3 flex items-center gap-2">
          <ShieldAlert size={19} />
          <h2 className="text-lg font-bold">Deployment Recommendation</h2>
        </div>
        <p>{report.deployment_recommendation}</p>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-bold">Issues</h2>
        <div className="flex flex-col gap-3">
          {report.issues.length === 0 ? <p className="text-sm text-slate-600">No major issues found.</p> : null}
          {report.issues.map((issue, index) => (
            <article key={`${issue.file}-${index}`} className="rounded-md border border-line p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <SeverityBadge value={issue.severity} />
                <span className="font-semibold">{issue.type}</span>
                <span className="text-sm text-slate-600">{issue.file}{issue.line ? `:${issue.line}` : ""}</span>
              </div>
              <p className="text-sm">{issue.description}</p>
              <p className="mt-2 text-sm font-semibold">Suggested fix</p>
              <p className="text-sm text-slate-700">{issue.suggested_fix}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <TestTube2 size={19} />
          <h2 className="text-lg font-bold">Suggested Tests</h2>
        </div>
        <div className="flex flex-col gap-3">
          {report.test_suggestions.map((test, index) => (
            <article key={`${test.file}-${index}`} className="rounded-md border border-line p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <span className="rounded border border-line px-2 py-1 text-xs font-semibold">{test.framework}</span>
                <span className="font-semibold">{test.file}</span>
              </div>
              <p className="mb-3 text-sm text-slate-700">{test.reason}</p>
              <pre className="rounded-md bg-slate-950 p-3 text-sm text-slate-100">{test.test_code}</pre>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-lg font-bold">Release Notes</h2>
        <p className="mb-4">{report.release_notes.summary}</p>
        <div className="grid gap-4 md:grid-cols-3">
          <NoteList title="User-facing" items={report.release_notes.user_facing_changes} />
          <NoteList title="Technical" items={report.release_notes.technical_changes} />
          <NoteList title="Risks" items={report.release_notes.risks} />
        </div>
        <p className="mt-4 text-sm font-semibold">Rollback plan</p>
        <p className="text-sm text-slate-700">{report.release_notes.rollback_plan}</p>
      </section>
    </main>
  );
}

function NoteList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <p className="mb-2 text-sm font-semibold">{title}</p>
      <ul className="flex flex-col gap-1 text-sm text-slate-700">
        {(items.length ? items : ["None identified."]).map((item, index) => (
          <li key={`${title}-${index}`}>- {item}</li>
        ))}
      </ul>
    </div>
  );
}
