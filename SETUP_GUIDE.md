# Bot Setup Guide

## How to Connect Your Bot to QuotexPartnerBot Group

### Step 1: Add Your Bot to the Partner Group
1. Go to the group where QuotexPartnerBot is an admin
2. Add your bot to the group
3. Make sure your bot has permission to send messages

### Step 2: Get the Group ID
1. Send `/get_chat_id` command to your bot in the partner group
2. Copy the Chat ID that the bot returns
3. Replace `YOUR_PARTNER_GROUP_ID` in the code with this ID

### Step 3: Test the Connection
1. Send `/join_partner` command to your bot
2. The bot will confirm if it can connect to the partner group

### Step 4: Update the Configuration
In `bot.py`, line 27, replace:
```python
PARTNER_GROUP_ID = "YOUR_PARTNER_GROUP_ID"
```
With the actual group ID you got from step 2.

## How It Works Now

1. **User sends platform ID** → Bot checks database
2. **If ID exists** → Shows "already registered" message  
3. **If ID is new** → Saves to database + sends message to partner group
4. **Partner group receives** → QuotexPartnerBot can see and verify the ID

## Admin Commands

- `/start` - Main menu
- `/quiz_stats` - View quiz statistics
- `/registered_ids` - View all registered platform IDs
- `/get_chat_id` - Get current chat ID (for setup)
- `/join_partner` - Test connection to partner group

## Database Files

- `quiz_data.json` - Stores quiz responses
- `registered_ids.json` - Stores platform IDs and user info

The bot now sends verification requests directly to the partner group instead of using API tokens!


