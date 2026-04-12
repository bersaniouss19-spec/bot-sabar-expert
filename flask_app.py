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
        # On force l'utilisation de la méthode 'offline' sans PKCE
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        
        # L'astuce est ici : on ne génère PAS de code_verifier
        auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
        return redirect(auth_url)
    except Exception as e:
        return f"Erreur Login : {str(e)}"

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
        # On recrée le flow au retour
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        
        # On récupère le jeton directement depuis l'URL de retour
        flow.fetch_token(authorization_response=request.url)
        
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot est maintenant lié à Blogger.</p>"
    except Exception as e:
        # Si ça échoue encore, ce message nous dira pourquoi
        return f"Détail de l'erreur callback : {str(e)}"
