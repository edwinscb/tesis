# Usa una imagen base con Python
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto al contenedor
COPY . /app

# Copia el archivo best.pt al directorio adecuado dentro del contenedor
COPY best.pt /app/camaraweb/best.pt

# Instalar Python y herramientas del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Instalar las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Exponer el puerto 5000 (puerto predeterminado de Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python3", "app.py"]
