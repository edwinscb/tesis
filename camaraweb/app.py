import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from PIL import Image
import io
import cv2
from ultralytics import YOLO
import numpy as np  # Necesario para convertir el ndarray a imagen

# Configuración de Flask y SocketIO
app = Flask(__name__)
model = YOLO("D:/tesis/runs/detect/yolo11l/weights/best.pt")  # Cargar el modelo una sola vez
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')  # Tu archivo HTML donde se carga el video

@socketio.on('start_video')
def handle_video_frame(data):
    try:
        # Extrae la cadena base64 del fotograma
        base64_string = data['frame']
        img_data = base64.b64decode(base64_string.split(',')[1])
        
        # Decodifica la imagen
        image = Image.open(BytesIO(img_data))

        # Asegúrate de que la imagen esté en modo RGB
        image = image.convert('RGB')

        # Realiza la detección con el modelo YOLO
        results = model(image)  # Detecta objetos en la imagen

        # Filtrar las detecciones con un umbral de confianza > 0.5
        detections = []
        for result in results:
            for box in result.boxes:
                conf = box.conf[0].item()  # Confianza de la detección
                if conf > 0.5:  # Filtro de confianza
                    detections.append({
                        'box': box.xyxy[0].tolist(),  # Coordenadas de la caja delimitadora
                        'confidence': conf,
                        'class_id': int(box.cls[0].item())  # Clase detectada
                    })

        # Procesar la imagen: dibujar resultados solo para detecciones con alta confianza
        annotated_image = results[0].plot()  # Añade las anotaciones de detección

        # Convertir el ndarray a RGB (si es necesario, depende del modelo)
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        # Voltear la imagen horizontalmente (modo espejo)
        mirrored_image = cv2.flip(annotated_image_rgb, 1)
        # Convertir el ndarray RGB a una imagen de PIL
        pil_image = Image.fromarray(mirrored_image)

        # Convierte la imagen procesada nuevamente a base64
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Envía el fotograma procesado al cliente
        emit('video_frame', {'frame': processed_image_base64})

    except Exception as e:
        print(f"Error al procesar el fotograma: {e}")
        emit('video_frame', {'frame': None})  # Enviar None si hubo un error

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context=('D:\\tesis\\server.crt', 'D:\\tesis\\server.key'))
