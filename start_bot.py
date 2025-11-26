#!/usr/bin/env python3
"""
Startup script for the bot with userbot
This handles the threading properly to avoid event loop conflicts
"""

import sys
import time
import threading
import asyncio
from userbot import start_userbot, stop_userbot

def run_userbot_thread():
    """Run userbot in its own thread with its own event loop"""
    def userbot_main():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            print("📱 Starting userbot thread...")
            loop.run_until_complete(start_userbot())
            print("✅ Userbot started successfully!")
            print("⏳ Waiting for userbot to initialize...")
            time.sleep(5)
            print("✅ Userbot ready!")
            loop.run_forever()
        except KeyboardInterrupt:
            print("🛑 Stopping userbot...")
            loop.run_until_complete(stop_userbot())
        except Exception as e:
            print(f"❌ Userbot error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            loop.close()
    
    thread = threading.Thread(target=userbot_main, daemon=True)
    thread.start()
    return thread

def main():
    """Main startup function"""
    print("🚀 Starting Telegram Bot with Userbot...")
    print("=" * 50)
    
    # Start userbot in separate thread
    print("📱 Initializing userbot...")
    userbot_thread = run_userbot_thread()
    
    # Wait for userbot to initialize
    print("⏳ Waiting for userbot to initialize...")
    time.sleep(8)  # Give it more time to fully start
    
    # Import and run main bot
    print("🤖 Starting main bot...")
    try:
        from bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
