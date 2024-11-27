import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from PIL import Image
import cv2
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)
model = YOLO("D:/tesis/runs/detect/yolo11l/weights/best.pt")
socketio = SocketIO(app)

is_track_active = False 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('model_toggle')
def handle_model_toggle(data):
    global is_track_active
    is_track_active = data.get('isTrack', False)

@socketio.on('start_video')
def handle_video_frame(data):
    global is_track_active
    try:
        base64_string = data['frame']
        img_data = base64.b64decode(base64_string.split(',')[1])
        image = Image.open(BytesIO(img_data)).convert('RGB')
        if is_track_active:
            mirrored_image = Image.fromarray(np.array(image)[:, ::-1, :])  # Volteo horizontal
            buffered = BytesIO()
            mirrored_image.save(buffered, format="JPEG")
            mirrored_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            emit('video_frame', {'frame': mirrored_image_base64})

        else:
            results = model(image)
            detections = [
                {
                    'box': box.xyxy[0].tolist(),
                    'confidence': box.conf[0].item(),
                    'class_id': int(box.cls[0].item())
                }
                for result in results for box in result.boxes if box.conf[0].item() > 0.5
            ]
            annotated_image = results[0].plot()
            annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
            mirrored_image = cv2.flip(annotated_image_rgb, 1)
            pil_image = Image.fromarray(mirrored_image)
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            emit('video_frame', {'frame': processed_image_base64})
    except Exception as e:
        print(f"Error al procesar el fotograma: {e}")
        emit('video_frame', {'frame': None})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context=('D:\\tesis\\server.crt', 'D:\\tesis\\server.key'))
