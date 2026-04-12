import os
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_777')

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"

access_tokens = {}

# --- ROUTES AUTHENTIFICATION ---
@app.route('/')
def home():
    return "<h1>Sabar Digital : Système Opérationnel</h1>"

@app.route('/login')
def login():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/blogger&"
        "access_type=offline&"
        "prompt=consent"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        if not code:
            return "Erreur : Aucun code reçu de Google."

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
            return "<h1>Succès !</h1><p>Sabar, votre bot est enfin connecté.</p>"
        return f"Erreur Google : {token_data}"
    except Exception as e:
        return f"Erreur technique : {str(e)}"

# --- LOGIQUE INTELLIGENTE (GROQ) ---
def generer_contenu_ia(sujet):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    En tant qu'expert copywriter Sabar Digital, rédige un article de blog optimisé SEO sur le sujet suivant : {sujet}.
    Réponds EXCLUSIVEMENT avec ce format, chaque partie séparée par une barre verticale '|' :
    TITRE_ICI | CONTENU_HTML_ICI (balises <p>, <b>, <h2> et liens <a> pertinents) | MOTS_CLES_ICI (libellés séparés par virgules) | META_DESCRIPTION_ICI
    """
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return res.json()['choices'][0]['message']['content']

# --- PUBLICATION BLOGGER ---
def publier_sur_blogger(titre, contenu_html, mots_cles, meta_desc):
    token = access_tokens.get('current')
    if not token: return "❌ Non autorisé. Allez sur /login"
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "kind": "blogger#post",
        "title": titre,
        "content": contenu_html,
        "labels": [label.strip() for label in mots_cles.split(",")],
        "customMetaData": meta_desc
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return "✅ Article IA publié avec succès !" if res.status_code == 200 else f"❌ Erreur : {res.text}"

# --- WEBHOOK TELEGRAM ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # Commande intelligente
        if text.startswith("publier_ia :"):
            sujet = text.replace("publier_ia :", "").strip()
            try:
                # 1. L'IA rédige tout selon ton profil d'expert
                bloc_ia = generer_contenu_ia(sujet)
                parts = bloc_ia.split("|")
                # 2. Publication automatique
                reponse = publier_sur_blogger(
                    parts[0].strip(), 
                    parts[1].strip(), 
                    parts[2].strip(), 
                    parts[3].strip()
                )
            except Exception as e:
                reponse = f"⚠️ Erreur de traitement : {str(e)}"
            
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reponse})
            
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
