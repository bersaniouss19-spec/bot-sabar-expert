import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Récupération sécurisée du Token via l'environnement
TOKEN = os.environ.get('TELEGRAM_TOKEN')

@app.route('/')
def index():
    return "L'expert Sabar Digital est en ligne et opérationnel !", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Vérification de la structure du message Telegram
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data.get("message", {}).get("text", "")

        # Préparation de la réponse (ton expert et direct)
        reply = f"Bonjour Sabar ! J'ai bien reçu votre message : '{text}'"
        
        # Envoi de la réponse via l'API Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": reply}
        
        try:
            requests.post(url, json=payload, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'envoi : {e}")

    return "OK", 200

if __name__ == '__main__':
    # Configuration du port dynamique pour Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
