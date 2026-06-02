export type PullRequestInfo = {
  owner: string;
  repo: string;
  number: number;
  title: string;
  author: string;
  branch: string;
  base_branch: string;
  url: string;
  files_changed: number;
  additions: number;
  deletions: number;
};

export type Issue = {
  type: string;
  severity: "Low" | "Medium" | "High" | "Critical" | string;
  file: string;
  line?: number | null;
  description: string;
  suggested_fix: string;
};

export type TestSuggestion = {
  framework: string;
  file: string;
  reason: string;
  test_code: string;
};

export type ReleaseNotes = {
  summary: string;
  user_facing_changes: string[];
  technical_changes: string[];
  risks: string[];
  rollback_plan: string;
};

export type AnalysisReport = {
  id: number;
  pr: PullRequestInfo;
  summary: string;
  risk_score: number;
  risk_level: "Low" | "Medium" | "High" | string;
  deployment_recommendation: string;
  issues: Issue[];
  test_suggestions: TestSuggestion[];
  release_notes: ReleaseNotes;
  created_at: string;
};
