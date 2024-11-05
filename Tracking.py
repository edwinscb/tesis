from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2

# Inicializar el modelo YOLO y DeepSORT
model = YOLO("runs/detect/train4/weights/best.pt")
tracker = DeepSort(max_age=30, n_init=3, nn_budget=100)

# Capturar el video (0 para webcam o URL de cámara IP)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Detección con YOLO
    results = model(frame)
    detections = []

    for result in results:
        for box in result.boxes:
            # Verificar que box.xyxy exista y sea compatible
            if hasattr(box, 'xyxy') and hasattr(box, 'conf') and hasattr(box, 'cls'):
                # Convertir las coordenadas del tensor a escalares
                try:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    width, height = x2 - x1, y2 - y1
                    conf = box.conf.item()
                    class_id = int(box.cls.item())

                    # Filtrar detecciones de balones (ajusta el ID de clase si es necesario)
                    if conf > 0.5 and class_id == 0:
                        detections.append(([x1, y1, width, height], conf, class_id))
                except Exception as e:
                    print("Error procesando las coordenadas:", e)
                    continue

    # Seguimiento con DeepSORT
    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed() or track.time_since_update > 1:
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)
        
        # Dibujar las cajas y el ID del rastreo
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID {track_id}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Mostrar el frame
    cv2.imshow("YOLO + DeepSORT Tracking", frame)
    
    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
