from typing import Optional

from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings
from app.models import AnalysisReport, StoredReport


engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def save_report(report: AnalysisReport) -> AnalysisReport:
    stored = StoredReport(
        pr_url=report.pr.url,
        owner=report.pr.owner,
        repo=report.pr.repo,
        pr_number=report.pr.number,
        title=report.pr.title,
        author=report.pr.author,
        risk_score=report.risk_score,
        risk_level=report.risk_level,
        report_json=report.model_dump(mode="json"),
    )
    with Session(engine) as session:
        session.add(stored)
        session.commit()
        session.refresh(stored)
    report.id = stored.id
    return report


def get_report(report_id: int) -> Optional[AnalysisReport]:
    with Session(engine) as session:
        stored = session.get(StoredReport, report_id)
        if not stored:
            return None
        data = stored.report_json
        data["id"] = stored.id
        return AnalysisReport.model_validate(data)


def list_reports() -> list[AnalysisReport]:
    with Session(engine) as session:
        rows = session.exec(select(StoredReport).order_by(StoredReport.created_at.desc())).all()
        reports: list[AnalysisReport] = []
        for row in rows:
            data = row.report_json
            data["id"] = row.id
            reports.append(AnalysisReport.model_validate(data))
        return reports
