import os
import requests
from flask import Flask, request, jsonify, redirect
from google_auth_oauthlib.flow import Flow

# 1. Création de l'application (LE MOTEUR)
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_digital_777')

# 2. Configuration des variables
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']
access_tokens = {}

# 3. Les Routes
@app.route('/')
def home():
    return "<h1>Sabar Digital Bot : Opérationnel</h1>"

@app.route('/login')
def login():
    try:
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
        return redirect(auth_url)
    except Exception as e:
        return f"Erreur Login : {str(e)}"

@app.route('/callback')
def callback():
    try:
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(authorization_response=request.url)
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot est lié à Blogger.</p>"
    except Exception as e:
        return f"Erreur Callback : {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
