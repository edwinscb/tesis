import cv2
import time
from ultralytics import YOLO

# Cargar el modelo YOLO
model = YOLO("YOLO/runs/detect/yolo11l/weights/best.pt")

def mostrar_stream(indice_camara=0, nombre_ventana="Camara"):
    # Configuración de la resolución
    resolucion_ancho = 1280  # Ancho de la imagen (resolución optimizada para rendimiento)
    resolucion_alto = 720    # Alto de la imagen

    # Crear una instancia de VideoCapture con el índice de la cámara
    cap = cv2.VideoCapture(indice_camara)
    
    # Verificar si se pudo abrir el stream
    if not cap.isOpened():
        print("Error: No se pudo abrir el stream de video.")
        return

    # Establecer la resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolucion_ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucion_alto)

    # Obtener y mostrar la resolución actual
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Resolución del video: {ancho}x{alto}")

    # Variables para el cálculo de FPS
    prev_time = 0
    fps = 0
    frame_counter = 0

    print(f"Mostrando el stream de la cámara en la ventana '{nombre_ventana}'")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el fotograma.")
            break

        frame_counter += 1
        if frame_counter % 2 == 0:  # Realizar predicción cada 2 fotogramas
            # Realizar la predicción con el modelo YOLO
            resultados = model.predict(frame, imgsz=640)

            # Dibujar las detecciones en el fotograma
            for result in resultados[0].boxes:
                x1, y1, x2, y2 = map(int, result.xyxy[0])  # Coordenadas de la caja delimitadora
                conf = result.conf[0].item()  # Confianza de la detección
                class_id = int(result.cls[0].item())  # Clase detectada (ej., balón)
                
                # Filtrar solo detecciones de balón y ajustar el umbral de confianza
                if class_id == 0 and conf > 0.5:
                    # Dibujar el rectángulo de la detección y la confianza
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"Conf {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"Balón", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Calcular FPS
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time))
        prev_time = curr_time

        # Mostrar los FPS en el fotograma
        cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        # Mostrar el fotograma anotado en una ventana con el nombre proporcionado
        cv2.imshow(nombre_ventana, frame)

        # Salir si se presiona 'q' o pausar/reanudar con 'p'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Saliendo...")
            break
        elif key == ord('p'):
            print("Pausado. Presione 'r' para reanudar.")
            while True:
                if cv2.waitKey(1) & 0xFF == ord('r'):
                    print("Reanudando...")
                    break

    # Liberar recursos y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()

# Llamada al método con el índice de la cámara y el nombre de la ventana
mostrar_stream(0, "Camara Edwin")  # Cambia 0 si es necesario
