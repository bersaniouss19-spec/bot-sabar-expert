@app.route('/login')
def login():
    try:
        client_config = {
            "web": {
                "client_id": CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI]
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        # On force le prompt pour être sûr d'avoir le jeton de rafraîchissement
        auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
        return redirect(auth_url)
    except Exception as e:
        return f"Erreur Configuration Login: {str(e)}"

@app.route('/callback')
def callback():
    try:
        client_config = {
            "web": {
                "client_id": CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI]
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(authorization_response=request.url)
        
        # On stocke le token
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot peut désormais publier sur Blogger.</p>"
    except Exception as e:
        # Cela nous dira EXACTEMENT ce qui bloque au lieu du message générique
        return f"Erreur lors du callback : {str(e)}"
