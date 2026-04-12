import os
import requests
from flask import Flask, request, jsonify, redirect

# --- INITIALISATION (CRUCIAL : C'est ce que Gunicorn cherche) ---
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sabar_777')

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://bot-sabar-expert.onrender.com/callback"

# Stockage temporaire en mémoire
access_tokens = {}

# --- ROUTES D'AUTHENTIFICATION ---
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
    En tant qu'expert copywriter Sabar Digital, rédige un article SEO sur : {sujet}.
    Réponds EXCLUSIVEMENT avec ce format strict :
    TITRE | CONTENU_HTML | TAGS | META_DESCRIPTION
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=25)
        res_json = res.json()
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content'].strip()
        return f"ERREUR_IA: {res.text}"
    except Exception as e:
        return f"ERREUR_IA: {str(e)}"

# --- PUBLICATION SUR BLOGGER (VERSION SÉCURISÉE) ---
def publier_sur_blogger(titre, contenu_html, mots_cles, meta_desc):
    token = access_tokens.get('current')
    if not token: return "❌ Non autorisé. Allez sur /login"
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    liste_tags = [t.strip() for t in mots_cles.replace('"', '').split(",") if t.strip()]
    
    payload = {
        "kind": "blogger#post",
        "title": titre,
        "content": contenu_html,
        "labels": liste_tags
    }

    if meta_desc and len(meta_desc) > 5:
        payload["customMetaData"] = meta_desc[:150]
    
    res = requests.post(url, headers=headers, json=payload)
    
    if res.status_code == 200:
        return "✅ Article IA publié avec succès !"
    else:
        # Deuxième tentative sans meta-data au cas où Blogger bloque
        payload.pop("customMetaData", None)
        res_retry = requests.post(url, headers=headers, json=payload)
        if res_retry.status_code == 200:
            return "✅ Publié (sans méta-description)"
        return f"❌ Erreur Blogger : {res.text}"

# --- WEBHOOK TELEGRAM ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text.startswith("publier_ia :"):
            sujet = text.replace("publier_ia :", "").strip()
            try:
                bloc_ia = generer_contenu_ia(sujet)
                if "|" in bloc_ia:
                    parts = bloc_ia.split("|")
                    titre = parts[0].strip()
                    html = parts[1].strip()
                    tags = parts[2].strip() if len(parts) > 2 else "Expertise"
                    meta = parts[3].strip() if len(parts) > 3 else titre
                    reponse = publier_sur_blogger(titre, html, tags, meta)
                else:
                    reponse = f"⚠️ L'IA a répondu hors format : {bloc_ia[:100]}..."
            except Exception as e:
                reponse = f"⚠️ Erreur système : {str(e)}"
            
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": reponse})
            
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
