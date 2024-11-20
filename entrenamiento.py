from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("yolo11l.pt")

    train_results = model.train(
        data="YOLODataset/dataset.yaml",  # path to dataset YAML
        epochs=100,  # number of training epochs
        imgsz=640,  # training image size
        device=0,  # use the first GPU
        batch=5,  # specify batch size
        half=True,
    )