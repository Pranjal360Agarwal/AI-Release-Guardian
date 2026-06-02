from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, JSON
from sqlmodel import Field as SQLField, SQLModel


class AnalyzeRequest(BaseModel):
    pr_url: str = Field(..., examples=["https://github.com/owner/repo/pull/12"])


class CommentRequest(BaseModel):
    report_id: int


class PullRequestInfo(BaseModel):
    owner: str
    repo: str
    number: int
    title: str
    author: str
    branch: str
    base_branch: str
    url: str
    files_changed: int
    additions: int
    deletions: int


class Issue(BaseModel):
    type: str
    severity: str
    file: str
    line: Optional[int] = None
    description: str
    suggested_fix: str


class TestSuggestion(BaseModel):
    framework: str
    file: str
    reason: str
    test_code: str


class ReleaseNotes(BaseModel):
    summary: str
    user_facing_changes: list[str] = []
    technical_changes: list[str] = []
    risks: list[str] = []
    rollback_plan: str


class AnalysisReport(BaseModel):
    id: Optional[int] = None
    pr: PullRequestInfo
    summary: str
    risk_score: int
    risk_level: str
    deployment_recommendation: str
    issues: list[Issue]
    test_suggestions: list[TestSuggestion]
    release_notes: ReleaseNotes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StoredReport(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    pr_url: str
    owner: str
    repo: str
    pr_number: int
    title: str
    author: str
    risk_score: int
    risk_level: str
    report_json: dict[str, Any] = SQLField(sa_column=Column(JSON))
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
