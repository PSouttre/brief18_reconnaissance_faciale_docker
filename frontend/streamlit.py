import streamlit as st
import requests
from PIL import Image
import io

# Configuration de la page
st.set_page_config(page_title="Login FaceID", layout="centered")

# Titre de l'application
st.title("Authentification avec reconnaissance faciale")

# Champs login
username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

# Upload webcam
photo = st.camera_input("Prenez une photo avec la webcam")

if st.button("Connexion") and username and password and photo:

    # Appel API login pour récupérer user_id
    login_url = "http://api_flask:8000/login"                                              # URL du service API
    login_data = {"username": username, "password": password}                                # Données à envoyer   
    login_resp = requests.post(login_url, json=login_data)                                   # Requête POST pour login   

    if login_resp.status_code == 200:
        # Utilisateur connu
        user_id = login_resp.json().get("user_id")
        verify_url = "http://api_flask:8000/verify_face"
        files = {"file": (f"{username}.jpg", photo.getvalue(), "image/jpeg")}             
        data = {"user_id": user_id}
        ver_resp = requests.post(verify_url, files=files, data=data)                       # Requête POST pour vérification

        
        if ver_resp.status_code == 200 and ver_resp.json().get("success"):
            st.success("Bravo vous êtes connecté !")
        else:
            st.error(f"Erreur vérification : {ver_resp.json().get('message')}")

    else:
        # Utilisateur inconnu → création + enregistrement
        st.info("Utilisateur inconnu → création d'un compte temporaire.")
        register_url = "http://api_flask:8000/register_face"
        files = {"file": (f"{username}.jpg", photo.getvalue(), "image/jpeg")}
        data = {"username": username, "password": password}   

        reg_resp = requests.post(register_url, files=files, data=data)                    # Requête POST pour enregistrement

        if reg_resp.status_code == 200 and reg_resp.json().get("success"):
            st.success("Utilisateur créé et photo enregistrée ! Vous pouvez maintenant vous reconnecter.")
        else:
            st.error(f"Erreur enregistrement : {reg_resp.json().get('message', reg_resp.text)}")