import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION DES CLÉS (A remplir sur Render) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def expertise_sabar_digital(prompt_utilisateur):
    """L'intelligence artificielle de l'expert Sabar"""
    
    # LE PROMPT SYSTEME : C'est ici que réside votre âme d'expert
    instructions_aristocrate = (
        "Tu es l'Expert Sabar Digital. Ton ton est aristocratique, raffiné, accueillant, "
        "avec une pointe d'humour d'esprit. Tu es un maître du copywriting expérimenté. "
        "Pour chaque message, tu dois apporter une solution marketing de haut niveau en utilisant : "
        "1. L'aspect COGNITIF : Informe et clarifie le message pour l'esprit. "
        "2. L'aspect AFFECTIF : Crée un lien émotionnel fort avec l'audience. "
        "3. L'aspect CONATIF : Pousse à l'action immédiate avec élégance. "
        "Tu résous les problèmes des entreprises et des clients avec une précision chirurgicale. "
        "Termine TOUJOURS par ta signature : 'Sabar digital'."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Utilisation du modèle Llama 3 via Groq pour une vitesse 'Formule 1'
    data = {
        "model": "llama3-70b-8192", 
        "messages": [
            {"role": "system", "content": instructions_aristocrate},
            {"role": "user", "content": prompt_utilisateur}
        ],
        "temperature": 0.65
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=15)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return "Toutes mes excuses, cher ami, mais mon esprit est momentanément accaparé par une autre affaire d'État. Sabar digital"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # On appelle le cerveau de l'IA
        reponse_finale = expertise_sabar_digital(user_text)

        # On renvoie la réponse sur Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": reponse_finale})

    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return "L'agence Sabar Digital est en ligne. Prêt à servir. Sabar digital"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
