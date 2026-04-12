def publier_sur_blogger(titre, contenu_html, mots_cles, meta_desc):
    token = access_tokens.get('current')
    if not token: return "❌ Non autorisé. Allez sur /login"
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Nettoyage simple des tags (enlève les caractères bizarres)
    liste_tags = [t.strip() for t in mots_cles.replace('"', '').split(",") if t.strip()]
    
    payload = {
        "kind": "blogger#post",
        "title": titre,
        "content": contenu_html,
        "labels": liste_tags
    }

    # On n'ajoute la méta-description QUE si elle est courte et propre
    # Blogger limite souvent à 150 caractères
    if meta_desc and len(meta_desc) > 5:
        payload["customMetaData"] = meta_desc[:150]
    
    res = requests.post(url, headers=headers, json=payload)
    
    if res.status_code == 200:
        return "✅ Article IA publié avec succès !"
    else:
        # Si ça échoue encore, on tente SANS la méta-description (sécurité ultime)
        payload.pop("customMetaData", None)
        res_retry = requests.post(url, headers=headers, json=payload)
        if res_retry.status_code == 200:
            return "✅ Publié (mais sans méta-description - vérifiez vos réglages Blogger)"
        return f"❌ Erreur persistante : {res.text}"
