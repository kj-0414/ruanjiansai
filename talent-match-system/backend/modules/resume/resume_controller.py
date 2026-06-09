from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from modules.resume.resume_service import ResumeService
from modules.resume.schemas import ResumeUpdate
from modules.resume.exceptions import (
    InvalidFileTypeException,
    FileSizeExceededException,
    ResumeNotFoundException,
    AccessDeniedException
)
from utils.auth import get_current_user, require_role
from models import get_db
from sqlalchemy.orm import Session

router = APIRouter()
resume_service = ResumeService()


@router.post("/upload")
async def upload_resume(
    resume_name: str = Form(...),
    file: UploadFile = File(None),
    name: str = Form("未知"),
    age: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    desired_position: str = Form(""),
    address: str = Form(""),
    education: str = Form(""),
    school: str = Form(""),
    major: str = Form(""),
    degree: str = Form("不限"),
    graduation_date: str = Form(""),
    experience: str = Form("未知"),
    skills: str = Form("[]"),
    self_evaluation: str = Form(""),
    certificates: str = Form("[]"),
    projects: str = Form("[]"),
    work_experience: str = Form("[]"),
    internship_experience: str = Form("[]"),
    skills_detail: str = Form("[]"),
    experiences: str = Form("[]"),
    honors: str = Form("[]"),
    desired_salary: str = Form(""),
    work_years: int = Form(0),
    current_user: dict = Depends(require_role("job_seeker")),
    db: Session = Depends(get_db)
):
    try:
        return await resume_service.upload_resume(
            file=file,
            current_user=current_user,
            db=db,
            resume_name=resume_name,
            name=name,
            age=age,
            phone=phone,
            email=email,
            desired_position=desired_position,
            address=address,
            education=education,
            school=school,
            major=major,
            degree=degree,
            experience=experience,
            skills=skills,
            self_evaluation=self_evaluation,
            certificates=certificates,
            projects=projects,
            work_experience=work_experience,
            internship_experience=internship_experience,
            skills_detail=skills_detail,
            desired_salary=desired_salary,
            work_years=work_years
        )
    except InvalidFileTypeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="简历文件格式不正确，请上传 PDF、DOCX 或图片文件"
        )
    except FileSizeExceededException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="简历文件过大，请上传小于10MB的文件"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"简历上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="简历上传失败，请稍后重试"
        )


@router.get("")
async def get_resumes(db: Session = Depends(get_db)):
    return resume_service.get_resumes(db)


@router.get("/all")
async def get_all_resumes(
    current_user: dict = Depends(require_role("company")),
    db: Session = Depends(get_db)
):
    try:
        return resume_service.get_all_resumes_for_company(db)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取简历列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取简历列表失败，请稍后重试"
        )


@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return resume_service.get_resume_detail(resume_id, db)
    except ResumeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在或已被删除"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取简历详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取简历详情失败，请稍后重试"
        )


@router.post("/extract-resume")
async def extract_resume_info_endpoint(files: list[UploadFile] = File(...)):
    try:
        return await resume_service.extract_resume_info_endpoint(files)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"简历解析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="简历解析失败，请检查文件格式是否正确"
        )


@router.put("/{resume_id}")
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    current_user: dict = Depends(require_role("job_seeker")),
    db: Session = Depends(get_db)
):
    try:
        return resume_service.update_resume(resume_id, resume_data, current_user, db)
    except ResumeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在或已被删除"
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限修改此简历"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"更新简历失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="简历更新失败，请稍后重试"
        )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: dict = Depends(require_role("job_seeker")),
    db: Session = Depends(get_db)
):
    try:
        return resume_service.delete_resume(resume_id, current_user, db)
    except ResumeNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在或已被删除"
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此简历"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"删除简历失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="简历删除失败，请稍后重试"
        )