from fastapi import APIRouter, Depends, HTTPException, status
from modules.match.match_service import MatchService
from modules.match.schemas import MatchRequest
from modules.match.exceptions import ResumeNotFoundException, JobNotFoundException, MatchNotFoundException
from modules.resume.exceptions import AccessDeniedException
from utils.auth import get_current_user
from models import get_db
from sqlalchemy.orm import Session

router = APIRouter()
match_service = MatchService()


@router.post("")
async def match_resume_job(
    request: MatchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return match_service.match_resume_job(request, db)
    except ResumeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except JobNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/records")
async def get_match_records(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return match_service.get_match_records(db)


@router.get("/recommendations")
async def get_recommendations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    return match_service.get_recommendations(user_id, user_role, db)


@router.get("/{match_id}")
async def get_match_record(
    match_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return match_service.get_match_record(match_id, db)
    except MatchNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/deliver")
async def deliver_resume(
    request: MatchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return match_service.deliver_resume(request.resume_id, request.job_id, current_user["user_id"], db)
    except ResumeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except JobNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )