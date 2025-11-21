# app/services/chat_manager.py - UPDATED
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
# app/services/chat_manager.py
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        user_id_str = str(user_id)
        await websocket.accept()
        self.active_connections[user_id_str] = websocket
        print(f"✅ User {user_id_str} connected. Total: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        user_id_str = str(user_id)
        if user_id_str in self.active_connections:
            del self.active_connections[user_id_str]
            print(f"🔴 User {user_id_str} disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, user_id: str) -> bool:
        user_id_str = str(user_id)
        
        if user_id_str in self.active_connections:
            websocket = self.active_connections[user_id_str]
            try:
                await websocket.send_text(message)
                return True
            except Exception as e:
                print(f"❌ Error sending to user {user_id_str}: {e}")
                self.disconnect(user_id_str)
                return False
        return False

    def is_user_online(self, user_id: str) -> bool:
        return str(user_id) in self.active_connections

    def get_online_users(self):
        return list(self.active_connections.keys())