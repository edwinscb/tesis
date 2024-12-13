from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("yolo8n.pt")

    train_results = model.train(
        data="YOLO/dataset.yaml",  # path to dataset YAML
        epochs=100,  # Reduce epochs a 50 para entrenamiento más rápido
        imgsz=640,  # Reduce la resolución de la imagen para mayor velocidad
        device=0,  # Usar la primera GPU (asegúrate de tener CUDA activado)
        batch=8,  # Aumenta el batch si la memoria de la GPU lo permite (ajústalo según tu GPU)
        half=True,  # Activar precisión de 16 bits (half precision) para mayor velocidad
        conf_thres=0.45,  # Ajuste de umbral de confianza (solo durante la inferencia)
    )
