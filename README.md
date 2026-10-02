# CodeGuard AI

## Write Better Code. Find Bugs Before They Find You.

CodeGuard AI is a full-stack code analysis platform for developers. It combines static analysis, bug detection, security scanning, complexity analysis, quality scoring, and AI-assisted review in a single developer-focused workflow.

## Goals

- Detect common code issues before they reach production.
- Provide deterministic static-analysis signals with AI explanation layered on top.
- Support Python, JavaScript, TypeScript, Java, C, and C++.
- Give a polished dashboard with history, scoring, and downloadable reports.
- Keep the architecture modular so more languages and integrations can be added later.

## Architecture

This project follows a modular full-stack monorepo layout:

- Frontend: Next.js + TypeScript + Tailwind CSS + Monaco Editor
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Alembic
- AI layer: provider abstraction with retry/validation support
- Analysis pipeline: language detection, static analysis, security scan, complexity, scoring, and AI review

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system design.

## Folder Structure

```text
codeguard/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── analyzers/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── main.py
│   │   └── __init__.py
│   ├── migrations/
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   └── .env.example
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── DATABASE_SCHEMA.md
│   └── PHASE_1.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API_SPEC.md](docs/API_SPEC.md)
- [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- [docs/PHASE_1.md](docs/PHASE_1.md)

## Quick Start With Docker

Install and start Docker Desktop, then from the repository root run:

```bash
docker compose up --build
```

Open the frontend at <http://localhost:3001> and the API docs at <http://localhost:8000/docs>. Compose starts PostgreSQL, the FastAPI backend, and the Next.js frontend. The host port is 3001 to avoid conflicting with an existing local development server. Source files are mounted for local development, so edits are picked up by the dev servers.

The Compose file supplies local-only defaults. For local overrides, create a root `.env` file using [.env.example](.env.example). Change the development database password and JWT secret before exposing services beyond your machine.

Stop the services with `Ctrl+C`, or run:

```bash
docker compose down
```

To also remove the local PostgreSQL data volume, run `docker compose down --volumes`.

## Deploy Publicly on Render

The repository includes a [Render Blueprint](render.yaml) for the production frontend, API, and PostgreSQL database.

1. Push this repository to GitHub.
2. In the Render Dashboard, choose **New > Blueprint** and connect this repository.
3. Review the three services in `render.yaml` and confirm creation. Render generates the JWT secret and runs database migrations when the API starts.
4. When deployment finishes, open the `codeguard-web` service URL. The API is available from that service at `/api` and its interactive documentation at the `codeguard-api` service URL plus `/docs`.

The Blueprint selects Render's free plans for a demo deployment. Free services may sleep, and free database availability or retention can change; choose an appropriate paid plan for a site that needs reliable uptime and persistent production data. Do not commit `.env` files or real credentials.

## Run Services Without Docker

Docker is optional. For a manual setup, install Python, Node.js, and PostgreSQL, then configure the environment files.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Phase 1 Delivered

This repository includes the structure and implementation needed for the first phase:

- Monorepo architecture
- Full-stack project skeleton
- PostgreSQL + SQLAlchemy model design
- API contract definitions
- Authentication route stubs
- Project and analysis route scaffolds
- Frontend pages and editor shell
- Docker configuration for backend/frontend/postgres
- Test scaffolding

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Monaco Editor
- Recharts
- Lucide React

### Backend
- FastAPI
- Pydantic v2
- SQLAlchemy
- PostgreSQL
- Alembic
- PyJWT
- Passlib

### Analysis
- Python AST
- Ruff/Pylint/Bandit patterns
- Rule-based bug detection
- Security heuristic engine
- Complexity analyzers

## Security Note

This project intentionally avoids arbitrary code execution on the host machine. Uploaded user code is treated as untrusted input and should be isolated behind a sandbox or containerized executor when advanced execution features are enabled.

## License

This project is intended for educational and portfolio use unless otherwise specified.
