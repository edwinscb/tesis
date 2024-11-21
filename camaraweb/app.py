import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from PIL import Image, ImageOps
import io

# Configuración de Flask y SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')  # Tu archivo HTML donde se carga el video

@socketio.on('start_video')
def handle_video_frame(data):
    try:
        # Extrae la cadena base64
        base64_string = data['frame']
        # Elimina el prefijo 'data:image/jpeg;base64,' de la cadena
        img_data = base64.b64decode(base64_string.split(',')[1])

        # Decodifica la imagen en base64
        image = Image.open(BytesIO(img_data))

        # Procesa la imagen (ejemplo: convertirla a escala de grises)
        image = ImageOps.grayscale(image)

        # Convierte la imagen procesada nuevamente a base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Envía el fotograma procesado al cliente
        emit('video_frame', {'frame': processed_image_base64})

    except Exception as e:
        print(f"Error al procesar el fotograma: {e}")
        emit('video_frame', {'frame': None})  # Envía None si hubo un error
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context=('D:\\tesis\\server.crt', 'D:\\tesis\\server.key'))
