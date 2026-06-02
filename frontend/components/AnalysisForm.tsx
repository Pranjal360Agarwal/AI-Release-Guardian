"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { analyzePr } from "@/lib/api";

export function AnalysisForm() {
  const router = useRouter();
  const [prUrl, setPrUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const report = await analyzePr(prUrl);
      router.push(`/reports/${report.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze PR");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-3 rounded-lg border border-line bg-white p-4 shadow-sm">
      <label className="text-sm font-semibold text-ink" htmlFor="pr-url">
        GitHub pull request URL
      </label>
      <div className="flex flex-col gap-3 md:flex-row">
        <input
          id="pr-url"
          className="min-h-11 flex-1 rounded-md border border-line px-3 outline-none focus:border-teal"
          placeholder="https://github.com/owner/repo/pull/12"
          value={prUrl}
          onChange={(event) => setPrUrl(event.target.value)}
          required
        />
        <button
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-md bg-teal px-4 font-semibold text-white disabled:opacity-60"
          disabled={loading}
          type="submit"
        >
          <ShieldCheck size={18} />
          {loading ? "Analyzing..." : "Analyze PR"}
        </button>
      </div>
      {error ? <p className="text-sm text-rose">{error}</p> : null}
    </form>
  );
}
