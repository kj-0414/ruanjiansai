import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func
from models import Conversation, Message, SystemMessageTemplate, SystemMessage, MessageStatus, User, Job, Resume
from modules.message.schemas import (
    MessageCreate, MessageResponse, ConversationResponse,
    SystemMessageTemplateCreate, SystemMessageTemplateUpdate,
    SystemMessageCreate, SystemMessageResponse
)

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self):
        pass
    
    def _validate_user_in_conversation(self, db: Session, conversation_id: int, user_id: str) -> bool:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            or_(
                Conversation.job_seeker_id == user_id,
                Conversation.company_id == user_id
            )
        ).first()
        return conversation is not None
    
    def create_conversation(self, db: Session, job_seeker_id: str, company_id: str, 
                           job_id: int, resume_id: int) -> Conversation:
        try:
            existing_conversation = db.query(Conversation).filter(
                and_(
                    Conversation.job_seeker_id == job_seeker_id,
                    Conversation.company_id == company_id,
                    Conversation.job_id == job_id,
                    Conversation.resume_id == resume_id
                )
            ).first()
            
            if existing_conversation:
                existing_conversation.updated_at = datetime.now()
                db.commit()
                db.refresh(existing_conversation)
                return existing_conversation
            
            conversation = Conversation(
                job_seeker_id=job_seeker_id,
                company_id=company_id,
                job_id=job_id,
                resume_id=resume_id,
                status="pending",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create conversation: {str(e)}")
            raise
    
    def activate_conversation(self, db: Session, conversation_id: int, company_id: str) -> dict:
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.company_id == company_id
            ).first()
            
            if not conversation:
                return {"success": False, "message": "会话不存在"}
            
            if conversation.status == "active":
                return {"success": False, "message": "会话已开启"}
            
            if conversation.status == "closed":
                return {"success": False, "message": "会话已关闭，无法重新开启"}
            
            conversation.status = "active"
            conversation.updated_at = datetime.now()
            db.commit()
            db.refresh(conversation)
            
            return {"success": True, "message": "会话开启成功", "conversation_id": conversation.id}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to activate conversation {conversation_id}: {str(e)}")
            return {"success": False, "message": "操作失败"}
    
    def send_message(self, db: Session, conversation_id: int, sender_id: str, 
                    receiver_id: str, content: str, user_role: str = None) -> dict:
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return {"success": False, "message": "会话不存在"}
            
            if not self._validate_user_in_conversation(db, conversation_id, sender_id):
                return {"success": False, "message": "无权访问此会话"}
            
            if conversation.status != "active":
                if conversation.status == "pending":
                    if user_role == "job_seeker":
                        return {"success": False, "message": "企业尚未开启会话，暂无法发送消息"}
                    return {"success": False, "message": "会话待确认，请先开启会话"}
                elif conversation.status == "closed":
                    return {"success": False, "message": "会话已关闭，无法继续发送消息"}
            
            message = Message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                is_read=0,
                created_at=datetime.now()
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            conversation.updated_at = datetime.now()
            db.commit()
            
            return {
                "success": True, 
                "message": "消息发送成功", 
                "message_id": message.id,
                "created_at": message.created_at.isoformat() if message.created_at else ""
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to send message to conversation {conversation_id}: {str(e)}")
            return {"success": False, "message": "消息发送失败"}
    
    def get_conversation_messages(self, db: Session, conversation_id: int, user_id: str = None,
                                  page: int = 1, page_size: int = 20) -> Dict:
        try:
            if user_id and not self._validate_user_in_conversation(db, conversation_id, user_id):
                return {"data": [], "total": 0, "page": page, "page_size": page_size, "error": "无权访问此会话"}
            
            query = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(desc(Message.created_at))
            
            total = query.count()
            messages = query.offset((page - 1) * page_size).limit(page_size).all()
            
            sender_ids = {msg.sender_id for msg in messages}
            senders = {u.id: u for u in db.query(User).filter(User.id.in_(sender_ids)).all()}
            
            messages_data = []
            for msg in messages:
                sender = senders.get(msg.sender_id)
                messages_data.append({
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "sender_id": msg.sender_id,
                    "sender_phone": sender.phone if sender else None,
                    "sender_nickname": sender.nickname if sender else None,
                    "receiver_id": msg.receiver_id,
                    "content": msg.content,
                    "is_read": msg.is_read,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                })
            
            return {
                "data": messages_data,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            logger.error(f"Failed to get conversation messages {conversation_id}: {str(e)}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}
    
    def mark_messages_as_read(self, db: Session, conversation_id: int, user_id: str):
        try:
            if not self._validate_user_in_conversation(db, conversation_id, user_id):
                logger.warning(f"User {user_id} attempted to mark messages read in unauthorized conversation {conversation_id}")
                return
            
            db.query(Message).filter(
                Message.conversation_id == conversation_id,
                Message.receiver_id == user_id,
                Message.is_read == 0
            ).update({"is_read": 1})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to mark messages as read for conversation {conversation_id}: {str(e)}")
    
    def get_user_conversations(self, db: Session, user_id: str, user_role: str,
                               page: int = 1, page_size: int = 20, status: str = None) -> Dict:
        try:
            if user_role == "job_seeker":
                query = db.query(Conversation).filter(
                    Conversation.job_seeker_id == user_id
                )
            elif user_role == "company":
                query = db.query(Conversation).filter(
                    Conversation.company_id == user_id
                )
            else:
                return {"data": [], "total": 0, "page": page, "page_size": page_size}
            
            if status:
                query = query.filter(Conversation.status == status)
            
            query = query.order_by(desc(Conversation.updated_at))
            total = query.count()
            conversations = query.offset((page - 1) * page_size).limit(page_size).all()
            
            conversation_ids = [conv.id for conv in conversations]
            
            last_messages = {}
            if conversation_ids:
                msg_query = db.query(Message).filter(
                    Message.conversation_id.in_(conversation_ids)
                ).order_by(Message.conversation_id, desc(Message.created_at))
                
                for msg in msg_query.all():
                    if msg.conversation_id not in last_messages:
                        last_messages[msg.conversation_id] = msg
            
            unread_counts = {}
            if conversation_ids:
                unread_query = db.query(
                    Message.conversation_id,
                    Message.receiver_id,
                    func.count(Message.id).label('count')
                ).filter(
                    Message.conversation_id.in_(conversation_ids),
                    Message.receiver_id == user_id,
                    Message.is_read == 0
                ).group_by(Message.conversation_id, Message.receiver_id)
                
                for row in unread_query.all():
                    unread_counts[row.conversation_id] = row.count
            
            other_user_ids = []
            job_ids = []
            resume_ids = []
            for conv in conversations:
                other_user_ids.append(conv.company_id if user_role == "job_seeker" else conv.job_seeker_id)
                job_ids.append(conv.job_id)
                resume_ids.append(conv.resume_id)
            
            other_users = {u.id: u for u in db.query(User).filter(User.id.in_(other_user_ids)).all()}
            jobs = {j.id: j for j in db.query(Job).filter(Job.id.in_(job_ids)).all()}
            resumes = {r.id: r for r in db.query(Resume).filter(Resume.id.in_(resume_ids)).all()}
            
            result = []
            for conv in conversations:
                other_user_id = conv.company_id if user_role == "job_seeker" else conv.job_seeker_id
                other_user = other_users.get(other_user_id)
                last_msg = last_messages.get(conv.id)
                
                result.append({
                    "conversation": {
                        "id": conv.id,
                        "job_seeker_id": conv.job_seeker_id,
                        "company_id": conv.company_id,
                        "job_id": conv.job_id,
                        "resume_id": conv.resume_id,
                        "status": conv.status,
                        "created_at": conv.created_at.isoformat() if conv.created_at else None,
                        "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                    },
                    "last_message": {
                        "id": last_msg.id,
                        "conversation_id": last_msg.conversation_id,
                        "sender_id": last_msg.sender_id,
                        "receiver_id": last_msg.receiver_id,
                        "content": last_msg.content,
                        "is_read": last_msg.is_read,
                        "created_at": last_msg.created_at.isoformat() if last_msg.created_at else None
                    } if last_msg else None,
                    "unread_count": unread_counts.get(conv.id, 0),
                    "other_user": {
                        "id": other_user.id,
                        "phone": other_user.phone,
                        "nickname": other_user.nickname,
                        "roles": other_user.roles
                    } if other_user else None,
                    "job": {
                        "id": jobs[conv.job_id].id,
                        "title": jobs[conv.job_id].job_name
                    } if conv.job_id and jobs.get(conv.job_id) else None,
                    "resume": {
                        "id": resumes[conv.resume_id].id,
                        "name": resumes[conv.resume_id].name
                    } if conv.resume_id and resumes.get(conv.resume_id) else None
                })
            
            return {
                "data": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            logger.error(f"Failed to get user conversations for {user_id}: {str(e)}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}
    
    def get_pending_conversations(self, db: Session, company_id: str) -> Dict:
        try:
            query = db.query(Conversation).filter(
                Conversation.company_id == company_id,
                Conversation.status == "pending"
            ).order_by(desc(Conversation.created_at))
            
            total = query.count()
            conversations = query.all()
            
            job_ids = [conv.job_id for conv in conversations]
            resume_ids = [conv.resume_id for conv in conversations]
            job_seeker_ids = [conv.job_seeker_id for conv in conversations]
            
            jobs = {j.id: j for j in db.query(Job).filter(Job.id.in_(job_ids)).all()}
            resumes = {r.id: r for r in db.query(Resume).filter(Resume.id.in_(resume_ids)).all()}
            job_seekers = {u.id: u for u in db.query(User).filter(User.id.in_(job_seeker_ids)).all()}
            
            result = []
            for conv in conversations:
                result.append({
                    "conversation": conv,
                    "job": jobs.get(conv.job_id),
                    "resume": resumes.get(conv.resume_id),
                    "job_seeker": job_seekers.get(conv.job_seeker_id)
                })
            
            return {"data": result, "total": total}
        except Exception as e:
            logger.error(f"Failed to get pending conversations for company {company_id}: {str(e)}")
            return {"data": [], "total": 0}
    
    def get_pending_conversations_for_job_seeker(self, db: Session, job_seeker_id: str) -> Dict:
        try:
            query = db.query(Conversation).filter(
                Conversation.job_seeker_id == job_seeker_id,
                Conversation.status == "pending"
            ).order_by(desc(Conversation.created_at))
            
            total = query.count()
            conversations = query.all()
            
            job_ids = [conv.job_id for conv in conversations]
            company_ids = [conv.company_id for conv in conversations]
            
            jobs = {j.id: j for j in db.query(Job).filter(Job.id.in_(job_ids)).all()}
            companies = {u.id: u for u in db.query(User).filter(User.id.in_(company_ids)).all()}
            
            result = []
            for conv in conversations:
                company = companies.get(conv.company_id)
                result.append({
                    "conversation": conv,
                    "job": jobs.get(conv.job_id),
                    "company": company
                })
            
            return {"data": result, "total": total}
        except Exception as e:
            logger.error(f"Failed to get pending conversations for job seeker {job_seeker_id}: {str(e)}")
            return {"data": [], "total": 0}
    
    def activate_conversation_by_job_seeker(self, db: Session, conversation_id: int, job_seeker_id: str) -> dict:
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.job_seeker_id == job_seeker_id
            ).first()
            
            if not conversation:
                return {"success": False, "message": "会话不存在"}
            
            if conversation.status == "active":
                return {"success": False, "message": "会话已开启"}
            
            if conversation.status == "closed":
                return {"success": False, "message": "会话已关闭，无法重新开启"}
            
            conversation.status = "active"
            conversation.updated_at = datetime.now()
            db.commit()
            db.refresh(conversation)
            
            return {"success": True, "message": "会话开启成功", "conversation_id": conversation.id}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to activate conversation {conversation_id} by job seeker: {str(e)}")
            return {"success": False, "message": "操作失败"}
    
    def get_conversation_by_id(self, db: Session, conversation_id: int, user_id: str = None) -> Optional[Conversation]:
        try:
            query = db.query(Conversation).filter(Conversation.id == conversation_id)
            if user_id:
                query = query.filter(
                    or_(
                        Conversation.job_seeker_id == user_id,
                        Conversation.company_id == user_id
                    )
                )
            return query.first()
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {str(e)}")
            return None
    
    def close_conversation(self, db: Session, conversation_id: int, user_id: str = None):
        try:
            query = db.query(Conversation).filter(Conversation.id == conversation_id)
            if user_id:
                query = query.filter(
                    or_(
                        Conversation.job_seeker_id == user_id,
                        Conversation.company_id == user_id
                    )
                )
            
            conversation = query.first()
            if conversation:
                conversation.status = "closed"
                conversation.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to close conversation {conversation_id}: {str(e)}")
    
    def create_system_message_template(self, db: Session, data: SystemMessageTemplateCreate) -> SystemMessageTemplate:
        try:
            template = SystemMessageTemplate(
                name=data.name,
                category=data.category,
                template_content=data.template_content,
                description=data.description,
                is_active=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create system message template: {str(e)}")
            raise
    
    def update_system_message_template(self, db: Session, template_id: int, 
                                       data: SystemMessageTemplateUpdate) -> Optional[SystemMessageTemplate]:
        try:
            template = db.query(SystemMessageTemplate).filter(
                SystemMessageTemplate.id == template_id
            ).first()
            if not template:
                return None
            
            if data.name:
                template.name = data.name
            if data.category:
                template.category = data.category
            if data.template_content:
                template.template_content = data.template_content
            if data.description:
                template.description = data.description
            if data.is_active is not None:
                template.is_active = data.is_active
            template.updated_at = datetime.now()
            
            db.commit()
            db.refresh(template)
            return template
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update system message template {template_id}: {str(e)}")
            return None
    
    def get_system_message_templates(self, db: Session, category: str = None, 
                                     page: int = 1, page_size: int = 20) -> Dict:
        try:
            query = db.query(SystemMessageTemplate)
            if category:
                query = query.filter(SystemMessageTemplate.category == category)
            
            total = query.count()
            templates = query.offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                "data": templates,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            logger.error(f"Failed to get system message templates: {str(e)}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}
    
    def get_system_message_template(self, db: Session, template_id: int) -> Optional[SystemMessageTemplate]:
        try:
            return db.query(SystemMessageTemplate).filter(
                SystemMessageTemplate.id == template_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get system message template {template_id}: {str(e)}")
            return None
    
    def delete_system_message_template(self, db: Session, template_id: int) -> bool:
        try:
            template = db.query(SystemMessageTemplate).filter(
                SystemMessageTemplate.id == template_id
            ).first()
            if not template:
                return False
            
            db.delete(template)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete system message template {template_id}: {str(e)}")
            return False
    
    def send_system_message(self, db: Session, data: SystemMessageCreate) -> SystemMessage:
        try:
            template = None
            content = data.content
            
            if data.template_id:
                template = db.query(SystemMessageTemplate).filter(
                    SystemMessageTemplate.id == data.template_id
                ).first()
                if template:
                    content = self._render_template(template.template_content, data.variables or {})
            
            system_message = SystemMessage(
                user_id=data.user_id,
                template_id=data.template_id,
                content=content,
                category=data.category or (template.category if template else "system"),
                is_read=0,
                created_at=datetime.now()
            )
            db.add(system_message)
            db.commit()
            db.refresh(system_message)
            return system_message
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to send system message to user {data.user_id}: {str(e)}")
            raise
    
    def send_system_message_to_multiple_users(self, db: Session, user_ids: List[str], 
                                              template_id: int = None, content: str = None,
                                              category: str = "system", 
                                              variables: Dict = None) -> List[SystemMessage]:
        try:
            messages = []
            
            template = None
            if template_id:
                template = db.query(SystemMessageTemplate).filter(
                    SystemMessageTemplate.id == template_id
                ).first()
            
            for user_id in user_ids:
                message_content = content
                if template:
                    message_content = self._render_template(template.template_content, variables or {})
                
                system_message = SystemMessage(
                    user_id=user_id,
                    template_id=template_id,
                    content=message_content,
                    category=category or (template.category if template else "system"),
                    is_read=0,
                    created_at=datetime.now()
                )
                db.add(system_message)
                messages.append(system_message)
            
            db.commit()
            for msg in messages:
                db.refresh(msg)
            
            return messages
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to send system message to multiple users: {str(e)}")
            return []
    
    def _render_template(self, template_content: str, variables: Dict) -> str:
        content = template_content
        for key, value in variables.items():
            content = content.replace(f"${{{key}}}", str(value))
        return content
    
    def get_user_system_messages(self, db: Session, user_id: str, category: str = None,
                                 page: int = 1, page_size: int = 20) -> Dict:
        try:
            query = db.query(SystemMessage).filter(SystemMessage.user_id == user_id)
            if category:
                query = query.filter(SystemMessage.category == category)
            
            query = query.order_by(desc(SystemMessage.created_at))
            total = query.count()
            messages = query.offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                "data": messages,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        except Exception as e:
            logger.error(f"Failed to get system messages for user {user_id}: {str(e)}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size}
    
    def mark_system_message_as_read(self, db: Session, message_id: int, user_id: str):
        try:
            message = db.query(SystemMessage).filter(
                SystemMessage.id == message_id,
                SystemMessage.user_id == user_id
            ).first()
            if message:
                message.is_read = 1
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to mark system message {message_id} as read: {str(e)}")
    
    def mark_all_system_messages_as_read(self, db: Session, user_id: str):
        try:
            db.query(SystemMessage).filter(
                SystemMessage.user_id == user_id,
                SystemMessage.is_read == 0
            ).update({"is_read": 1})
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to mark all system messages as read for user {user_id}: {str(e)}")
    
    def get_unread_count(self, db: Session, user_id: str, user_role: str) -> Dict:
        try:
            chat_unread = db.query(Message).filter(
                Message.receiver_id == user_id,
                Message.is_read == 0
            ).count()
            
            system_unread = db.query(SystemMessage).filter(
                SystemMessage.user_id == user_id,
                SystemMessage.is_read == 0
            ).count()
            
            return {
                "chat": chat_unread,
                "system": system_unread,
                "total": chat_unread + system_unread
            }
        except Exception as e:
            logger.error(f"Failed to get unread count for user {user_id}: {str(e)}")
            return {"chat": 0, "system": 0, "total": 0}