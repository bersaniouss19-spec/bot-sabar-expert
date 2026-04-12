import os
import requests
from flask import Flask, request, jsonify, redirect
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_777')

# Variables d'environnement
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']

access_tokens = {}

@app.route('/')
def home():
    return "<h1>Sabar Digital : Système Opérationnel</h1>"

@app.route('/login')
def login():
    client_config = {"web": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token"}}
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    # On désactive manuellement le PKCE pour éviter le bug du "verifier"
    auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        # On refait l'échange manuellement sans passer par la gestion de session Flask
        data = {
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        token_data = response.json()
        
        if 'access_token' in token_data:
            access_tokens['current'] = token_data['access_token']
            return "<h1>Succès !</h1><p>Sabar, votre bot est enfin connecté à Blogger.</p>"
        else:
            return f"Erreur Google : {token_data}"
    except Exception as e:
        return f"Erreur technique : {str(e)}"

# --- FONCTIONS DE PUBLICATION ---
def publier_sur_blogger(titre, contenu):
    token = access_tokens.get('current')
    if not token: return "❌ Non autorisé. Allez sur /login"
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"kind": "blogger#post", "title": titre, "content": contenu}
    res = requests.post(url, headers=headers, json=payload)
    return "✅ Article publié !" if res.status_code == 200 else f"❌ Erreur : {res.text}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text.startswith("publier :"):
            parts = text.replace("publier :", "").split("|")
            reponse = publier_sur_blogger(parts[0].strip(), parts[1].strip())
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reponse})
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
