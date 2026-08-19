### Personal logging of changes
#
# ??? : Creation of the bot
# 19/8/2026: Added help, budget command, and set_commands because I thought it would look cooler hahaha, also updated my personal budget db after reviewing my finances lol

# Import standard modules
from decimal import InvalidOperation
from pathlib import Path
import asyncio
import logging
import sys
from dotenv import load_dotenv
import os

# Import telebot modules
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, BotCommand

# Import parser modules
from parser.expense_parser import parse_tele_text
from database.expense_functions import insert_expense, update_expense, show_budget

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

## Gives me the created commands as of now to get quick infos (But like, not completed.. soon haha)
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show this message"),
        BotCommand(command="ping", description="Check if I am online"),
        BotCommand(command="echo", description="I will repeat your text"),
        BotCommand(command="budget", description="Check your budget")
    ]
    await bot.set_my_commands(commands)

@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    help_text = (
        'Here are my commands:\n'
        '/start - Start the bot\n'
        '/help - Show this message\n'
        '/ping - Check if I am online\n'
        '/echo &lt;text&gt; - I will repeat your text\n'
        '/budget - Check your remaining budget'
    )
    await message.answer(help_text)

@dp.message(Command("budget"))
async def show_budget_command(message: Message) -> None:
    """
    This handler receives messages with `/budget` command
    """
    # Here you can implement the logic to show the user's budget

    # Display the remaining budgets for each category
    remaining_budget = show_budget()
    lines = []

    for line in remaining_budget:
        cat_name, sub_cat, remaining_budget = line
        lines.append(
            f"Remaining budget for {cat_name} - {sub_cat}: {remaining_budget / 100:.2f}"
        )
        
    await message.answer("\n".join(lines))

    await message.answer("Your budget details will be shown here.")

@dp.message()
async def handle_messages(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Segmented part of the code to parse the Telegram message text and extract expense information
        dateOfMessage = message.date.astimezone().isoformat()
        chatId = message.chat.id
        messageId = message.message_id
        expense_name, expense_amount, category_name, subcategory = parse_tele_text(message.text)
        print(f"Expense Name: {expense_name}, Amount: {expense_amount}, Category: {category_name}, Subcategory: {subcategory}")

        remaining_budgets = insert_expense(expense_name, expense_amount, dateOfMessage, category_name, subcategory, chatId, messageId)

        # Display the remaining budgets for each category
        lines = []
        for cat_name, sub_cat, remaining_budget in remaining_budgets:
            lines.append(
                f"Remaining budget for {cat_name} - {sub_cat}: {remaining_budget / 100:.2f}"
            )
        await message.answer("\n".join(lines))

        # await message.send_copy(chat_id=message.chat.id)
    except (TypeError, ValueError, InvalidOperation) as e:
        # But not all the types is supported to be copied so need to handle it
        await message.answer(f"knn,,, {str(e)}")

@dp.edited_message()
async def handle_edited_messages(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Segmented part of the code to parse the Telegram message text and extract expense information
        dateOfMessage = message.date.astimezone().isoformat()
        chatId = message.chat.id
        messageId = message.message_id
        expense_name, expense_amount, category_name, subcategory = parse_tele_text(message.text)
        print(f"Expense Name: {expense_name}, Amount: {expense_amount}, Category: {category_name}, Subcategory: {subcategory}")

        remaining_budgets = update_expense(expense_name, expense_amount, dateOfMessage, category_name, subcategory, chatId, messageId)

        # Display the remaining budgets for each category
        lines = []

        for cat_name, sub_cat, remaining_budget in remaining_budgets:
            lines.append(
                f"Remaining budget for {cat_name} - {sub_cat}: {remaining_budget / 100:.2f}"
            )

        await message.answer("\n".join(lines))

        # await message.send_copy(chat_id=message.chat.id)
    except (TypeError, ValueError, InvalidOperation) as e:
        # But not all the types is supported to be copied so need to handle it
        await message.answer(f"knn,,, {str(e)}")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    load_dotenv(PROJECT_ROOT / ".env")
    token = os.getenv("BUDGET_TELEGRAM_BOT")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())