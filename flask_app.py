import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')

def audit_pagespeed(url_a_tester):
    """Interroge Google PageSpeed Insights pour obtenir le score de performance"""
    # Nettoyage de l'URL au cas où l'utilisateur envoie du texte autour
    url = url_a_tester.strip()
    if not url.startswith("http"):
        url = "https://" + url

    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": PAGESPEED_API_KEY,
        "category": "PERFORMANCE",
        "strategy": "mobile" 
    }
    
    try:
        # L'audit prend du temps, timeout rallongé à 45s
        response = requests.get(endpoint, params=params, timeout=45)
        response.raise_for_status()
        data = response.json()
        
        score = data['lighthouseResult']['categories']['performance']['score'] * 100
        return f"L'analyse de {url} est terminée, cher ami. Le score de performance est de **{int(score)}/100**. C'est une base de travail intéressante. Sabar digital."
    except Exception as e:
        print(f"Erreur PageSpeed : {e}")
        return "Je n'ai pas pu accéder aux registres de performance de ce site. L'URL est-elle correcte ? Sabar digital."

def expertise_sabar_digital(prompt_utilisateur):
    """L'intelligence de l'expert Sabar Digital via Groq"""
    instructions = (
        "Tu es l'Expert Sabar Digital. Ton ton est aristocratique, raffiné et accueillant. "
        "Tu es un maître du copywriting expérimenté. Pour chaque message, apporte "
        "une solution marketing de haut niveau en utilisant les piliers : "
        "1. COGNITIF, 2. AFFECTIF, 3. CONATIF. "
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
        return "Toutes mes excuses, cher ami, mais une affaire d'État requiert mon attention immédiate. Sabar digital"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # --- LOGIQUE DE DÉCISION ---
        # Si le message contient une URL, on lance l'audit, sinon on discute
        if "http" in user_text.lower() or "." in user_text:
            reponse_finale = audit_pagespeed(user_text)
        else:
            reponse_finale = expertise_sabar_digital(user_text)

        # Envoi de la réponse sur Telegram
        tel_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tel_url, json={"chat_id": chat_id, "text": reponse_finale})

    return jsonify({"status": "ok"}), 200
    if __name__ == '__main__':
    # Render utilise la variable d'environnement PORT
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host='0.0.0.0', port=port)

@app.route('/')
def home():
    return "Sabar Digital est en ligne. Prêt à servir avec distinction. Sabar digital"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
