import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from PIL import Image
import cv2
from ultralytics import YOLO
import numpy as np
from collections import defaultdict


app = Flask(__name__)
model = YOLO("YOLODataset/runs/detect/yolo11l/weights/best.pt")
socketio = SocketIO(app)

is_track_active = False 
track_history = defaultdict(list)
history_limit = 40

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('model_toggle')
def handle_model_toggle(data):
    global is_track_active
    is_track_active = data.get('isTrack', False)

def perform_tracking(image):
    global track_history

    # Convertir imagen PIL a formato OpenCV
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.flip(frame, 1)
    # Realizar tracking
    results = model.track(
        frame,
        persist=True,  # Usar GPU
        conf=0.2,       # Umbral de confianza
        iou=0.7         # Umbral de IOU
    )

    # Anotar frame con el historial de seguimiento
    for result in results:
        if result.boxes.xywh is not None and result.boxes.id is not None:
            boxes = result.boxes.xywh.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))

                if len(track) > history_limit:
                    track.pop(0)

                points = np.array(track, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=2)

                # Dibujar la caja y el ID
                x1, y1 = int(x - w / 2), int(y - h / 2)
                x2, y2 = int(x + w / 2), int(y + h / 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(
                    frame, f"ID: {track_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
                )
    return frame

@socketio.on('start_video')
def handle_video_frame(data):
    global is_track_active
    try:
        base64_string = data['frame']
        img_data = base64.b64decode(base64_string.split(',')[1])
        image = Image.open(BytesIO(img_data)).convert('RGB')

        if is_track_active:
            tracked_frame = perform_tracking(image)

            # Convertir OpenCV a PIL y luego a base64
            tracked_frame_rgb = cv2.cvtColor(tracked_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(tracked_frame_rgb)
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            emit('video_frame', {'frame': processed_image_base64})

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
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context=('camaraweb/server.crt', 'camaraweb/server.key'))
