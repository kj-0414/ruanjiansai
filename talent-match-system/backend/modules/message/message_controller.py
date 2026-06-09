from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import get_db
from modules.message.message_service import MessageService
from modules.message.schemas import (
    MessageCreate, SystemMessageTemplateCreate, SystemMessageTemplateUpdate,
    SystemMessageCreate, SendSystemMessageToMultipleRequest, UnreadCountResponse
)
from utils.auth import get_current_user, RoleChecker
from typing import Dict, List
import asyncio

router = APIRouter()
message_service = MessageService()

active_connections: Dict[str, WebSocket] = {}
connections_lock = asyncio.Lock()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    async with connections_lock:
        active_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(data, user_id)
    except WebSocketDisconnect:
        async with connections_lock:
            if user_id in active_connections:
                del active_connections[user_id]
    except Exception as e:
        async with connections_lock:
            if user_id in active_connections:
                del active_connections[user_id]

async def handle_websocket_message(data: dict, user_id: str):
    message_type = data.get("type")
    
    if message_type == "send_message":
        conversation_id = data.get("conversation_id")
        receiver_id = data.get("receiver_id")
        content = data.get("content")
        
        db = next(get_db())
        result = message_service.send_message(db, conversation_id, user_id, receiver_id, content)
        
        if not result["success"]:
            async with connections_lock:
                if user_id in active_connections:
                    await active_connections[user_id].send_json({
                        "type": "error",
                        "message": result["message"]
                    })
            return
        
        async with connections_lock:
            if receiver_id in active_connections:
                await active_connections[receiver_id].send_json({
                    "type": "new_message",
                    "data": {
                        "id": result.get("message_id"),
                        "conversation_id": conversation_id,
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "content": content,
                        "is_read": 0,
                        "created_at": result.get("created_at", "")
                    }
                })
            
            if user_id in active_connections:
                await active_connections[user_id].send_json({
                    "type": "message_sent",
                    "data": {
                        "id": result.get("message_id"),
                        "conversation_id": conversation_id,
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "content": content,
                        "is_read": 0,
                        "created_at": result.get("created_at", "")
                    }
                })
    
    elif message_type == "mark_read":
        conversation_id = data.get("conversation_id")
        
        db = next(get_db())
        message_service.mark_messages_as_read(db, conversation_id, user_id)
        
        async with connections_lock:
            if user_id in active_connections:
                await active_connections[user_id].send_json({
                    "type": "marked_read",
                    "conversation_id": conversation_id
                })

async def send_system_notification(user_id: str, message_data: dict):
    async with connections_lock:
        if user_id in active_connections:
            await active_connections[user_id].send_json({
                "type": "system_message",
                "data": message_data
            })

@router.post("/conversations")
async def create_conversation(
    job_seeker_id: str,
    company_id: str,
    job_id: int,
    resume_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    conversation = message_service.create_conversation(db, job_seeker_id, company_id, job_id, resume_id)
    
    welcome_message = f"您好！我已投递了职位申请，期待与您沟通。"
    message_service.send_message(db, conversation.id, job_seeker_id, company_id, welcome_message)
    
    return {"message": "会话创建成功", "conversation_id": conversation.id}

@router.get("/conversations")
async def get_user_conversations(
    user_role: str,
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    print(f"[DEBUG] get_user_conversations - user_id: {current_user['user_id']}, role: {user_role}")
    result = message_service.get_user_conversations(db, current_user["user_id"], user_role, page, page_size, status)
    print(f"[DEBUG] get_user_conversations - result: {len(result.get('data', []))} conversations")
    return result

@router.get("/conversations/pending")
async def get_pending_conversations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.get_pending_conversations(db, current_user["user_id"])
    return result

@router.get("/conversations/pending/job-seeker")
async def get_pending_conversations_for_job_seeker(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.get_pending_conversations_for_job_seeker(db, current_user["user_id"])
    return result

@router.post("/conversations/{conversation_id}/activate")
async def activate_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.activate_conversation(db, conversation_id, current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/conversations/{conversation_id}/activate-by-job-seeker")
async def activate_conversation_by_job_seeker(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.activate_conversation_by_job_seeker(db, conversation_id, current_user["user_id"])
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    conversation = message_service.get_conversation_by_id(db, conversation_id, current_user["user_id"])
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    message_service.mark_messages_as_read(db, conversation_id, current_user["user_id"])
    
    return conversation

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    receiver_id: str,
    content: str,
    user_role: str = "job_seeker",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.send_message(db, conversation_id, current_user["user_id"], receiver_id, content, user_role)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.get_conversation_messages(db, conversation_id, current_user["user_id"], page, page_size)
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    message_service.mark_messages_as_read(db, conversation_id, current_user["user_id"])
    return result

@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    message_service.mark_messages_as_read(db, conversation_id, current_user["user_id"])
    return {"message": "已标记为已读"}

@router.delete("/conversations/{conversation_id}/read")
async def mark_conversation_read_delete(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    message_service.mark_messages_as_read(db, conversation_id, current_user["user_id"])
    return {"message": "已标记为已读"}

@router.put("/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    message_service.close_conversation(db, conversation_id, current_user["user_id"])
    return {"message": "会话已关闭"}

@router.get("/unread-count")
async def get_unread_count(
    user_role: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.get_unread_count(db, current_user["user_id"], user_role)
    return result

@router.post("/system/templates", dependencies=[Depends(RoleChecker(allowed_roles=["admin"]))])
async def create_system_message_template(
    data: SystemMessageTemplateCreate,
    db: Session = Depends(get_db)
):
    template = message_service.create_system_message_template(db, data)
    return {"message": "模板创建成功", "data": template}

@router.get("/system/templates")
async def get_system_message_templates(
    category: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    result = message_service.get_system_message_templates(db, category, page, page_size)
    return result

@router.get("/system/templates/{template_id}")
async def get_system_message_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    template = message_service.get_system_message_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template

@router.put("/system/templates/{template_id}", dependencies=[Depends(RoleChecker(allowed_roles=["admin"]))])
async def update_system_message_template(
    template_id: int,
    data: SystemMessageTemplateUpdate,
    db: Session = Depends(get_db)
):
    template = message_service.update_system_message_template(db, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "模板更新成功", "data": template}

@router.delete("/system/templates/{template_id}", dependencies=[Depends(RoleChecker(allowed_roles=["admin"]))])
async def delete_system_message_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    success = message_service.delete_system_message_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "模板删除成功"}

@router.post("/system/messages")
async def send_system_message(
    data: SystemMessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    system_message = message_service.send_system_message(db, data)
    
    await send_system_notification(data.user_id, {
        "id": system_message.id,
        "user_id": system_message.user_id,
        "content": system_message.content,
        "category": system_message.category,
        "created_at": system_message.created_at.isoformat()
    })
    
    return {"message": "系统消息发送成功", "data": system_message}

@router.post("/system/messages/batch", dependencies=[Depends(RoleChecker(allowed_roles=["admin"]))])
async def send_system_message_to_multiple(
    data: SendSystemMessageToMultipleRequest,
    db: Session = Depends(get_db)
):
    messages = message_service.send_system_message_to_multiple_users(
        db, data.user_ids, data.template_id, data.content, data.category, data.variables
    )
    
    for msg in messages:
        await send_system_notification(msg.user_id, {
            "id": msg.id,
            "user_id": msg.user_id,
            "content": msg.content,
            "category": msg.category,
            "created_at": msg.created_at.isoformat()
        })
    
    return {"message": f"系统消息已发送给 {len(messages)} 个用户", "count": len(messages)}

@router.get("/system/messages")
async def get_user_system_messages(
    category: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = message_service.get_user_system_messages(db, current_user["user_id"], category, page, page_size)
    return result

@router.put("/system/messages/{message_id}/read")
async def mark_system_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    message_service.mark_system_message_as_read(db, message_id, current_user["user_id"])
    return {"message": "已标记为已读"}

@router.put("/system/messages/read-all")
async def mark_all_system_messages_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    message_service.mark_all_system_messages_as_read(db, current_user["user_id"])
    return {"message": "所有系统消息已标记为已读"}