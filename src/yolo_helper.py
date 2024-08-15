import torch


def load_model():
    model_ = torch.hub.load('ultralytics/yolov8', 'custom', force_reload=True)
    print("model to ", model_)
    return model_

if __name__ == "__main__":
    load_model()
