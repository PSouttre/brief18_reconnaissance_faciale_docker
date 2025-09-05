# Image de base légère avec Python
FROM python:3.12-slim 

# Définir un dossier de travail
WORKDIR /app

# Installer dépendances système utiles 
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# Copier requirements
COPY requirements.txt .

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code Streamlit
COPY . .

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Lancer Streamlit automatiquement
CMD ["streamlit", "run", "streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
