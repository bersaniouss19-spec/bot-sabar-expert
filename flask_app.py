from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Token Sabar Digital
TOKEN = "8432540961:AAE_fTwVhI1sMS9ZS8ylOll2oh6TT_F6J2U"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/')
def index():
    return "<h1>Sabar Digital : Systeme Operationnel sur Render</h1>", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data.get("message", {}).get("text", "")
        
        # Message automatique de l'expert
        response = f"Bonjour Sabar ! Je suis votre bot expert en copywriting. J'ai bien reçu votre message : '{user_text}'. Je suis prêt pour la mission."
        send_message(chat_id, response)
        
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
