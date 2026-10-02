from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    project = Project(user_id=user.id, name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "data": ProjectResponse(id=project.id, name=project.name, description=project.description).model_dump(),
    }


@router.get("", response_model=dict)
def list_projects(db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    projects = db.query(Project).filter(Project.user_id == user.id).all()
    data = [ProjectResponse(id=item.id, name=item.name, description=item.description).model_dump() for item in projects]
    return {"success": True, "data": data}


@router.get("/{project_id}", response_model=dict)
def get_project(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    return {
        "success": True,
        "data": ProjectResponse(id=project.id, name=project.name, description=project.description).model_dump(),
    }


@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()
    return {"success": True, "message": "Project deleted successfully."}
