import json

from openai import OpenAI

from app.config import settings
from app.models import Issue, PullRequestInfo, ReleaseNotes, TestSuggestion


class AIService:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        ) if settings.openai_api_key else None

    async def analyze(self, pr: PullRequestInfo, diff: str) -> dict:
        if not self.client:
            return self._fallback_report(pr, diff)

        prompt = f"""
You are AI Release Guardian, an expert software release reviewer.
Analyze this GitHub pull request diff and return only valid JSON.

PR:
- Title: {pr.title}
- Author: {pr.author}
- Files changed: {pr.files_changed}
- Additions: {pr.additions}
- Deletions: {pr.deletions}

Return JSON with this exact shape:
{{
  "summary": "short plain English summary",
  "issues": [
    {{
      "type": "Bug Risk | Security Risk | Test Gap | Performance Risk | Maintainability",
      "severity": "Low | Medium | High | Critical",
      "file": "path",
      "line": 1,
      "description": "specific problem",
      "suggested_fix": "specific fix"
    }}
  ],
  "test_suggestions": [
    {{
      "framework": "Jest | PyTest | Playwright | Unknown",
      "file": "suggested test path",
      "reason": "why this test matters",
      "test_code": "compact example test code"
    }}
  ],
  "release_notes": {{
    "summary": "release summary",
    "user_facing_changes": ["change"],
    "technical_changes": ["change"],
    "risks": ["risk"],
    "rollback_plan": "rollback plan"
  }}
}}

Diff:
{diff[:24000]}
"""
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Return only strict JSON. Do not wrap in markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._fallback_report(pr, diff)

    def normalize(self, data: dict) -> tuple[str, list[Issue], list[TestSuggestion], ReleaseNotes]:
        issues = [Issue.model_validate(item) for item in data.get("issues", [])]
        tests = [TestSuggestion.model_validate(item) for item in data.get("test_suggestions", [])]
        notes = ReleaseNotes.model_validate(data.get("release_notes", {}))
        return data.get("summary", "PR analysis completed."), issues, tests, notes

    def _fallback_report(self, pr: PullRequestInfo, diff: str) -> dict:
        has_tests = any(token in diff.lower() for token in ["test", "spec", "__tests__"])
        issue = {
            "type": "Test Gap",
            "severity": "Medium",
            "file": "Unknown",
            "line": None,
            "description": "This PR changes code but no related test changes were detected in the diff.",
            "suggested_fix": "Add targeted unit or integration tests for the modified behavior.",
        }
        return {
            "summary": f"{pr.title} changes {pr.files_changed} files with {pr.additions} additions and {pr.deletions} deletions.",
            "issues": [] if has_tests else [issue],
            "test_suggestions": [
                {
                    "framework": "Unknown",
                    "file": "tests/release_guardian_suggested_test",
                    "reason": "Guardian could not confirm test coverage for the changed behavior.",
                    "test_code": "Add a regression test covering the main changed path and at least one failure/edge case.",
                }
            ],
            "release_notes": {
                "summary": f"Updated implementation for: {pr.title}",
                "user_facing_changes": [],
                "technical_changes": ["Code changes detected in this pull request."],
                "risks": ["AI provider not configured, so fallback analysis was used."],
                "rollback_plan": "Revert this pull request if production errors increase after deployment.",
            },
        }
