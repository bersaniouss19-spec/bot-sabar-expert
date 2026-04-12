@app.route('/callback')
def callback():
    try:
        # On extrait le code directement de l'URL
        code = request.args.get('code')
        
        client_config = {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        # On recrée le flow au retour
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        
        # LA CORRECTION : On échange le code contre le token sans passer par le verifier de session
        # Cette méthode est la plus directe pour éviter l'erreur "Missing code verifier"
        flow.fetch_token(code=code)
        
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot est enfin lié. Vous pouvez fermer cette page.</p>"
    except Exception as e:
        # On affiche l'erreur précise si ça échoue encore
        return f"Détail de l'erreur technique : {str(e)}"
