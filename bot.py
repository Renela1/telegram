from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler 
)
import V2Ray_API
import logging
import time
# from Authentication import handle_user_input
import telegram_data_base
import requests
import asyncio 

keyboard = [
    [ "تایین قیمت سرویس", "🛒 خرید سرویس"],
    ["🐝 مشاهده موجودی", "💰 شارژ کیف پول"],
    ["⚙ مدیریت نمایندگان", "سرویس های من"]
]

# Convert to markup
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def set_bot_commands(update: Update, context: CallbackContext):
    commands = [
        ('start', 'استارت بات'),
        ('services', ' خرید سرویس از نماینده'),
        ('signup', 'ثبت نام'),
        ('balance', 'مشاهده اعتبار'),
        ('charge_wallet', 'افزایش اعتبار')
    ]
    
    await context.bot.set_my_commands(commands)
    await update.message.reply_text("Bot commands have been set!")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "7554088954:AAHElaxcg3V8rnMH9HJYy6UBeUQHYiiawl0"
ADMINS = [6001068123, 5215610894]
PAYMENT_API_KEY = "YOUR_PAYMENT_API_KEY_HERE"
PAYMENT_API_URL = "https://your-payment-gateway.com/api/create_payment"  # Placeholder URL
CHECK_PAYMENT_URL = "https://your-payment-gateway.com/api/check_payment"  # Placeholder

# Services List
SERVICES = telegram_data_base.all_services()
print(SERVICES)
# strat command
async def start(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id
    await update.message.reply_text(f"Your User ID is: \n<code>{user_id}</code>", parse_mode="HTML")
    await update.message.reply_text(f'ابتدا لطفا ثبت نام کنید :')
    await signup(update, context)


# checking if user is admin
def is_admin(user_id):
    return user_id in ADMINS


# showing the list of users
async def get_user_list(update:Update, context:CallbackContext):

    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("You do not have permission to view the users list.")
        return

    users = telegram_data_base.get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    user_list = "\n".join([f"{user['id']}. {user['username']}" for user in users])

    keyboard = [
        [InlineKeyboardButton("Previous", callback_data="prev"),
         InlineKeyboardButton("Next", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Users:\n{user_list}", reply_markup=reply_markup)


async def admin_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("You do not have permission to use this command.")
        return

    await update.message.reply_text("You are an admin!")



async def signup(update: Update, context: CallbackContext):
    """Start the sign-up process by prompting for a username."""
    # Clear any conflicting states when starting sign-up
    context.user_data.clear()
    
    await update.message.reply_text("لطفا نام کاربری دلخواه خود را وارد کنید:")
    context.user_data['awaiting_username'] = True  # State: Awaiting username


async def add_services(update: Update, context: CallbackContext):
    """Start the add service process by prompting for the service name."""
    # Clear any conflicting states when starting add service
    context.user_data.clear()
    
    await update.message.reply_text("لطفا نام سرویس خود را وارد کنید:")
    context.user_data['awaiting_service_name'] = True  # State: Awaiting service name


async def add_users(update: Update, context: CallbackContext):
    """
    Prompt user for username, password, and email for sign-up.
    """
    # Prompt for username
    await update.message.reply_text("لطفا نام کاربری دلخواه خود را وارد کنید:")

    # Store state to wait for next messages
    context.user_data['awaiting_username'] = True


async def check_payment(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /check_payment TRANSACTION_ID")
        return
    
    transaction_id = context.args[0]
    response = requests.get(f"{CHECK_PAYMENT_URL}?api_key={PAYMENT_API_KEY}&transaction_id={transaction_id}")
    result = response.json()
    
    if result.get("status") == "success":
        user_id = result.get("user_id")
        amount = result.get("amount")
        
        with telegram_data_base.connection.cursor() as cursor:

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id = %s", (amount, user_id))

            telegram_data_base.connection.commit()
        
        await update.message.reply_text(f"Payment confirmed! {amount} IRL added to user {user_id}.")
        await context.bot.send_message(user_id, f"Your payment of {amount} IRL was successful! 🎉")
    else:
        await update.message.reply_text("Payment not found or still pending.")


async def check_balance(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    selected_service = context.user_data.get("selected_service", None)

    if not selected_service:
        await query.answer("Something went wrong! Please try again.")
        return

    # Get price of the selected service
    service_price = next((s["price"] for s in SERVICES if s["name"] == selected_service), None)

    if service_price is None:
        await query.edit_message_text("Invalid service selection.")
        return

    # Get user's wallet balance
    user_balance = get_user_balance(user_id)

    if user_balance is None:
        await query.edit_message_text("Could not retrieve your wallet balance. Please try again later.")
        return

    # Check if the user has enough balance
    if user_balance >= service_price:
        await query.edit_message_text(f"✅ Payment successful! You have been charged {service_price} IRL.")
        # Here, you can proceed with deducting the balance and providing the service
    else:
        await query.edit_message_text(f"❌ Insufficient balance. Your balance: {user_balance} IRL, Required: {service_price} IRL.")



async def handle_promotion_code(update: Update, context: CallbackContext):
    """Handle the user entering the promotion code."""

    # Ensure the bot is actually waiting for the promotion code
    if context.user_data.get('awaiting_user_promotion_code'):
        # Capture the promotion code from user input
        promotion_code = update.message.text.strip()  
        context.user_data['user_promotion_code'] = promotion_code  
        context.user_data['awaiting_promotion_code'] = False

        # Proceed to show available services
        await show_services(update, context)


# Step 3: Modify the show_services function to use the dynamic promotion code
async def show_services(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id

    SERVICE = telegram_data_base.buy_services(user_id=user_id)  # No need for global
    print(SERVICE)
    if not SERVICE:  # Handle case where no services are found
        await update.message.reply_text("⛔ هیچ سرویسی برای خرید در دسترس نیست.")
        return

    # Store in context so `handle_selection()` can access it
    context.user_data["available_services"] = SERVICE  

    # Create inline keyboard buttons
    keyboard = [
        [InlineKeyboardButton(
            text=f"{service['name']} - {service['profile']} - {int(service['price'])} تومان",
            callback_data=service['name']  # You can use service ID here if needed
        )]
        for service in SERVICE
    ]
    print(SERVICE)  # Debugging

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("سرویس مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)



async def show_seller_services(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id  # Seller's Telegram ID

    # Fetch seller services and store them in user-specific context
    services = telegram_data_base.retrieve_services(user_id)

    if not services:  
        await update.message.reply_text("⛔ شما هیچ سرویسی برای فروش ندارید.")
        return

    # Save services in user-specific storage (context.user_data)
    context.user_data["services"] = services  

    # Create inline buttons
    keyboard = [
        [InlineKeyboardButton(
            text=f"{service['name']} - {service['profile']} - {int(service['price'])} تومان",
            callback_data=f"service_{service['name']}"  # Unique callback data
        )]
        for service in services
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📌 سرویس‌های شما:", reply_markup=reply_markup)


async def get_user_balance(update: Update, context: CallbackContext):
    global amount
   
    user_id = update.message.from_user.id
    print(user_id)
    try: 
        result = telegram_data_base.get_balance(user_id)
        print(result)
        await update.message.reply_text(f"{result['wallet']}")

    except Exception as e:
        print(f"Error getting user balance: {e}")

    amount = result['wallet']

async def check_user_balance(user_id):

    global amount
    
    try:
        with telegram_data_base.connection.cursor() as cursor:
           
            cursor.execute("SELECT wallet FROM users WHERE promotion_code = %s", (user_id,))
           
            result = cursor.fetchone()

            print("Query executed. Result:", result)  
            

    except Exception as e:
        print(f"Error getting user balance: {e}")

    amount = result['wallet']

    return amount


async def show_services(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id

    SERVICE = telegram_data_base.buy_services(user_id=user_id)  # No need for global
    print(SERVICE)
    if not SERVICE:  # Handle case where no services are found
        await update.message.reply_text("⛔ هیچ سرویسی برای خرید در دسترس نیست.")
        return

    # Store in context so `handle_selection()` can access it
    context.user_data["available_services"] = SERVICE  

    # Create inline keyboard buttons
    keyboard = [
        [InlineKeyboardButton(
            text=f"{service['name']} - {service['profile']} - {service['type']} - {int(service['price'])} تومان",
            callback_data=service['name']  # You can use service ID here if needed
        )]
        for service in SERVICE
    ]
    print(SERVICE)  # Debugging

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("سرویس مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)



async def update_seller_services(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id

    SERVICE = telegram_data_base.retrieve_services(user_id)  # No need for global
    print(SERVICE)
    if not SERVICE:  # Handle case where no services are found
        await update.message.reply_text("⛔ هیچ سرویسی برای خرید در دسترس نیست.")
        return

    # Store in context so `handle_selection()` can access it
    context.user_data["available_services"] = SERVICE  

    keyboard = [
        [InlineKeyboardButton(
            text=f"{service['name']} - {service['profile']} - {service['type']} - {service['price']} تومان",
            callback_data=f"update_{service['name']}"  # You can use service ID here if needed
        )]
        
        for service in SERVICE
    ]
    print(SERVICE)  # Debugging
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("سرویس مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)

async def validate_payment(update: Update, context: CallbackContext):

    context.user_data.clear()  # Clear any previous input state
        

    await context.bot.send_message(
        chat_id=int(6001068123), 
        text=f"کد کاربر را وارد کنید"
    )

    context.user_data['awaiting_user_code'] = True
    print('awaiting_user_code', context.user_data['awaiting_user_code'])


async def handle_selection(update: Update, context: CallbackContext):

    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    selected_data = query.data  
    available_services = context.user_data.get("available_services", [])

    if selected_data.startswith("update_"):

        service_name = selected_data.replace("update_", "")
        print(service_name)
        await query.message.reply_text(f"لطفا قیمت جدید را وارد کنید برای سرویس: {service_name}:")
       
        service_id = next((s["user_service_service_id"] for s in available_services if s["name"] == service_name), None)

        context.user_data["service_id"] = service_id 
        

        context.user_data['awaiting_new_price'] = True

        print(service_id)

    elif query.data.startswith("validate_"):
        user_id = query.data.replace("validate_", "")
        await validate_payment(update, context)

    else:

        selected_service = query.data  # Here we get the selected service
        service_name = selected_data.replace("update_", "")
        print(f"User selected: {selected_service}")  # Debugging

        # Retrieve available services from `context.user_data`
        service_ids = next((s["user_service_id"] for s in available_services if s["name"] == selected_service), None)
        context.user_data["service_id"] = service_ids

        global service_price
        service_price = next((s["price"] for s in available_services if s["name"] == selected_service), None)

        if service_price is None:
            await query.message.reply_text("⛔ خطا: این سرویس دیگر در دسترس نیست.")
            return
        
        await check_user_balance(user_id)
        context.user_data["selected_service"] = selected_service
        context.user_data["service_price"] = service_price

        print(f"Service price: {service_price}")  # Debugging

        await query.message.reply_text(f"✅ سرویس انتخاب‌شده: {selected_service}\n💰 قیمت: {service_price} تومان")

        global service_profile
        service_profile = next((s["profile"] for s in available_services if s["name"] == selected_service), None)

        global service_code
        service_code = next((s["promotion_code"] for s in available_services if s["name"] == selected_service), None)

        # service_price = next((s["price"] for s in SERVICE if s["name"] == selected_service), None)

        print('profile',service_profile)
        print('price',service_price)
        print('code',service_code)


        global treshhold
        if (service_price <= int(amount)) == True:
            treshhold = True
            print(treshhold)
        else:
            treshhold = False
            print(treshhold)

        print(treshhold)
        await query.edit_message_text(f"شما سرویس: {selected_service} {service_price <= int(amount)} \n را انتخاب کردید")
        await handle_confirmation(update, context)


async def handle_confirmation(update: Update, context: CallbackContext):

    query2 = update.callback_query

    await query2.answer() 
    
    user_id = query2.from_user.id

    print(user_id)
    
    result = telegram_data_base.get_user_pass(user_id)

    print('hellooooooo',result)

    service_id = context.user_data.get('service_id')
    print(service_id)

    if treshhold == True:
        
        await query2.edit_message_text(f"اعتبار کافی{amount}")
        
        await query2.edit_message_text(f"تایید, لطفا چند لحظه صبر کنید")

        telegram_data_base.distribute_commission(user_id, (int(service_id)), (int(amount)))

        try:

            print('prf ', service_profile)

            if service_profile == '1month':
                limit = V2Ray_API.expiry_timestamp_1

            elif service_profile == '2month':
                limit = V2Ray_API.expiry_timestamp_2

            elif service_profile == '3month':
                limit =  V2Ray_API.expiry_timestamp_3

            print(int(limit))

            config = V2Ray_API.add_client(2, (str(user_id)), (int(limit)))
            print(config)

            await query2.edit_message_text(f'{config}')

                
        except Exception as e:
            print('error creating inbound', e)
    else:
        await query2.edit_message_text(f"❌ اعتبار شما کافی نیست.")


async def get_user_id(update: Update, context: CallbackContext):
    
    user_id = update.message.from_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("You do not have permission to use this command.")
        return


    if not context.args:
        await update.message.reply_text("Usage: /getid @username")
        return

    username = context.args[0]

    # Ensure username starts with '@'
    if not username.startswith("@"):
        await update.message.reply_text("Please provide a valid username starting with '@'.")
        return

    try:
        # Get user info from Telegram
        user_info = await context.bot.get_chat(username)

        # Extract and send the user's Telegram ID
        telegram_id = user_info.id
        await update.message.reply_text(f"User {username} has Telegram ID: {telegram_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ Could not find user {username}. Error: {e}")


async def signup(update: Update, context: CallbackContext):
    """Start the sign-up process by prompting for a username."""
    # Clear any conflicting states when starting sign-up
    context.user_data.clear()
    
    await update.message.reply_text("لطفا نام کاربری دلخواه خود را وارد کنید:")
    context.user_data['awaiting_username'] = True  # State: Awaiting username


async def add_services(update: Update, context: CallbackContext):
    """Start the add service process by prompting for the service name."""
    # Clear any conflicting states when starting add service
    context.user_data.clear()
    
    await update.message.reply_text("لطفا نام سرویس خود را وارد کنید:")
    context.user_data['awaiting_service_name'] = True  # State: Awaiting service name
    print(context.user_data['awaiting_service_name'])


async def handle_user_input(update: Update, context: CallbackContext):

    """
    Handle user input for both sign-up and adding services (service name, price, and profile name).
    """
    # Handle Sign-Up Process
    if context.user_data.get('awaiting_username'):
        username = update.message.text.strip()
        context.user_data['username'] = username
        context.user_data['awaiting_username'] = False
        context.user_data['awaiting_seller'] = True  # Next step: Ask for password

        await update.message.reply_text(f"نام کاربری شما: {username}. لطفا کد نماینده خود را وارد کنید:")
        return  # Exit function to prevent further processing during sign-up
    
    elif context.user_data.get('awaiting_seller'):

        seller_code = update.message.text.strip()
        context.user_data['seller'] = seller_code
        context.user_data['awaiting_seller'] = False 
        context.user_data['awaiting_password'] = True

        await update.message.reply_text(f"کد نماینده شما: {seller_code}. لطفا رمز عبوری را وارد کنید:")
        

    elif context.user_data.get('awaiting_password'):
        password = update.message.text.strip()
        seller = context.user_data.get('seller')
        user_name = context.user_data.get('username')
        promotion_code = update.message.from_user.id  # Get promotion code from user ID
        wallet = 0  # Initialize wallet balance


        # Call the sign-up function (you can define it elsewhere)
        if telegram_data_base.sign_up(user_name, password, promotion_code, wallet, seller):
            await update.message.reply_text(f"خوش آمدید {user_name}! شما با موفقیت ثبت نام شدید.", reply_markup=reply_markup)
        else:
            await update.message.reply_text("error")

        print(telegram_data_base.add_seller_services_to_user(promotion_code))


        # Reset states after sign-up
        context.user_data.clear()
        return  # Exit function

    # Handle Add Service Process
    elif context.user_data.get('awaiting_service_name'):
        service_name = update.message.text.strip()
        context.user_data['service_name'] = service_name
        context.user_data['awaiting_service_name'] = False
        context.user_data['awaiting_profile_name'] = True  # Next step: Ask for service price

        await update.message.reply_text(f" زمان محدودیت سرویس را وارد کنید (یک عدد بین 1 تا 3 وارد کنید):")
        return  # Exit function to prevent further processing during add service


    elif context.user_data.get('awaiting_profile_name'):

        profile_name = update.message.text.strip()
        context.user_data['service_profile'] = profile_name

        service_name = context.user_data.get('service_name')
        profile = context.user_data.get('service_profile')

        context.user_data['awaiting_profile_name'] = False
        context.user_data['awaiting_service_price'] = True 

        await update.message.reply_text(f" نام سرویس شما: {service_name}.\  زمان سرویس شما {profile} : \n لطفا قیمت سرویس را وارد کنید:")

    
    elif context.user_data.get('awaiting_service_price'):

        profile = context.user_data.get('service_profile')
        price = float(update.message.text.strip()) 
        print(price)
        print(profile)


        if price >= 500000.0 :

            context.user_data['service_price'] = price

            service_name = context.user_data.get('service_name')

            promotion_code = update.message.from_user.id  # Get user ID as promotion code (or other logic)

            telegram_data_base.save_service(service_name, 'v2ray', (f'{profile}month'), price, promotion_code)

            await update.message.reply_text(
                f"✅ **سرویس با موفقیت افزوده شد:**\n"
                f"📌 نام سرویس: {service_name}\n"
                f"💰 قیمت: {price} تومان\n"
                f"👤 زمان: {profile}ماه\n"
                "نوع سرویس: v2ray"
            )

            context.user_data.clear()
            return  # Exit function
        
        else:
            await update.message.reply_text('قیمت سرویس نمیتواند کمتر از 500000 ریال باشد')
            return 
            
    elif context.user_data.get('awaiting_user_promotion_code'):
        try:
            if context.user_data.get('awaiting_user_promotion_code'):
                # Capture the promotion code from user input
                promotion_code = update.message.text.strip()  
                context.user_data['user_promotion_code'] = promotion_code  
                context.user_data['awaiting_promotion_code'] = False

                # Proceed to show available services
                await show_services(update, context)

                context.user_data.clear()
                return 

        except ValueError:
            await update.message.reply_text("❌ لطفا یک کد معتبر وارد کنید (عدد صحیح).")
            return  # Keep waiting for a valid code
        
    elif context.user_data.get('awaiting_user_code'):
        print('("لطفا کد کاربر را وارد کنید:")')

        try:
            
            if context.user_data.get('awaiting_user_code'):

                user_code = update.message.text.strip()  
                context.user_data['user_code'] = int(user_code)  
                context.user_data['awaiting_user_code'] = False

                context.user_data['awaiting_amount'] = True

                await update.message.reply_text('لطفا مبلغ را وارد کنید')
                print(user_code)

        except ValueError:
            await update.message.reply_text("❌ لطفا یک کد معتبر وارد کنید (عدد صحیح).")
            return  # Keep waiting for a valid code
        
    elif context.user_data.get('awaiting_amount'):
      
        user_code = context.user_data.get('user_code')
        print(user_code)
        
        try:
            if context.user_data.get('awaiting_amount'):

                add_amount = int(update.message.text.strip())  
                context.user_data['amount'] = add_amount  
                context.user_data['awaiting_amount'] = False

                telegram_data_base.update_wallet(first_user=user_code, amount=add_amount)

                await update.message.reply_text(f'مبلغ {add_amount} \n به کاربر اضافه شد')

                await context.bot.send_message(
                    chat_id=int(user_code), 
                    text=f"✅ پرداخت شما تایید شد! مبلغ {add_amount} به کیف پول شما اضافه شد."
                )

                context.user_data.clear()
                return 

        except ValueError:
            await update.message.reply_text("❌ لطفا یک عدد معتبر وارد کنید (عدد صحیح).")
            return  # Keep waiting for a valid code
        
    elif context.user_data.get('awaiting_new_price'):

        try:

            service_id = context.user_data.get('service_id')
            update_amount = int(update.message.text.strip())
            context.user_data['amount'] = update_amount
            user_id = update.message.from_user.id
     
            result = telegram_data_base.update_service_price(user_id, service_id, update_amount )
            print(result)

            if result == True:

                await update.message.reply_text(f"مبلغ سرویس به {update_amount} اپدیت شد")
            else: 
                await update.message.reply_text(f"مبلغ جدید نمیتواند کمتر از مبلغ تایین شده باشد")
                return
            
            context.user_data.clear()
            return 
        
        except ValueError:
            await update.message.reply_text("❌ لطفا یک عدد معتبر وارد کنید (عدد صحیح).")
            return  
        
    user_message = update.message.text.strip()
    print(user_message)

    if user_message == "🛒 خرید سرویس":
        await show_services(update, context)
    
    elif user_message == "🐝 مشاهده موجودی":
        await get_user_balance(update, context)
    
    elif user_message == "تایین قیمت سرویس":
        await update_seller_services(update, context)

    elif user_message == "سرویس های من":
        await show_seller_services(update, context)

    elif user_message == "💰 شارژ کیف پول":
        await charge_wallet(update, context)


async def charge_wallet(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id

    await update.message.reply_text(
        "✅ برای افزایش اعتبار خود، مبلغ مورد نظر را به شماره کارت 6063731048002936 واریز کنید.\n"
        "📸 سپس عکس رسید خود را در همین چت ارسال کنید."
    )

    # Store that the user is awaiting a receipt
    context.user_data["awaiting_receipt"] = True
    context.user_data["user_id"] = user_id


async def handle_photo(update: Update, context: CallbackContext):

    user_id = context.user_data.get("user_id")

    if context.user_data.get("awaiting_receipt"):
    
        photo = update.message.photo[-1].file_id

        keyboard = [[InlineKeyboardButton("✅ تایید", callback_data=f"validate_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=6001068123,
            photo=photo,
            caption=f"📩 رسید پرداخت جدید از کاربر:\n\n<code>{user_id}</code>",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

        # Confirm receipt submission to user
        await update.message.reply_text("✅ رسید شما دریافت شد و برای بررسی به ادمین ارسال شد.")

        # Clear the state
        context.user_data["awaiting_receipt"] = False
        context.clear()
    else:
        await update.message.reply_text("❌ لطفاً ابتدا از دستور /charge_wallet استفاده کنید.")


def main():
    
    try:
        # Create the application to be called on start 

        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("services", show_services))
        app.add_handler(CommandHandler("my_services", show_seller_services))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("users", get_user_list))
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CallbackQueryHandler(handle_selection))
        app.add_handler(CommandHandler("signup", signup))
        app.add_handler(CommandHandler("add_user", add_users))
        app.add_handler(CommandHandler("check_payment", check_payment))
        app.add_handler(CallbackQueryHandler(handle_confirmation, pattern="^(accept|cancel)$"))
        app.add_handler(CommandHandler('balance', get_user_balance))
        app.add_handler(CommandHandler('getid', get_user_id))
        app.add_handler(CommandHandler('setmycommands', set_bot_commands))
        app.add_handler(CommandHandler('add_service', add_services))
        app.add_handler(CommandHandler('vlidate', validate_payment))
        app.add_handler(CommandHandler('charge_wallet', charge_wallet))
        app.add_handler(CommandHandler('update_price', update_seller_services))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        logger.info("Bot is running...")
        app.run_polling()

    except Exception as e:

        logger.error(f"Unexpected error occurred: {e}")
        logger.info("Retrying in 5 seconds...")
        time.sleep(5)

        main()  

if __name__ == "__main__":
    main()