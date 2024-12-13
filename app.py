from flask import Flask, request, send_file, render_template
import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict
import os

app = Flask(__name__)

# Configuraciones
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Inicializar el modelo YOLO
model = YOLO("YOLO/runs/detect/yolo11l/weights/best.pt")

# Configuración de parámetros
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
LINE_THICKNESS = 2
CONF_THRESHOLD = 0.8
IOU_THRESHOLD = 0.4
TRACK_HISTORY_LENGTH = 50

track_history = defaultdict(list)

@app.route('/')
def index():
    return render_template('tracking.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No se proporcionó un archivo", 400

    video_file = request.files['video']
    if video_file.filename == '':
        return "Archivo no válido", 400

    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{video_file.filename}")

    video_file.save(video_path)
    apply_tracking(video_path, processed_path)

    return send_file(processed_path, as_attachment=True)

def draw_annotations_tracking(frame, results):
    active_ids = set()

    for result in results:
        if result.boxes.xywh is not None and result.boxes.id is not None:
            boxes = result.boxes.xywh.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                active_ids.add(track_id)
                x, y, w, h = box
                track_history[track_id].append((float(x), float(y)))

                if len(track_history[track_id]) > TRACK_HISTORY_LENGTH:
                    track_history[track_id].pop(0)

    for track_id, track in track_history.items():
        points = np.array(track, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=LINE_THICKNESS)

        if track_id in active_ids:
            x, y = track[-1]
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return frame

def apply_tracking(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Error al abrir el video.")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (FRAME_WIDTH, FRAME_HEIGHT))

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        results = model.track(frame, imgsz=FRAME_WIDTH, persist=False, device="cuda",
                              conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
        annotated_frame = draw_annotations_tracking(frame.copy(), results)
        out.write(annotated_frame)

    cap.release()
    out.release()

if __name__ == "__main__":
    app.run(debug=True)
