from flask import Flask, request, jsonify
import psycopg2
import requests
import os

app = Flask(__name__)

# Récupération des variables d'environnement (passées par docker-compose.yml)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "face_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "face_pass")
DB_NAME = os.getenv("DB_NAME", "faces")

# Connexion à la base PostgreSQL
def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
    except Exception as e:
        print(f"Erreur de connexion BDD : {e}")
        return None


# Initialisation de la BDD (création de la table users si elle n'existe pas)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            photo_path TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- Endpoint login (username/password) ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json                                                                      # Récupération des données JSON
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()                                                               # Connexion à la BDD
    cur = conn.cursor()                                                                      # Création d'un curseur
    cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))             # Requête SQL pour récupérer l'utilisateur 
    user = cur.fetchone()                                                                    # Récupération du résultat
    conn.close()                                                                             # Fermeture de la connexion

    if not user:
        return jsonify({"success": False, "message": "Utilisateur inconnu"}), 401

    # Vérification du mot de passe
    user_id, stored_password = user
    if stored_password != password:
        return jsonify({"success": False, "message": "Mot de passe incorrect"}), 401

    return jsonify({"success": True, "user_id": user_id})

# --- Endpoint pour enregistrer la première photo ---
@app.route("/register_face", methods=["POST"])
def register_face():
    username = request.form.get("username")
    password = request.form.get("password")
    file = request.files.get("file")

    if not username or not password or not file:
        return jsonify({"success": False, "message": "Missing username, password or file"}), 400

    # 1) Insérer / mettre à jour l'utilisateur et récupérer son id
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON CONFLICT (username) DO UPDATE SET password = EXCLUDED.password
            RETURNING id;
        """, (username, password))
        user_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"DB error: {e}"}), 500
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass

    # 2) Appeler le service de reconnaissance pour enregistrer l'encodage
    files = {"file": (file.filename, file, file.content_type)}
    try:
        response = requests.post("http://recognition_service:5000/register",
                                 files=files, data={"user_id": user_id}, timeout=15)
    except Exception as e:
        return jsonify({"success": False, "message": f"Recognition service error: {e}"}), 502

    # Sécuriser le parsing JSON
    try:
        result = response.json()
    except Exception:
        return jsonify({"success": False, "message": "Recognition service returned non-JSON"}), 502

    if response.status_code == 200 and result.get("success"):
        # 3) Mise à jour du chemin du .npy
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            encoding_path = f"/app/recognition/encodings/{user_id}.npy"
            cur.execute("UPDATE users SET photo_path=%s WHERE id=%s", (encoding_path, user_id))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            return jsonify({"success": False, "message": f"DB update error: {e}"}), 500
        finally:
            try:
                cur.close(); conn.close()
            except Exception:
                pass

        # Succès — on peut déjà considérer l’utilisateur connecté
        return jsonify({"success": True, "user_id": user_id})

    # Erreur du service de reco
    return jsonify({"success": False, "message": result.get("message", "Registration failed")}), 400



# --- Endpoint pour vérifier une photo ---
@app.route("/verify_face", methods=["POST"])
def verify_face():
    user_id = request.form.get("user_id")
    file = request.files.get("file")
    if not user_id or not file:
        return jsonify({"success": False, "message": "Missing user_id or file"}), 400

    files = {"file": (file.filename, file, file.content_type)}
    try:
        response = requests.post("http://recognition_service:5000/verify",
                                 files=files, data={"user_id": user_id}, timeout=15)
    except Exception as e:
        return jsonify({"success": False, "message": f"Recognition service error: {e}"}), 502

    # Renvoie direct la réponse JSON du service (avec garde-fou)
    try:
        return jsonify(response.json()), response.status_code
    except Exception:
        return jsonify({"success": False, "message": "Recognition service returned non-JSON"}), 502
    
if __name__ == "__main__":
    init_db()  # Initialisation de la BDD au démarrage
    app.run(host="0.0.0.0", port=8000, debug=True)
