"""
通义千问客户端 - 增强版
- 支持重试机制
- 更好的错误处理
- 使用配置管理
"""

import json
import re
import logging
import time
from typing import Optional, Dict, Any, Callable, Type, Tuple
from functools import wraps
import requests

from modules.common import get_settings, LLMException, ConfigurationException

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (requests.RequestException,),
) -> Callable:
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            if last_exception:
                raise last_exception
            return None
        return wrapper
    return decorator


class QwenClient:
    """通义千问客户端"""
    
    def __init__(self):
        """初始化客户端，从配置读取参数"""
        settings = get_settings()
        
        self.api_key = settings.qwen_api_key
        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY is not set")
        
        self.model = settings.qwen_model
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.timeout = settings.qwen_timeout
        self.max_retries = settings.qwen_max_retries
        self.retry_delay = settings.qwen_retry_delay
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(requests.RequestException,)
    )
    def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起API请求（内部方法）
        
        Args:
            payload: 请求载荷
        
        Returns:
            API响应
        
        Raises:
            LLMException: API调用失败
        """
        if not self.api_key:
            raise ConfigurationException("API key not configured. Please set DASHSCOPE_API_KEY environment variable.")
        
        logger.debug("Sending chat request to Qwen API")
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.debug("Successfully received response from Qwen API")
            return result
        else:
            error_msg = f"API调用失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise LLMException(error_msg)
    
    def chat(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        发送对话请求到Qwen
        
        Args:
            prompt: 用户输入的提示
            system_prompt: 系统提示（可选）
        
        Returns:
            返回AI的响应内容
        """
        # 构建OpenAI格式的请求参数
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            result = self._make_api_request(payload)
            content = result["choices"][0]["message"]["content"]
            return {
                "success": True,
                "content": content,
                "raw_response": result
            }
        except LLMException as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.exception(f"Unexpected error calling Qwen API: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从AI响应中提取JSON内容
        
        Args:
            text: AI响应的文本
        
        Returns:
            解析后的JSON对象，如果解析失败返回None
        """
        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = text
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
            return None


# 全局客户端实例
_qwen_client: Optional[QwenClient] = None


def get_qwen_client() -> QwenClient:
    """获取Qwen客户端单例"""
    global _qwen_client
    if _qwen_client is None:
        _qwen_client = QwenClient()
    return _qwen_client


def reset_qwen_client() -> None:
    """重置客户端（用于测试）"""
    global _qwen_client
    _qwen_client = None
