# test_sequential_chat_debug.py
import asyncio
import websockets
import json
import requests

USERS = {
    "channu": {
        "email": "channu@gmail.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MDMwZWE0OS1hMDhmLTRmMDItODhkZC00MzNjY2QwODdmMDgiLCJleHAiOjE3NjM1Nzc0Mjl9.IxXWI4eTuqJBIlKbWJhBy2UUCqqKIZ_OgNhJOTsyzZo"
    },
    "bob": {
        "email": "bob@example.com", 
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZDNhMGEzNS1kODI0LTRjMWUtYTJjYi00ODBhZWMwMzg1MTAiLCJleHAiOjE3NjM1Nzc2NDF9.3kIwVa4jrFMmkr5FQRuowvEem4Frrc-KZ68rRWA3Uk0"
    }
}

def check_database_messages():
    """Check if messages are being saved to database"""
    print("\n🔍 Checking database for messages...")
    
    headers = {
        "Authorization": f"Bearer {USERS['channu']['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/chat/all-messages",
            headers=headers
        )
        if response.status_code == 200:
            messages = response.json()
            print(f"📊 Total messages in database: {len(messages)}")
            for msg in messages[:5]:  # Show first 5 messages
                print(f"   - {msg.get('sender_email')} -> {msg.get('receiver_email')}: {msg.get('content')}")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking database: {e}")

async def debug_channu_send():
    """Debug Channu sending messages"""
    print("=" * 50)
    print("DEBUG: Channu sending messages")
    print("=" * 50)
    
    channu_uri = f"ws://localhost:8000/api/v1/chat/ws/{USERS['channu']['email']}?token={USERS['channu']['token']}"
    
    async with websockets.connect(channu_uri) as channu_ws:
        print("✅ Channu connected!")
        welcome = await channu_ws.recv()
        print(f"📨 Welcome: {json.loads(welcome).get('content')}")
        
        messages = [
            "Hello Bob! This is Channu.",
            "How are you doing today?",
            "Can you see these messages?"
        ]
        
        for i, msg in enumerate(messages, 1):
            message = {
                "receiver_identifier": USERS['bob']['email'],
                "content": msg,
                "type": "text"
            }
            print(f"\n📤 Channu sending message {i}: {msg}")
            await channu_ws.send(json.dumps(message))
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(channu_ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                print(f"📨 Response: {response_data}")
                
                if response_data.get('status') == 'sent':
                    print("✅ Message delivered to online user!")
                elif response_data.get('status') == 'saved_offline':
                    print("💾 Message saved (receiver offline)")
                else:
                    print(f"❓ Unknown status: {response_data}")
                    
            except asyncio.TimeoutError:
                print("⏰ TIMEOUT: No response received for message!")
                break
            
            await asyncio.sleep(1)
        
        print(f"\n✅ Channu sent {i} messages")

async def debug_bob_receive():
    """Debug Bob receiving messages"""
    print("\n" + "=" * 50)
    print("DEBUG: Bob receiving messages")
    print("=" * 50)
    
    bob_uri = f"ws://localhost:8000/api/v1/chat/ws/{USERS['bob']['email']}?token={USERS['bob']['token']}"
    
    async with websockets.connect(bob_uri) as bob_ws:
        print("✅ Bob connected!")
        welcome = await bob_ws.recv()
        print(f"📨 Welcome: {json.loads(welcome).get('content')}")
        
        print("👂 Bob listening for messages...")
        received_count = 0
        
        # Listen for 10 seconds
        try:
            while received_count < 3:  # Expecting 3 messages
                message = await asyncio.wait_for(bob_ws.recv(), timeout=10.0)
                message_data = json.loads(message)
                
                print(f"\n💬 Bob received message:")
                print(f"   From: {message_data.get('sender_email')}")
                print(f"   Content: {message_data.get('content')}")
                print(f"   Type: {message_data.get('type')}")
                print(f"   Timestamp: {message_data.get('timestamp')}")
                
                received_count += 1
                
                # Bob replies
                reply_content = f"Thanks for message {received_count}! Bob here."
                reply = {
                    "receiver_identifier": USERS['channu']['email'],
                    "content": reply_content,
                    "type": "text"
                }
                print(f"📤 Bob replying: {reply_content}")
                await bob_ws.send(json.dumps(reply))
                
                # Get delivery confirmation
                response = await asyncio.wait_for(bob_ws.recv(), timeout=5.0)
                print(f"📨 Bob's delivery status: {json.loads(response).get('status')}")
                
        except asyncio.TimeoutError:
            print(f"⏰ Timeout: Bob received {received_count} messages")
        
        print(f"📊 Bob received total: {received_count} messages")

async def simultaneous_connection_test():
    """Test both users connected at the same time"""
    print("\n" + "=" * 50)
    print("SIMULTANEOUS CONNECTION TEST")
    print("=" * 50)
    
    async def channu_send_simultaneous():
        channu_uri = f"ws://localhost:8000/api/v1/chat/ws/{USERS['channu']['email']}?token={USERS['channu']['token']}"
        async with websockets.connect(channu_uri) as ws:
            await ws.recv()  # Welcome
            print("✅ Channu connected simultaneously")
            
            # Send message when both are connected
            message = {
                "receiver_identifier": USERS['bob']['email'],
                "content": "Hi Bob! We're both online now!",
                "type": "text"
            }
            await ws.send(json.dumps(message))
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"📨 Channu delivery (simultaneous): {json.loads(response).get('status')}")
    
    async def bob_listen_simultaneous():
        bob_uri = f"ws://localhost:8000/api/v1/chat/ws/{USERS['bob']['email']}?token={USERS['bob']['token']}"
        async with websockets.connect(bob_uri) as ws:
            await ws.recv()  # Welcome
            print("✅ Bob connected simultaneously")
            
            # Listen for message
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10.0)
                message_data = json.loads(message)
                print(f"💬 Bob received (simultaneous): {message_data.get('content')}")
            except asyncio.TimeoutError:
                print("⏰ Bob didn't receive message in simultaneous test")
    
    # Run both simultaneously
    await asyncio.gather(
        channu_send_simultaneous(),
        bob_listen_simultaneous()
    )

async def main():
    # First check current database state
    check_database_messages()
    
    # Test 1: Channu sends messages
    await debug_channu_send()
    
    # Check database after sending
    check_database_messages()
    
    # Test 2: Bob receives messages
    await debug_bob_receive()
    
    # Test 3: Simultaneous connection
    await simultaneous_connection_test()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())