from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackContext, CallbackQueryHandler
)
import logging
import time
from telegram_data_base import sign_up


async def signup(update: Update, context: CallbackContext):
    """
    Start the sign-up process by prompting for a username.
    """
    await update.message.reply_text("Please enter your desired username:")
    context.user_data['awaiting_username'] = True
    

async def handle_user_input(update: Update, context: CallbackContext):
    """
    Handle user input during the sign-up process.
    """
    promotion_code = update.message.from_user.id
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
        if sign_up(username, password, promotion_code, wallet):
            await update.message.reply_text(f"Welcome {username}! You have successfully signed up.")

        else:
            await update.message.reply_text("Username already exists. Please choose another username.")

        # Reset state
        context.user_data['awaiting_password'] = False
        context.user_data['username'] = None
        context.user_data['password'] = None


async def add_users(update: Update, context: CallbackContext):
    """
    Start the sign-up process by prompting for a username.
    """
    await update.message.reply_text("Please enter your desired username:")
    context.user_data['awaiting_username_2'] = True
    

