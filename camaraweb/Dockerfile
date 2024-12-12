# Usa una imagen base oficial de Python con soporte para CUDA
FROM nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu20.04

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará tu aplicación
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["python3", "app.py"]
