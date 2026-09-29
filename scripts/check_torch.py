import torch
print("PYTORCH_VERSION:", torch.__version__)
print("CUDA_AVAILABLE:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("DEVICE_NAME:", torch.cuda.get_device_name(0))
    print("DEVICE_COUNT:", torch.cuda.device_count())
    print("VRAM_GB:", round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2))
else:
    print("RUNNING_ON: CPU")
