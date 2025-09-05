import os
import numpy as np
import face_recognition
from flask import Flask, jsonify, request


app = Flask(__name__) 


# Config du dossier de stockage des images et encodages
UPLOAD_FOLDER = "uploads"
ENCODINGS_FOLDER = "encodings"


# Créer les dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODINGS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


# Fonction pour obtenir le chemin de l'encodage d'un utilisateur
def get_encoding_path(user_id: str) -> str:
    """Retourne le chemin du fichier .npy contenant l'encodage du user."""
    return os.path.join(ENCODINGS_FOLDER, f"{user_id}.npy")


# --- Route pour enregistrer un visage ---
@app.route("/register", methods=["POST"])
def register():
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not user_id or not file:
        return jsonify({"success": False, "message": "Missing user_id or file"}), 400

    # Sauvegarde temporaire de la photo
    image_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.jpg")
    file.save(image_path)

    # Extraction de l'encodage
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    # Vérification qu'un visage a bien été détecté
    if len(encodings) == 0:
        return jsonify({"success": False, "message": "No face detected"}), 400
    # On prend le premier visage détecté
    encoding = encodings[0]

    # Sauvegarde dans un fichier .npy
    encoding_path = get_encoding_path(user_id)
    np.save(encoding_path, encoding)

    return jsonify({"success": True, "message": "Face registered successfully"})


# --- Route pour vérifier un visage ---
@app.route("/verify", methods=["POST"])
def verify():
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not user_id or not file:
        return jsonify({"success": False, "message": "Missing user_id or file"}), 400

    # Sauvegarde temporaire
    image_path = os.path.join(UPLOAD_FOLDER, f"verify_{user_id}.jpg")
    file.save(image_path)

    # Encodage du visage envoyé
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        return jsonify({"success": False, "message": "No face detected"}), 400

    new_encoding = encodings[0] 

    # Chargement de l'encodage enregistré
    encoding_path = get_encoding_path(user_id)
    if not os.path.exists(encoding_path):
        return jsonify({"success": False, "message": "No registered face for this user"}), 404

    known_encoding = np.load(encoding_path)

    # Comparaison des encodages
    matches = face_recognition.compare_faces([known_encoding], new_encoding)
    if matches[0]:
        return jsonify({"success": True, "message": "Face verified successfully"})
    else:
        return jsonify({"success": False, "message": "Face mismatch"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)