import asyncio
import logging
import json
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram API credentials
API_ID = 22209395
API_HASH = "97e4178a45878fcd36052bf0b0b5b0a3"

# Bot configuration
PARTNER_BOT_USERNAME = "QuotexPartnerBot"
SESSION_NAME = "userbot_session"

# Data files
PENDING_REQUESTS_FILE = "pending_requests.json"
RESPONSES_FILE = "responses.json"

class QuotexUserbot:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.partner_bot = None
        self.pending_requests = {}
        
    async def start(self):
        """Start the userbot"""
        await self.client.start()
        logger.info("Userbot started successfully")
        
        # Get the partner bot entity
        self.partner_bot = await self.client.get_entity(PARTNER_BOT_USERNAME)
        logger.info(f"Connected to {PARTNER_BOT_USERNAME}")
        
        # Set up message handler
        self.client.add_event_handler(self.handle_message, events.NewMessage)
        
        # Load pending requests
        self.load_pending_requests()
        
    async def stop(self):
        """Stop the userbot"""
        await self.client.disconnect()
        logger.info("Userbot stopped")
        
    def parse_balance(self, message_text):
        """Parse balance from QuotexPartnerBot response"""
        try:
            # Look for "Balance: $" line
            import re
            balance_match = re.search(r'Balance:\s*\$?\s*([\d.]+)', message_text)
            if balance_match:
                balance_str = balance_match.group(1).replace(',', '')
                balance = float(balance_str)
                return balance
            return 0
        except Exception as e:
            logger.error(f"Error parsing balance: {e}")
            return 0
            
    def load_pending_requests(self):
        """Load pending requests from file"""
        try:
            if os.path.exists(PENDING_REQUESTS_FILE):
                with open(PENDING_REQUESTS_FILE, 'r', encoding='utf-8') as f:
                    self.pending_requests = json.load(f)
            logger.info(f"Loaded {len(self.pending_requests)} pending requests")
        except Exception as e:
            logger.error(f"Error loading pending requests: {e}")
            self.pending_requests = {}
            
    def save_pending_requests(self):
        """Save pending requests to file"""
        try:
            with open(PENDING_REQUESTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.pending_requests, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving pending requests: {e}")
            
    def save_response(self, platform_id, response, user_id, balance=0):
        """Save response from QuotexPartnerBot"""
        try:
            response_data = {
                "platform_id": platform_id,
                "response": response,
                "user_id": user_id,
                "balance": balance,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Load existing responses
            responses = []
            if os.path.exists(RESPONSES_FILE):
                with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                    responses = json.load(f)
            
            # Add new response
            responses.append(response_data)
            
            # Save back to file
            with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved response for platform ID {platform_id}")
            
        except Exception as e:
            logger.error(f"Error saving response: {e}")
            
    async def send_verification_request(self, platform_id, user_id, username):
        """Send verification request to QuotexPartnerBot"""
        try:
            # Send only the platform ID to QuotexPartnerBot
            message = platform_id
            
            # Send message to QuotexPartnerBot
            await self.client.send_message(self.partner_bot, message)
            
            # Store pending request
            self.pending_requests[platform_id] = {
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending"
            }
            
            # Save pending requests
            self.save_pending_requests()
            
            logger.info(f"Sent verification request for platform ID {platform_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending verification request: {e}")
            return False
            
    async def handle_message(self, event):
        """Handle incoming messages from QuotexPartnerBot"""
        try:
            # Check if message is from QuotexPartnerBot
            if event.sender_id != self.partner_bot.id:
                return
                
            message_text = event.message.message.strip()
            logger.info(f"Received message from QuotexPartnerBot: {message_text}")
            
            # Look for platform ID in the message
            platform_id = None
            for pid in self.pending_requests.keys():
                if pid in message_text:
                    platform_id = pid
                    break
                    
            if not platform_id:
                logger.warning("Could not find platform ID in response")
                return
                
            # Get request info
            request_info = self.pending_requests.get(platform_id)
            if not request_info:
                logger.warning(f"No pending request found for platform ID {platform_id}")
                return
                
            # Determine response type and parse balance
            if "was not found" in message_text:
                response_type = "not_found"
                balance = 0
            else:
                response_type = "found"
                # Parse balance from message
                balance = self.parse_balance(message_text)
                
            # Save response with balance info
            self.save_response(platform_id, message_text, request_info["user_id"], balance)
            
            # Remove from pending requests
            del self.pending_requests[platform_id]
            self.save_pending_requests()
            
            logger.info(f"Processed response for platform ID {platform_id}: {response_type}, balance: ${balance}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            
    def get_response(self, platform_id):
        """Get response for a platform ID"""
        try:
            if os.path.exists(RESPONSES_FILE):
                with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                    responses = json.load(f)
                    
                # Find the latest response for this platform ID
                for response in reversed(responses):
                    if response["platform_id"] == platform_id:
                        return response
                        
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            
        return None

# Global userbot instance
userbot_instance = None
userbot_loop = None

async def start_userbot():
    """Start the userbot"""
    global userbot_instance, userbot_loop
    userbot_instance = QuotexUserbot()
    await userbot_instance.start()
    userbot_loop = asyncio.get_event_loop()
    return userbot_instance

async def stop_userbot():
    """Stop the userbot"""
    global userbot_instance
    if userbot_instance:
        await userbot_instance.stop()

def send_verification(platform_id, user_id, username):
    """Send verification request to QuotexPartnerBot (sync wrapper)"""
    global userbot_instance, userbot_loop
    if userbot_instance and userbot_loop:
        try:
            # Schedule the coroutine on the userbot's event loop
            future = asyncio.run_coroutine_threadsafe(
                userbot_instance.send_verification_request(platform_id, user_id, username),
                userbot_loop
            )
            return future.result(timeout=10)  # Wait up to 10 seconds
        except Exception as e:
            print(f"Error sending verification: {e}")
            return False
    return False

def get_verification_response(platform_id):
    """Get verification response for platform ID"""
    global userbot_instance
    if userbot_instance:
        return userbot_instance.get_response(platform_id)
    return None

if __name__ == "__main__":
    # Run userbot
    async def main():
        userbot = await start_userbot()
        try:
            # Keep running
            await userbot.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Stopping userbot...")
        finally:
            await stop_userbot()
    
    asyncio.run(main())
