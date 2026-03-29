import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration des clés (Assurez-vous qu'elles sont sur Render)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def analyser_copywriting_expert(texte_client):
    """L'intelligence de l'expert Sabar via Groq"""
    
    # Le "Prompt" qui définit votre identité d'aristocrate
    system_prompt = (
        "Tu es l'Expert Sabar Digital, un maître du copywriting de haut rang. "
        "Ton ton est aristocratique, raffiné, accueillant, avec une touche d'humour subtile. "
        "Tu analyses chaque texte selon trois axes : "
        "1. Cognitif (clarté du message), 2. Affectif (émotion générée), 3. Conatif (appel à l'action). "
        "Termine toujours tes analyses par la signature exacte : 'Sabar digital'."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-8b-8192", # Modèle ultra-rapide via Groq
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyse ce texte et optimise-le : {texte_client}"}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return "Navré, mon esprit est momentanément indisponible. Sabar digital"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Appel à l'intelligence de l'IA
        reponse_expert = analyser_copywriting_expert(text)

        # Envoi de la réponse sur Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": reponse_expert})

    return jsonify({"status": "ok"})

@app.route('/')
def index():
    return "L'aristocratie du Copywriting est en ligne. Sabar digital"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
