import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict

# Configuraciones como variables
FRAME_WIDTH = 1920  # Ancho del frame
FRAME_HEIGHT = 1080  # Alto del frame
LINE_THICKNESS = 3  # Grosor de la línea de tracking
CONF_THRESHOLD = 0.2  # Umbral de confianza mínimo
IOU_THRESHOLD = 0.7  # Umbral de IOU para supresión de máximos
TRACK_HISTORY_LENGTH = 100  # Duración de la línea de tracking en fotogramas

# Inicializar el modelo YOLO y forzar uso de GPU
model = YOLO("YOLO/runs/detect/yolo11l/weights/best.pt")

# Inicializar captura de video
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error al abrir la cámara.")
    exit()

# Configurar resolución de captura
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Historial de seguimiento
track_history = defaultdict(list)

# Función para procesar detecciones
def draw_annotations(frame, results):
    for result in results:
        # Verificar si hay detecciones válidas
        if result.boxes.xywh is not None and result.boxes.id is not None:
            boxes = result.boxes.xywh.cpu().numpy()  # Coordenadas de las cajas
            track_ids = result.boxes.id.int().cpu().tolist()  # IDs de seguimiento

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))
                if len(track) > TRACK_HISTORY_LENGTH:  # Limitar historial
                    track.pop(0)

                # Dibujar líneas de seguimiento
                points = np.array(track, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [points], isClosed=False, color=(0, 255, 0), thickness=LINE_THICKNESS)

                # Dibujar caja delimitadora
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
    success, frame = cap.read()
    if not success:
        print("No se pudo leer el fotograma.")
        break
    frame = cv2.flip(frame, 1)
    
    # Realizar seguimiento con los parámetros configurados
    results = model.track(frame, 
                          persist=True, 
                          device="cuda",  # Forzar uso de GPU
                          conf=CONF_THRESHOLD,  # Umbral de confianza mínimo
                          iou=IOU_THRESHOLD,    # Umbral de IOU para supresión de máximos
                          )  # Mostrar el fotograma anotado
    
    # Anotar el fotograma con las detecciones y trayectorias
    annotated_frame = draw_annotations(frame.copy(), results)

    # Mostrar el fotograma anotado
    cv2.imshow("Seguimiento YOLO", annotated_frame)

    # Controlar la velocidad de actualización
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
