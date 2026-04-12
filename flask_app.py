import os
import requests
from flask import Flask, request, jsonify, redirect
from google_auth_oauthlib.flow import Flow

# 1. INITIALISATION DU MOTEUR (CRUCIAL)
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_digital_777')

# 2. CONFIGURATION DES VARIABLES (RECUPEREES DE RENDER)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Stockage en mémoire vive (attention, s'efface si Render redémarre)
access_tokens = {}

@app.route('/')
def home():
    return "<h1>Sabar Digital Bot : Opérationnel</h1>"

@app.route('/login')
def login():
    try:
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        # On force la méthode simple sans PKCE pour éviter l'erreur "Missing code verifier"
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
        return redirect(auth_url)
    except Exception as e:
        return f"Erreur Login : {str(e)}"

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        # Échange du code contre le jeton sans passer par la session Flask
        flow.fetch_token(code=code)
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot est lié. Testez-le sur Telegram.</p>"
    except Exception as e:
        return f"Erreur Callback : {str(e)}"

def publier_sur_blogger(titre, contenu):
    token = access_tokens.get('current')
    if not token:
        return "❌ Erreur : Bot non autorisé. Allez sur /login"
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"kind": "blogger#post", "title": titre, "content": contenu}
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return f"✅ Publié ! Lien : {res.json().get('url')}"
        return f"❌ Erreur Blogger : {res.status_code}"
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"

def expertise_sabar_digital(prompt):
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Tu es l'Expert Sabar Digital. Signe: Sabar digital."}, {"role": "user", "content": prompt}]}
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
        if user_text.lower().startswith("publier :"):
            try:
                parts = user_text.replace("publier :", "").split("|")
                reponse = publier_sur_blogger(parts[0].strip(), parts[1].strip())
            except:
                reponse = "⚠️ Format : publier : Titre | Contenu"
        else:
            reponse = expertise_sabar_digital(user_text)
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reponse})
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
