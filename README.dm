# Alias Telegram Bot

This project is a Telegram bot for playing the classic Alias game in Ukrainian.

## Features

- Supports two teams
- Choose word difficulty (simple/hard)
- Automatic score counting
- Round timer (111 seconds)
- Intuitive menu and control buttons
- Win when a team reaches the set score

## Project Structure

- `bot.py` — main Telegram bot code
- `simple_words.txt` — list of simple words
- `hard_words.txt` — list of hard words
- `requirements.txt` — dependencies (pyTelegramBotAPI)

## Installation

1. Install dependencies:
    pip install -r requirements.txt
2. Find BotFather in Telegram and generate your bot token.
3. Add your Telegram Bot Token to the `TOKEN`.
4. Run the bot:
    python bot.py

## Usage

- Go to the bot link (e.g. t.me/classic_alias_bot)
- Use the `/start` command to begin the game.
- Follow the instructions in chat to register teams, choose difficulty, and start
