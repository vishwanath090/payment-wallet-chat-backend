# app/api/v1/chat/routes.py - COMPLETELY FIXED
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime
import json
from uuid import UUID
# app/api/v1/chat/routes.py - FIXED VERSION
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime
import json
import logging

from app.db.session import get_db
from app.core.jwt import get_current_user, get_current_user_ws_light
from app.models.user import User
from app.models.chat import ChatMessage
from app.services.chat_manager import ConnectionManager

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Create connection manager instance
manager = ConnectionManager()
from app.schemas.chat import MessageCreate, MessageResponse
from app.services.chat_manager import ConnectionManager
from app.crud.chat import (
    create_message, 
    get_chat_history, 
    get_conversation_users, 
    get_last_message, 
    get_unread_count,
    get_received_messages,
    get_all_user_messages,
    mark_messages_as_read
)

router = APIRouter(prefix="/chat", tags=["Chat"])
# Add this to your routes.py for debugging
@router.get("/debug-token")
async def debug_token(current_user: User = Depends(get_current_user)):
    """Debug endpoint to check token contents"""
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "token_valid": True
    }
# Add to app/api/v1/chat/routes.py
@router.get("/public-test")
async def public_test():
    """Public test endpoint without authentication"""
    return {
        "message": "Public endpoint works",
        "status": "success"
    }
# Create connection manager instance
manager = ConnectionManager()
async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """Get user by ID with error handling"""
    try:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    except Exception as e:
        print(f"❌ Error getting user by ID {user_id}: {e}")
        return None

async def find_user_by_identifier(db: AsyncSession, identifier: str) -> User:
    """Find user by email or full name with error handling"""
    try:
        from sqlalchemy import select, or_
        
        # Try by email
        query = select(User).where(User.email == identifier)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return user
            
        # Try by full name
        query = select(User).where(User.full_name == identifier)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        return user
        
    except Exception as e:
        print(f"❌ Error finding user by identifier {identifier}: {e}")
        return None
    

@router.get("/test-websocket")
async def test_websocket_connection(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test if WebSocket connection would work for current user"""
    user_id_str = str(current_user.id)
    is_online = user_id_str in manager.active_connections
    
    return {
        "user_id": user_id_str,
        "user_email": current_user.email,
        "is_online": is_online,
        "active_connections": len(manager.active_connections),
        "websocket_url": f"ws://localhost:8000/api/v1/chat/ws/{current_user.email}?token=YOUR_TOKEN"
    }
async def send_pending_messages(db: AsyncSession, user: User, websocket: WebSocket):
    """Send any undelivered messages to user when they connect"""
    try:
        # Get messages where this user is receiver and not read
        from sqlalchemy import select
        from app.models.chat import ChatMessage
        
        query = select(ChatMessage).where(
            ChatMessage.receiver_id == user.id,
            ChatMessage.is_read == False
        ).order_by(ChatMessage.timestamp.asc())
        
        result = await db.execute(query)
        pending_messages = result.scalars().all()
        
        for message in pending_messages:
            # Get sender info
            sender_query = select(User).where(User.id == message.sender_id)
            sender_result = await db.execute(sender_query)
            sender = sender_result.scalar_one_or_none()
            
            if sender:
                message_data = {
                    "id": message.id,
                    "sender_id": str(message.sender_id),
                    "receiver_id": str(message.receiver_id),
                    "content": message.content,
                    "message_type": message.message_type,
                    "timestamp": message.timestamp.isoformat(),
                    "is_read": message.is_read,
                    "sender_email": sender.email,
                    "sender_name": sender.full_name,
                    "receiver_email": user.email,
                    "receiver_name": user.full_name,
                    "is_pending": True  # Flag to indicate this was a pending message
                }
                
                await websocket.send_text(json.dumps(message_data))
                print(f"📨 Delivered pending message {message.id} to {user.email}")
        
        if pending_messages:
            print(f"✅ Delivered {len(pending_messages)} pending messages to {user.email}")
            
    except Exception as e:
        print(f"❌ Error delivering pending messages: {e}")
# Add this to your app/api/v1/chat/routes.py WebSocket endpoint
@router.websocket("/ws/{user_identifier}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_identifier: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat
    """
    print(f"🔗 WebSocket connection attempt for: {user_identifier}")
    
    user = None
    try:
        # Authenticate user
        authenticated_user_id = await get_current_user_ws_light(websocket)
        if not authenticated_user_id:
            await websocket.close(code=1008)
            return

        # Get full user object from database
        user = await get_user_by_id(db, authenticated_user_id)
        if not user:
            await websocket.close(code=1008)
            return

        print(f"✅ User {user.email} authenticated")

        # Connect user
        user_id_str = str(user.id)
        await manager.connect(websocket, user_id_str)
        print(f"✅ User {user.email} connected. Active connections: {len(manager.active_connections)}")

        # Send connection confirmation
        welcome_msg = {
            "type": "connection",
            "content": "WebSocket connected successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id_str,
            "user_email": user.email
        }
        await websocket.send_text(json.dumps(welcome_msg))

        # Send pending messages if any
        await send_pending_messages(db, user, websocket)

        # Main message loop
        while True:
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                
                # Validate message data
                if not all(k in message_data for k in ["receiver_identifier", "content"]):
                    error_msg = {"error": "Invalid message format. Required: receiver_identifier, content"}
                    await websocket.send_text(json.dumps(error_msg))
                    continue

                # Validate content
                content = message_data.get("content", "").strip()
                if not content:
                    error_msg = {"error": "Message content cannot be empty"}
                    await websocket.send_text(json.dumps(error_msg))
                    continue

                # Find receiver
                receiver_identifier = message_data["receiver_identifier"]
                receiver = await find_user_by_identifier(db, receiver_identifier)
                if not receiver:
                    error_msg = {"error": f"Receiver '{receiver_identifier}' not found"}
                    await websocket.send_text(json.dumps(error_msg))
                    continue

                # Create message in database
                try:
                    from app.crud.chat import create_message
                    message = await create_message(
                        db=db,
                        sender_id=user.id,
                        receiver_id=receiver.id,
                        content=content,
                        message_type=message_data.get("type", "text")
                    )
                except Exception as e:
                    print(f"❌ Error saving message: {e}")
                    error_msg = {"error": "Failed to save message"}
                    await websocket.send_text(json.dumps(error_msg))
                    continue

                # Prepare message response
                message_response = {
                    "id": message.id,
                    "sender_id": str(message.sender_id),
                    "receiver_id": str(message.receiver_id),
                    "content": message.content,
                    "message_type": message.message_type,
                    "timestamp": message.timestamp.isoformat(),
                    "is_read": message.is_read,
                    "sender_email": user.email,
                    "sender_name": user.full_name,
                    "receiver_email": receiver.email,
                    "receiver_name": receiver.full_name
                }

                # Send to receiver if online
                receiver_id_str = str(receiver.id)
                receiver_sent = await manager.send_personal_message(
                    json.dumps(message_response),
                    receiver_id_str
                )

                # Send confirmation to sender
                confirmation = {
                    "type": "message_status",
                    "status": "sent" if receiver_sent else "saved_offline",
                    "message_id": message.id,
                    "receiver_online": receiver_sent,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_text(json.dumps(confirmation))

            except json.JSONDecodeError:
                error_msg = {"error": "Invalid JSON format"}
                await websocket.send_text(json.dumps(error_msg))
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                error_msg = {"error": f"Error processing message: {str(e)}"}
                await websocket.send_text(json.dumps(error_msg))
                
    except WebSocketDisconnect:
        print(f"🔴 WebSocket disconnected for {user_identifier}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        # Always clean up connection
        if user:
            manager.disconnect(str(user.id))
            print(f"🧹 Cleaned up connection for {user.email}")
# Keep your existing HTTP endpoints...
@router.post("/test-send-message")
async def test_send_message(
    receiver_identifier: str,
    content: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test endpoint to send a message without WebSocket"""
    logger.info(f"🧪 Testing message send: from {current_user.email} to {receiver_identifier}")
    
    # Find receiver
    receiver = await find_user_by_identifier(db, receiver_identifier)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    logger.info(f"✅ Found receiver: {receiver.email} (ID: {receiver.id})")
    
    # Create message
    from app.crud.chat import create_message
    message = await create_message(
        db=db,
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=content,
        message_type="text"
    )
    
    logger.info(f"✅ Test message created: {message.id}")
    
    # Prepare message response
    message_dict = {
        "id": message.id,
        "sender_id": str(message.sender_id),
        "receiver_id": str(message.receiver_id),
        "content": message.content,
        "message_type": message.message_type,
        "timestamp": message.timestamp.isoformat(),
        "is_read": message.is_read,
        "sender_email": current_user.email,
        "sender_name": current_user.full_name,
        "receiver_email": receiver.email,
        "receiver_name": receiver.full_name
    }
    
    # Try to send via WebSocket
    receiver_sent = await manager.send_personal_message(
        json.dumps(message_dict),
        str(receiver.id)
    )
    
    # Send to sender
    sender_sent = await manager.send_personal_message(
        json.dumps(message_dict),
        str(current_user.id)
    )
    
    return {
        "message_id": message.id,
        "receiver_found": True,
        "receiver_email": receiver.email,
        "receiver_online": receiver_sent,
        "sender_online": sender_sent,
        "active_connections": list(manager.active_connections.keys()),
        "message_content": content
    }

@router.get("/history/{receiver_identifier}")
async def get_chat_history_endpoint(
    receiver_identifier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history between current user and receiver
    """
    receiver = await find_user_by_identifier(db, receiver_identifier)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    messages = await get_chat_history(db, current_user.id, receiver.id)
    
    # Convert to response format
    response_messages = []
    for message in messages:
        response_messages.append({
            "id": message.id,
            "sender_id": str(message.sender_id),
            "receiver_id": str(message.receiver_id),
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.timestamp.isoformat(),
            "is_read": message.is_read,
            "is_sent_by_me": message.sender_id == current_user.id
        })
    
    return response_messages

@router.get("/users")
async def get_available_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available users to chat with
    """
    query = select(User.id, User.email, User.full_name).where(User.id != current_user.id)
    result = await db.execute(query)
    users = result.all()
    
    return [
        {
            "id": str(user.id),  # Convert UUID to string
            "email": user.email,
            "full_name": user.full_name
        }
        for user in users
    ]

@router.get("/conversations")
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conversations for current user
    """
    users = await get_conversation_users(db, current_user.id)
    
    conversations = []
    for user in users:
        last_message = await get_last_message(db, current_user.id, user.id)
        unread_count = await get_unread_count(db, current_user.id, user.id)
        
        conversations.append({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name
            },
            "last_message": {
                "content": last_message.content if last_message else None,
                "timestamp": last_message.timestamp.isoformat() if last_message else None,
                "is_sent_by_me": last_message.sender_id == current_user.id if last_message else None
            },
            "unread_count": unread_count
        })
    
    # Sort by timestamp
    conversations.sort(key=lambda x: x["last_message"]["timestamp"] or "0001-01-01T00:00:00", reverse=True)
    
    return conversations

@router.get("/received-messages")
async def get_received_messages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all messages received by current user - SIMPLEST VERSION
    """
    try:
        # Direct query for messages
        query = select(ChatMessage).where(
            ChatMessage.receiver_id == current_user.id
        ).order_by(ChatMessage.timestamp.desc())
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        response_messages = []
        for message in messages:
            # Get sender info with separate query
            sender_query = select(User).where(User.id == message.sender_id)
            sender_result = await db.execute(sender_query)
            sender = sender_result.scalar_one_or_none()
            
            response_messages.append({
                "id": message.id,
                "sender_id": str(message.sender_id),
                "sender_email": sender.email if sender else "Unknown",
                "sender_name": sender.full_name if sender else "Unknown User",
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "is_read": message.is_read
            })
        
        return response_messages
        
    except Exception as e:
        print(f"❌ Error in /received-messages: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

 
@router.get("/all-messages")
async def get_all_user_messages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all messages for current user - SIMPLEST VERSION
    """
    try:
        # Direct query for messages
        query = select(ChatMessage).where(
            or_(
                ChatMessage.sender_id == current_user.id,
                ChatMessage.receiver_id == current_user.id
            )
        ).order_by(ChatMessage.timestamp.desc())
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        response_messages = []
        for message in messages:
            # Get sender info
            sender_query = select(User).where(User.id == message.sender_id)
            sender_result = await db.execute(sender_query)
            sender = sender_result.scalar_one_or_none()
            
            # Get receiver info
            receiver_query = select(User).where(User.id == message.receiver_id)
            receiver_result = await db.execute(receiver_query)
            receiver = receiver_result.scalar_one_or_none()
            
            response_messages.append({
                "id": message.id,
                "sender_id": str(message.sender_id),
                "sender_email": sender.email if sender else "Unknown",
                "sender_name": sender.full_name if sender else "Unknown User",
                "receiver_id": str(message.receiver_id),
                "receiver_email": receiver.email if receiver else "Unknown",
                "receiver_name": receiver.full_name if receiver else "Unknown User",
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "is_read": message.is_read,
                "is_sent_by_me": message.sender_id == current_user.id
            })
        
        return response_messages
        
    except Exception as e:
        print(f"❌ Error in /all-messages: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a message as read
    """
    query = select(ChatMessage).where(
        and_(
            ChatMessage.id == message_id,
            ChatMessage.receiver_id == current_user.id
        )
    )
    result = await db.execute(query)
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    await db.commit()
    
    return {"status": "success", "message": "Message marked as read"}

# Also fix the conversations endpoint to handle empty cases
@router.get("/conversations")
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conversations for current user (users they've chatted with)
    """
    try:
        from app.crud.chat import get_conversation_users, get_last_message, get_unread_count
        
        # Get all users that current user has chatted with
        users = await get_conversation_users(db, current_user.id)
        
        conversations = []
        for user in users:
            # Get last message
            last_message = await get_last_message(db, current_user.id, user.id)
            
            # Get unread message count
            unread_count = await get_unread_count(db, current_user.id, user.id)
            
            conversations.append({
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name
                },
                "last_message": {
                    "content": last_message.content if last_message else None,
                    "timestamp": last_message.timestamp.isoformat() if last_message else None,
                    "is_sent_by_me": last_message.sender_id == current_user.id if last_message else None
                },
                "unread_count": unread_count
            })
        
        # Sort conversations by last message timestamp (most recent first)
        conversations.sort(key=lambda x: x["last_message"]["timestamp"] or "0001-01-01T00:00:00", reverse=True)
        
        return conversations
        
    except Exception as e:
        print(f"❌ Error in /conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")