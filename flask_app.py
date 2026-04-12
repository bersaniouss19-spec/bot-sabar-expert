# --- LOGIQUE INTELLIGENTE (GROQ) AMÉLIORÉE ---
def generer_contenu_ia(sujet):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    Tu es Sabar Digital, expert copywriter. Rédige un article SEO sur : {sujet}.
    Réponds UNIQUEMENT sous ce format strict sans aucun autre texte :
    TITRE | CORPS_HTML | TAGS | META_DESCRIPTION
    """
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7 # Un peu plus de stabilité
    }
    
    res = requests.post(url, headers=headers, json=payload)
    contenu = res.json()['choices'][0]['message']['content']
    return contenu.strip()

# --- WEBHOOK TELEGRAM SÉCURISÉ ---
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
                # Sécurité : on vérifie si les barres verticales sont bien là
                if "|" in bloc_ia:
                    parts = bloc_ia.split("|")
                    # On s'assure d'avoir au moins les 4 parties
                    titre = parts[0].strip()
                    html = parts[1].strip()
                    tags = parts[2].strip() if len(parts) > 2 else "Expertise"
                    meta = parts[3].strip() if len(parts) > 3 else titre
                    
                    reponse = publier_sur_blogger(titre, html, tags, meta)
                else:
                    reponse = "⚠️ L'IA n'a pas respecté le format. Réessayez."
            except Exception as e:
                reponse = f"⚠️ Erreur technique : {str(e)}"
            
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reponse})
            
    return jsonify({"status": "ok"}), 200
