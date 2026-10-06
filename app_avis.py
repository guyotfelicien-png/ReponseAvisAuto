import streamlit as st
import requests

# ==========================================
# BLOC 1 : LE TRAITEMENT (Le Moteur IA)
# ==========================================
def generer_reponse(nom_client, note, commentaire, nom_commerce, cle_api):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={cle_api}"
    
    # Ajustement des tons pour être beaucoup plus naturel
    if note >= 4:
        ton = "amical, simple et direct. Comme un vrai commerçant qui remercie de vive voix au comptoir."
    elif note == 3:
        ton = "professionnel et à l'écoute, sans en faire trop."
    else:
        ton = "calme, factuel et poli, orienté solution sans formules toutes faites. Propose toujours d'en discuter."

    prompt = f"""
    Tu es le gérant du commerce '{nom_commerce}'. 
    Un client nommé {nom_client} a laissé un avis de {note}/5 étoiles avec ce commentaire : "{commentaire}"

    Rédige la réponse à cet avis. 
    Contraintes strictes :
    - Le ton doit être {ton}
    - Parle comme un véritable humain. Banni absolument le jargon d'intelligence artificielle, les tournures trop commerciales et les phrases à rallonge.
    - Si le commentaire du client est très court (ex: 1 ou 2 mots comme "top" ou "super"), ta réponse doit être extrêmement courte (une seule phrase simple, ex: "Merci beaucoup {nom_client}, ravi que ça vous plaise !").
    - N'ajoute aucun texte avant ou après.
    - Signe avec "L'équipe de {nom_commerce}".
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 
        donnees = response.json()
        return donnees['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        return f"⚠️ Erreur de génération : {e}"

# ==========================================
# BLOC 2 : L'INTERFACE GRAPHIQUE (Streamlit)
# ==========================================
st.set_page_config(page_title="Générateur d'Avis Pro", page_icon="⭐", layout="centered")

st.title("📱 Tableau de Bord - Gestion des Avis")
st.markdown("Générez des réponses intelligentes aux avis Google de vos clients.")

with st.sidebar:
    st.header("⚙️ Configuration du commerce")
   cle_api_utilisateur = st.secrets["GEMINI_API_KEY"]
    nom_commerce_utilisateur = st.text_input("Nom de votre commerce", value="Mon Super Commerce")
    st.success("✅ Connexion au serveur IA active")

st.subheader("📥 Nouvel avis reçu")

col1, col2 = st.columns(2)
with col1:
    nom_client_saisi = st.text_input("Nom du client", placeholder="Ex: Marie Martin")
with col2:
    note_saisie = st.slider("Note sur 5", min_value=1, max_value=5, value=5)

commentaire_saisi = st.text_area("Commentaire laissé par le client", placeholder="Ex: Super expérience, je recommande !")

if st.button("🚀 Générer la réponse", type="primary"):
    if not cle_api_utilisateur:
        st.warning("⚠️ Veuillez entrer une clé API dans la configuration à gauche.")
    elif not nom_client_saisi or not commentaire_saisi:
        st.warning("⚠️ Veuillez remplir le nom du client et le commentaire.")
    else:
        with st.spinner('Analyse de l\'avis et génération en cours...'):
            reponse_ia = generer_reponse(
                nom_client=nom_client_saisi, 
                note=note_saisie, 
                commentaire=commentaire_saisi, 
                nom_commerce=nom_commerce_utilisateur,
                cle_api=cle_api_utilisateur
            )
            
            st.divider()
            
            # --- LOGIQUE HUMAN-IN-THE-LOOP ---
            if note_saisie >= 3:
                # Mode Automatique : L'IA a répondu
                st.success("✅ **Publié automatiquement :** L'IA a traité cet avis positif.")
                st.text_area("Réponse envoyée :", value=reponse_ia, height=150, disabled=True)
            else:
                # Mode Manuel : Alerte rouge pour le gérant
                st.error("⚠️ **Action requise :** Cet avis critique nécessite votre attention.")
                st.write("Voici la suggestion de l'IA pour désamorcer la situation. Vous pouvez la modifier avant publication.")
                
                # Zone de texte éditable par le commerçant
                reponse_finale = st.text_area("Suggestion de réponse (modifiable) :", value=reponse_ia, height=150)
                
                # Faux bouton de publication pour la démo
                if st.button("Publier cette réponse sur Google"):
                    st.success("✅ Réponse validée et publiée !")