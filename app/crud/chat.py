# app/crud/chat.py - FIXED WITH PROPER ALIASES
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import aliased
from app.models.chat import ChatMessage
from app.models.user import User
from datetime import datetime
from uuid import UUID
from typing import List, Optional
# app/crud/chat.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatMessage
from datetime import datetime

async def create_message(
    db: AsyncSession, 
    sender_id: int, 
    receiver_id: int, 
    content: str, 
    message_type: str = "text"
) -> ChatMessage:
    """Create a new chat message"""
    print(f"💾 Creating message: {sender_id} -> {receiver_id}: {content}")
    
    try:
        message = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            timestamp=datetime.utcnow(),
            is_read=False
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        print(f"✅ Message created successfully: {message.id}")
        return message
        
    except Exception as e:
        print(f"❌ Error creating message: {e}")
        await db.rollback()
        raise e
async def get_chat_history(
    db: AsyncSession,
    user1_id: UUID,
    user2_id: UUID,
    limit: int = 100,
    offset: int = 0
) -> List[ChatMessage]:
    query = select(ChatMessage).where(
        or_(
            and_(ChatMessage.sender_id == user1_id, ChatMessage.receiver_id == user2_id),
            and_(ChatMessage.sender_id == user2_id, ChatMessage.receiver_id == user1_id)
        )
    ).order_by(ChatMessage.timestamp.asc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()

async def mark_messages_as_read(
    db: AsyncSession,
    sender_id: UUID,
    receiver_id: UUID
) -> None:
    query = select(ChatMessage).where(
        and_(
            ChatMessage.sender_id == sender_id,
            ChatMessage.receiver_id == receiver_id,
            ChatMessage.is_read == False
        )
    )
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    for message in messages:
        message.is_read = True
    
    await db.commit()

async def get_conversation_users(db: AsyncSession, user_id: UUID) -> List[User]:
    """
    Get all users that have chatted with the given user
    """
    # Users who received messages from this user
    sent_to = select(ChatMessage.receiver_id).where(ChatMessage.sender_id == user_id).distinct()
    
    # Users who sent messages to this user
    received_from = select(ChatMessage.sender_id).where(ChatMessage.receiver_id == user_id).distinct()
    
    # Combine
    user_ids = sent_to.union(received_from)
    
    # Handle case where there are no conversations yet
    if not user_ids.selected_columns:
        return []
    
    users_query = select(User).where(User.id.in_(user_ids))
    result = await db.execute(users_query)
    return result.scalars().all()

async def get_unread_count(db: AsyncSession, user_id: UUID, sender_id: UUID = None) -> int:
    """
    Get count of unread messages for a user
    """
    query = select(func.count(ChatMessage.id)).where(
        and_(
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False
        )
    )
    
    if sender_id:
        query = query.where(ChatMessage.sender_id == sender_id)
    
    result = await db.execute(query)
    count = result.scalar()
    return count if count else 0

async def get_received_messages(db: AsyncSession, user_id: UUID) -> List[ChatMessage]:
    """
    Get all messages received by user
    """
    # Simple query without joins
    query = select(ChatMessage).where(
        ChatMessage.receiver_id == user_id
    ).order_by(ChatMessage.timestamp.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_all_user_messages(db: AsyncSession, user_id: UUID) -> List[ChatMessage]:
    """
    Get all messages for user (both sent and received)
    """
    # Simple query without complex joins
    query = select(ChatMessage).where(
        or_(
            ChatMessage.sender_id == user_id,
            ChatMessage.receiver_id == user_id
        )
    ).order_by(ChatMessage.timestamp.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_last_message(db: AsyncSession, user1_id: UUID, user2_id: UUID) -> Optional[ChatMessage]:
    """
    Get the last message between two users
    """
    query = select(ChatMessage).where(
        or_(
            and_(ChatMessage.sender_id == user1_id, ChatMessage.receiver_id == user2_id),
            and_(ChatMessage.sender_id == user2_id, ChatMessage.receiver_id == user1_id)
        )
    ).order_by(ChatMessage.timestamp.desc()).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_all_user_messages_with_users(db: AsyncSession, user_id: UUID):
    """
    Get all messages with user details using proper aliases
    """
    # Create aliases for the User table
    Sender = aliased(User)
    Receiver = aliased(User)
    
    query = (
        select(ChatMessage, Sender, Receiver)
        .join(Sender, ChatMessage.sender_id == Sender.id)
        .join(Receiver, ChatMessage.receiver_id == Receiver.id)
        .where(
            or_(
                ChatMessage.sender_id == user_id,
                ChatMessage.receiver_id == user_id
            )
        )
        .order_by(ChatMessage.timestamp.desc())
    )
    
    result = await db.execute(query)
    return result.all()