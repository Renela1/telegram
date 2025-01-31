from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
)
import logging
import time
from authentication import sign_up, handle_user_input
import telegram_data_base


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "7554088954:AAHElaxcg3V8rnMH9HJYy6UBeUQHYiiawl0"
ADMINS = [6001068123]
# Services List
SERVICES = [
    {"name": "Service 1", "price": 100},
    {"name": "Service 2", "price": 200},
    {"name": "Service 3", "price": 300},
]

# strat command
async def start(update: Update, context: CallbackContext):

    await update.message.reply_text("Hello, welcome! This is my first test of the bot.")
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Your User ID is: {user_id}")


# show list of services command
async def show_services(update: Update, context: CallbackContext):

    keyboard = [
        [InlineKeyboardButton(f"{service['name']} - {service['price']} IRL", callback_data=service['name'])]
        for service in SERVICES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a service:", reply_markup=reply_markup)


# handeling the list delection of services
async def handle_selection(update: Update, context: CallbackContext):

    query = update.callback_query
    await query.answer()
    selected_service = query.data
    await query.edit_message_text(f"You selected: {selected_service}")

    await update.message.reply_text("Please upload a screenshot or send the transaction ID of your payment.")
    context.user_data['awaiting_receipt'] = True


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


async def handle_receipt(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if context.user_data.get('awaiting_receipt'):

        if update.message.photo:  # If user sends an image
            photo_file = await update.message.photo[-1].get_file()
            file_path = f"receipts/{user_id}.jpg"
            await photo_file.download(file_path)

            await update.message.reply_text("Receipt received! Admin will verify and update your wallet soon.")

            # Notify admin and send the photo
            admin_id = 6001068123  # Replace with actual admin user ID
            await context.bot.send_photo(
                admin_id,
                photo=update.message.photo[-1].file_id,
                caption=f"User {user_id} uploaded a receipt.\nCheck it manually and update their wallet."
            )

        elif update.message.text:  # If user sends a transaction ID
            transaction_id = update.message.text
            await update.message.reply_text(f"Transaction ID '{transaction_id}' received! Admin will verify soon.")

            # Notify admin about the text transaction
            admin_id = 123456789
            await context.bot.send_message(
                admin_id,
                f"User {user_id} sent transaction ID: {transaction_id}\nCheck it manually and update their wallet."
            )

        # Reset state
        context.user_data['awaiting_receipt'] = False


async def approve_transaction(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /approve user_id amount")
        return
    
    user_id, amount = context.args[0], float(context.args[1])

    # Update wallet balance in the database
    with telegram_data_base.connection.cursor() as cursor:
        cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id = %s", (amount, user_id))
        telegram_data_base.connection.commit()

    await update.message.reply_text(f"User {user_id} has been credited with {amount} IRL.")
    await context.bot.send_message(user_id, f"Your wallet has been credited with {amount} IRL. 🎉")
    
# Main Bot Application

def main():
    try:
        # Create the application
        app = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("services", show_services))
        app.add_handler(CommandHandler("users", get_user_list))
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CallbackQueryHandler(handle_selection))
        app.add_handler(CommandHandler("signup", signup))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
        # app.add_handler(CommandHandler("upload_receipt", upload_receipt))
        app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_receipt))
        app.add_handler(CommandHandler("approve", approve_transaction))

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