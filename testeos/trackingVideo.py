import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict

# Configuraciones como variables
FRAME_WIDTH = 800    # Ancho del frame
FRAME_HEIGHT = 600  # Alto del frame
LINE_THICKNESS = 2  # Grosor de la línea de tracking
CONF_THRESHOLD = 0.8  # Umbral de confianza mínimo
IOU_THRESHOLD = 0.5  # Umbral de IOU para supresión de máximos
TRACK_HISTORY_LENGTH = 80  # Duración de la línea de tracking en fotogramas

# Inicializar el modelo YOLO y forzar uso de GPU
model = YOLO("YOLO/runs/detect/yolo11l/weights/best.pt")

# Ruta del video
VIDEO_PATH = "setter.mp4"
OUTPUT_PATH = "output_video.mp4"  # Ruta del video de salida

# Inicializar captura de video desde archivo
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("Error al abrir el video.")
    exit()

# Configurar resolución de captura
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cv2.setUseOptimized(True)

# Configurar el escritor de video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Códec para MP4
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, 30.0, (FRAME_WIDTH, FRAME_HEIGHT))  # 30 FPS

# Historial de seguimiento (almacena trayectorias incluso si el objeto no está activo)
track_history = defaultdict(list)

# Función para procesar seguimientos (trayectoria persistente)
def draw_annotations_tracking(frame, results):
    active_ids = set()

    # Actualizar historial con objetos visibles en este frame
    for result in results:
        if result.boxes.xywh is not None and result.boxes.id is not None:
            boxes = result.boxes.xywh.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                active_ids.add(track_id)  # Registrar ID activo
                x, y, w, h = box
                track_history[track_id].append((float(x), float(y)))

                # Limitar la longitud del historial si es necesario
                if len(track_history[track_id]) > TRACK_HISTORY_LENGTH:
                    track_history[track_id].pop(0)

    # Dibujar trayectorias de todos los objetos históricos
    for track_id, track in track_history.items():
        points = np.array(track, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=LINE_THICKNESS)

        # Si el objeto está activo, dibujar su caja y etiqueta
        if track_id in active_ids:
            x, y = track[-1]
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                frame, f"ID: {track_id}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
            )
    return frame

# Bucle principal
while True:
    start_time = time.time()

    success, frame = cap.read()
    if not success:
        print("Fin del video o error al leer el fotograma.")
        break

    frame = cv2.flip(frame, 1)  # Modo espejo
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Realizar seguimiento
    results = model.track(frame, imgsz=FRAME_WIDTH, persist=False, device="cuda", conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
    annotated_frame = draw_annotations_tracking(frame.copy(), results)

    # Calcular y mostrar el tiempo por iteración
    elapsed_time = time.time() - start_time
    fps = 1 / elapsed_time
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Escribir el fotograma procesado en el archivo de salida
    out.write(annotated_frame)

# Agregar un fotograma con el mensaje final
final_frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
cv2.putText(final_frame, "Modelo aplicado al video", (FRAME_WIDTH // 6, FRAME_HEIGHT // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

# Escribir el fotograma final con el mensaje
out.write(final_frame)

# Liberar recursos
cap.release()
out.release()
cv2.destroyAllWindows()

print("Modelo aplicado al video y proceso terminado.")
