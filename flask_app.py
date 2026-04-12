import os
import requests
from flask import Flask, request, jsonify, redirect, session
from google_auth_oauthlib.flow import Flow
import json

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_digital_secret_777')

# TES VARIABLES
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']

# STOCKAGE TEMPORAIRE (En production, utiliser une DB)
access_tokens = {}

@app.route('/')
def home():
    return "<h1>Sabar Digital Bot : Opérationnel</h1><p>Prêt pour l'action.</p>"

@app.route('/login')
def login():
    client_config = {"web": {"client_id": CLIENT_ID, "project_id": "sabar-digital", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
    return redirect(auth_url)

@app.route('/callback')
def callback():
    client_config = {"web": {"client_id": CLIENT_ID, "project_id": "sabar-digital", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=request.url)
    access_tokens['current'] = flow.credentials.token
    return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot peut désormais publier.</p>"

def publier_sur_blogger(titre, contenu):
    """Fonction de publication directe"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {access_tokens.get('current')}", "Content-Type": "application/json"}
    payload = {"kind": "blogger#post", "title": titre, "content": contenu}
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        return f"✅ **Article publié avec succès !**\nLien : {res.json().get('url')}"
    return f"❌ Erreur de publication : {res.status_code}"

def expertise_sabar_digital(prompt):
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Tu es l'Expert Sabar Digital. Aristocratique, tranchant. Signe: Sabar digital."}, {"role": "user", "content": prompt}]}
    try:
        res = requests.post(url_groq, headers=headers, json=data, timeout=25)
        return res.json()['choices'][0]['message']['content']
    except: return "Sabar digital."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "").strip()

        # LOGIQUE DE COMMANDE
        if user_text.lower().startswith("publier :"):
            # Format attendu : "Publier : Titre | Contenu"
            try:
                parts = user_text.replace("publier :", "").split("|")
                titre = parts[0].strip()
                contenu = parts[1].strip()
                reponse = publier_sur_blogger(titre, contenu)
            except:
                reponse = "Sabar, utilisez le format : `Publier : Titre | Contenu`"
        else:
            reponse = expertise_sabar_digital(user_text)

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reponse})
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
