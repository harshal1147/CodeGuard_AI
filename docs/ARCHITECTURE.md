# CodeGuard AI Architecture

## 1. System Overview

CodeGuard AI is a developer-focused static analysis platform that accepts source code, performs static and security checks, calculates quality metrics, stores results, and returns a human-readable report with optional AI explanations and suggested fixes.

It uses a layered architecture:

- Presentation layer: Next.js frontend with responsive IDE-inspired UI
- API layer: FastAPI REST endpoints with validation and auth
- Domain layer: analyzers, security rules, complexity logic, scoring, AI service
- Persistence layer: PostgreSQL with SQLAlchemy models and Alembic migrations
- Infrastructure layer: Docker, environment config, optional sandbox execution

## 2. Core Principles

- Deterministic analysis first
- AI only for explanation and improvement suggestions
- Never execute untrusted code directly on the host
- Structured and typed data, not ad hoc dictionaries only
- Modular analyzers for each language
- Clear separation of concerns between routing, services, and persistence

## 3. Layered Design

### Presentation Layer

Responsibilities:

- Login and registration flow
- Project pages and dashboard
- Monaco Editor with language selection
- Results UI and history viewer
- Diff view for original vs improved code

### Application Layer

Responsibilities:

- API route orchestration
- Request validation
- Authentication checks
- Analysis orchestration pipeline
- Background-task readiness

### Domain Layer

Responsibilities:

- Language detection
- Static analysis rules
- Bug detection heuristics
- Security scanning
- Complexity estimation
- Quality scoring
- AI prompt orchestration

### Persistence Layer

Responsibilities:

- Users, projects, files, analyses, issues, reviews, reports
- History and report retrieval
- Query sorting and filtering

## 4. Analyzer Design

The analyzer system is intentionally extensible.

```text
Analyzer
├── PythonAnalyzer
├── JavaScriptAnalyzer
├── TypeScriptAnalyzer
├── JavaAnalyzer
├── CppAnalyzer
├── CAnalyzer
└── SecurityAnalyzer
```

Each analyzer exposes a common contract:

- detect_language(code, filename)
- analyze(code, metadata)
- collect_issues()
- produce_metrics()

This keeps analysis logic independent from route handlers and the database layer.

## 5. Analysis Pipeline

```text
User upload or paste
       ↓
Language detection
       ↓
Create analysis record
       ↓
Run static analyzer
       ↓
Run bug detection
       ↓
Run security scan
       ↓
Run complexity analysis
       ↓
Calculate quality score
       ↓
Run AI review (validated schema)
       ↓
Store results
       ↓
Return analysis report
```

## 6. AI Integration Pattern

The AI layer is abstracted as a provider interface, allowing future swapping between providers without rewriting application logic.

```text
backend/app/ai/
├── provider.py
├── openai_provider.py
├── service.py
├── prompts.py
└── schema.py
```

Provider contract:

- generate_review(payload)
- generate_fix(payload)
- validate_response(response)

The AI receives only relevant context, not arbitrary project data.

## 7. Database Design

Core entities:

- User
- Project
- File
- Analysis
- Issue
- AIReview
- Report

Relationships:

```text
User
  └── Projects
        └── Files
                └── Analyses
                        ├── Issues
                        ├── AIReview
                        └── Reports
```

This structure supports project grouping, analysis history, issue tracking, and report generation.

## 8. Security Model

Security is handled explicitly due to code ingestion.

- Uploaded files are validated for extension and size.
- Code is never executed on the host.
- Optional execution uses isolated Docker/sandbox containers with:
  - CPU limits
  - Memory limits
  - Timeout
  - Network disabled
  - Non-root user
  - Temporary filesystem
  - Cleanup after execution
- Secrets are masked before displaying or storing in logs.

## 9. Frontend Design

The frontend uses a dark-first developer UI with a polished IDE aesthetic, not copied from any vendor UI. It includes:

- landing page
- auth pages
- project dashboard
- code editor + analysis workflow
- results panels and metrics cards
- history and report pages
- mobile-responsive cards and compact layouts

## 10. Future Expansion

This architecture supports later integration for:

- GitHub PR review
- GitLab scanners
- CI/CD checks
- team workspaces
- organization accounts
- dependency vulnerability scanning
- custom lint rules and coding standards

## 11. Phase 1 Scope

This repository begins with the foundational implementation of the architecture:

- project scaffolding
- backend app skeleton
- SQLAlchemy base models
- API route stubs
- auth flow structure
- frontend shell and pages
- Docker setup
- initial documentation

The next phases will expand the real analyzers and reporting logic.
