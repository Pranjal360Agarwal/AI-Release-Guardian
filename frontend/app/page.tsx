import Link from "next/link";
import { AnalysisForm } from "@/components/AnalysisForm";
import { listReports } from "@/lib/api";
import { ShieldCheck } from "lucide-react";

export default async function HomePage() {
  const reports = await listReports();
  const highRisk = reports.filter((report) => report.risk_level === "High").length;

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-teal">
            <ShieldCheck size={24} />
            <span className="font-bold">AI Release Guardian</span>
          </div>
          <h1 className="text-3xl font-bold text-ink">Release risk analysis for GitHub pull requests</h1>
        </div>
      </header>

      <AnalysisForm />

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Reports</p>
          <p className="mt-2 text-3xl font-bold">{reports.length}</p>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">High-risk PRs</p>
          <p className="mt-2 text-3xl font-bold text-rose">{highRisk}</p>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-600">Latest status</p>
          <p className="mt-2 text-3xl font-bold">{reports[0]?.risk_level || "Ready"}</p>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-bold">Recent Reports</h2>
        <div className="flex flex-col gap-3">
          {reports.length === 0 ? <p className="text-sm text-slate-600">No reports yet. Analyze a PR to start.</p> : null}
          {reports.map((report) => (
            <Link
              className="flex flex-col gap-2 rounded-md border border-line p-4 transition hover:border-teal md:flex-row md:items-center md:justify-between"
              href={`/reports/${report.id}`}
              key={report.id}
            >
              <div>
                <p className="font-semibold">{report.pr.title}</p>
                <p className="text-sm text-slate-600">
                  {report.pr.owner}/{report.pr.repo} #{report.pr.number}
                </p>
              </div>
              <div className="text-sm font-semibold">
                {report.risk_level} · {report.risk_score}/100
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
