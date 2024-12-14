# Usa una imagen base con Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto al contenedor
COPY . /app

# Copia el archivo best.pt al directorio adecuado dentro del contenedor
COPY best.pt /app/camaraweb/best.pt

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# Exponer el puerto 5000 (puerto predeterminado de Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "app.py", "run", "--host=0.0.0.0"]

