import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION (Identique à vos variables sur Render) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def expertise_sabar_digital(prompt_utilisateur):
    """L'intelligence de l'expert Sabar Digital via Groq"""
    
    # Votre ADN d'expert aristocrate
    instructions = (
        "Tu es l'Expert Sabar Digital. Ton ton est aristocratique, raffiné et accueillant. "
        "Tu es un maître du copywriting expérimenté. Pour chaque message, apporte "
        "une solution marketing de haut niveau en utilisant les piliers : "
        "1. COGNITIF (Informer), 2. AFFECTIF (Émotion), 3. CONATIF (Action). "
        "Signe toujours : Sabar digital."
    )

    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt_utilisateur}
        ],
        "temperature": 0.65
    }

    try:
        response = requests.post(url_groq, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erreur technique : {e}")
        return "Toutes mes excuses, cher ami, mais une affaire d'État requiert mon attention immédiate. Sabar digital"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # Appel au cerveau de l'expert
        reponse_finale = expertise_sabar_digital(user_text)

        # Envoi de la réponse sur Telegram
        tel_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tel_url, json={"chat_id": chat_id, "text": reponse_finale})

    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "Sabar Digital est en ligne. Prêt à servir avec distinction. Sabar digital"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
