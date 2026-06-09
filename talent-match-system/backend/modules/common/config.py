"""
配置管理模块
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    api_host: str = Field(default="0.0.0.0", description="API监听地址")
    api_port: int = Field(default=8000, description="API监听端口")
    debug: bool = Field(default=True, description="调试模式")
    app_name: str = Field(default="Talent Match System", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    
    # 通义千问配置
    qwen_api_key: Optional[str] = Field(default=None, description="通义千问API Key")
    qwen_model: str = Field(default="qwen-turbo", description="模型名称")
    qwen_api_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation", description="API地址")
    qwen_timeout: int = Field(default=60, description="API超时时间(秒)")
    qwen_max_retries: int = Field(default=3, description="最大重试次数")
    qwen_retry_delay: float = Field(default=1.0, description="重试延迟(秒)")
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./talent_match.db", description="数据库连接字符串")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # 知识库配置
    kb_data_path: str = Field(default="./data", description="知识库数据路径")
    
    # 文件上传配置
    upload_dir: str = Field(default="./uploads", description="文件上传目录")
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小(字节)")
    
    # 兼容性别名
    @property
    def MAX_UPLOAD_SIZE(self):
        return self.max_upload_size
    
    # JWT 配置
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    
    # 兼容性别名
    @property
    def UPLOAD_DIR(self):
        return self.upload_dir
    
    # 兼容性别名
    @property
    def SECRET_KEY(self):
        return self.secret_key
    
    @property
    def ALGORITHM(self):
        return self.algorithm
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self):
        return self.access_token_expire_minutes
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
    
    @field_validator('qwen_api_key')
    @classmethod
    def check_api_key(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            # 尝试从环境变量获取
            return os.environ.get('DASHSCOPE_API_KEY')
        return v


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = None
    return get_settings()


# 导出全局配置实例
settings = get_settings()
