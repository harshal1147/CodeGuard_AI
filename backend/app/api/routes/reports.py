from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user

router = APIRouter()


@router.get("/{analysis_id}", response_model=dict)
def get_report(analysis_id: str, current_user=Depends(get_current_user)) -> dict:
    if not analysis_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Analysis id is required.")

    return {
        "success": True,
        "data": {
            "analysis_id": analysis_id,
            "title": "CodeGuard AI Report",
            "project_name": "Demo Project",
            "language": "python",
            "score": 84,
            "issues": [],
            "summary": "Generated report scaffold.",
        },
    }
