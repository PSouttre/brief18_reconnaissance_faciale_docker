# https://github.com/ageitgey/face_recognition/blob/master/Dockerfile

FROM python:3.10.3-slim-bullseye 

# Installer des dépendances système
RUN apt-get -y update

# Installer dépendances système nécessaires pour dlib et face_recognition
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

# Installer dlib (version 19.9)
RUN cd ~ && \
    # dossier temporaire pour cloner dlib
    mkdir -p dlib && \  
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \ 
    cd  dlib/ && \ 
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS  


WORKDIR /app

# Copier uniquement requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 

# Lance le service Python   
CMD ["python3", "service.py"]


#RUN cd /root/face_recognition && \
#   pip3 install -r requirements.txt && \
#   python3 setup.py install

# Add pip3 install opencv-python==4.1.2.30 if you want to run the live webcam examples

#CMD cd /root/face_recognition/examples && \
#    python3 recognize_faces_in_pictures.py