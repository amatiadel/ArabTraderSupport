# Userbot Setup Guide

## Overview
The bot now uses a userbot (Telethon) to communicate with QuotexPartnerBot. The userbot acts as a bridge between your main bot and QuotexPartnerBot.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. First Run Setup
When you run the bot for the first time, it will ask for:
- **Phone Number**: Your Telegram phone number (with country code, e.g., +1234567890)
- **Verification Code**: Code sent to your Telegram app
- **Password**: Your 2FA password (if enabled)

### 3. Session File
After first run, a `userbot_session.session` file will be created. This stores your login session.

## How It Works

1. **User sends platform ID** → Main bot
2. **Main bot** → Sends to userbot
3. **Userbot** → Sends "Check ID: {platform_id}" to QuotexPartnerBot
4. **QuotexPartnerBot** → Responds with verification result
5. **Userbot** → Receives response and saves it
6. **Main bot** → Checks response and shows appropriate message to user

## Response Handling

### If QuotexPartnerBot responds: "Trader with ID = 'id' was not found."
- User sees: "حسابك غير مسجل معانا ❌ سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️"

### If QuotexPartnerBot responds with anything else:
- User sees: "حسابك مسجل معانا ✅ باقي خطوة اخير للدخول معانا في القروب المغلق..."

## Files Created
- `userbot_session.session` - Your Telegram session
- `pending_requests.json` - Pending verification requests
- `responses.json` - Responses from QuotexPartnerBot
- `registered_ids.json` - Registered platform IDs

## Running the Bot

### Recommended: Use the startup script
```bash
python start_bot.py
```

This script will:
1. Start the userbot in a separate thread
2. Wait for it to initialize
3. Start the main bot

### Alternative: Test userbot only
```bash
python test_userbot.py
```

### Direct run (for debugging)
```bash
python bot.py
```

## Troubleshooting

### If userbot fails to start:
1. Delete `userbot_session.session` file
2. Run the bot again and re-enter credentials

### If QuotexPartnerBot doesn't respond:
1. Check if the bot is working
2. Check the message format (should be "Check ID: {platform_id}")

### If responses are not processed:
1. Check `responses.json` file for saved responses
2. Check logs for any errors

## Security Notes
- The userbot uses your personal Telegram account
- Keep the session file secure
- Don't share your API credentials
- The userbot only communicates with QuotexPartnerBot

## API Credentials Used
- API ID: 22209395
- API Hash: 97e4178a45878fcd36052bf0b0b5b0a3
- These are already configured in the code
