import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Sabar Digital : Systeme Operationnel sur Render</h1>", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    return "OK", 200

if __name__ == "__main__":
    # Render utilise dynamiquement le port 10000 ou celui de l'environnement
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
