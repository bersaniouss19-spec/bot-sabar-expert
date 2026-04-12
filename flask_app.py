@app.route('/login')
def login():
    try:
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        
        # FORCE : On génère l'URL sans PKCE (code_verifier)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return redirect(auth_url)
    except Exception as e:
        return f"Erreur Login : {str(e)}"

@app.route('/callback')
def callback():
    try:
        # On récupère le code de l'URL sans chercher de verifier en session
        code = request.args.get('code')
        client_config = {"web": {"client_id": CLIENT_ID, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": CLIENT_SECRET, "redirect_uris": [REDIRECT_URI]}}
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        
        # FORCE : On échange le code contre le token sans passer par la session
        flow.fetch_token(code=code)
        
        access_tokens['current'] = flow.credentials.token
        return "<h1>Autorisation réussie !</h1><p>Sabar, votre bot est ENFIN prêt.</p>"
    except Exception as e:
        return f"Erreur Callback Finale : {str(e)}"
