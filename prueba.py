import cv2
from ultralytics import YOLO

# Cargar el modelo YOLO
#model = YOLO("runs/detect/train/weights/best.pt")

def mostrar_stream(url, nombre_ventana="Camara"):
    # Crear una instancia de VideoCapture con la URL proporcionada
    cap = cv2.VideoCapture(url)
    
    # Verificar si se pudo abrir el stream
    if not cap.isOpened():
        print("Error: No se pudo abrir el stream de video.")
        return

    print(f"Mostrando el stream de {url} en la ventana '{nombre_ventana}'")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el fotograma.")
            break

        # Realizar la predicción con el modelo YOLO
        #resultados = model.predict(frame, imgsz=640)

        # Dibujar las anotaciones en el fotograma
        #anotaciones = resultados[0].plot()

        # Mostrar el fotograma en una ventana con el nombre proporcionado
        cv2.imshow(nombre_ventana, frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saliendo...")
            break

    # Liberar recursos y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()

# Llamada al método con la URL del stream y el nombre de la ventana
mostrar_stream("http://192.168.1.34:8080/video", "Camara Edwin")
