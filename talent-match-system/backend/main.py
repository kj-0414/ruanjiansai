from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from modules.auth import auth_router
from modules.resume import resume_router
from modules.job import job_router
from modules.match import match_router
from modules.admin import admin_router
from modules.message.message_controller import router as message_router
from modules.ai.ai_controller import router as ai_router
from modules.agents.agents_controller import router as agents_router
from modules.common import get_settings, setup_logging, get_logger
from models import create_tables

# 初始化配置和日志
settings = get_settings()
setup_logging()
logger = get_logger(__name__)

create_tables()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="人才智能匹配系统API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=JSONResponse
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    logger.warning(f"请求参数验证失败: {str(exc)[:200]}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数格式不正确，请检查输入格式",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器 - 捕获所有未处理的异常"""
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误，请稍后重试"
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/user", tags=["用户"])
app.include_router(resume_router, prefix="/api/resume", tags=["简历"])
app.include_router(job_router, prefix="/api/job", tags=["岗位"])
app.include_router(match_router, prefix="/api/match", tags=["匹配"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理员"])
app.include_router(message_router, prefix="/api/message", tags=["消息"])
app.include_router(ai_router, prefix="/api/ability", tags=["能力分析"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体"])

logger.info("=== Registered Routes ===")
for route in app.routes:
    if hasattr(route, 'path'):
        logger.info(f"  {route.path}")
logger.info("=========================")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Talent Match System API",
        "version": settings.app_version,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )