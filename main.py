import os
import json
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# ==== TOKEN & WEBHOOK ====
TOKEN = os.environ['TELEGRAM_TOKEN']
URL = os.environ.get('RENDER_EXTERNAL_URL')
bot = Bot(TOKEN)

# ==== FLASK ====
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# ==== Dateinamen ====
players_file = "players.json"
votes_file = "votes.json"
used_words_file = "used_words.json"
game_state_file = "game_state.json"
bot_state_file = "bot_state.json"

# ==== Wortliste (100 Begriffe) ====
all_words = [
    # Essen
    "pizza", "burger", "sushi", "nudeln", "reis", "kartoffeln", "kuchen", "schokolade", "banane", "apfel",
    "birne", "erdbeere", "käse", "wurst", "lachs", "steak", "hähnchen", "salat", "wrap", "taco",

    # Spicy
    "stripclub", "kondom", "orgasmus", "sex", "porno", "lust", "knutschen", "fetisch", "escort", "spielzeug",
    "dirty talk", "nackt", "one night stand", "quickie", "verführung", "handschellen", "leder", "nachttisch", "schnaps", "cocktail",

    # Hobbies
    "lesen", "zeichnen", "tanzen", "singen", "gärtnern", "schwimmen", "joggen", "radfahren", "fotografieren", "kochen",
    "backen", "reisen", "stricken", "basteln", "filme", "serien", "angeln", "reiten", "schach", "yoga",

    # Gegenstände
    "tasse", "stuhl", "tisch", "lampe", "schlüssel", "messer", "brille", "telefon", "rucksack", "schirm",
    "heft", "stift", "akku", "ladekabel", "bildschirm", "maus", "fernseher", "kissen", "matratze", "uhr"
]

# ==== Hilfsfunktionen ====
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def get_bot_state():
    try:
        with open(bot_state_file, "r") as f:
            return json.load(f)
    except:
        return {}

def set_bot_state(key, value):
    state = get_bot_state()
    state[key] = value
    save_json(bot_state_file, state)

def clear_bot_state(key):
    state = get_bot_state()
    state.pop(key, None)
    save_json(bot_state_file, state)

def reset_game():
    for f in [players_file, votes_file, game_state_file]:
        save_json(f, [])
    clear_bot_state('awaiting')

# ==== Bot-Kommandos ====
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Willkommen beim Imposter-Spiel! Tippe /join um mitzumachen.")

def join(update: Update, context: CallbackContext):
    players = set(load_json(players_file))
    players.add(update.effective_user.id)
    save_json(players_file, list(players))
    update.message.reply_text("✅ Du bist im Spiel.")

def spieler(update: Update, context: CallbackContext):
    players = load_json(players_file)
    if not players:
        update.message.reply_text("👥 Es haben sich noch keine Spieler angemeldet.")
        return
    namen = []
    for uid in players:
        try:
            user = bot.get_chat(uid)
            namen.append(user.first_name)
        except:
            namen.append(str(uid))
    text = "👥 Aktuelle Spieler:\n" + "\n".join(namen)
    update.message.reply_text(text)
    
def startgame(update: Update, context: CallbackContext):
    players = load_json(players_file)
    if len(players) < 2:
        update.message.reply_text("❗ Mindestens 2 Spieler:innen nötig.")
        return
    set_bot_state('awaiting', 'trigger')
    update.message.reply_text("🕹️ Schreibe jetzt etwas, um das Spiel zu starten!")

def vote(update: Update, context: CallbackContext):
    update.message.reply_text("✉️ Stimme anonym ab: /vote @username")

def handle_vote(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if not text.startswith("/vote"):
        return
    try:
        voted_id = int(text.split()[1].replace("@", ""))
    except:
        update.message.reply_text("❌ Ungültige Stimme.")
        return
    votes = load_json(votes_file)
    votes.append(voted_id)
    save_json(votes_file, votes)
    players = load_json(players_file)
    if len(votes) >= (len(players) // 2 + 1):
        imposter = load_json(game_state_file).get("imposter")
        winner = "CREWMATES" if votes.count(imposter) > len(players) // 2 else "IMPOSTER"
        update.message.reply_text(f"🏆 {winner} GEWINNT!")
        update.message.reply_text("🔁 Neue Runde starten? 'ja' oder 'nein'")
        set_bot_state('awaiting', 'restart')

# ==== Spiel-Logik ====
def handle_all_messages(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower().lstrip("/")
    user_id = update.effective_user.id
    awaiting = get_bot_state().get('awaiting')

    if awaiting == 'trigger':
        used_words = load_json(used_words_file)
        available = [w for w in all_words if w not in used_words]
        if not available:
            used_words = []
            available = all_words[:]
        word = random.choice(available)
        used_words.append(word)
        save_json(used_words_file, used_words)
        players = load_json(players_file)
        imposter = random.choice(players)
        random.shuffle(players)

        for uid in players:
            try:
                if uid == imposter:
                    bot.send_message(uid, "🤫 Du bist der IMPOSTER! Sag nichts.")
                else:
                    bot.send_message(uid, f"🔤 Dein Wort ist: {word}")
            except:
                continue

        save_json(game_state_file, {"word": word, "imposter": imposter})
        clear_bot_state('awaiting')

        msg = "💬 Schreibreihenfolge:\n"
        for i, uid in enumerate(players):
            try:
                user = bot.get_chat(uid)
                msg += f"{i+1}. {user.first_name}\n"
            except:
                continue
        update.message.reply_text(msg + "➡️ Jetzt schreibt jede:r in dieser Reihenfolge eine Nachricht.")
        return

    if awaiting == 'restart':
        if text == 'ja':
            reset_game()
            update.message.reply_text("🔄 Neues Spiel! Tippt wieder /join.")
        elif text == 'nein':
            update.message.reply_text("🛑 Spiel beendet.")
        clear_bot_state('awaiting')
        return

    state = load_json(game_state_file)
    if state and 'word' in state:
        word = state['word'].lower()
        if word in text:
            update.message.reply_text("💥 IMPOSTER GEWONNEN!")
            update.message.reply_text("🔁 Neue Runde starten? Antworte mit 'ja' oder 'nein'")
            set_bot_state('awaiting', 'restart')

# ==== Telegram Dispatcher ====
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("join", join))
dispatcher.add_handler(CommandHandler("startgame", startgame))
dispatcher.add_handler(CommandHandler("vote", vote))
dispatcher.add_handler(CommandHandler("spieler", spieler))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_all_messages))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, handle_vote))

# ==== Webhook Routen ====
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Bot is running!'

# ==== Start ====
if __name__ == '__main__':
    bot.set_webhook(f"{URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
