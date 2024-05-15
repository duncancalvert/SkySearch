import torch


def load_model(path, device):
    model_ = torch.hub.load('ultralytics/yolov8', 'custom', path=path, force_reload=True)
    model_.to(device)
    print("model to ", device)
    return model_
