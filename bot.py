from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
)
import V2Ray_API
import logging
import time
from Authentication import handle_user_input
import telegram_data_base
import requests
import asyncio 


async def set_bot_commands(update: Update, context: CallbackContext):
    commands = [
        ('start', 'Start the bot'),
        ('help', 'Get help with the bot'),
        ('services', 'Show available services'),
        ('signup', 'signup'),
        ('balance', 'check your balance'),
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
ADMINS = [6001068123]
PAYMENT_API_KEY = "YOUR_PAYMENT_API_KEY_HERE"
PAYMENT_API_URL = "https://your-payment-gateway.com/api/create_payment"  # Placeholder URL
CHECK_PAYMENT_URL = "https://your-payment-gateway.com/api/check_payment"  # Placeholder

# Services List
SERVICES = telegram_data_base.services()

# strat command
async def start(update: Update, context: CallbackContext):

    await update.message.reply_text("Hello, welcome! This is my first test of the bot.")
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Your User ID is: {user_id}")



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
    """
    Prompt user for username, password, and email for sign-up.
    """
    # Prompt for username
    await update.message.reply_text("Please enter your desired username:")

    # Store state to wait for next messages
    context.user_data['awaiting_username'] = True


async def add_users(update: Update, context: CallbackContext):
    """
    Prompt user for username, password, and email for sign-up.
    """
    # Prompt for username
    await update.message.reply_text("Please enter the desired username:")

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



async def show_services(update: Update, context: CallbackContext):

    user_id = update.message.from_user.id
    await check_user_balance(user_id)
    keyboard = [
        [InlineKeyboardButton(f"{service['name']} - {service['price']} IRL", callback_data=service['name'])]
        for service in SERVICES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a service:", reply_markup=reply_markup)


async def get_user_balance(update: Update, context: CallbackContext):

   
    user_id = update.message.from_user.id
    print(user_id)
    try: 
        result = telegram_data_base.get_balance(user_id)
        print(result)
        await update.message.reply_text(f"{result['wallet']}")

    except Exception as e:
        print(f"Error getting user balance: {e}")



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


async def handle_selection(update: Update, context: CallbackContext):

    query = update.callback_query
    await query.answer()

    selected_service = query.data  # Here we get the selected service

    # Store the selected service in context.user_data
    context.user_data["selected_service"] = selected_service

    # Get the price of the selected service
    global service_price
    service_price = next((s["price"] for s in SERVICES if s["name"] == selected_service), None)

    global service_profile
    service_profile = next((s["profile"] for s in SERVICES if s["name"] == selected_service), None)

    
    service_price = next((s["price"] for s in SERVICES if s["name"] == selected_service), None)

    print('profile',service_profile)
    print('price',service_price)


    global treshhold
    if (service_price <= int(amount)) == True:
        treshhold = True
        print(treshhold)
    else:
        treshhold = False
        print(treshhold)

    print(treshhold)
    await query.edit_message_text(f"You selected: {selected_service} {service_price <= int(amount)} \nDo you want to proceed?")
    await handle_confirmation(update, context)


async def handle_confirmation(update: Update, context: CallbackContext):

    query2 = update.callback_query

    await query2.answer() 
    
    user_id = query2.from_user.id

    print(user_id)
    
    result = telegram_data_base.get_user_pass(user_id)

    print('hellooooooo',result)

    if treshhold == True:
        
        await query2.edit_message_text(f"balance sufficient{amount}")
        
        await query2.edit_message_text(f"account with name and pass {result['username']} {result['password']} has been created")

        # telegram_data_base.update_wallet_cost(user_id, service_price)
        try:

            print('prf ', service_profile)

            if service_profile == '1month':
                limit = V2Ray_API.expiry_timestamp_1

            elif service_profile == '2month':
                limit = V2Ray_API.expiry_timestamp_2

            elif service_profile == '3month':
                limit =  V2Ray_API.expiry_timestamp_3

            print(int(limit))


            config = V2Ray_API.add_client(1, (str(user_id)), (int(limit)))
            print(config)

            await query2.edit_message_text(f'your config file is \n {config}')



                
        except Exception as e:
            print('error creating inbound', e)
    else:
        await query2.edit_message_text(f"❌ Insufficient balance. Your balance: IRL, Required: IRL.")


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


async def handle_admin_input(update: Update, context: CallbackContext):

    wallet = 0

    if context.user_data.get('awaiting_username'):
        # Handle username input
        username = update.message.text
        context.user_data['username'] = username
        await update.message.reply_text(f"Username set to {username}. Now, please enter your password:")
        context.user_data['awaiting_username'] = False
        context.user_data['awaiting_password'] = True

    elif context.user_data.get('awaiting_password'):
        # Handle password input
        password = update.message.text
        username = context.user_data.get('username')

        # Call sign_up function to register the user
        if telegram_data_base.sign_up(username, password, promotion_code, wallet):
            await update.message.reply_text(f"Welcome {username}! You have successfully signed up.")

        else:
            await update.message.reply_text("Username already exists. Please choose another username.")

        user_id = int(get_user_id(username))
        promotion_code = user_id

        # Reset state
        context.user_data['awaiting_password'] = False
        context.user_data['username'] = None
        context.user_data['password'] = None


async def add_services():
    pass


def main():
    
    try:
        # Create the application
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("services", show_services))
        app.add_handler(CommandHandler("users", get_user_list))
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CallbackQueryHandler(handle_selection))
        app.add_handler(CommandHandler("signup", signup))
        app.add_handler(CommandHandler("add_user", add_users))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))
        app.add_handler(CommandHandler("check_payment", check_payment))
        app.add_handler(CallbackQueryHandler(handle_confirmation, pattern="^(accept|cancel)$"))
        app.add_handler(CommandHandler('balance', get_user_balance))
        app.add_handler(CommandHandler('getid', get_user_id))
        app.add_handler(CommandHandler('setmycommands', set_bot_commands))
        
        # Start polling
        logger.info("Bot is running...")
        app.run_polling()

    except Exception as e:

        logger.error(f"Unexpected error occurred: {e}")
        logger.info("Retrying in 5 seconds...")
        time.sleep(5)

        main()  # Restart the application in case of an error

if __name__ == "__main__":
    main()