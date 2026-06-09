"""
自定义异常类
"""

class TalentMatchException(Exception):
    """基础异常类"""
    pass

class AgentException(TalentMatchException):
    """Agent相关异常"""
    pass

class ParseException(AgentException):
    """解析异常"""
    pass

class LLMException(AgentException):
    """LLM调用异常"""
    pass

class KnowledgeBaseException(TalentMatchException):
    """知识库异常"""
    pass

class ConfigurationException(TalentMatchException):
    """配置异常"""
    pass

class ValidationException(TalentMatchException):
    """验证异常"""
    pass
