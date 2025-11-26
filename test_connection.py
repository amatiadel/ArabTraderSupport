#!/usr/bin/env python3
"""
Test Telegram bot connection
This script tests if the bot can connect to Telegram
"""

import asyncio
import os
from telegram import Bot

# Disable proxy
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('all_proxy', None)

BOT_TOKEN = "7948819240:AAFHyTpDKr7-oVp6WNBrkgjZWn6TNzKtwsc"

async def test_connection():
    """Test bot connection to Telegram"""
    print("🧪 Testing Telegram Bot Connection...")
    print("=" * 50)
    
    try:
        print("📡 Creating bot instance...")
        bot = Bot(BOT_TOKEN)
        
        print("🔌 Connecting to Telegram...")
        me = await bot.get_me()
        
        print("✅ Connection successful!")
        print(f"🤖 Bot username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"📝 Bot name: {me.first_name}")
        
        print("\n✅ Bot is ready to use!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout!")
        print("⚠️  Check your internet connection or firewall settings")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check internet connection")
        print("2. Check firewall/antivirus settings")
        print("3. Check if using a proxy")
        print("4. Try using a VPN")
        return False
    finally:
        try:
            await bot.close()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Telegram Bot Connection Test")
    print("=" * 50)
    print()
    
    try:
        result = asyncio.run(test_connection())
        if result:
            print("\n✅ Test passed! You can now run the bot.")
        else:
            print("\n❌ Test failed! Please fix the issues before running the bot.")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


