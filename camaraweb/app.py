from flask import Flask, request, send_from_directory, render_template
import cv2
import numpy as np
from ultralytics import YOLO
import os
from collections import defaultdict

app = Flask(__name__)

# Configuraciones
UPLOAD_FOLDER = 'camaraweb\\static\\uploads'
PROCESSED_FOLDER = 'camaraweb\\static\\processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Inicializar el modelo YOLO
model = YOLO("camaraweb/best.pt")

# Configuración de parámetros
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CONF_THRESHOLD = 0.8
IOU_THRESHOLD = 0.2
TRACK_HISTORY_LENGTH = 50

track_history = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tracking')
def models():
    return render_template('tracking.html')

@app.route('/aprendizaje')
def aprendizaje():
    return render_template('aprendizaje.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    # Verifica si se ha enviado el archivo
    if 'video' not in request.files:
        return "No se proporcionó un archivo", 400

    video_file = request.files['video']
    if video_file.filename == '':
        return "Archivo no válido", 400

    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    processed_filename = f"processed_{video_file.filename}"
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)

    # Asegúrate de que las carpetas existan
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    # Guardar el archivo de video
    print(f"Guardando el archivo en: {video_path}")
    video_file.save(video_path)
    print(f"Archivo guardado correctamente, procesando...")

    # Aplicar seguimiento al video
    apply_tracking(video_path, processed_path)
    
    # Verificar si el archivo procesado existe
    if not os.path.exists(processed_path):
        print(f"El archivo no existe: {processed_path}")
        return "Error: el archivo no se pudo encontrar", 404

    print(f"Enviando el archivo procesado desde: {PROCESSED_FOLDER}")
    filename = os.path.basename(processed_path)
    print(f"Enviando el archivo procesado: {filename}")
    # Enviar el archivo procesado
    return send_from_directory(os.path.join(os.getcwd(), 'camaraweb', 'static', 'processed'), filename, as_attachment=True)

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
        results = model.track(frame, imgsz=FRAME_WIDTH, persist=False, device="cuda", conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
        annotated_frame = draw_annotations_tracking(frame.copy(), results)
        out.write(annotated_frame)

    cap.release()
    out.release()

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

                # Mantener el historial limitado a TRACK_HISTORY_LENGTH
                if len(track_history[track_id]) > TRACK_HISTORY_LENGTH:
                    track_history[track_id].pop(0)

    for track_id, track in track_history.items():
        points = np.array(track, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=2)

        # Dibujar la caja delimitadora y el ID
        if track_id in active_ids:
            x, y = track[-1]
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return frame

if __name__ == "__main__":
    app.run(debug=True)
