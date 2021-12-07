#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "https://github.com/rizorko"
__copyright__ = "Copyright (C) 2021"
__audience__ = "Specially for Dmitriy Sorkin and K_3_D community"
__license__ = "CC-BY (https://creativecommons.org/licenses/by/4.0/)"
__version__ = "0.2"

import os
import sys

# Python 2 & 3 compatability 
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

# Telegram packages
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, TelegramError)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

# Setting up logging
import logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global valiables
global chat_username
global bot_token

global bot


def start(update, context):
    # Dummy /start callback
    update.message.reply_text('Здесь ничего нет, совсем 🤨')


def chat(update, context):
    # /chat callback, returns sender and chat id's (debug)
    update.message.reply_text("user_id = {0}, chat_id = {1}".format(update.from_user.id, update.chat.id))

def handle_chat_message(update, context):
    # logger.info(update)
    # This condition should not fire, but checking it just to be sure
    if (not hasattr(update, 'message')):
        logger.info("Received an update from chat (ID: "+ str(update.channel_post.message_id) +"), but it's not a Chat message Post, skipping")

        return

    message = update.message
    voice = getattr(message, "voice", None)
    if voice is not None:
        logger.info("Received new voice message , it's ID: " + str(update.message.message_id) + ", deleting")
        bot.delete_message("@" + chat_username, update.message.message_id)
        return
    
    sender_chat = getattr(message, "sender_chat", None)
    if sender_chat is not None:
        logger.info("Received new sender_chat message , it's ID: " + str(update.message.message_id) + ", deleting")
        bot.delete_message("@" + chat_username, update.message.message_id)
        return


def create_config():
    # Creating (or overwriting) config with default settings
    config = configparser.ConfigParser()
    config.add_section("Bot")
    config.set("Bot", "token", "set_me")
    config.set("Bot", "chat_username", "@set_me")
    
    # Writing settings to config file
    with open("config.ini", "w") as config_file:
        config.write(config_file)


def validate_config(config):
    # Getting config options
    bot_token = config.get("Bot", "token")
    chat_username = config.get("Bot", "chat_username")

    # Checking wether config options are the default ones
    if (bot_token == "set_me" or chat_username == "@set_me"):
        # If yes — config is invalid
        return False
    else:
        #If no — overwrite global variables with config values
        globals()['bot_token'] = bot_token
        globals()['chat_username'] = chat_username
        return True

def handle_errors(update, context):
    # Wow
    logger.error("An unhandled error raised: ")
    logger.error(context.error)


def main():
    logger.info("Initializing K3D Sentinel bot...")

    # Checking config file existance
    if (not os.path.exists("config.ini")):
        # Create if doesn't exist
        logger.info("Creating default config, please fill it with correct values and restart me")
        create_config()
        # Exit
        sys.exit()
        return


    # Loading config
    config = configparser.ConfigParser()
    config.read("config.ini")

    #Validating it
    if (not validate_config(config)):
        logger.info("Please check if you've changed default settings in ./config.ini")
        # Exit
        sys.exit()
        return

    # Dumping settings to screen
    logger.info("Chat username: " + chat_username)

    # Setting up Telegram bot and updae listener using token
    globals()['bot'] = Bot(bot_token)

    bot_username = bot.get_me().username
    logger.info("Bot: @{0} <https:/t.me/{0}>".format(bot_username))

    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('chat', chat))
    # Receive only messages from specified Chat (config)
    dp.add_handler(MessageHandler(Filters.chat(username=chat_username), handle_chat_message, pass_chat_data=True))
    # Handling errors globally (but there should not be any)
    dp.add_error_handler(handle_errors)

    logger.info("Starting the mighty Sentinel bot!")
    # Start polling for updates
    updater.start_polling()
    logger.info("Bot started, ready to work")

    # Idle bot while it's working (wait for SIGINT, SIGTERM)
    updater.idle()


if __name__ == '__main__':
    main()