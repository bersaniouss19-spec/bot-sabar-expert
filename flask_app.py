import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')

def audit_pagespeed(url_a_tester):
    """EXÉCUTION : Analyse technique profonde via Google"""
    url = url_a_tester.strip()
    if not url.startswith("http"):
        url = "https://" + url
    
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url, 
        "key": PAGESPEED_API_KEY, 
        "category": ["PERFORMANCE", "SEO"], 
        "strategy": "mobile"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=70)
        data = response.json()
        
        # Extraction des données d'exécution
        lighthouse = data['lighthouseResult']
        score = lighthouse['categories']['performance']['score'] * 100
        
        # Temps de chargement (LCP) et Interactivité (TBT)
        lcp = lighthouse['audits']['largest-contentful-paint']['displayValue']
        tbt = lighthouse['audits']['total-blocking-time']['displayValue']
        
        return (
            f"⚔️ **ORDRE D'AUDIT EXÉCUTÉ** ⚔️\n\n"
            f"Analyse de : {url}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"● **Score Performance** : {int(score)}/100\n"
            f"● **Chargement (LCP)** : {lcp}\n"
            f"● **Blocage (TBT)** : {tbt}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Cher ami, les chiffres parlent. Voici la réalité technique de ce domaine. Sabar digital."
        )
    except Exception as e:
        return f"L'exécution a rencontré un obstacle technique. Vérifiez l'URL. Sabar digital."

def expertise_sabar_digital(prompt):
    """PAROLE : Conseil stratégique via Groq"""
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    instructions = (
        "Tu es l'Expert Sabar Digital. Ton ton est aristocratique et tranchant. "
        "Applique les piliers : 1. COGNITIF, 2. AFFECTIF, 3. CONATIF. "
        "Signe toujours : Sabar digital."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": instructions}, {"role": "user", "content": prompt}],
        "temperature": 0.6
    }
    try:
        res = requests.post(url_groq, headers=headers, json=data, timeout=25)
        return res.json()['choices'][0]['message']['content']
    except:
        return "Une affaire d'État requiert mon attention immédiate. Sabar digital."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "").strip()

        if not user_text:
            return jsonify({"status": "ok"}), 200

        # DÉTECTION STRICTE : URL seule = ACTION / Texte = PAROLE
        if "." in user_text and " " not in user_text:
            # On informe l'utilisateur que l'action est lancée
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": "Bien reçu. Je lance l'audit technique de ce pas... ⏳"})
            
            reponse = audit_pagespeed(user_text)
        else:
            reponse = expertise_sabar_digital(user_text)

        # Envoi du résultat final
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": chat_id, "text": reponse})
    
    return jsonify({"status": "ok"}), 200

@app.route('/')
def home():
    return "Sabar Digital : Prêt à l'exécution."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
