from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings
from app.models import AnalysisReport, StoredReport


engine: Engine | None = None
db_initialized = False


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    return database_url


def get_engine() -> Engine:
    global engine
    if engine is None:
        database_url = normalize_database_url(settings.database_url)
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        engine = create_engine(database_url, echo=False, connect_args=connect_args)
    return engine


def init_db() -> None:
    global db_initialized
    if not db_initialized:
        SQLModel.metadata.create_all(get_engine())
        db_initialized = True


def save_report(report: AnalysisReport) -> AnalysisReport:
    init_db()
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
    with Session(get_engine()) as session:
        session.add(stored)
        session.commit()
        session.refresh(stored)
    report.id = stored.id
    return report


def get_report(report_id: int) -> AnalysisReport | None:
    init_db()
    with Session(get_engine()) as session:
        stored = session.get(StoredReport, report_id)
        if not stored:
            return None
        data = stored.report_json
        data["id"] = stored.id
        return AnalysisReport.model_validate(data)


def list_reports() -> list[AnalysisReport]:
    init_db()
    with Session(get_engine()) as session:
        rows = session.exec(select(StoredReport).order_by(StoredReport.created_at.desc())).all()
        reports: list[AnalysisReport] = []
        for row in rows:
            data = row.report_json
            data["id"] = row.id
            reports.append(AnalysisReport.model_validate(data))
        return reports