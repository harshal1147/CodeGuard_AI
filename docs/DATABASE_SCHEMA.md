# Database Schema

## Core Tables

### users

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| name | VARCHAR | NOT NULL |
| email | VARCHAR | UNIQUE, NOT NULL |
| password_hash | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

### projects

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| user_id | UUID | FK -> users.id, NOT NULL |
| name | VARCHAR | NOT NULL |
| description | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL |

### files

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| project_id | UUID | FK -> projects.id, NOT NULL |
| name | VARCHAR | NOT NULL |
| language | VARCHAR | NOT NULL |
| content | TEXT | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

### analyses

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| project_id | UUID | FK -> projects.id, NOT NULL |
| file_id | UUID | FK -> files.id, nullable |
| language | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| score | INTEGER | nullable |
| findings_count | INTEGER | default 0 |
| created_at | TIMESTAMP | NOT NULL |

### issues

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| analysis_id | UUID | FK -> analyses.id, NOT NULL |
| type | VARCHAR | NOT NULL |
| severity | VARCHAR | NOT NULL |
| title | VARCHAR | NOT NULL |
| message | TEXT | NOT NULL |
| line | INTEGER | nullable |
| file | VARCHAR | nullable |
| recommendation | TEXT | nullable |
| confidence | VARCHAR | default 'MEDIUM' |
| created_at | TIMESTAMP | NOT NULL |

### ai_reviews

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| analysis_id | UUID | FK -> analyses.id, NOT NULL |
| summary | TEXT | NOT NULL |
| issues | JSON | nullable |
| explanation | TEXT | nullable |
| improvements | JSON | nullable |
| optimized_code | TEXT | nullable |
| complexity_explanation | TEXT | nullable |
| security_summary | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL |

### reports

| Column | Type | Constraints |
| --- | --- | --- |
| id | UUID | PK |
| analysis_id | UUID | FK -> analyses.id, NOT NULL |
| title | VARCHAR | NOT NULL |
| payload | JSON | NOT NULL |
| generated_at | TIMESTAMP | NOT NULL |

## Indexes

Add indexes for:

- user_id on projects
- project_id on files and analyses
- created_at on analyses, issues, reports
- severity on issues

## Relationship View

```text
users
  └── projects
        └── files
        └── analyses
             ├── issues
             ├── ai_reviews
             └── reports
```

## Notes

- Use UUIDs for distributed-safe identifiers.
- Keep issue payloads structured for dashboards and charts.
- Ensure secrets are never stored in plain text.
