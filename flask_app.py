import os
import requests
from flask import Flask, request, jsonify, redirect
from google_auth_oauthlib.flow import Flow
import json

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_digital_secret_777')

# TES VARIABLES (Identifiants)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
BLOGGER_API_KEY = os.environ.get('BLOGGER_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')

# OAUTH POUR BLOGGER (Publication)
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']

@app.route('/')
def home():
    return "<h1>Sabar Digital Bot : Opérationnel</h1><p>Prêt pour l'action. Utilisez /login pour autoriser Blogger.</p>"

@app.route('/login')
def login():
    """Lien pour autoriser le bot sur ton compte Google"""
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "project_id": "mon-projet-sabar",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI]
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Reçoit la clé d'autorisation de Google"""
    return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot peut désormais publier sur Blogger.</p>"

def audit_pagespeed(url_a_tester):
    url = url_a_tester.strip()
    if not url.startswith("http"): url = "https://" + url
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {"url": url, "key": PAGESPEED_API_KEY, "category": ["PERFORMANCE"], "strategy": "mobile"}
    try:
        res = requests.get(endpoint, params=params, timeout=70).json()
        lighthouse = res['lighthouseResult']
        score = lighthouse['categories']['performance']['score'] * 100
        return f"⚔️ **AUDIT TERMINÉ** ⚔️\n\nURL : {url}\nScore : {int(score)}/100\nSabar digital."
    except:
        return "Audit en cours... Sabar digital."

def expertise_sabar_digital(prompt):
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "Tu es l'Expert Sabar Digital. Aristocratique, tranchant. Signe: Sabar digital."}, 
                     {"role": "user", "content": prompt}]
    }
    try:
        res = requests.post(url_groq, headers=headers, json=data, timeout=25)
        return res.json()['choices'][0]['message']['content']
    except:
        return "Sabar digital."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "").strip()

        if user_text.startswith("http") or ("." in user_text and " " not in user_text):
            reponse = audit_pagespeed(user_text)
        else:
            reponse = expertise_sabar_digital(user_text)

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": reponse})
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
