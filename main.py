import os
import json
import random
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ['TELEGRAM_TOKEN']
bot = Bot(TOKEN)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

word_list = [
    "Apfel", "Banane", "Haus", "Auto", "Katze", "Hund", "Buch", "Berg", "Pizza", "Baum",
    "Fluss", "Lampe", "Stuhl", "Fenster", "Brille", "Zug", "Schule", "Tasche", "Kaffee", "Tisch"
]

def load_players():
    try:
        with open("players.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_players(players):
    with open("players.json", "w") as f:
        json.dump(list(players), f)

def load_used_words():
    try:
        with open("used_words.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_used_words(used_words):
    with open("used_words.json", "w") as f:
        json.dump(list(used_words), f)

def get_unused_word():
    used = load_used_words()
    unused = [w for w in word_list if w not in used]
    if not unused:
        return None
    word = random.choice(unused)
    used.add(word)
    save_used_words(used)
    return word

def reset_game():
    save_players(set())
    save_used_words(set())
    print("🔁 Spiel wurde zurückgesetzt.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Willkommen beim Imposter-Spiel!\n"
        "Mit /join kannst du mitspielen.\n"
        "Mit /startgame startet das Spiel.\n"
        "Wer das geheime Wort im Chat nennt, beendet das Spiel!"
    )

def join(update: Update, context: CallbackContext):
    players = load_players()
    uid = update.effective_user.id
    if uid in players:
        update.message.reply_text("✅ Du bist bereits dabei.")
    else:
        players.add(uid)
        save_players(players)
        update.message.reply_text("👍 Du wurdest zur Spielerliste hinzugefügt.")

def startgame(update: Update, context: CallbackContext):
    players = load_players()
    if len(players) < 3:
        update.message.reply_text("❗ Mindestens 3 Spieler:innen nötig.")
        return

    word = get_unused_word()
    if not word:
        update.message.reply_text("📃 Alle Wörter wurden bereits verwendet.")
        return

    imp = random.choice(list(players))
    for uid in players:
        try:
            if uid == imp:
                bot.send_message(uid, "🤫 Du bist der IMPOSTER!\nSag nichts!")
            else:
                bot.send_message(uid, f"🔤 Dein Wort ist: {word}")
        except:
            update.message.reply_text(f"⚠️ Konnte Spieler {uid} nicht erreichen.")

    context.bot_data['active_word'] = word
    context.bot_data['imposter'] = imp
    update.message.reply_text("🎭 Spiel gestartet! Rollen wurden privat verteilt.")

def handle_message(update: Update, context: CallbackContext):
    if 'active_word' not in context.bot_data:
        return

    text = update.message.text.strip().lower()
    target = context.bot_data['active_word'].lower()

    if text == target:
        update.message.reply_text(
            f"💥 Das geheime Wort **{target}** wurde genannt!\n"
            f"🎮 Spiel ist beendet – alle zurück auf /join!"
        )
        reset_game()

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("join", join))
dispatcher.add_handler(CommandHandler("startgame", startgame))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, handle_message))

updater.start_polling()
