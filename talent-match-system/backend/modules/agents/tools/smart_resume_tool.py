"""
智能简历解析工具
集成SmartResume完整功能，使用项目现有的LLM引擎进行解析
"""

import time
import asyncio
import os
from typing import Dict, Any, Optional
from .base import BaseTool, ToolResult

import PyPDF2
from docx import Document


class SmartResumeParseTool(BaseTool):
    """智能简历解析工具 - 集成SmartResume完整功能"""

    def __init__(self):
        super().__init__(
            name="smart_resume_parse",
            description="使用SmartResume解析简历文件，支持PDF、Word、图片等格式，具备版面检测和OCR能力",
            parameters=[
                {"name": "file_path", "type": "string", "description": "简历文件路径", "required": True},
                {"name": "use_fallback", "type": "boolean", "description": "解析失败时是否降级到自研方案", "required": False}
            ]
        )
        self.smart_resume_parser = None

    async def _init_parser(self):
        """延迟初始化SmartResume解析器"""
        if self.smart_resume_parser is None:
            try:
                from third_party.smartresume import get_parser
                self.smart_resume_parser = get_parser()
                self.logger.info("SmartResume parser initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize SmartResume: {e}")
                self.smart_resume_parser = None

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """从PDF文件提取文本"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            self.logger.error(f"Failed to extract text from PDF: {e}")
        return text

    def _extract_text_from_docx(self, file_path: str) -> str:
        """从Word文档提取文本"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            self.logger.error(f"Failed to extract text from DOCX: {e}")
        return text

    def _extract_text(self, file_path: str) -> str:
        """根据文件类型提取文本"""
        if file_path.lower().endswith('.pdf'):
            return self._extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self._extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
        else:
            self.logger.warning(f"Unsupported file type: {file_path}")
            return ""

    async def execute(self, file_path: str, use_fallback: bool = True) -> ToolResult:
        start_time = time.time()

        try:
            await self._init_parser()

            if self.smart_resume_parser is None:
                if use_fallback:
                    return await self._fallback_parse(file_path)
                return ToolResult(
                    success=False,
                    error="SmartResume解析器未初始化",
                    execution_time=time.time() - start_time
                )

            # 使用SmartResume进行解析
            result = await asyncio.to_thread(
                self.smart_resume_parser.parse,
                file_path
            )

            structured_result = {
                "name": result.get("name", "未提供"),
                "phone": result.get("phone", ""),
                "email": result.get("email", ""),
                "education": result.get("education", "未提供"),
                "experience_years": result.get("experience_years", "未提供"),
                "skills": result.get("skills", []),
                "work_experience": result.get("work_experience", []),
                "education_history": result.get("education_history", []),
                "self_evaluation": result.get("self_evaluation", ""),
                "highlights": result.get("highlights", []),
                "source": "smartresume",
                "confidence": result.get("confidence", 0.93)
            }

            return ToolResult(
                success=True,
                data=structured_result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            self.logger.error(f"SmartResume parse failed: {e}")
            if use_fallback:
                return await self._fallback_parse(file_path)
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    async def _fallback_parse(self, file_path: str) -> ToolResult:
        """降级到自研简历解析方案"""
        self.logger.info("Falling back to native resume parser")
        
        try:
            from utils.resume_parser import parse_resume
            result = parse_resume(file_path)
            
            parsed_data = {
                "name": result.get("name", "未提供"),
                "phone": result.get("phone", ""),
                "email": result.get("email", ""),
                "education": result.get("education", "未提供"),
                "experience_years": result.get("experience", "未提供"),
                "skills": result.get("skills", []),
                "work_experience": [],
                "education_history": [],
                "self_evaluation": "",
                "highlights": [],
                "source": "fallback",
                "confidence": 0.5
            }

            return ToolResult(
                success=True,
                data=parsed_data,
                execution_time=0.0
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Fallback parse failed: {e}",
                execution_time=0.0
            )


smart_resume_parse_tool = SmartResumeParseTool()
