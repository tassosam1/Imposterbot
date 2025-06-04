import os
import json
import random
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ['TELEGRAM_TOKEN']
bot = Bot(TOKEN)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# -------------------- Wortlisten --------------------
categories = {
    "alles": [],
    "tiere": [
        "Hund", "Katze", "Maus", "Fisch", "Adler", "Esel", "Pferd", "Löwe", "Elefant", "Schlange",
        "Tiger", "Panther", "Wal", "Hai", "Zebra", "Giraffe", "Frosch", "Kröte", "Huhn", "Kuh",
        "Schaf", "Geiß", "Igel", "Fuchs", "Dachs", "Marder", "Schwein", "Hirsch", "Reh", "Ameise",
        "Biene", "Wespe", "Hornisse", "Spinne", "Krebs", "Qualle", "Seestern", "Tintenfisch", "Robbe", "Delphin",
        "Papagei", "Taube", "Kanarienvogel", "Pfau", "Strauß", "Flamingo", "Waschbär", "Murmel", "Wiesel", "Otter"
    ],
    "essen": [
        "Pizza", "Burger", "Salat", "Banane", "Currywurst", "Suppe", "Spaghetti", "Döner", "Apfel", "Käse",
        "Toast", "Croissant", "Schnitzel", "Bockwurst", "Ravioli", "Chili", "Pfannkuchen", "Brot", "Reis", "Couscous",
        "Steak", "Torte", "Kuchen", "Eis", "Pudding", "Joghurt", "Müsli", "Cornflakes", "Milch", "Wasser",
        "Saft", "Smoothie", "Kaffee", "Tee", "Cola", "Fanta", "Pommes", "Chips", "Kekse", "Gummibärchen",
        "Schokolade", "Lakritz", "Zuckerwatte", "Creme", "Lasagne", "Wrap", "Sushi", "Tofu", "Falafel", "Kichererbse"
    ],
    "spicy": [
        "Stripclub", "Kondom", "Exfreundin", "Porno", "Seitensprung", "Handschellen", "One Night Stand",
        "Affäre", "Erotik", "Lust", "Nackt", "Dessous", "Sexspielzeug", "Dirty Talk", "Blindfold", "Massageöl", "Gleitgel", "Latex", "Peitsche", "Fessel",
        "Intimrasur", "Tinder", "Sexdate", "Fetisch", "Lover", "Quickie", "One-Night-Stand", "Hintern", "Brüste", "Lustobjekt",
        "Dominanz", "Unterwerfung", "Nippel", "Kamasutra", "Stöhn", "Sexting", "Pornosite", "Webcam", "Camgirl", "Callboy",
        "Sexfilm", "Oralsex", "Dirty Pics", "Pikant", "Verführer", "Reizwäsche", "Nylon", "Korsett", "BDSM", "Stöckelschuh"
    ],
    "arbeit": [
        "Chef", "Laptop", "Schreibtisch", "Büro", "Kaffeepause", "Meeting", "Deadline",
        "Protokoll", "Vertrag", "Drucker", "E-Mail", "Telefon", "Kollege", "Projekt", "Leitung", "Pause", "Urlaub", "Homeoffice", "Zeiterfassung", "Mitarbeiter",
        "Gehaltsabrechnung", "Lohn", "Team", "Arbeitsplatz", "Anruf", "Besprechung", "Kantine", "Auftrag", "Excel", "PowerPoint",
        "Chefsekretär", "Mitarbeiterin", "Projektmanager", "Kopierer", "Scanner", "Server", "Ablage", "Bewerbung", "Stellenanzeige", "Stempeluhr",
        "Pendler", "Vertrieb", "Kundengespräch", "Meetingraum", "Whiteboard", "Mitarbeitergespräch", "Chefetage", "Firmenausweis", "Personalakte", "Zeugnis"
    ],
    "gegenstände": [
        "Lampe", "Tisch", "Rucksack", "Glas", "Handy", "Stuhl", "Regenschirm", "Schere",
        "Messer", "Gabel", "Löffel", "Teller", "Becher", "Fernbedienung", "Wecker", "Kamera", "Schrank", "Spiegel", "Kissen",
        "Decke", "Stift", "Block", "Heft", "Taschenlampe", "Feuerzeug", "Flasche", "Zahnbürste", "Seife", "Badeente",
        "Kamm", "Bügeleisen", "Staubsauger", "Laptop", "Monitor", "Tastatur", "Maus", "Ladegerät", "Kabel", "Schraubenzieher",
        "Hammer", "Nagel", "Bohrer", "Besen", "Schwamm", "Waschmittel", "Mülleimer", "Kerze", "Batterie", "Uhr"
    ],
    "hobbies": [
        "Lesen", "Schwimmen", "Gitarre", "Gaming", "Malen", "Fotografieren", "Backen",
        "Kochen", "Wandern", "Joggen", "Fahrradfahren", "Skaten", "Basteln", "Gärtnern", "Reiten", "Schreiben", "Zeichnen", "Origami", "Tanzen",
        "Singen", "Musik machen", "Stricken", "Häkeln", "Angeln", "Klettern", "Yoga", "Meditieren", "Schach", "Brettspiele",
        "Videospiele", "Filme schauen", "Serien schauen", "Bloggen", "Podcasten", "Heimwerken", "Modellbau", "Astronomie", "Vögel beobachten", "Kochvideos drehen",
        "Cocktails mixen", "Instrumente spielen", "Improtheater", "Kunst machen", "Sprachen lernen", "Leserunden", "Zaubern", "Speedcubing", "Parkour", "Slacklinen"
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

def handle_all_messages(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id

    awaiting = context.bot_data.get('awaiting')

    # Kategorieeingabe
    if awaiting == 'category':
        if text not in categories:
            update.message.reply_text("❌ Unbekannte Kategorie. Versuch es erneut.")
            return
        players = load_json(players_file)
        word = get_category_word(text)
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

    # Neustart
    if awaiting == 'restart':
        if text == 'ja':
            reset_game()
            update.message.reply_text("🆕 Neue Runde: Alle bitte /join tippen!")
        elif text == 'nein':
            update.message.reply_text("🛑 Spiel beendet.")
        context.bot_data['awaiting'] = None
        return

    # Wortüberprüfung
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
dispatcher.add_handler(MessageHandler(Filters.text, handle_all_messages))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, handle_vote))

updater.start_polling()
updater.idle()
