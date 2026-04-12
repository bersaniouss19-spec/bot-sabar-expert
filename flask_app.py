import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# TES VARIABLES
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PAGESPEED_API_KEY = os.environ.get('PAGESPEED_API_KEY')
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
BLOGGER_API_KEY = os.environ.get('BLOGGER_API_KEY')
BLOGGER_BLOG_ID = os.environ.get('BLOGGER_BLOG_ID')

@app.route('/')
def home():
    """Route d'accueil pour supprimer le 404 et tester Blogger"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts?key={BLOGGER_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            dernier_titre = items[0]['title'] if items else "Aucun article trouvé"
            return f"<h1>Sabar Digital Bot : Opérationnel</h1><p>Connexion Blogger OK. Dernier article : <b>{dernier_titre}</b></p>"
        else:
            return f"<h1>Bot Actif</h1><p>Statut Blogger : {response.status_code}</p>"
    except Exception as e:
        return f"<h1>Sabar Digital Bot en ligne</h1><p>Erreur test : {str(e)}</p>"

def audit_pagespeed(url_a_tester):
    """TON CODE ORIGINAL PageSpeed (COMPLÈT)"""
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
        lighthouse = data['lighthouseResult']
        score = lighthouse['categories']['performance']['score'] * 100
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
            f"Cher ami, les chiffres parlent. Sabar digital."
        )
    except:
        return "Audit technique en cours. Sabar digital."

def expertise_sabar_digital(prompt):
    """TON CODE GROQ ORIGINAL (COMPLÈT)"""
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
        return "Sabar digital."

def activate_cloudflare_zone(domain):
    """TON CODE CLOUDFLARE"""
    headers = {'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}', 'Content-Type': 'application/json'}
    data = {'name': domain}
    try:
        response = requests.post('https://api.cloudflare.com/client/v4/zones', headers=headers, json=data)
        if response.status_code == 200:
            zone = response.json()['result']
            return f"✅ **Cloudflare activé !**\nDNS : {', '.join(zone['name_servers'])}"
        return "Cloudflare en cours..."
    except:
        return "Cloudflare activation..."

def mistral_expertise(prompt):
    """TON CODE MISTRAL"""
    headers = {'Authorization': f'Bearer {MISTRAL_API_KEY}', 'Content-Type': 'application/json'}
    data = {'model': 'mistral-small-latest', 'messages': [{'role': 'user', 'content': prompt}]}
    try:
        res = requests.post('https://api.mistral.ai/v1/chat/completions', headers=headers, json=data)
        return res.json()['choices'][0]['message']['content']
    except:
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "").strip()

        if "." in user_text and " " not in user_text:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                         json={"chat_id": chat_id, "text": "🚀 Audit + Cloudflare..."})
            
            pagespeed = audit_pagespeed(user_text)
            cloudflare = activate_cloudflare_zone(user_text)
            reponse = f"{pagespeed}\n\n{cloudflare}\n💰 **Speed 497€ ?** Sabar digital."
        else:
            reponse = mistral_expertise(user_text) or expertise_sabar_digital(user_text)

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                     json={"chat_id": chat_id, "text": reponse})
    
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
