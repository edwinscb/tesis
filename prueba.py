import cv2
from ultralytics import YOLO

def mostrar_stream(url, nombre_ventana="Camara"):
    # Crear una instancia de VideoCapture con la URL proporcionada
    cap = cv2.VideoCapture(url)
    
    # Verificar si se pudo abrir el stream
    if not cap.isOpened():
        print("Error: No se pudo abrir el stream de video.")
        return

    # Bucle para capturar y mostrar los fotogramas
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mostrar el fotograma en una ventana con el nombre proporcionado
        cv2.imshow(nombre_ventana, frame)

        # Presionar 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()


# Llamada al método con la URL del stream y el nombre de la ventana
mostrar_stream("http://192.168.1.12:8080/video", "Camara Edwin")
