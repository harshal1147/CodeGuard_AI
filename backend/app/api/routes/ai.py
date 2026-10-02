from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user

router = APIRouter()


@router.post("/review", response_model=dict)
def review_code(payload: dict, current_user=Depends(get_current_user)) -> dict:
    if not payload.get("code"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code content for review.")

    return {
        "success": True,
        "data": {
            "summary": "Review request accepted for the next AI service integration.",
            "issues": [],
            "explanation": "This endpoint is scaffolded for the provider abstraction and validation layer.",
            "improvements": ["Improve naming and readability."],
            "optimized_code": payload.get("code", ""),
            "complexity_explanation": "Estimated complexity is deferred to the analyzer pipeline.",
            "security_summary": "No active security issues detected by the scaffold configuration.",
        },
    }


@router.post("/fix", response_model=dict)
def fix_code(payload: dict, current_user=Depends(get_current_user)) -> dict:
    if not payload.get("code"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing source code for fix generation.")

    return {
        "success": True,
        "data": {
            "fixed_code": payload.get("code", ""),
            "diff": [],
            "message": "AI fix endpoint is ready for provider integration.",
        },
    }
