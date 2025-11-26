# Bot Startup Troubleshooting

## Problem: Connection Timeout

If you're getting "Timed out" errors when starting the bot, here are the solutions:

### Solution 1: Check Internet Connection
Make sure your internet connection is working properly.

### Solution 2: Firewall/Antivirus
- Check if Windows Firewall is blocking the connection
- Check if your antivirus is blocking Python
- Temporarily disable firewall/antivirus to test

### Solution 3: Proxy Issues
If you're behind a proxy:
1. Configure proxy in your environment
2. Or disable proxy completely by setting:
```bash
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
```

### Solution 4: Run as Administrator
Try running the bot as Administrator:
1. Right-click on Command Prompt
2. Select "Run as administrator"
3. Navigate to your bot directory
4. Run `python start_bot.py`

### Solution 5: Use VPN
If Telegram is blocked in your country/network, use a VPN:
1. Connect to VPN
2. Run the bot

### Solution 6: Check Telegram Status
Verify Telegram API is accessible:
```bash
ping api.telegram.org
```

### Solution 7: Increase Timeout
You can modify the timeout in the code if the network is slow.

### Solution 8: Test Connection First
Before running the full bot, test with a simple script:
```python
import asyncio
from telegram import Bot

async def test_connection():
    bot = Bot("YOUR_BOT_TOKEN")
    me = await bot.get_me()
    print(f"Bot username: {me.username}")
    
asyncio.run(test_connection())
```

## Recommended Order:
1. Test internet connection
2. Try Solution 3 (proxy)
3. Try Solution 4 (run as admin)
4. Try Solution 5 (VPN)

## Still Not Working?
If nothing works, try running the bot on a different network or server.


