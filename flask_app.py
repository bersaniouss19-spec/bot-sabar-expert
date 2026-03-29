import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Récupération du Token sécurisé
TOKEN = os.environ.get('TELEGRAM_TOKEN')

@app.route('/')
def index():
    return "L'expert Sabar Digital est en ligne !", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # 1. On prépare la réponse
        reply = f"Bonjour Sabar ! J'ai bien reçu votre message : '{text}'"
        
        # 2. ON ENVOIE RÉELLEMENT LE MESSAGE (C'est ce qui manquait)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": reply}
        requests.post(url, json=payload)

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
