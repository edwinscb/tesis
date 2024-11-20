from fastapi import FastAPI
from ultralytics import YOLO
from fastapi.responses import JSONResponse
import cv2
import numpy as np

app = FastAPI()
model = YOLO("runs/detect/yolo11l/weights/best.pt")  # Ruta a tu modelo YOLO

# Inicializa la cámara
camera = cv2.VideoCapture(0)  # Usa la cámara predeterminada (0). Cambia si tienes varias cámaras.

@app.post("/predict_camera/")
async def predict_camera():
    # Captura un cuadro de la cámara
    ret, frame = camera.read()
    if not ret:
        return JSONResponse({"error": "No se pudo capturar un cuadro de la cámara"}, status_code=500)

    # Realiza la predicción
    results = model.predict(frame, device="cuda")  # Usa GPU
    detections = results[0].boxes.xyxy.tolist()  # Formato de las detecciones

    # Retorna las detecciones
    return {"detections": detections}

# Cierra la cámara cuando el servidor se detenga
@app.on_event("shutdown")
def shutdown_event():
    camera.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
