import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict

# Configuraciones como variables
FRAME_WIDTH = 800   # Ancho del frame
FRAME_HEIGHT = 600  # Alto del frame
LINE_THICKNESS = 2  # Grosor de la línea de tracking
CONF_THRESHOLD = 0.2  # Umbral de confianza mínimo
IOU_THRESHOLD = 0.7  # Umbral de IOU para supresión de máximos
TRACK_HISTORY_LENGTH = 50  # Duración de la línea de tracking en fotogramas

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
cv2.setUseOptimized(True)

# Historial de seguimiento (almacena trayectorias incluso si el objeto no está activo)
track_history = defaultdict(list)

# Variable para controlar el modo (True = Detección, False = Seguimiento)
modo_deteccion = False

# Función para procesar detecciones en modo de seguimiento (trayectoria persistente)
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

# Función para realizar detección
def draw_annotations_detection(frame, results):
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Coordenadas de la caja delimitadora
        conf = result.conf[0].item()  # Confianza de la detección
        class_id = int(result.cls[0].item())  # Clase detectada

        # Filtrar solo detecciones de balón y ajustar el umbral de confianza
        if class_id == 0 and conf > 0.5:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"Conf {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame

# Bucle principal
while True:
    start_time = time.time()

    success, frame = cap.read()
    if not success:
        print("No se pudo leer el fotograma.")
        break
    
    frame = cv2.flip(frame, 1)  # Modo espejo
    frame = cv2.resize(frame, (FRAME_WIDTH,FRAME_HEIGHT))
    # Realizar detección si el modo está activado
    # Alternar entre detección y seguimiento solo cuando sea necesario
    if modo_deteccion:
        results = model.predict(frame, imgsz=FRAME_WIDTH)  # Usar tamaño de imagen adecuado
        annotated_frame = draw_annotations_detection(frame.copy(), results)
    else:
        # Modificar el código de seguimiento para hacerlo más eficiente
        results = model.track(frame, imgsz=FRAME_WIDTH, persist=False, device="cuda", conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
        annotated_frame = draw_annotations_tracking(frame.copy(), results)

    # Calcular y mostrar el tiempo por iteración
    elapsed_time = time.time() - start_time
    fps = 1 / elapsed_time
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Mostrar el fotograma anotado
    cv2.imshow("YOLO - Detección/Seguimiento", annotated_frame)

    # Controlar la alternancia de modo con la tecla 'a'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('a'):
        modo_deteccion = not modo_deteccion  # Alternar entre detección y seguimiento
        estado = "detección" if modo_deteccion else "seguimiento"
        print(f"Modo cambiado a {estado}.")

    # Salir si se presiona 'q'
    if key == ord('q'):
        print("Saliendo...")
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
