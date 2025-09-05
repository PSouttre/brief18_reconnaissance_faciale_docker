Reconnaissance faciale avec Streamlit, Flask et Docker



Ce projet permet d’authentifier un utilisateur via reconnaissance faciale. Il utilise Python, Docker, PostgreSQL, Streamlit et la librairie face_recognition.


Fonctionnalités

Connexion via nom d’utilisateur, mot de passe et photo prise avec la webcam.

Enregistrement automatique pour les nouveaux utilisateurs.

Vérification faciale pour les utilisateurs existants.

Gestion des utilisateurs et des encodages faciaux via PostgreSQL.

Interface frontale simple avec Streamlit.

Architecture

Le projet est composé de 4 conteneurs Docker :

Conteneur	Description	Port
frontend_service	Interface utilisateur Streamlit	8501
api_flask	Backend Flask pour login, enregistrement et vérification	8000
recognition_service	Service de reconnaissance faciale avec face_recognition	5000
db_service	Base de données PostgreSQL	5432
Installation

Cloner le projet :

git clone https://github.com/PSouttre/brief18_reconnaissance_faciale_docker.git
cd brief18_reconnaissance_faciale_docker


Lancer Docker Compose :

docker-compose up --build


Accéder à l’interface Streamlit :

http://localhost:8501

Connexion à PostgreSQL (optionnel) :

Hôte : localhost:5432

Utilisateur : face_user

Mot de passe : face_pass

Base : faces

Test rapide (nouvel utilisateur)

Ouvrir l’interface Streamlit dans le navigateur.

Saisir un nom d’utilisateur et un mot de passe.

Prendre une photo via la webcam.

Si l’utilisateur est nouveau, il sera automatiquement enregistré et un message s’affiche :
"Utilisateur créé et photo enregistrée ! Vous pouvez maintenant vous reconnecter."

Se reconnecter avec le même nom et mot de passe :

Si le visage correspond : "Bravo vous êtes connecté !"

Sinon : "Utilisateur non reconnu, merci d'envoyer à nouveau votre photo"

Structure du projet
.
├── frontend/
│   └── streamlit.py
├── api/
│   └── app_flask.py
├── recognition/
│   └── service.py
├── docker-compose.yml
├── requirements.txt
└── README.md

Base de données

Table principale : users

Colonne	Type	Description
id	SERIAL	Identifiant unique
username	VARCHAR	Nom de l’utilisateur
password	VARCHAR	Mot de passe
photo_path	TEXT	Chemin vers l’encodage facial .npy
Dépendances

Python 3.x

face_recognition

Flask

Streamlit

psycopg2

Docker & Docker Compose

Auteur

Peggy Souttre