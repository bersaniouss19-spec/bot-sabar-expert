import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION DES CLÉS (Variables Render) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
MAKE_WEBHOOK_URL = os.environ.get('MAKE_WEBHOOK_URL')

# --- CONFIGURATION EXPERT SABAR ---
PROMPT_SYSTEME = (
    "Tu es l'Expert Sabar Digital. Ton ton est aristocratique, raffiné, accueillant, "
    "avec une pointe d'humour d'esprit. Tu es un maître du copywriting expérimenté. "
    "Pour chaque message, tu dois apporter une solution marketing de haut niveau en utilisant : "
    "1. L'aspect COGNITIF : Informe et clarifie le message pour l'esprit. "
    "2. L'aspect AFFECTIF : Crée un lien émotionnel fort avec l'audience. "
    "3. L'aspect CONATIF : Pousse à l'action immédiate avec élégance. "
    "Termine TOUJOURS par ta signature : 'Sabar digital'."
)

def appel_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": PROMPT_SYSTEME}, {"role": "user", "content": prompt}],
        "temperature": 0.65
    }
    r = requests.post(url, headers=headers, json=data, timeout=15)
    return r.json()['choices'][0]['message']['content']

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")
        username = data["message"].get("from", {}).get("first_name", "Ami")

        # Exécution de l'expertise
        try:
            reponse = appel_groq(user_text)
        except:
            reponse = "Mon esprit est momentanément indisponible, cher ami. Sabar digital"

        # Envoi à Telegram
        tel_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tel_url, json={"chat_id": chat_id, "text": reponse})

        # Envoi à Make pour vos "Dossiers secrets"
        if MAKE_WEBHOOK_URL:
            requests.post(MAKE_WEBHOOK_URL, json={
                "source": "Telegram Bot",
                "nom": username,
                "message": user_text,
                "reponse_sabar": reponse
            })

    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "Sabar Digital est en ligne."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
