import cv2
import numpy as np
from ultralytics import YOLO
import mss

# Cargar el modelo YOLO
model = YOLO("runs/detect/yolo11l/weights/best.pt")  # Ruta del modelo

def mostrar_pantalla(nombre_ventana="Captura de Pantalla"):
    """Captura la pantalla y muestra las detecciones del modelo YOLO."""
    # Crear una instancia de mss para la captura de pantalla
    with mss.mss() as sct:
        # Obtener el tamaño de la pantalla
        monitor = sct.monitors[1]  # Monitor principal; ajusta si tienes múltiples monitores
        print(f"Mostrando la captura de pantalla en la ventana '{nombre_ventana}'")
        
        while True:
            # Capturar la pantalla como imagen
            screenshot = sct.grab(monitor)
            
            # Convertir la imagen a un formato compatible con OpenCV
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convertir BGRA a BGR

            # Realizar la predicción con el modelo YOLO
            resultados = model.predict(frame, imgsz=640)
            detecciones = []
            # Procesar las detecciones
            for result in resultados[0].boxes:
                x1, y1, x2, y2 = map(int, result.xyxy[0])  # Coordenadas de la caja delimitadora
                conf = result.conf[0].item()  # Confianza de la detección
                class_id = int(result.cls[0].item())  # Clase detectada (ej., balón)

                # Filtrar solo detecciones de balón y ajustar el umbral de confianza
                if class_id == 0 and conf > 0.5:
                    detecciones.append({
                        'box': (x1, y1, x2, y2),
                        'confidence': conf,
                        'class_id': class_id
                    })
                    # Dibujar el rectángulo de la detección y la confianza
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"Conf {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            print(detecciones)
            # Mostrar el fotograma anotado en una ventana con el nombre proporcionado
            cv2.imshow(nombre_ventana, frame)

            # Salir si se presiona 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Saliendo...")
                break

        # Cerrar ventanas
        cv2.destroyAllWindows()

# Llamada al método para mostrar la captura de pantalla
if __name__ == "__main__":
    mostrar_pantalla("Captura de Pantalla")
