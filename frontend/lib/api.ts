import { AnalysisReport } from "./types";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export async function analyzePr(prUrl: string): Promise<AnalysisReport> {
  const response = await fetch(`${API_URL}/analyze-pr`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pr_url: prUrl }),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function listReports(): Promise<AnalysisReport[]> {
  const response = await fetch(`${API_URL}/reports`, { cache: "no-store" });
  if (!response.ok) {
    return [];
  }
  return response.json();
}

export async function getReport(id: string): Promise<AnalysisReport> {
  const response = await fetch(`${API_URL}/reports/${id}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Report not found");
  }
  return response.json();
}

export async function postComment(reportId: number): Promise<void> {
  const response = await fetch(`${API_URL}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_id: reportId }),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
}
