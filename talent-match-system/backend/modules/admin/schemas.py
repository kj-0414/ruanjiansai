from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AdminUserResponse(BaseModel):
    id: str = Field(..., description="用户ID")
    phone: str = Field(..., description="手机号")
    nickname: str = Field(..., description="昵称")
    roles: List[str] = Field(..., description="角色列表")
    created_at: datetime = Field(..., description="创建时间")

class UserListResponse(BaseModel):
    total: int = Field(..., description="总用户数")
    users: List[AdminUserResponse] = Field(..., description="用户列表")

class SystemStatsResponse(BaseModel):
    total_users: int = Field(..., description="总用户数")
    total_resumes: int = Field(..., description="总简历数")
    total_jobs: int = Field(..., description="总岗位数")
    total_matches: int = Field(..., description="总匹配数")
    job_seeker_count: int = Field(..., description="求职者数量")
    company_count: int = Field(..., description="企业数量")

class RoleUpdateRequest(BaseModel):
    roles: List[str] = Field(..., description="新的角色列表")

class UserSearchRequest(BaseModel):
    phone: Optional[str] = Field(None, description="手机号模糊搜索")
    role: Optional[str] = Field(None, description="角色筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    start_date: Optional[datetime] = Field(None, description="注册起始日期")
    end_date: Optional[datetime] = Field(None, description="注册结束日期")

class UserDetailResponse(BaseModel):
    id: str = Field(..., description="用户ID")
    phone: str = Field(..., description="手机号")
    nickname: str = Field(..., description="昵称")
    roles: List[str] = Field(..., description="角色列表")
    created_at: datetime = Field(..., description="创建时间")
    resume_count: int = Field(0, description="简历数量")
    job_count: int = Field(0, description="发布岗位数量")
    match_count: int = Field(0, description="匹配次数")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")

class DashboardSummary(BaseModel):
    total_users: int = Field(..., description="总用户数")
    total_resumes: int = Field(..., description="总简历数")
    total_jobs: int = Field(..., description="总岗位数")
    total_matches: int = Field(..., description="总匹配数")
    job_seeker_count: int = Field(..., description="求职者数量")
    company_count: int = Field(..., description="企业数量")
    today_new_users: int = Field(0, description="今日新增用户")
    today_new_resumes: int = Field(0, description="今日新增简历")
    today_new_jobs: int = Field(0, description="今日新增岗位")
    today_matches: int = Field(0, description="今日匹配次数")

class UserTrendItem(BaseModel):
    date: str = Field(..., description="日期")
    count: int = Field(..., description="数量")

class UserTrendResponse(BaseModel):
    user_trend: List[UserTrendItem] = Field(..., description="用户趋势")
    resume_trend: List[UserTrendItem] = Field(..., description="简历趋势")
    job_trend: List[UserTrendItem] = Field(..., description="岗位趋势")

class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="系统状态")
    database: str = Field(..., description="数据库状态")
    api_version: str = Field(..., description="API版本")
    uptime: str = Field(..., description="运行时间")
    database_tables: dict = Field(..., description="数据表统计")

class AdminProfileResponse(BaseModel):
    user_id: str = Field(..., description="管理员ID")
    phone: str = Field(..., description="手机号")
    roles: List[str] = Field(..., description="角色列表")
    permissions: List[str] = Field(..., description="权限列表")
