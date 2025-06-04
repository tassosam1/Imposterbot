import os
import json
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ['TELEGRAM_TOKEN']
URL = os.environ.get('RENDER_EXTERNAL_URL')  # Render setzt diese automatisch
bot = Bot(TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# -------------------- Wortlisten --------------------
categories = {
    "alles": [],  # wird automatisch befüllt
    "tiere": [
        "hund", "katze", "löwe", "tiger", "bär", "affe", "pferd", "maus", "elefant", "giraffe",
        "schwein", "huhn", "ente", "eule", "delfin", "fuchs", "wolf", "kaninchen", "schildkröte", "krokodil",
        "ziege", "schaf", "hase", "pinguin", "wal", "krabbe", "hai", "adler", "papagei", "specht",
        "pferd", "meerschweinchen", "ameise", "biene", "käfer", "schlange", "echse", "frosch", "storch", "sträuß",
        "waschbär", "marder", "alpaka", "lama", "otter", "wiesel", "gepard", "panther", "pfau", "molch"
    ],
    "essen": [
        "pizza", "burger", "nudeln", "sushi", "reis", "kartoffeln", "brötchen", "toast", "kuchen", "schokolade",
        "keks", "banane", "apfel", "birne", "erdbeere", "schinken", "käse", "wurst", "lachs", "steak",
        "hähnchen", "pommes", "salat", "müsli", "joghurt", "milch", "quark", "honig", "marmelade", "brot",
        "wrap", "taco", "lasagne", "suppe", "gulasch", "curry", "chips", "donut", "pudding", "tomate",
        "gurke", "zwiebel", "knoblauch", "paprika", "mais", "avocado", "kakao", "cola", "saft", "eis"
    ],
    "spicy": [
        "stripclub", "alkohol", "nackt", "affäre", "kondom", "orgasmus", "sex", "porno", "unterwäsche", "lust",
        "knutschen", "fetisch", "flirt", "escort", "kater", "joint", "katerfrühstück", "spielzeug", "dirty talk", "kneipe",
        "dates", "one night stand", "handcuffs", "liebesbrief", "whatsapp", "flachgelegt", "nacktbilder", "massageöl", "sexting", "verführung",
        "balkon", "quickie", "geheimnis", "schlüpfer", "gleitmittel", "hängematte", "urlaubsliebe", "pick-up", "bar", "hotel",
        "schnaps", "bier", "cocktail", "stripper", "spiegel", "handschellen", "nachttisch", "zimmer", "nippel", "leder"
    ],
    "arbeit": [
        "meeting", "chef", "büro", "lohn", "vertrag", "pause", "drucker", "kaffee", "projekt", "maus",
        "email", "notebook", "deadline", "besprechung", "stift", "praktikum", "bewerbung", "urlaub", "stress", "kollege",
        "leiter", "druck", "papier", "ablage", "arbeitszeit", "stempel", "pause", "kopierer", "arbeitsvertrag", "lohnabrechnung",
        "team", "zoom", "anruf", "storno", "dienstreise", "tagesordnung", "aufgabe", "ziel", "vorgesetzter", "feedback",
        "planung", "arbeitsplatz", "open space", "co-working", "whiteboard", "leiterin", "umsatz", "bericht", "kalkulation", "excel"
    ],
    "gegenstände": [
        "tasse", "buch", "stuhl", "tisch", "lampe", "schlüssel", "messer", "brille", "telefon", "handy",
        "rucksack", "schirm", "heft", "kugelschreiber", "akku", "ladekabel", "bildschirm", "maus", "fernseher", "box",
        "kissen", "matratze", "uhr", "kamera", "fahrrad", "helm", "jacke", "schuh", "socke", "hose",
        "tür", "fenster", "batterie", "seife", "zahnbürste", "shampoo", "schere", "kerze", "feuerzeug", "decke",
        "mikrofon", "waschmaschine", "ventilator", "rucksack", "lupe", "lineal", "notizblock", "ordner", "drucker", "radio"
    ],
    "hobbies": [
        "lesen", "zeichnen", "kochen", "tanzen", "singen", "gärtnern", "schwimmen", "joggen", "radfahren", "fotografieren",
        "schreiben", "backen", "spielen", "reisen", "nähen", "stricken", "basteln", "filme", "serien", "angeln",
        "reiten", "schach", "yoga", "klettern", "wandern", "campen", "gamen", "gitarre", "piano", "zeichnen",
        "skaten", "basketball", "fußball", "geocaching", "puzzeln", "kartenspiele", "imkern", "segeln", "tauchen", "surfen",
        "modellbau", "magie", "drohnen", "videodreh", "tik-tok", "podcast", "schreiben", "karaoke", "autotuning", "spazieren"
    ]
}

for k, lst in categories.items():
    if k != "alles":
        categories["alles"].extend(lst)

players_file = "players.json"
votes_file = "votes.json"
used_words_file = "used_words.json"
chat_order_file = "chat_order.json"
game_state_file = "game_state.json"

# -------------------- Hilfsfunktionen --------------------
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return [] if filename.endswith(".json") else {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def get_category_word(category):
    used_words = load_json(used_words_file)
    if category not in used_words:
        used_words[category] = []
    available = [w for w in categories[category] if w not in used_words[category]]
    if not available:
        used_words[category] = []
        available = categories[category][:]
    if not available:
        return None
    word = random.choice(available)
    used_words[category].append(word)
    save_json(used_words_file, used_words)
    return word.lower()

def reset_game():
    for f in [players_file, votes_file, chat_order_file, game_state_file]:
        save_json(f, [])

# -------------------- Bot-Befehle --------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Willkommen beim Imposter-Spiel!")

def join(update: Update, context: CallbackContext):
    players = set(load_json(players_file))
    players.add(update.effective_user.id)
    save_json(players_file, list(players))
    update.message.reply_text("✅ Du bist dabei.")

def startgame(update: Update, context: CallbackContext):
    players = load_json(players_file)
    if len(players) < 3:
        update.message.reply_text("❗ Mindestens 3 Spieler:innen nötig.")
        return
    update.message.reply_text("Bitte gib eine Kategorie ein (z.B. tiere, essen, spicy, arbeit, gegenstände, hobbies, alles):")
    context.bot_data['awaiting'] = 'category'

def kategorien(update: Update, context: CallbackContext):
    update.message.reply_text("📚 Verfügbare Kategorien:\n" + ", ".join(categories.keys()))

def handle_all_messages(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id

    awaiting = context.bot_data.get('awaiting')

    if awaiting == 'category':
        if text not in categories:
            update.message.reply_text("❌ Unbekannte Kategorie. Versuch es erneut.")
            return
        if not categories[text]:
            update.message.reply_text("⚠️ Diese Kategorie ist leer. Bitte andere wählen.")
            return
        players = load_json(players_file)
        word = get_category_word(text)
        if word is None:
            update.message.reply_text("⚠️ In dieser Kategorie sind keine Wörter mehr übrig. Bitte andere wählen.")
            return
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
        save_json(chat_order_file, players)
        context.bot_data['awaiting'] = None

        msg = "💬 Schreibreihenfolge:\n"
        for i, uid in enumerate(players):
            try:
                user = bot.get_chat(uid)
                msg += f"{i+1}. {user.first_name}\n"
            except:
                continue
        update.message.reply_text(msg + "\n➡️ Bitte in dieser Reihenfolge eine Nachricht im Gruppenchat schreiben.")
        return

    if awaiting == 'restart':
        if text == 'ja':
            reset_game()
            update.message.reply_text("🆕 Neue Runde: Alle bitte /join tippen!")
        elif text == 'nein':
            update.message.reply_text("🛑 Spiel beendet.")
        context.bot_data['awaiting'] = None
        return

    state = load_json(game_state_file)
    if state and 'word' in state:
        word = state['word'].lower()
        if word in text:
            update.message.reply_text("💥 IMPOSTER GEWONNEN!")
            update.message.reply_text("🔁 Neue Runde starten? Antworte mit 'ja' oder 'nein'")
            context.bot_data['awaiting'] = 'restart'
            return

def vote(update: Update, context: CallbackContext):
    update.message.reply_text("✉️ Bitte stimme anonym ab: /vote @username")

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
        context.bot_data['awaiting'] = 'restart'

# -------------------- Dispatcher --------------------
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("join", join))
dispatcher.add_handler(CommandHandler("startgame", startgame))
dispatcher.add_handler(CommandHandler("vote", vote))
dispatcher.add_handler(CommandHandler("kategorien", kategorien))
dispatcher.add_handler(MessageHandler(Filters.text, handle_all_messages))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, handle_vote))

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Bot is running!'
    
if __name__ == '__main__':
    bot.set_webhook(f"{URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
