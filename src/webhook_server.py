from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.exceptions import InvalidSignatureError
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
import signal
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')

if not LINE_CHANNEL_SECRET or not LINE_ACCESS_TOKEN:
    logger.error("LINE_CHANNEL_SECRET and LINE_ACCESS_TOKEN must be set in .env file")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="LINE Webhook Server", 
              description="Receives and processes LINE webhook events",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LINE API
configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
line_api = MessagingApi(ApiClient(configuration))

# Define message storage path
MESSAGES_FILE = os.getenv('MESSAGES_FILE', '/app/data/messages.json')

def save_message(timestamp: str, user_id: str, message_type: str, content: str):
    """Save message to messages.json with improved error handling"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(MESSAGES_FILE), exist_ok=True)
        
        # Load existing messages
        messages = {'messages': []}
        if os.path.exists(MESSAGES_FILE) and os.path.getsize(MESSAGES_FILE) > 0:
            try:
                with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in messages file. Creating new file.")
        
        # Add new message
        messages['messages'].append({
            'timestamp': timestamp,
            'user_id': user_id,
            'type': message_type,
            'content': content
        })
        
        # Save to file (atomic write)
        temp_file = f"{MESSAGES_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, MESSAGES_FILE)
        logger.info("Message saved: %s", content[:30] + "..." if len(content) > 30 else content)
        return True
    except Exception as e:
        logger.error("Error saving message: %s", str(e))
        return False

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhook events from LINE"""
    try:
        # Get signature and body
        signature = request.headers.get('X-Line-Signature', '')
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Log request receipt
        logger.info("Received webhook request")
        
        # Verify signature (important security step)
        try:
            handler.handle(body_str, signature)
        except InvalidSignatureError:
            logger.warning("Invalid signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process message
        body_json = json.loads(body_str)
        events = body_json.get("events", [])
        
        if not events:
            return {"status": "OK", "message": "No events"}
        
        # Process each event (currently only handling the first one)
        event = events[0]
        if event["type"] != "message":
            return {"status": "OK", "message": f"Non-message event received: {event['type']}"}
            
        # Extract message details
        timestamp = datetime.fromtimestamp(event["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        user_id = event["source"]["userId"]
        message_type = event["message"]["type"]
        
        # Handle different message types
        if message_type == "text":
            content = event["message"].get("text", "")
        elif message_type == "sticker":
            sticker_id = event["message"].get("stickerId", "unknown")
            package_id = event["message"].get("packageId", "unknown")
            content = f"[Sticker: package={package_id}, sticker={sticker_id}]"
        elif message_type == "image":
            content = "[Image message]"
        else:
            content = f"[{message_type} message]"
        
        # Save message
        if save_message(timestamp, user_id, message_type, content):
            return {"status": "OK", "message": "Message processed successfully"}
        else:
            return {"status": "Error", "message": "Failed to save message"}
        
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON: %s", str(e))
        return {"status": "Error", "message": "Invalid JSON payload"}
    except Exception as e:
        error_msg = f"Webhook error: {str(e)}"
        logger.error(error_msg)
        return {"status": "Error", "message": error_msg}

@app.get("/")
async def root():
    """Healthcheck endpoint"""
    return {
        "status": "LINE Webhook Server is running",
        "version": "1.0.0",
        "health": "OK"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

# Graceful shutdown handler
def handle_exit(signum, frame):
    logger.info("Received shutdown signal. Exiting gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    
    # Run the server
    import uvicorn
    port = int(os.getenv('SERVER_PORT', 8000))
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=port)