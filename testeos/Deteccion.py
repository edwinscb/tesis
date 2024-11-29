import cv2
from ultralytics import YOLO

# Cargar el modelo YOLO
model = YOLO("runs/detect/yolo11l/weights/best.pt")
def mostrar_stream(indice_camara=0, nombre_ventana="Camara"):
    # Crear una instancia de VideoCapture con el índice de la cámara
    cap = cv2.VideoCapture(indice_camara)
    
    # Verificar si se pudo abrir el stream
    if not cap.isOpened():
        print("Error: No se pudo abrir el stream de video.")
        return

    print(f"Mostrando el stream de la cámara en la ventana '{nombre_ventana}'")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el fotograma.")
            break

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

        # Mostrar el fotograma anotado en una ventana con el nombre proporcionado
        cv2.imshow(nombre_ventana, frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saliendo...")
            break

    # Liberar recursos y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()

# Llamada al método con el índice de la cámara y el nombre de la ventana
mostrar_stream(0, "Camara Edwin")  # Cambia 0 si es necesario
