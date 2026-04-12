import os
import requests
from flask import Flask, request, jsonify, redirect
from google_auth_oauthlib.flow import Flow
import json

# 1. On crée l'application D'ABORD
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_digital_secret_777')

# 2. On définit les variables et le dictionnaire de jetons
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"
SCOPES = ['https://www.googleapis.com/auth/blogger']

access_tokens = {}

# 3. ENSUITE on peut utiliser @app.route
@app.route('/')
def home():
    return "<h1>Sabar Digital Bot : Opérationnel</h1>"

@app.route('/login')
def login():
    # ... le reste de ton code login ...
