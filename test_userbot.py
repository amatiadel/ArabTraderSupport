#!/usr/bin/env python3
"""
Test script for userbot functionality
Run this to test if the userbot can communicate with QuotexPartnerBot
"""

import asyncio
import sys
from userbot import start_userbot, stop_userbot, send_verification, get_verification_response

async def test_userbot():
    """Test the userbot functionality"""
    print("🚀 Starting userbot test...")
    
    try:
        # Start userbot
        print("📱 Starting userbot...")
        await start_userbot()
        print("✅ Userbot started successfully!")
        
        # Wait a moment for the event loop to be set up
        await asyncio.sleep(1)
        
        # Test sending a verification request
        test_platform_id = "123456789"
        test_user_id = 123456789
        test_username = "test_user"
        
        print(f"📤 Sending test verification for platform ID: {test_platform_id}")
        success = send_verification(test_platform_id, test_user_id, test_username)
        
        if success:
            print("✅ Verification request sent successfully!")
            
            # Wait for response
            print("⏳ Waiting for response from QuotexPartnerBot...")
            await asyncio.sleep(5)
            
            # Check for response
            response = get_verification_response(test_platform_id)
            if response:
                print(f"📥 Received response: {response['response']}")
                
                if "was not found" in response["response"]:
                    print("❌ Platform ID not found (expected response)")
                else:
                    print("✅ Platform ID found (unexpected response)")
            else:
                print("⏳ No response yet, this is normal for first run")
        else:
            print("❌ Failed to send verification request")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        
    finally:
        # Stop userbot
        print("🛑 Stopping userbot...")
        await stop_userbot()
        print("✅ Test completed!")

if __name__ == "__main__":
    print("🧪 Userbot Test Script")
    print("=" * 50)
    print("This will test if the userbot can communicate with QuotexPartnerBot")
    print("Make sure you have your phone ready for verification!")
    print("=" * 50)
    
    try:
        asyncio.run(test_userbot())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
