from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.file import File
from app.models.issue import Issue
from app.models.project import Project
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.analysis_service import analyze_python
from app.services.javascript_analysis import analyze_javascript
from app.services.native_analysis import analyze_native

router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    if len(payload.code.encode("utf-8")) > settings.max_file_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Code exceeds the maximum allowed size.")

    language_aliases = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "c++": "cpp",
    }
    extension_languages = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "java": "java",
        "c": "c",
        "h": "c",
        "cc": "cpp",
        "cpp": "cpp",
        "cxx": "cpp",
        "hh": "cpp",
        "hpp": "cpp",
        "hxx": "cpp",
    }
    language = language_aliases.get(payload.language.strip().lower(), payload.language.strip().lower())
    if language == "auto":
        extension = payload.filename.rsplit(".", maxsplit=1)[-1].lower() if "." in payload.filename else ""
        language = extension_languages.get(extension, "")
    if language not in {"python", "javascript", "typescript", "java", "c", "cpp"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Supported analysis languages are Python, JavaScript, TypeScript, Java, C, and C++.",
        )

    project = db.query(Project).filter(Project.id == payload.project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if language == "python":
        report = analyze_python(payload.code)
    elif language in {"javascript", "typescript"}:
        report = analyze_javascript(payload.code, language)
    else:
        report = analyze_native(payload.code, language)
    issues = report["issues"]
    metrics = report["metrics"]
    severity_counts = dict(Counter(issue["severity"] for issue in issues))
    stored_result = {
        "filename": payload.filename,
        "issues": issues,
        "metrics": metrics,
        "severity_counts": severity_counts,
    }

    source_file = File(
        project_id=project.id,
        name=payload.filename,
        language=language,
        content=payload.code,
    )
    analysis = Analysis(
        project_id=project.id,
        file=source_file,
        language=language,
        status="completed",
        score=metrics["quality_scores"]["overall"],
        findings_count=len(issues),
        result=stored_result,
    )
    db.add(analysis)
    for issue in issues:
        db.add(
            Issue(
                analysis=analysis,
                type=issue["type"],
                severity=issue["severity"],
                title=issue["title"],
                message=issue["message"],
                line=issue["line"],
                file=payload.filename,
                recommendation=issue["recommendation"],
                confidence=issue["confidence"],
            )
        )
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save the analysis report.") from exc
    db.refresh(analysis)

    return {
        "success": True,
        "data": AnalysisResponse(
            id=analysis.id,
            project_id=analysis.project_id,
            language=analysis.language,
            status=analysis.status,
            score=analysis.score,
            findings_count=analysis.findings_count,
            result=analysis.result,
            created_at=analysis.created_at,
        ).model_dump(),
    }


@router.get("/history", response_model=dict)
def get_analysis_history(db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    analyses = (
        db.query(Analysis)
        .join(Project)
        .filter(Project.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    data = []
    for item in analyses:
        result = item.result or {}
        data.append(
            {
                "id": item.id,
                "project_id": item.project_id,
                "project_name": item.project.name,
                "filename": result.get("filename") or (item.file.name if item.file else "Untitled"),
                "language": item.language,
                "status": item.status,
                "score": item.score,
                "findings_count": item.findings_count,
                "created_at": item.created_at,
                "severity_counts": result.get("severity_counts", {}),
            }
        )
    return {"success": True, "data": data}


@router.get("/{analysis_id}", response_model=dict)
def get_analysis(analysis_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    analysis = db.query(Analysis).join(Project).filter(Analysis.id == analysis_id, Project.user_id == user.id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    return {
        "success": True,
        "data": AnalysisResponse(
            id=analysis.id,
            project_id=analysis.project_id,
            language=analysis.language,
            status=analysis.status,
            score=analysis.score,
            findings_count=analysis.findings_count,
            result=analysis.result,
            created_at=analysis.created_at,
        ).model_dump(),
    }


@router.delete("/{analysis_id}", response_model=dict)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    analysis = db.query(Analysis).join(Project).filter(Analysis.id == analysis_id, Project.user_id == user.id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    db.delete(analysis)
    db.commit()
    return {"success": True, "message": "Analysis deleted successfully."}
