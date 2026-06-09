from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from modules.job.job_service import JobService
from modules.job.schemas import JobCreate, JobUpdate, JobAbilityCreate
from modules.job.exceptions import JobNotFoundException, AccessDeniedException
from utils.auth import get_current_user, require_role
from models import get_db
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
job_service = JobService()


@router.post("")
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(require_role("company")),
    db: Session = Depends(get_db)
):
    try:
        return job_service.create_job(job_data, current_user, db)
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        return {"error": "Internal Server Error", "detail": str(e)}


@router.get("")
async def get_jobs(
    current_user: dict = Depends(get_current_user),
    x_role: str = None,
    db: Session = Depends(get_db)
):
    role = current_user.get("role", "").lower() if current_user else ""
    if not role and x_role:
        role = x_role.lower()
    return job_service.get_jobs(current_user, role, db)


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return job_service.get_job_detail(job_id, db)
    except JobNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{job_id}")
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: dict = Depends(require_role("company")),
    db: Session = Depends(get_db)
):
    try:
        return job_service.update_job(job_id, job_data, current_user, db)
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


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: dict = Depends(require_role("company")),
    db: Session = Depends(get_db)
):
    try:
        return job_service.delete_job(job_id, current_user, db)
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


@router.post("/upload")
async def upload_job_requirement(
    job_name: str = Form(...),
    company_name: str = Form(None),
    company_size: str = Form(None),
    company_industry: str = Form(None),
    company_intro: str = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role("company")),
    db: Session = Depends(get_db)
):
    try:
        return await job_service.upload_job_requirement(
            file=file,
            job_name=job_name,
            current_user=current_user,
            db=db,
            company_name=company_name,
            company_size=company_size,
            company_industry=company_industry,
            company_intro=company_intro
        )
    except Exception as e:
        logger.error(f"Error uploading job requirement: {str(e)}")
        return {"error": "Internal Server Error", "detail": str(e)}


@router.post("/extract-job")
async def extract_job_info(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(require_role("company"))
):
    try:
        return await job_service.extract_job_info(files, current_user)
    except Exception as e:
        logger.error(f"Error extracting job info: {str(e)}")
        return {"error": "Internal Server Error", "detail": str(e)}


@router.post("/ability/create")
async def create_job_ability_map(
    request_data: JobAbilityCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return job_service.create_job_ability_map(request_data, db)
    except JobNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建岗位能力图谱失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建岗位能力图谱失败: {str(e)}"
        )


@router.get("/ability/tree/{job_id}")
async def get_job_ability_tree(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return job_service.get_job_ability_tree(job_id, db)
    except JobNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取岗位能力树失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取岗位能力树失败: {str(e)}"
        )


@router.put("/ability/update/{node_id}")
async def update_job_ability_node(
    node_id: str,
    node_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return job_service.update_job_ability_node(node_id, node_data)
    except Exception as e:
        logger.error(f"更新岗位能力节点失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新岗位能力节点失败: {str(e)}"
        )


@router.delete("/ability/delete/{job_id}")
async def delete_job_ability_map(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return job_service.delete_job_ability_map(job_id)
    except Exception as e:
        logger.error(f"删除岗位能力图谱失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除岗位能力图谱失败: {str(e)}"
        )
