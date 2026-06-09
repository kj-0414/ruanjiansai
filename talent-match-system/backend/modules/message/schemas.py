from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: str
    receiver_id: str
    content: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: str
    receiver_id: str
    content: str
    is_read: int
    created_at: str
    
    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    job_seeker_id: str
    company_id: str
    job_id: int
    resume_id: int

class ConversationResponse(BaseModel):
    id: int
    job_seeker_id: str
    company_id: str
    job_id: int
    resume_id: int
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class SystemMessageTemplateCreate(BaseModel):
    name: str
    category: str
    template_content: str
    description: Optional[str] = None

class SystemMessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    template_content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None

class SystemMessageTemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    template_content: str
    description: Optional[str]
    is_active: int
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class SystemMessageCreate(BaseModel):
    user_id: str
    template_id: Optional[int] = None
    content: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[Dict[str, str]] = None

class SystemMessageResponse(BaseModel):
    id: int
    user_id: str
    template_id: Optional[int]
    content: str
    category: str
    is_read: int
    created_at: str
    
    class Config:
        orm_mode = True

class SendSystemMessageToMultipleRequest(BaseModel):
    user_ids: List[str]
    template_id: Optional[int] = None
    content: Optional[str] = None
    category: Optional[str] = "system"
    variables: Optional[Dict[str, str]] = None

class MessageQueryRequest(BaseModel):
    conversation_id: Optional[int] = None
    page: int = 1
    page_size: int = 20

class UnreadCountResponse(BaseModel):
    chat: int
    system: int
    total: int