from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackContext, CallbackQueryHandler
)
import logging
import time
from telegram_data_base import sign_up, save_service


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


async def handle_user_input(update: Update, context: CallbackContext):
    """
    Handle user input for both sign-up and adding services (service name, price, and profile name).
    """
    # Handle Sign-Up Process
    if context.user_data.get('awaiting_username'):
        username = update.message.text.strip()
        context.user_data['username'] = username
        context.user_data['awaiting_username'] = False
        context.user_data['awaiting_password'] = True  # Next step: Ask for password

        await update.message.reply_text(f"نام کاربری شما: {username}. لطفا رمز عبوری را وارد کنید:")
        return  # Exit function to prevent further processing during sign-up

    elif context.user_data.get('awaiting_password'):
        password = update.message.text.strip()
        username = context.user_data.get('username')
        promotion_code = update.message.from_user.id  # Get promotion code from user ID
        wallet = 0  # Initialize wallet balance

        # Call the sign-up function (you can define it elsewhere)
        if sign_up(username, password, promotion_code, wallet):
            await update.message.reply_text(f"خوش آمدید {username}! شما با موفقیت ثبت نام شدید.")
        else:
            await update.message.reply_text("این نام کاربری وجود دارد لطفا نام دیگری انتخاب کنید")

        # Reset states after sign-up
        context.user_data.clear()
        return  # Exit function

    # Handle Add Service Process
    elif context.user_data.get('awaiting_service_name'):
        service_name = update.message.text.strip()
        context.user_data['service_name'] = service_name
        context.user_data['awaiting_service_name'] = False
        context.user_data['awaiting_service_price'] = True  # Next step: Ask for service price

        await update.message.reply_text(f"نام سرویس شما: {service_name}.\nلطفا قیمت سرویس را وارد کنید:")
        return  # Exit function to prevent further processing during add service

    elif context.user_data.get('awaiting_service_price'):
        try:
            price = int(update.message.text.strip())  # Ensure input is an integer
            context.user_data['service_price'] = price
            context.user_data['awaiting_service_price'] = False
            context.user_data['awaiting_profile_name'] = True  # Next step: Ask for profile name

            await update.message.reply_text(f"قیمت سرویس شما: {price} تومان.\nلطفا نام پروفایل خود را وارد کنید:")
            return  # Exit function
        except ValueError:
            await update.message.reply_text("❌ لطفا یک قیمت معتبر وارد کنید (عدد صحیح).")
            return  # Keep waiting for a valid price

    elif context.user_data.get('awaiting_profile_name'):
        profile_name = update.message.text.strip()
        context.user_data['profile_name'] = profile_name

        # Retrieve saved values
        service_name = context.user_data.get('service_name')
        price = context.user_data.get('service_price')

        # Save the service to the database
        promotion_code = update.message.from_user.id  # Get user ID as promotion code (or other logic)
        save_service(service_name, 'v2ray', profile_name, price, promotion_code)

        await update.message.reply_text(
            f"✅ **سرویس با موفقیت افزوده شد:**\n"
            f"📌 نام سرویس: {service_name}\n"
            f"💰 قیمت: {price} تومان\n"
            f"👤 پروفایل: {profile_name}"
        )

        # Clear user data after successful input
        context.user_data.clear()
        return  # Exit function

    # If the user sends a message without an active state
    else:
        await update.message.reply_text("❌ لطفاً ابتدا دستور /signup یا /add_service را اجرا کنید.")

