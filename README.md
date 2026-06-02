# AI Release Guardian

AI Release Guardian is an AI-native release quality gate for GitHub pull requests. It fetches a PR diff, analyzes release risk, flags bugs/security concerns, suggests missing tests, generates release notes, and can post the report back to GitHub.

## Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, OpenAI API, GitHub REST API
- Storage: SQLite by default, Supabase/PostgreSQL-ready

## Project Structure

```text
ai-release-guardian/
  backend/
    app/
      main.py
      config.py
      models.py
      storage.py
      services/
        ai_service.py
        github_service.py
        risk_service.py
    requirements.txt
    .env.example
  frontend/
    app/
      page.tsx
      reports/[id]/page.tsx
      globals.css
      layout.tsx
    components/
      AnalysisForm.tsx
      ReportView.tsx
      SeverityBadge.tsx
    lib/
      api.ts
      types.ts
    package.json
    tailwind.config.ts
    postcss.config.js
    tsconfig.json
    next.config.mjs
    .env.example
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill `backend/.env`:

```env
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_token
DATABASE_URL=sqlite:///./guardian.db
ALLOWED_ORIGINS=http://localhost:3000
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open:

```text
http://localhost:3000
```

## Demo Flow

1. Open a GitHub pull request.
2. Copy the PR URL.
3. Paste it into AI Release Guardian.
4. Click `Analyze PR`.
5. Review the generated risk score, issues, tests, release notes, and rollback plan.
6. Click `Post GitHub Comment` to publish the report on the PR.
7. Open `http://localhost:8000/quality-gate/{report_id}` to show pass/warn/fail CI/CD behavior.

## GitHub Token Permissions

For private repositories, create a fine-grained GitHub token with:

- Repository contents: read
- Pull requests: read/write
- Issues: read/write
- Metadata: read

For public repositories, read-only access works for analysis. Comment posting requires write permission.

## MVP Features

- GitHub PR URL parsing
- PR metadata and diff fetch
- AI review with structured JSON output
- Risk score and deployment recommendation
- Missing test suggestions
- Release notes and rollback plan
- Report history
- GitHub PR comment posting
- CI/CD quality gate endpoint

## API Endpoints

```text
GET  /health
POST /analyze-pr
GET  /reports
GET  /reports/{report_id}
GET  /quality-gate/{report_id}
POST /comments
```
