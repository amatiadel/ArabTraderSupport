import logging
import json
import os
import requests
import asyncio
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from userbot import start_userbot, stop_userbot, send_verification, get_verification_response

# Disable proxy for Telegram bot and requests
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('all_proxy', None)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - replace with your actual bot token
BOT_TOKEN = "7948819240:AAFHyTpDKr7-oVp6WNBrkgjZWn6TNzKtwsc"

# Partner bot configuration
PARTNER_BOT_USERNAME = "QuotexPartnerBot"
PARTNER_BOT_LINK = "https://t.me/QuotexPartnerBot?start=40711_baf509e8fccec7ed1d5d"
PARTNER_GROUP_ID = "YOUR_PARTNER_GROUP_ID"  # Optional: for direct group messaging if available

# Data files
QUIZ_DATA_FILE = "quiz_data.json"
REGISTERED_IDS_FILE = "registered_ids.json"
GROUP_ACCESS_FILE = "group_access.json"
NON_REGISTERED_IDS_FILE = "non_registered_ids.json"
ADMIN_POSTS_FILE = "admin_posts.json"
USER_DATA_FILE = "user_data.json"

def save_quiz_data(user_id, username, age, source, goal):
    """Save quiz data to JSON file"""
    try:
        # Load existing data
        if os.path.exists(QUIZ_DATA_FILE):
            with open(QUIZ_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Create new quiz entry
        quiz_entry = {
            "user_id": user_id,
            "username": username,
            "quiz_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "responses": {
                "age": age,
                "source": source,
                "goal": goal
            },
            "completed": True
        }
        
        # Add to data
        data.append(quiz_entry)
        
        # Save back to file
        with open(QUIZ_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Quiz data saved for user {user_id}")
        
    except Exception as e:
        print(f"Error saving quiz data: {e}")

def get_quiz_stats():
    """Get quiz statistics"""
    try:
        if os.path.exists(QUIZ_DATA_FILE):
            with open(QUIZ_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        return []
    except Exception as e:
        print(f"Error loading quiz data: {e}")
        return []

def has_user_completed_quiz(user_id):
    """Check if user has already completed the quiz"""
    try:
        data = get_quiz_stats()
        for entry in data:
            if entry['user_id'] == user_id and entry.get('completed', False):
                return True
        return False
    except Exception as e:
        print(f"Error checking quiz completion: {e}")
        return False

def mark_platform_id_as_used(platform_id, user_id):
    """Mark platform ID as used for group access"""
    try:
        if os.path.exists(QUIZ_DATA_FILE):
            with open(QUIZ_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Find user and mark platform ID as used
        for entry in data:
            if entry['user_id'] == user_id:
                entry['platform_id'] = platform_id
                entry['group_access_granted'] = True
                break
        
        # Save back to file
        with open(QUIZ_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Platform ID {platform_id} marked as used by user {user_id}")
        
    except Exception as e:
        print(f"Error marking platform ID as used: {e}")

# Database functions for registered platform IDs
def load_registered_ids():
    """Load registered platform IDs from database"""
    try:
        if os.path.exists(REGISTERED_IDS_FILE):
            with open(REGISTERED_IDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading registered IDs: {e}")
        return []

def save_registered_id(platform_id, user_id, username):
    """Save a new platform ID to the database"""
    try:
        registered_ids = load_registered_ids()
        
        # Check if ID already exists
        for entry in registered_ids:
            if entry['platform_id'] == platform_id:
                return False  # ID already exists
        
        # Add new ID
        new_entry = {
            "platform_id": platform_id,
            "user_id": user_id,
            "username": username,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "verified": True
        }
        
        registered_ids.append(new_entry)
        
        # Save back to file
        with open(REGISTERED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(registered_ids, f, ensure_ascii=False, indent=2)
            
        print(f"Platform ID {platform_id} saved for user {user_id}")
        return True
        
    except Exception as e:
        print(f"Error saving platform ID: {e}")
        return False

def is_platform_id_registered(platform_id):
    """Check if platform ID is already registered in our database"""
    try:
        registered_ids = load_registered_ids()
        for entry in registered_ids:
            if entry['platform_id'] == platform_id:
                return True
        return False
    except Exception as e:
        print(f"Error checking platform ID registration: {e}")
        return False

# Database functions for non-registered platform IDs
def load_non_registered_ids():
    """Load non-registered platform IDs from database"""
    try:
        if os.path.exists(NON_REGISTERED_IDS_FILE):
            with open(NON_REGISTERED_IDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading non-registered IDs: {e}")
        return []

def save_non_registered_id(platform_id, user_id, username):
    """Save a non-registered platform ID to the database"""
    try:
        non_registered_ids = load_non_registered_ids()
        
        # Check if ID already exists
        for entry in non_registered_ids:
            if entry['platform_id'] == platform_id:
                return False  # ID already exists
        
        # Add new ID
        new_entry = {
            "platform_id": platform_id,
            "user_id": user_id,
            "username": username,
            "rejection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rejected": True
        }
        
        non_registered_ids.append(new_entry)
        
        # Save back to file
        with open(NON_REGISTERED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(non_registered_ids, f, ensure_ascii=False, indent=2)
            
        print(f"Non-registered platform ID {platform_id} saved for user {user_id}")
        return True
        
    except Exception as e:
        print(f"Error saving non-registered platform ID: {e}")
        return False

def is_platform_id_non_registered(platform_id):
    """Check if platform ID is in non-registered database"""
    try:
        non_registered_ids = load_non_registered_ids()
        for entry in non_registered_ids:
            if entry['platform_id'] == platform_id:
                return True
        return False
    except Exception as e:
        print(f"Error checking non-registered platform ID: {e}")
        return False

# Group access database functions
def load_group_access():
    """Load group access records from database"""
    try:
        if os.path.exists(GROUP_ACCESS_FILE):
            with open(GROUP_ACCESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading group access: {e}")
        return []

def save_group_access(platform_id, user_id, username, group_link):
    """Save user who got group access"""
    try:
        group_access = load_group_access()
        
        # Check if already has access
        for entry in group_access:
            if entry['platform_id'] == platform_id:
                return False  # Already has access
        
        # Add new access record
        new_entry = {
            "platform_id": platform_id,
            "user_id": user_id,
            "username": username,
            "group_link": group_link,
            "access_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        group_access.append(new_entry)
        
        # Save back to file
        with open(GROUP_ACCESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(group_access, f, ensure_ascii=False, indent=2)
            
        print(f"Group access saved for platform ID {platform_id}")
        return True
        
    except Exception as e:
        print(f"Error saving group access: {e}")
        return False

# Admin post functions
def load_admin_posts():
    """Load admin posts from database"""
    try:
        if os.path.exists(ADMIN_POSTS_FILE):
            with open(ADMIN_POSTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading admin posts: {e}")
        return []

def save_admin_post(post_data):
    """Save admin post to database"""
    try:
        posts = load_admin_posts()
        posts.append(post_data)
        
        with open(ADMIN_POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
            
        print(f"Admin post saved: {post_data.get('title', 'Untitled')}")
        return True
        
    except Exception as e:
        print(f"Error saving admin post: {e}")
        return False

def load_user_data():
    """Load user data from database"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading user data: {e}")
        return []

def save_user_data(user_data):
    """Save user data to database"""
    try:
        users = load_user_data()
        
        # Check if user already exists
        user_exists = False
        for i, user in enumerate(users):
            if user['user_id'] == user_data['user_id']:
                users[i] = user_data
                user_exists = True
                break
        
        if not user_exists:
            users.append(user_data)
        
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
            
        print(f"User data saved for user {user_data['user_id']}")
        return True
        
    except Exception as e:
        print(f"Error saving user data: {e}")
        return False

def get_all_user_ids():
    """Get all user IDs from various sources"""
    user_ids = set()
    
    # From quiz data
    quiz_data = get_quiz_stats()
    for entry in quiz_data:
        user_ids.add(entry['user_id'])
    
    # From registered IDs
    registered_ids = load_registered_ids()
    for entry in registered_ids:
        user_ids.add(entry['user_id'])
    
    # From group access
    group_access = load_group_access()
    for entry in group_access:
        user_ids.add(entry['user_id'])
    
    # From non-registered IDs
    non_registered_ids = load_non_registered_ids()
    for entry in non_registered_ids:
        user_ids.add(entry['user_id'])
    
    return list(user_ids)

def create_post_buttons(buttons_data):
    """Create inline keyboard from buttons data"""
    if not buttons_data:
        return None
    
    keyboard = []
    for button in buttons_data:
        if button.get('type') == 'url':
            url = button['url']
            # Handle Telegram usernames
            if url.startswith('@'):
                # Convert @username to proper Telegram link
                url = f"https://t.me/{url[1:]}"
            elif not url.startswith(('http://', 'https://', 'tg://')):
                # If it's not a proper URL, assume it's a username and add https://t.me/
                if not url.startswith('@'):
                    url = f"https://t.me/{url}"
                else:
                    url = f"https://t.me/{url[1:]}"
            
            keyboard.append([InlineKeyboardButton(
                button['text'], 
                url=url
            )])
        elif button.get('type') == 'callback':
            keyboard.append([InlineKeyboardButton(
                button['text'], 
                callback_data=button['callback_data']
            )])
        elif button.get('type') == 'web_app':
            keyboard.append([InlineKeyboardButton(
                button['text'], 
                web_app={"url": button['url']}
            )])
    
    return InlineKeyboardMarkup(keyboard) if keyboard else None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    
    # Welcome message in Arabic
    welcome_message = "اهلا وسهلا 💛\n\nهنا تقدر تتحصل على استراتيجيات مجانية و كمان فرصة دخول للقروب المغلق"
    
    # Create inline keyboard with 4 buttons
    keyboard = [
        [InlineKeyboardButton("💎 الدخول الى قروب المغلق", callback_data="private_group")],
        [InlineKeyboardButton("🎁 5 استراتيجيات مجانية", callback_data="free_strategies")],
        [InlineKeyboardButton("💫 القروب العام", url="https://t.me/arabtrader7")],
        [InlineKeyboardButton("⚙️ دعم القناة", callback_data="support_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message
    await update.message.reply_text(
        f"{welcome_message}",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "private_group":
        # Create keyboard with 2 buttons
        keyboard = [
            [InlineKeyboardButton("💵 اشتراك مجاني", callback_data="free_entry")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """وش بنلقى داخل القروب؟ 👇

💎 صفقات المستقبلية: كل يوم نرسل صفقات دقيقة على ساعة 10:00 صبح بتوقيت السعودية، ما تحتاج تتابع السوق 24 ساعة، احنا نتابع عنك 😉

📅 تحديثات يومية: جدول التداول يتحدث يومياً، تعرف متى تدخل ومتى تطلع بدون لخبطه أو تخمين.

📰 تحليل الأخبار: ما نخليك تمشي عالعمياني، نغطي أهم أخبار السوق ونوضح تأثيرها على الصفقات.

🏆 استراتيجيات جاهزة: مثلاً عندنا خطة تداول بـ 100 دولار نوريك كيف تكبر راس مالك بخطوات بسيطة وواضحة.

🔥 شرح كامل لطريقة التداول: حتى لو ما عندك خبرة، نشرح لك خطوة بخطوة كيف تستخدم الإشارات وتنفذها بنفسك.

⚙️ بوت تداول: إذا استصعبت شيء أو احتجت توجيه، احنا معك دايم في الخاص أو داخل القروب.""",
            reply_markup=reply_markup
        )
    elif query.data == "free_strategies":
        user = update.effective_user
        
        # Check if user already completed the quiz
        if has_user_completed_quiz(user.id):
            # User already completed quiz - show strategies directly
            keyboard = [
                [InlineKeyboardButton("Candlestick Patterns", callback_data="strategy_1")],
                [InlineKeyboardButton("Keltner Channel", callback_data="strategy_2")],
                [InlineKeyboardButton("Fractal Breakout", callback_data="strategy_3")],
                [InlineKeyboardButton("Inside Bar", callback_data="strategy_4")],
                [InlineKeyboardButton("Triple Confirmation", callback_data="strategy_5")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Delete current message and any parent messages (PDF files)
            try:
                # Delete current message (image+text+buttons)
                await query.message.delete()
                
                # If current message was a reply, also delete the parent message (PDF)
                if query.message.reply_to_message:
                    await context.bot.delete_message(
                        chat_id=query.message.chat_id,
                        message_id=query.message.reply_to_message.message_id
                    )
            except Exception as e:
                logger.warning(f"Failed to delete messages: {e}")
            
            # Send new strategy menu
            try:
                img_path = os.path.join('img', 'main.png')
                with open(img_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption="قدامك كل الاستراتيجيات لي عندك ، اختار اللي تبغاه وابدأ فوراً ✨",
                        reply_markup=reply_markup
                    )
            except FileNotFoundError:
                # If image not found, send text message
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="قدامك كل الاستراتيجيات لي عندك ، اختار اللي تبغاه وابدأ فوراً ✨",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        else:
            # User hasn't completed quiz - show introduction
            keyboard = [
                [InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "جهزنا لك 5 استراتيجيات قوية مجانا 🤩\n\n"
                "راح تساعدك على رفع مستواك في التداول .\n"
                "بتصير متاحة لك مباشرة بعد ما تخلص هذا الاختبار القصير.",
                reply_markup=reply_markup
            )
    elif query.data == "start_quiz":
        # Question 1: Age
        keyboard = [
            [InlineKeyboardButton("18–24", callback_data="age_18_24")],
            [InlineKeyboardButton("25–35", callback_data="age_25_35")],
            [InlineKeyboardButton("36+", callback_data="age_36_plus")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "3/1 كم عمرك ؟",
            reply_markup=reply_markup
        )
    elif query.data.startswith("age_"):
        # Store age response and show question 2
        context.user_data['quiz_age'] = query.data
        
        keyboard = [
            [InlineKeyboardButton("اليوتوب", callback_data="source_youtube")],
            [InlineKeyboardButton("انستقرام", callback_data="source_instagram")],
            [InlineKeyboardButton("اعلان", callback_data="source_ad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "3/2 كيف تعرفت على قروبنا خاص بتداول ؟",
            reply_markup=reply_markup
        )
    elif query.data.startswith("source_"):
        # Store source response and show question 3
        context.user_data['quiz_source'] = query.data
        
        keyboard = [
            [InlineKeyboardButton("💰 دخل إضافي", callback_data="goal_income")],
            [InlineKeyboardButton("🕊️ حرية مالية", callback_data="goal_freedom")],
            [InlineKeyboardButton("📚 تعلم التداول", callback_data="goal_learn")],
            [InlineKeyboardButton("📈 تنمية رأس المال", callback_data="goal_capital")],
            [InlineKeyboardButton("🎯 هدف شخصي", callback_data="goal_personal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "3/3 شو هو هدفك من التداول معنا ؟",
            reply_markup=reply_markup
        )
    elif query.data.startswith("goal_"):
        # Quiz completed - save data and show strategies
        user = update.effective_user
        
        # Get stored quiz responses
        age_response = context.user_data.get('quiz_age', 'unknown')
        source_response = context.user_data.get('quiz_source', 'unknown')
        goal_response = query.data.replace('goal_', '')
        
        # Map responses to readable format
        age_map = {
            'age_18_24': '18-24',
            'age_25_35': '25-35', 
            'age_36_plus': '36+'
        }
        source_map = {
            'source_youtube': 'youtube',
            'source_instagram': 'instagram',
            'source_ad': 'advertisement'
        }
        goal_map = {
            'goal_income': 'additional_income',
            'goal_freedom': 'financial_freedom',
            'goal_learn': 'learn_trading',
            'goal_capital': 'capital_growth',
            'goal_personal': 'personal_goal'
        }
        
        # Save quiz data
        save_quiz_data(
            user_id=user.id,
            username=user.username or f"user_{user.id}",
            age=age_map.get(age_response, age_response),
            source=source_map.get(source_response, source_response),
            goal=goal_map.get(goal_response, goal_response)
        )
        
        # Clear stored quiz data
        context.user_data.pop('quiz_age', None)
        context.user_data.pop('quiz_source', None)
        
        keyboard = [
            [InlineKeyboardButton("Candlestick Patterns", callback_data="strategy_1")],
            [InlineKeyboardButton("Keltner Channel", callback_data="strategy_2")],
            [InlineKeyboardButton("Fractal Breakout", callback_data="strategy_3")],
            [InlineKeyboardButton("Inside Bar", callback_data="strategy_4")],
            [InlineKeyboardButton("Triple Confirmation", callback_data="strategy_5")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send image with message
        try:
            img_path = os.path.join('img', 'main.png')
            with open(img_path, 'rb') as photo:
                # Delete the text message and send photo
                await query.message.delete()
                await query.message.reply_photo(
                    photo=photo,
                    caption=" شكراً على إجاباتك! 🎉\n\nتفضل هديتك 5 استراتيجيات قوية مجانا\nاختيار اللي تبغاه وابدأ فوراً ✨",
                    reply_markup=reply_markup
                )
        except FileNotFoundError:
            # If image not found, send text message
            await query.edit_message_text(
                "شكراً على إجاباتك! 🎉\n\n"
                "تفضل هديتك 5 استراتيجيات قوية مجانا .\n"
                "اختيار اللي تبغاه وابدأ فوراً ✨",
                reply_markup=reply_markup
            )
    elif query.data.startswith("strategy_"):
        # Handle individual strategy selection
        strategy_num = query.data.split("_")[1]
        
        # Define strategy-specific text messages
        strategy_texts = {
            "1": """1️⃣ استراتيجية الجنود الثلاثة والغربان الثلاثة

تسهل عليك ملاحظة لحظات الاستسلام عند المشترين أو البائعين وبداية اتجاه جديد.

🎯 ليش تعتبر قوية؟
• تكشف بداية ترند قبل ما ينتشر
• مثالية لنقاط الانعكاس
• تعطيك ثقة بدخولك

🕊 استخدمها لما:
• تكون عند دعم/مقاومة واضحة
• ما فيه شموع ذيولها طويلة
• تبغى دخول مباشر بعد إغلاق شمعة ثالثة""",
            
            "2": """2️⃣ استراتيجية ارتداد القناة – Keltner Channel

مجموعة خطوات بسيطة تساعدك تدخل صفقات مرتدة من مناطق قوية، بدون ما تطارد السوق أو تتوتر.

🎯 وش بتفيدك فيه؟
• تعطيك نقاط دخول واضحة عند الأطراف
• تخفّف من الصفقات العشوائية
• تناسب السوق يوم يكون فيه تصحيحات خفيفة

🕊 استخدمها إذا:
• تشوف شموع تطلع برا القناة ثم ترجع داخلها
• السوق مو ترند قوي ولا متذبذب بقوة
• تبي دخول سريع وخروج أسرع""",
            
            "3": """3️⃣ استراتيجية كسر الفراكتل – Fractal Breakout

تعتمد على كسر قمم وقيعان واضحة لأخذ فرص مع الترند بدون تعقيد.

🎯 وش تضمن لك؟
• تجاهل الفوضى والتركيز على القمم الحقيقية
• تأكيد ممتاز باستخدام EMA
• تناسب سكالبينغ الفريمات الصغيرة

🕊 ممتازة إذا:
• تنتظر إغلاق شمعة بعد الكسر
• السوق يمشي بترند لطيف
• تتجنب الشموع الكبيرة جدًا""",
            
            "4": """4️⃣ استراتيجية داخل الشمعة – Inside Bar Breakout

طريقة تركّز على فترة تجمّع السعر قبل ما ينفجر بقوة للاتجاه الصحيح.

🎯 وش بتعطيك؟
• دخول على بداية حركة قوية
• إدارة مخاطرة سهلة (حدود الشمعة الأم)
• فلترة ممتازة بالدعم والمقاومة

🕊 مناسبة إذا:
• تشوف شمعة أم كبيرة وبعدها 1–3 شموع صغيرة
• تنتظر كسر حقيقي مو حركة كاذبة
• تحب الصفقات السريعة والواضحة""",
            
            "5": """5️⃣ استراتيجية التأكيد الثلاثي – Triple Confirmation

أسلوب يعتمد 3 تأكيدات على الاتجاه، يخليك تدخل مرتاح بدون خوف من الانعكاسات.

🎯 مميزاتها:
• نسبة نجاح أعلى في الترند الواضح
• تمنعك من الصفقات العكسية
• مثالية لفترة تداخل الجلسات

🕊 تشتغل أفضل لما:
• كل SuperTrend نفس اللون
• شموع Heikin Ashi قوية
• انت ملتزم بالترند والمناطق"""
        }
        
        # Get the text message for this strategy
        text_message = strategy_texts.get(strategy_num, "استراتيجية غير محددة")
        
        # Map strategy number to PDF and image filenames
        strategy_files = {
            "1": {
                "pdf": "Candlestick Patterns.pdf",
                "image": "Candlestick Patterns.png"
            },
            "2": {
                "pdf": "Keltner Channel.pdf", 
                "image": "Keltner Channel.png"
            },
            "3": {
                "pdf": "Fractal Breakout.pdf",
                "image": "Fractal Breakout.png"
            },
            "4": {
                "pdf": "Inside Bar.pdf",
                "image": "Inside Bar.png"
            },
            "5": {
                "pdf": "TRIPLE CONFIRMATION.pdf",
                "image": "TRIPLE CONFIRMATION.png"
            }
        }
        
        # Get the files for this strategy
        strategy_data = strategy_files.get(strategy_num, {"pdf": "main.pdf", "image": "main.png"})
        pdf_filename = strategy_data["pdf"]
        image_filename = strategy_data["image"]
        
        # Create keyboard with two buttons
        keyboard = [
            [InlineKeyboardButton("⚙️قائمة الاستراتيجيات", callback_data="free_strategies")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Delete the strategy menu message first
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Failed to delete strategy menu message: {e}")
        
        # First, send the PDF file
        pdf_message = None
        try:
            pdf_path = os.path.join('doc', pdf_filename)
            with open(pdf_path, 'rb') as pdf_file:
                # Send PDF as document
                pdf_message = await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=pdf_file,
                    filename=pdf_filename
                )
        except FileNotFoundError:
            logger.warning(f"PDF file not found: {pdf_path}")
        
        # Then, send image with text as reply to the PDF
        if pdf_message:
            try:
                img_path = os.path.join('img', image_filename)
                with open(img_path, 'rb') as photo:
                    # Send photo as reply to the PDF message
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=text_message,
                        reply_markup=reply_markup,
                        reply_to_message_id=pdf_message.message_id
                    )
            except FileNotFoundError:
                # If image not found, send text message as reply
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    reply_to_message_id=pdf_message.message_id
                )
        else:
            # If PDF sending failed, send image and text as regular message
            try:
                img_path = os.path.join('img', image_filename)
                with open(img_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=text_message,
                        reply_markup=reply_markup
                    )
            except FileNotFoundError:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text_message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
    elif query.data == "support_channel":
        # Create keyboard with main menu button
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ دعم القناة\n\n"
            "تواصل مع الادمين ، راح نحاول نساعدك بكل سرور.\n\n"
            "[الادمين](https://t.me/MrTarekSupport)",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif query.data == "main_menu":
        # Return to main menu (same as start command)
        welcome_message = "اهلا وسهلا 💛\n\nهنا تقدر تتحصل على استراتيجيات مجانية و كمان فرصة دخول للقروب المغلق"
        
        # Create inline keyboard with 4 buttons
        keyboard = [
            [InlineKeyboardButton("💎 الدخول الى قروب المغلق", callback_data="private_group")],
            [InlineKeyboardButton("🎁 5 استراتيجيات مجانية", callback_data="free_strategies")],
            [InlineKeyboardButton("💫 القروب العام", url="https://t.me/arabtrader7")],
            [InlineKeyboardButton("⚙️ دعم القناة", callback_data="support_channel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Delete current message and any parent messages (PDF files)
        try:
            # Delete current message (image+text+buttons or any other message)
            await query.message.delete()
            
            # If current message was a reply, also delete the parent message (PDF)
            if query.message.reply_to_message:
                await context.bot.delete_message(
                    chat_id=query.message.chat_id,
                    message_id=query.message.reply_to_message.message_id
                )
        except Exception as e:
            logger.warning(f"Failed to delete messages: {e}")
        
        # Send new main menu
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"{welcome_message}",
            reply_markup=reply_markup
        )
    elif query.data == "free_entry":
        # Create keyboard with 4 buttons
        keyboard = [
            [InlineKeyboardButton("🔥 رابط المنصة", web_app={"url": "https://broker-qx.pro/?lid=1616934"})],
            [InlineKeyboardButton("🎥 فيديو عن طريقة التسجيل في المنصة", url="https://youtu.be/3GE2wwxMVyQ")],
            [InlineKeyboardButton("✅ تم التسجيل", callback_data="registration_complete")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على \"تم التسجيل ✅ \" فقط بعد ماتسجل في المنصة""",
            reply_markup=reply_markup
        )
    elif query.data == "paid_entry":
        # Nothing happens for paid entry as requested
        await query.answer("هذه الميزة غير متاحة حالياً", show_alert=True)
    elif query.data == "registration_complete":
        # Handle registration complete
        keyboard = [
            [InlineKeyboardButton("🔥 رابط المنصة", web_app={"url": "https://broker-qx.pro/?lid=1616934"})],
            [InlineKeyboardButton("↩️ عودة للخلف", callback_data="back_to_registration")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send image with message
        try:
            img_path = os.path.join('img', 'Id example.png')
            with open(img_path, 'rb') as photo:
                sent_message = await query.edit_message_media(
                    media=InputMediaPhoto(photo, caption="🔥 بعد التسجيل راح تتحصل على ID خاص بحسابك . ابعث ايدي هنا على شكل \"69482551\""),
                    reply_markup=reply_markup
                )
        except FileNotFoundError:
            # If image not found, send text message
            sent_message = await query.edit_message_text(
                "🔥 بعد التسجيل راح تتحصل على ID خاص بحسابك . ابعث ايدي هنا على شكل \"69482551\"",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        # Store the message ID for later deletion
        context.user_data['id_request_message_id'] = sent_message.message_id
    elif query.data == "back_to_registration":
        # Handle back to registration button
        keyboard = [
            [InlineKeyboardButton("🔥 رابط المنصة", web_app={"url": "https://broker-qx.pro/?lid=1616934"})],
            [InlineKeyboardButton("🎥 فيديو عن طريقة التسجيل في المنصة", url="https://youtu.be/3GE2wwxMVyQ")],
            [InlineKeyboardButton("✅ تم التسجيل", callback_data="registration_complete")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Check if current message is a photo
        if query.message.photo:
            # Message is a photo - delete it and send a new text message
            try:
                await query.message.delete()
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على \"تم التسجيل ✅ \" فقط بعد ماتسجل في المنصة""",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.warning(f"Failed to delete photo and send text: {e}")
        else:
            # Message is text, edit normally
            await query.edit_message_text(
                """سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على \"تم التسجيل ✅ \" فقط بعد ماتسجل في المنصة""",
                reply_markup=reply_markup
            )
    elif query.data == "find_id":
        # Handle find ID button
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔍 وين الاقي الايدي\n\n"
            "يمكنك العثور على الايدي الخاص بك في:\n"
            "1. صفحة الملف الشخصي في المنصة\n"
            "2. إعدادات الحساب\n"
            "3. أو في رسالة التأكيد التي وصلتك",
            reply_markup=reply_markup
        )
    elif query.data == "try_again":
        # Handle try again button - return to registration flow
        keyboard = [
            [InlineKeyboardButton("🔥 رابط المنصة", web_app={"url": "https://broker-qx.pro/?lid=1616934"})],
            [InlineKeyboardButton("🎥 فيديو عن طريقة التسجيل في المنصة", url="https://youtu.be/3GE2wwxMVyQ")],
            [InlineKeyboardButton("✅ تم التسجيل", callback_data="registration_complete")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على \"تم التسجيل ✅ \" فقط بعد ماتسجل في المنصة""",
            reply_markup=reply_markup
        )
    elif query.data == "account_charged":
        # Handle account charged button
        user = update.effective_user
        
        # Get the platform ID from user data (stored when they entered it)
        platform_id = context.user_data.get('platform_id', 'unknown')
        
        # Check if this is a test ID (bypass balance check)
        registered_ids = load_registered_ids()
        is_test_id = False
        for entry in registered_ids:
            if entry['platform_id'] == platform_id and entry.get('test_id', False):
                is_test_id = True
                break
        
        # Re-check balance by sending request to QuotexPartnerBot
        username = user.username or f"user_{user.id}"
        
        # For test IDs, skip balance check and go straight to link
        if is_test_id:
            # Save group access
            # Generate one-time invite link for private group
            try:
                # Create invite link that can be used once (bot must be admin in the private group)
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=-4762854142,  # Replace with your actual private group ID (negative number)
                    expire_date=None,  # No expiration
                    member_limit=1,  # Can only be used once
                    name="Private Group Access"
                )
                group_link = invite_link.invite_link
            except Exception as e:
                # Fallback if group link creation fails
                group_link = "https://t.me/your_private_group"  # Replace with your actual group link
            
            # Save group access to database
            save_group_access(platform_id, user.id, username, group_link)
            
            # Mark platform ID as used (for old functionality)
            mark_platform_id_as_used(platform_id, user.id)
            
            keyboard = [
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "ممتاز 🤩 لقد قمت بتطبيق كل خطوات بنجاح ✅\n\n"
                f"رابط القروب المغلق : {group_link}\n\n"
                "نتمنى لك التوفيق و نجاح معانا 💖",
                reply_markup=reply_markup
            )
            return
        
        verification_sent = send_verification(platform_id, user.id, username)
        
        if verification_sent:
            # Wait for response
            await asyncio.sleep(3)
            
            # Get response from userbot
            response = get_verification_response(platform_id)
            
            if response and 'balance' in response:
                balance = response['balance']
                
                if balance >= 30.0:
                    # Balance is sufficient - generate invite link
                    # Save group access
                    username = user.username or f"user_{user.id}"
                    
                    # Generate one-time invite link for private group
                    try:
                        # Create invite link that can be used once (bot must be admin in the private group)
                        invite_link = await context.bot.create_chat_invite_link(
                            chat_id=-4762854142,  # Replace with your actual private group ID (negative number)
                            expire_date=None,  # No expiration
                            member_limit=1,  # Can only be used once
                            name="Private Group Access"
                        )
                        group_link = invite_link.invite_link
                    except Exception as e:
                        # Fallback if group link creation fails
                        group_link = "https://t.me/your_private_group"  # Replace with your actual group link
                    
                    # Save group access to database
                    save_group_access(platform_id, user.id, username, group_link)
                    
                    # Mark platform ID as used (for old functionality)
                    mark_platform_id_as_used(platform_id, user.id)
                    
                    keyboard = [
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        "ممتاز 🤩 لقد قمت بتطبيق كل خطوات بنجاح ✅\n\n"
                        f"رابط القروب المغلق : {group_link}\n\n"
                        "نتمنى لك التوفيق و نجاح معانا 💖",
                        reply_markup=reply_markup
                    )
                else:
                    # Balance is insufficient
                    keyboard = [
                        [InlineKeyboardButton("✅ تم شحن حسابي", callback_data="account_charged")],
                        [InlineKeyboardButton("⚙️ دعم القناة", callback_data="support_channel")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        "حسابك غير مشحون للاسف بالمبلغ المحدد ❗\n\n"
                        "حاول تشحنها على اقل ب 30 دولار . هذا اقل مبلغ تقدر تبدا معنا فيه واكيد كل مبلغ اكبر كل مبلغ احسن .\n\n"
                        "بعد ماتشحن حسابك اضغط \"تم شحن حسابك\" و راح يوصلك رابط دعوة للقروب المغلق\n\n"
                        "⚡ اضغط على \"تم شحن الحساب\" فقط بعد ماتشحن حسابك",
                        reply_markup=reply_markup
                    )
            else:
                # No response found - show error
                keyboard = [
                    [InlineKeyboardButton("🔁 محاولة مرة ثانية", callback_data="try_again")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "حدث خطأ في التحقق من الرصيد ❌\n\n"
                    "حاول مرة ثانية",
                    reply_markup=reply_markup
                )
        else:
            # Verification sending failed
            keyboard = [
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "حدث خطأ في التحقق من الرصيد ❌\n\n"
                "حاول مرة ثانية",
                reply_markup=reply_markup
            )
    elif query.data.startswith("check_response_"):
        # Handle check response button
        platform_id = query.data.replace("check_response_", "")
        
        # Check for response
        response = get_verification_response(platform_id)
        
        if response:
            # Process response
            if "was not found" in response["response"]:
                # ID not found - save to non-registered database and show registration message
                user = update.effective_user
                username = user.username or f"user_{user.id}"
                save_non_registered_id(platform_id, user.id, username)
                
                keyboard = [
                    [InlineKeyboardButton("🔁 محاولة مرة ثانية", callback_data="try_again")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    """حسابك غير مسجل معانا ❌

سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على "تم التسجيل ✅ " فقط بعد ماتسجل في المنصة""",
                    reply_markup=reply_markup
                )
            else:
                # ID found - save to database and show charging message
                user = update.effective_user
                username = user.username or f"user_{user.id}"
                save_registered_id(platform_id, user.id, username)
                
                keyboard = [
                    [InlineKeyboardButton("✅ تم شحن حسابي", callback_data="account_charged")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "حسابك مسجل معانا ✅\n\n"
                    "باقي خطوة اخير للدخول معانا في القروب المغلق .\n\n"
                    "لازم تشحن حسابك على اقل ب 30 دولار . هذا اقل مبلغ تقدر تبدا معنا فيه و اكيد كل مكان اكبر كل مكان احسن .\n\n"
                    "بعد ماتشحن حسابك اضغط \"تم شحن حسابك\" و راح يوصلك رابط دعوة للقروب المغلق",
                    reply_markup=reply_markup
                )
        else:
            # Still no response - show waiting message
            keyboard = [
                [InlineKeyboardButton("🔄 تحقق مرة أخرى", callback_data=f"check_response_{platform_id}")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "جاري التحقق من الايدي... ⏳\n\n"
                "انتظر لحظة ثم اضغط \"تحقق مرة أخرى\"",
                reply_markup=reply_markup
            )
    elif query.data == "add_button":
        await add_button_command(update, context)
    elif query.data.startswith("button_type_"):
        await handle_button_type_selection(update, context)
    elif query.data == "preview_post":
        await preview_post_callback(update, context)
    elif query.data == "confirm_post_send":
        await confirm_post_send_callback(update, context)
    elif query.data == "cancel_post_creation":
        await cancel_post_creation_callback(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages from users"""
    user = update.effective_user
    
    # Only process platform ID verification in private chats with the bot
    if update.effective_chat.type != 'private':
        return  # Ignore messages in groups/channels
    
    # Handle post creation messages
    if context.user_data.get('creating_post', False):
        if context.user_data.get('current_button_type'):
            await handle_button_data(update, context)
        else:
            await handle_post_creation(update, context)
        return
    
    # Handle regular text messages (platform ID verification)
    if update.message.text:
        message_text = update.message.text.strip()
        
        # Check if message contains only numbers (platform ID)
        if message_text.isdigit():
            # Store the platform ID for later use
            context.user_data['platform_id'] = message_text
            
            # Delete the ID request message to clean up the conversation
            try:
                if 'id_request_message_id' in context.user_data:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['id_request_message_id']
                    )
                    # Clear the stored message ID
                    del context.user_data['id_request_message_id']
            except:
                pass  # Continue even if deletion fails
            
            # Delete error message if it exists
            try:
                if 'error_message_id' in context.user_data:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['error_message_id']
                    )
                    # Clear the stored error message ID
                    del context.user_data['error_message_id']
            except:
                pass  # Continue even if deletion fails
            
            # Check if this platform ID is already registered in our database
            if is_platform_id_registered(message_text):
                # ID already registered - skip verification and show charging message
                keyboard = [
                    [InlineKeyboardButton("✅ تم شحن حسابي", callback_data="account_charged")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "حسابك مسجل معانا ✅\n\n"
                    "باقي خطوة اخير للدخول معانا في القروب المغلق .\n\n"
                    "لازم تشحن حسابك على اقل ب 30 دولار . هذا اقل مبلغ تقدر تبدا معنا فيه واكيد كل مكان اكبر كل مكان احسن .\n\n"
                    "بعد ماتشحن حسابك اضغط \"تم شحن حسابك\" و راح يوصلك رابط دعوة للقروب المغلق",
                    reply_markup=reply_markup
                )
            elif is_platform_id_non_registered(message_text):
                # ID is in non-registered database - show registration message without contacting userbot
                keyboard = [
                    [InlineKeyboardButton("🔁 محاولة مرة ثانية", callback_data="try_again")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    """حسابك غير مسجل معانا ❌

سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على "تم التسجيل ✅ " فقط بعد ماتسجل في المنصة""",
                    reply_markup=reply_markup
                )
            else:
                # ID not in our database - send to userbot for verification
                username = user.username or f"user_{user.id}"
                
                # Send verification request to QuotexPartnerBot via userbot
                verification_sent = send_verification(message_text, user.id, username)
                
                if verification_sent:
                    # Wait a moment for response
                    await asyncio.sleep(2)
                    
                    # Check for response
                    response = get_verification_response(message_text)
                    
                    if response:
                        # Process response
                        if "was not found" in response["response"]:
                            # ID not found - save to non-registered database and show registration message
                            save_non_registered_id(message_text, user.id, username)
                            
                            keyboard = [
                                [InlineKeyboardButton("🔁 محاولة مرة ثانية", callback_data="try_again")],
                                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            await update.message.reply_text(
                                """حسابك غير مسجل معانا ❌

سجل من رابط المنصة الخاصة بنا عن طريق رابط تحت ⬇️


🔓 اضغط على "تم التسجيل ✅ " فقط بعد ماتسجل في المنصة""",
                                reply_markup=reply_markup
                            )
                        else:
                            # ID found - save to database and show charging message
                            save_registered_id(message_text, user.id, username)
                            
                            keyboard = [
                                [InlineKeyboardButton("✅ تم شحن حسابي", callback_data="account_charged")],
                                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            await update.message.reply_text(
                                "حسابك مسجل معانا ✅\n\n"
                                "باقي خطوة اخير للدخول معانا في القروب المغلق .\n\n"
                                "لازم تشحن حسابك على اقل ب 30 دولار . هذا اقل مبلغ تقدر تبدا معنا فيه واكيد كل مكان اكبر كل مكان احسن .\n\n"
                                "بعد ماتشحن حسابك اضغط \"تم شحن حسابك\" و راح يوصلك رابط دعوة للقروب المغلق",
                                reply_markup=reply_markup
                            )
                    else:
                        # No response yet - show waiting message
                        keyboard = [
                            [InlineKeyboardButton("🔄 تحقق مرة أخرى", callback_data=f"check_response_{message_text}")],
                            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            "جاري التحقق من الايدي... ⏳\n\n"
                            "انتظر لحظة ثم اضغط \"تحقق مرة أخرى\"",
                            reply_markup=reply_markup
                        )
                else:
                    # Failed to send verification - show error message
                    keyboard = [
                        [InlineKeyboardButton("🔁 محاولة مرة ثانية", callback_data="try_again")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "حدث خطأ في التحقق من الايدي ❌\n\n"
                        "حاول مرة ثانية او تواصل مع دعم القناة",
                        reply_markup=reply_markup
                    )
        else:
            # User sent text instead of numbers - show error message and store it
            keyboard = [
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            error_message = await update.message.reply_text(
                "❌ خطأ في كتابة الايدي\n\n"
                "اكتب الايدي بشكل صحيح (أرقام فقط) على شكل \"123456789\"\n\n"
                "مثال: 64827386",
                reply_markup=reply_markup
            )
            
            # Store error message ID to delete it later
            context.user_data['error_message_id'] = error_message.message_id

async def quiz_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view quiz statistics"""
    # Check if user is admin (you can add your user ID here)
    admin_ids = [5878017415]  # Replace with your actual user ID
    
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ هذا الأمر متاح للإدارة فقط")
        return
    
    try:
        data = get_quiz_stats()
        
        if not data:
            await update.message.reply_text("📊 لا توجد بيانات متاحة حالياً")
            return
        
        # Calculate statistics
        total_users = len(data)
        
        # Age distribution
        age_counts = {}
        source_counts = {}
        goal_counts = {}
        
        for entry in data:
            age = entry['responses']['age']
            source = entry['responses']['source']
            goal = entry['responses']['goal']
            
            age_counts[age] = age_counts.get(age, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            goal_counts[goal] = goal_counts.get(goal, 0) + 1
        
        # Create statistics message
        stats_message = f"📊 إحصائيات الاختبار\n\n"
        stats_message += f"👥 إجمالي المستخدمين: {total_users}\n\n"
        
        stats_message += f"📅 توزيع الأعمار:\n"
        for age, count in age_counts.items():
            stats_message += f"• {age}: {count}\n"
        
        stats_message += f"\n📱 مصادر الوصول:\n"
        for source, count in source_counts.items():
            stats_message += f"• {source}: {count}\n"
        
        stats_message += f"\n🎯 الأهداف:\n"
        for goal, count in goal_counts.items():
            stats_message += f"• {goal}: {count}\n"
        
        await update.message.reply_text(stats_message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الإحصائيات: {e}")
        
async def registered_ids_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view registered platform IDs"""
    # Check if user is admin (you can add your user ID here)
    admin_ids = [5878017415]  # Replace with your actual user ID
    
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ هذا الأمر متاح للإدارة فقط")
        return
    
    try:
        registered_ids = load_registered_ids()
        
        if not registered_ids:
            await update.message.reply_text("📊 لا توجد ايديات مسجلة حالياً")
            return
        
        # Create message with registered IDs
        message = f"📊 الأيديات المسجلة ({len(registered_ids)})\n\n"
        
        for i, entry in enumerate(registered_ids, 1):
            message += f"{i}. Platform ID: `{entry['platform_id']}`\n"
            message += f"   User: @{entry['username']} (ID: {entry['user_id']})\n"
            message += f"   Date: {entry['registration_date']}\n"
            message += f"   Verified: {'✅' if entry['verified'] else '❌'}\n\n"
        
        # Split message if too long
        if len(message) > 4000:
            # Send in chunks
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الأيديات المسجلة: {e}")

async def create_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to create a new post"""
    # Check if user is admin
    admin_ids = [5878017415]  # Replace with your actual user ID
    
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ هذا الأمر متاح للإدارة فقط")
        return
    
    # Initialize post creation state
    context.user_data['creating_post'] = True
    context.user_data['post_data'] = {
        'content': '',
        'buttons': [],
        'image': None,
        'created_by': update.effective_user.id,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    keyboard = [
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📝 إنشاء منشور جديد\n\n"
        "أرسل محتوى المنشور (يمكنك إرسال نص أو صورة مع نص):",
        reply_markup=reply_markup
    )

async def handle_post_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle post creation messages"""
    if not context.user_data.get('creating_post', False):
        return
    
    post_data = context.user_data.get('post_data', {})
    
    # Handle image messages
    if update.message.photo:
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        post_data['image'] = photo.file_id
        post_data['content'] = update.message.caption or ""
        context.user_data['post_data'] = post_data
        
        keyboard = [
            [InlineKeyboardButton("➕ إضافة زر", callback_data="add_button")],
            [InlineKeyboardButton("👁️ معاينة المنشور", callback_data="preview_post")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ تم حفظ الصورة والمحتوى\n\n"
            "يمكنك الآن إضافة أزرار أو معاينة المنشور",
            reply_markup=reply_markup
        )
    elif update.message.text:
        # Handle text messages
        message_text = update.message.text.strip()
        
        if not post_data.get('content'):
            # Set content
            post_data['content'] = message_text
            context.user_data['post_data'] = post_data
            
            keyboard = [
                [InlineKeyboardButton("➕ إضافة زر", callback_data="add_button")],
                [InlineKeyboardButton("👁️ معاينة المنشور", callback_data="preview_post")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ تم حفظ المحتوى\n\n"
                "يمكنك الآن إضافة أزرار أو معاينة المنشور",
                reply_markup=reply_markup
            )

async def add_button_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add button callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_button":
        keyboard = [
            [InlineKeyboardButton("🔗 رابط خارجي", callback_data="button_type_url")],
            [InlineKeyboardButton("📱 تطبيق ويب", callback_data="button_type_webapp")],
            [InlineKeyboardButton("⚙️ زر تفاعلي", callback_data="button_type_callback")],
            [InlineKeyboardButton("👁️ معاينة المنشور", callback_data="preview_post")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔘 إضافة زر جديد\n\n"
            "اختر نوع الزر:",
            reply_markup=reply_markup
        )

async def handle_button_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button type selection"""
    query = update.callback_query
    await query.answer()
    
    button_type = query.data.replace("button_type_", "")
    context.user_data['current_button_type'] = button_type
    
    keyboard = [
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if button_type == "url":
        await query.edit_message_text(
            "🔗 زر رابط خارجي\n\n"
            "أرسل نص الزر متبوعاً بالرابط في سطر منفصل:\n"
            "أمثلة:\n"
            "زيارة الموقع\n"
            "https://example.com\n\n"
            "أو للتواصل مع شخص:\n"
            "تواصل معاي\n"
            "@MrTarekSupport",
            reply_markup=reply_markup
        )
    elif button_type == "webapp":
        await query.edit_message_text(
            "📱 زر تطبيق ويب\n\n"
            "أرسل نص الزر متبوعاً برابط التطبيق في سطر منفصل:\n"
            "مثال:\n"
            "فتح التطبيق\n"
            "https://app.example.com",
            reply_markup=reply_markup
        )
    elif button_type == "callback":
        await query.edit_message_text(
            "⚙️ زر تفاعلي\n\n"
            "أرسل نص الزر متبوعاً بكود الاستجابة في سطر منفصل:\n"
            "مثال:\n"
            "زر التفاعل\n"
            "button_callback_data",
            reply_markup=reply_markup
        )

async def handle_button_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button data input"""
    if not context.user_data.get('creating_post', False):
        return
    
    message_text = update.message.text.strip()
    lines = message_text.split('\n')
    
    if len(lines) < 2:
        await update.message.reply_text("❌ يرجى إرسال نص الزر والرابط في سطرين منفصلين")
        return
    
    button_text = lines[0].strip()
    button_url = lines[1].strip()
    button_type = context.user_data.get('current_button_type', 'url')
    
    # Create button data
    button_data = {
        'text': button_text,
        'type': button_type
    }
    
    if button_type == 'url':
        button_data['url'] = button_url
    elif button_type == 'webapp':
        button_data['url'] = button_url
    elif button_type == 'callback':
        button_data['callback_data'] = button_url
    
    # Add button to post data
    post_data = context.user_data.get('post_data', {})
    if 'buttons' not in post_data:
        post_data['buttons'] = []
    post_data['buttons'].append(button_data)
    context.user_data['post_data'] = post_data
    
    # Clear current button type
    context.user_data.pop('current_button_type', None)
    
    keyboard = [
        [InlineKeyboardButton("➕ إضافة زر آخر", callback_data="add_button")],
        [InlineKeyboardButton("👁️ معاينة المنشور", callback_data="preview_post")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ تم إضافة الزر: {button_text}\n\n"
        "يمكنك إضافة المزيد من الأزرار أو معاينة المنشور",
        reply_markup=reply_markup
    )

async def preview_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle preview post callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "preview_post":
        post_data = context.user_data.get('post_data', {})
        
        if not post_data.get('content'):
            await query.edit_message_text("❌ يرجى إكمال محتوى المنشور أولاً")
            return
        
        # Create buttons for the post (same as users will see)
        reply_markup = create_post_buttons(post_data.get('buttons', []))
        
        # Send the exact message that users will receive
        if post_data.get('image'):
            # Send photo with caption
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=post_data['image'],
                caption=post_data['content'],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            # Send text message
            await query.edit_message_text(
                post_data['content'],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        
        # Send preview controls
        keyboard = [
            [InlineKeyboardButton("✅ تأكيد الإرسال", callback_data="confirm_post_send")],
            [InlineKeyboardButton("✏️ تعديل", callback_data="edit_post")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post_creation")]
        ]
        reply_markup_controls = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="👆 هذا هو الشكل الذي سيراه المستخدمون\n\nهل تريد تأكيد الإرسال؟",
            reply_markup=reply_markup_controls
        )

async def confirm_post_send_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm post send callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_post_send":
        post_data = context.user_data.get('post_data', {})
        
        # Save post to database
        save_admin_post(post_data)
        
        # Get all user IDs
        user_ids = get_all_user_ids()
        
        if not user_ids:
            await query.edit_message_text("❌ لا توجد مستخدمين لإرسال المنشور إليهم")
            return
        
        # Create buttons for the post
        reply_markup = create_post_buttons(post_data.get('buttons', []))
        
        # Send to all users
        sent_count = 0
        failed_count = 0
        
        await query.edit_message_text("📤 جاري إرسال المنشور...")
        
        for user_id in user_ids:
            try:
                if post_data.get('image'):
                    # Send photo with caption
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=post_data['image'],
                        caption=post_data['content'],
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    # Send text message
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=post_data['content'],
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                sent_count += 1
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to send message to user {user_id}: {e}")
        
        # Clear post creation state
        context.user_data.pop('creating_post', None)
        context.user_data.pop('post_data', None)
        context.user_data.pop('current_button_type', None)
        
        await query.edit_message_text(
            f"✅ تم إرسال المنشور بنجاح!\n\n"
            f"📊 الإحصائيات:\n"
            f"✅ تم الإرسال: {sent_count}\n"
            f"❌ فشل الإرسال: {failed_count}\n"
            f"📝 إجمالي المستخدمين: {len(user_ids)}"
        )

async def cancel_post_creation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel post creation callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_post_creation":
        # Clear post creation state
        context.user_data.pop('creating_post', None)
        context.user_data.pop('post_data', None)
        context.user_data.pop('current_button_type', None)
        
        await query.edit_message_text("❌ تم إلغاء إنشاء المنشور")

async def list_posts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list all posts"""
    # Check if user is admin
    admin_ids = [5878017415]  # Replace with your actual user ID
    
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ هذا الأمر متاح للإدارة فقط")
        return
    
    try:
        posts = load_admin_posts()
        
        if not posts:
            await update.message.reply_text("📝 لا توجد منشورات حالياً")
            return
        
        message = f"📝 المنشورات ({len(posts)})\n\n"
        
        for i, post in enumerate(posts, 1):
            content_preview = post.get('content', 'بدون محتوى')[:50] + "..." if len(post.get('content', '')) > 50 else post.get('content', 'بدون محتوى')
            message += f"{i}. {content_preview}\n"
            message += f"   📅 التاريخ: {post.get('created_at', 'غير محدد')}\n"
            message += f"   🔘 الأزرار: {len(post.get('buttons', []))}\n"
            message += f"   🖼️ صورة: {'نعم' if post.get('image') else 'لا'}\n\n"
        
        # Split message if too long
        if len(message) > 4000:
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب المنشورات: {e}")

def run_userbot():
    """Run userbot in separate thread"""
    def start_userbot_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_userbot())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(stop_userbot())
        finally:
            loop.close()
    
    userbot_thread = threading.Thread(target=start_userbot_thread, daemon=True)
    userbot_thread.start()
    return userbot_thread

def main():
    """Start the bot"""
    # Note: Userbot should be started separately before calling this function
    # This allows the userbot to be managed independently
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("quiz_stats", quiz_stats_command))
    application.add_handler(CommandHandler("registered_ids", registered_ids_command))
    application.add_handler(CommandHandler("create_post", create_post_command))
    application.add_handler(CommandHandler("list_posts", list_posts_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for text messages and photos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    
    # Add error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error("Exception while handling an update:", exc_info=context.error)
    
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("Bot is starting...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("Stopping bot...")
    finally:
        print("Bot stopped")

def run_bot():
    """Run the bot"""
    main()

if __name__ == '__main__':
    run_bot()
