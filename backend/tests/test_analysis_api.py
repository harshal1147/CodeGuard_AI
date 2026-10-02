import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.project import Project
from app.models.user import User


@pytest.fixture
def analysis_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    user = User(name="Test User", email=f"{uuid.uuid4()}@example.com", password_hash=hash_password("Password123!"))
    session.add(user)
    session.flush()
    project = Project(user_id=user.id, name="Analysis Test")
    session.add(project)
    session.commit()
    token = create_access_token(user.id)
    project_id = project.id
    user_id = user.id

    def override_get_db():
        try:
            yield session
        finally:
            pass

    def override_current_user():
        return session.get(User, user_id)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        with TestClient(app) as client:
            yield client, project_id, token, session
    finally:
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_analysis_endpoint_persists_and_returns_python_report(analysis_client):
    client, project_id, token, session = analysis_client
    response = client.post(
        "/api/analysis",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": project_id,
            "language": "python",
            "filename": "main.py",
            "code": "def calculate(items=[]):\n    return eval(items[0])\n",
        },
    )

    assert response.status_code == 201
    report = response.json()["data"]
    assert report["status"] == "completed"
    assert report["result"]["metrics"]["estimated_time_complexity"] == "O(1)"
    assert {issue["type"] for issue in report["result"]["issues"]} >= {
        "mutable_default_argument",
        "dynamic_code_execution",
    }
    assert len(session.query(Project).filter_by(id=project_id).one().analyses) == 1


def test_analysis_endpoint_accepts_typescript(analysis_client):
    client, project_id, token, _session = analysis_client
    response = client.post(
        "/api/analysis",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": project_id,
            "language": "typescript",
            "filename": "sample.ts",
            "code": "const source: string = 'input'; const output = eval(source);",
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["language"] == "typescript"
    assert "dynamic_code_execution" in {issue["type"] for issue in data["result"]["issues"]}


def test_analysis_history_includes_display_fields_and_detail_report(analysis_client):
    client, project_id, token, _session = analysis_client
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/analysis",
        headers=headers,
        json={
            "project_id": project_id,
            "language": "python",
            "filename": "review.py",
            "code": "eval(source)",
        },
    )
    analysis_id = created.json()["data"]["id"]

    history = client.get("/api/analysis/history", headers=headers)
    detail = client.get(f"/api/analysis/{analysis_id}", headers=headers)

    assert history.status_code == 200
    item = history.json()["data"][0]
    assert item["id"] == analysis_id
    assert item["project_name"] == "Analysis Test"
    assert item["filename"] == "review.py"
    assert item["created_at"]
    assert item["severity_counts"]["HIGH"] == 1
    assert detail.status_code == 200
    assert detail.json()["data"]["result"]["filename"] == "review.py"
    assert detail.json()["data"]["created_at"]


@pytest.mark.parametrize(
    ("language", "filename", "code", "expected_language", "expected_issue"),
    [
        ("auto", "Review.java", "class Runner { void run(String input) { Runtime.getRuntime().exec(input); } }", "java", "command_injection_risk"),
        ("c", "sample.c", "int main() { char buffer[8]; gets(buffer); return 0; }", "c", "unsafe_buffer_function"),
        ("cpp", "sample.cpp", 'int main() { system("whoami"); return 0; }', "cpp", "command_injection_risk"),
    ],
)
def test_analysis_endpoint_accepts_java_c_and_cpp(analysis_client, language, filename, code, expected_language, expected_issue):
    client, project_id, token, _session = analysis_client
    response = client.post(
        "/api/analysis",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": project_id,
            "language": language,
            "filename": filename,
            "code": code,
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["language"] == expected_language
    assert expected_issue in {issue["type"] for issue in data["result"]["issues"]}
