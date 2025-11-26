# Telegram Bot - Arabic Chat Interface

A Python Telegram bot with Arabic interface that provides trading strategies and group access.

## Features

- `/start` command with welcome message in Arabic
- Interactive inline keyboard with 4 buttons:
  - 💎 الدخول الى قروب المغلق (Private Group Access)
  - 5 استراتيجيات مجانية (5 Free Strategies)
  - القروب العام (Public Group)
  - ⚙️ دعم القناة (Channel Support)

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

1. Open `bot.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token from BotFather

### 4. Run the Bot

```bash
python bot.py
```

## Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` command
3. The bot will display the welcome message with 4 interactive buttons
4. Click any button to see the corresponding response

## File Structure

```
tgreplay/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Customization

You can modify the messages and button responses in the `bot.py` file:

- `start_command()`: Welcome message and button layout
- `button_callback()`: Responses for each button click

## Notes

- Make sure to keep your bot token secure
- The bot supports Arabic text and RTL (Right-to-Left) text direction
- All messages use Markdown formatting for bold text
