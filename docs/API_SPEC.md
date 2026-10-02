# CodeGuard AI API Specification

## Authentication Endpoints

### POST /api/auth/register

Creates a new user account.

Request body:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "StrongPassword123!"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Jane Doe",
      "email": "jane@example.com"
    },
    "token": "jwt-token"
  }
}
```

### POST /api/auth/login

Logs in an existing user.

### GET /api/auth/me

Returns the authenticated user session.

## Projects

### POST /api/projects

Creates a project.

Request:

```json
{
  "name": "College E-Commerce App",
  "description": "Demo project"
}
```

### GET /api/projects

Returns all projects for the current user.

### GET /api/projects/{id}

Returns a project with files and analyses.

### DELETE /api/projects/{id}

Deletes a project and its related records.

## Analysis

### POST /api/analysis

Creates an analysis job or immediate analysis result.

Request:

```json
{
  "project_id": "uuid",
  "language": "python",
  "filename": "main.py",
  "code": "print('hello')",
  "source": "paste"
}
```

### GET /api/analysis/{id}

Returns a single analysis report.

### GET /api/analysis/history

Returns the authenticated user's analysis history.

### DELETE /api/analysis/{id}

Deletes an analysis history entry.

## AI Endpoints

### POST /api/ai/review

Sends static findings to the AI for explanation.

### POST /api/ai/fix

Sends a selected issue and code context for a potential fix.

## Report Endpoints

### GET /api/reports/{analysis_id}

Returns a downloadable or previewable report package.

## Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Unable to analyze the provided code."
  }
}
```

## Status Codes

- 200: Success
- 201: Created
- 400: Validation error
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 409: Conflict
- 422: Request validation issue
- 429: Rate limit hit
- 500: Internal server error
