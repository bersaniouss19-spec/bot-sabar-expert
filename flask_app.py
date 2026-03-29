import os
from flask import Flask, request
import requests

app = Flask(__name__)

# L'expert récupère sa clé sécurisée depuis les variables de Render
TOKEN = os.environ.get('TELEGRAM_TOKEN')

@app.route('/')
def index():
    return "L'expert Sabar Digital est en ligne et opérationnel !", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # Réponse automatique personnalisée
        reply = f"Bonjour Sabar ! J'ai bien reçu votre message : '{text}'"
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": reply})
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

