import cv2
import numpy as np
from tkinter import Tk, Button, Canvas
from PIL import Image, ImageTk
from ultralytics import YOLO
from collections import defaultdict

# Cargar el modelo YOLO
model = YOLO("YOLO/runs/detect/yolo11l/weights/best.pt")

# Variables globales
is_track_active = False
track_history = defaultdict(list)
history_limit = 40

# Función para realizar el seguimiento
def perform_tracking(frame):
    global track_history
    results = model.track(frame, persist=True, conf=0.2, iou=0.7)
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
                cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=5)

                x1, y1 = int(x - w / 2), int(y - h / 2)
                x2, y2 = int(x + w / 2), int(y + h / 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return frame

# Función para convertir la imagen en base64
def convert_to_base64(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    return ImageTk.PhotoImage(pil_image)

# Función para capturar video desde la cámara
def capture_video():
    global is_track_active
    cap = cv2.VideoCapture(0)  # 0 es el índice de la cámara por defecto

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if is_track_active:
            frame = perform_tracking(frame)
        
        # Convertir a imagen para tkinter
        img_tk = convert_to_base64(frame)

        # Actualizar la imagen en el canvas
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk  # Mantener una referencia a la imagen

    cap.release()

# Función para cambiar el estado del seguimiento
def toggle_tracking():
    global is_track_active
    is_track_active = not is_track_active

# Configurar la interfaz gráfica
root = Tk()
root.title("SmartVolley - Seguimiento de Balón")

# Crear el canvas para mostrar el video
canvas = Canvas(root, width=640, height=480)
canvas.pack()

# Botón para iniciar/detener el seguimiento
tracking_button = Button(root, text="Iniciar Seguimiento", command=toggle_tracking)
tracking_button.pack()

# Botón para cambiar cámara (si tienes más de una)
change_camera_button = Button(root, text="Cambiar Cámara", command=lambda: None)  # No implementado en este caso
change_camera_button.pack()

# Iniciar la captura de video
capture_video()

# Ejecutar la interfaz gráfica
root.mainloop()
