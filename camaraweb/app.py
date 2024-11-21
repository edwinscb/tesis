from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")
    emit('status', {'message': 'Conexión establecida'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado")

@socketio.on('start_video')
def start_video(data):
    # Recibe el fotograma en base64 desde el cliente
    frame_data = data.get('frame')
    
    if not frame_data:
        return
    
    # Decodifica el fotograma de base64 a una imagen
    try:
        img_data = base64.b64decode(frame_data)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return
    except Exception as e:
        print(f"Error al procesar el fotograma: {e}")
        return
    
    # Convierte el fotograma a escala de grises
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("D:/tesis/camaraweb/templates", gray_frame)
    # Convierte el fotograma en escala de grises a formato JPEG
    _, buffer = cv2.imencode('.jpg', gray_frame)
    frame_encoded = base64.b64encode(buffer).decode('utf-8')
    
    # Envía el fotograma procesado (en escala de grises) al cliente
    emit('video_frame', {'frame': frame_encoded})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context=('D:\\tesis\\server.crt', 'D:\\tesis\\server.key'))
