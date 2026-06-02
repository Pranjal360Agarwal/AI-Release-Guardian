from app.models import Issue, PullRequestInfo


SENSITIVE_PATTERNS = [
    "auth",
    "login",
    "session",
    "token",
    "password",
    "payment",
    "billing",
    "database",
    "migration",
    ".env",
    "secret",
    "permission",
    "security",
    "config",
]


def calculate_risk(pr: PullRequestInfo, issues: list[Issue], changed_diff: str) -> tuple[int, str, str]:
    score = 10
    total_lines = pr.additions + pr.deletions

    if pr.files_changed >= 10:
        score += 15
    elif pr.files_changed >= 5:
        score += 8

    if total_lines >= 500:
        score += 20
    elif total_lines >= 150:
        score += 10

    lowered = changed_diff.lower()
    if any(pattern in lowered for pattern in SENSITIVE_PATTERNS):
        score += 20

    severity_weight = {"critical": 30, "high": 20, "medium": 10, "low": 4}
    for issue in issues:
        score += severity_weight.get(issue.severity.lower(), 6)

    score = max(0, min(score, 100))
    if score >= 70:
        return score, "High", "Block deployment until high-risk findings and missing tests are addressed."
    if score >= 40:
        return score, "Medium", "Deploy only after reviewer approval and targeted testing."
    return score, "Low", "Safe to deploy after normal review."
