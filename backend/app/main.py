from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPStatusError

from app.config import settings
from app.models import AnalysisReport, AnalyzeRequest, CommentRequest
from app.services.ai_service import AIService
from app.services.github_service import GitHubService
from app.services.risk_service import calculate_risk
from app.storage import get_report, init_db, list_reports, save_report

app = FastAPI(title="AI Release Guardian API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

github = GitHubService()
ai = AIService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze-pr", response_model=AnalysisReport)
async def analyze_pr(payload: AnalyzeRequest) -> AnalysisReport:
    try:
        pr_payload = await github.fetch_pull_request(payload.pr_url)
        ai_data = await ai.analyze(pr_payload.info, pr_payload.diff)
        summary, issues, tests, notes = ai.normalize(ai_data)
        score, level, recommendation = calculate_risk(pr_payload.info, issues, pr_payload.diff)
        report = AnalysisReport(
            pr=pr_payload.info,
            summary=summary,
            risk_score=score,
            risk_level=level,
            deployment_recommendation=recommendation,
            issues=issues,
            test_suggestions=tests,
            release_notes=notes,
        )
        try:
            return save_report(report)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Database save failed: {type(exc).__name__}",
            ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc


@app.get("/reports", response_model=list[AnalysisReport])
def reports() -> list[AnalysisReport]:
    return list_reports()


@app.get("/reports/{report_id}", response_model=AnalysisReport)
def report_detail(report_id: int) -> AnalysisReport:
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/quality-gate/{report_id}")
def quality_gate(report_id: int) -> dict[str, str | int]:
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.risk_score >= 70:
        status = "fail"
    elif report.risk_score >= 40:
        status = "warn"
    else:
        status = "pass"
    return {
        "status": status,
        "risk_score": report.risk_score,
        "risk_level": report.risk_level,
        "recommendation": report.deployment_recommendation,
    }


@app.post("/comments")
async def post_comment(payload: CommentRequest) -> dict[str, str]:
    report = get_report(payload.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    markdown = render_comment(report)
    await github.post_pr_comment(markdown, report.pr.owner, report.pr.repo, report.pr.number)
    return {"status": "posted"}


def render_comment(report: AnalysisReport) -> str:
    issues = "\n".join(
        f"- **{issue.severity} {issue.type}** in `{issue.file}`: {issue.description}\n  - Fix: {issue.suggested_fix}"
        for issue in report.issues
    ) or "- No major issues found."
    tests = "\n".join(
        f"- `{test.file}`: {test.reason}"
        for test in report.test_suggestions
    ) or "- No missing tests suggested."
    return f"""## AI Release Guardian Report

**Risk:** {report.risk_level} ({report.risk_score}/100)

**Summary:** {report.summary}

**Deployment Recommendation:** {report.deployment_recommendation}

### Issues
{issues}

### Suggested Tests
{tests}

### Release Notes
{report.release_notes.summary}

**Rollback Plan:** {report.release_notes.rollback_plan}
"""
