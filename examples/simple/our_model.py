import json
import os
import xlrd
from PIL import Image
import torch
from torchvision import transforms
from efficientnet_pytorch import EfficientNet
PATH = "/home/xiangyuliu/Downloads/images"
EXCEL = "/home/xiangyuliu/Downloads/label.xlsx"
def load_all_images(path):
    for _, _, file in os.walk(path):
        file_list = file
    return file_list
def load_labels(path):
    worksheet = xlrd.open_workbook(path).sheet_by_index(0)
    return worksheet.col_values()[1:], worksheet.col_values()[1:]



model = EfficientNet.from_pretrained('efficientnet-b7')

# Preprocess image
tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),])
all_images = load_all_images(PATH)
labels = load_labels(EXCEL)
img = tfms(Image.open('img.jpg')).unsqueeze(0)
print(img.shape) # torch.Size([1, 3, 224, 224])

# Load ImageNet class names
labels_map = json.load(open('labels_map.txt'))
labels_map = [labels_map[str(i)] for i in range(1000)]

# Classify
model.eval()
with torch.no_grad():
    outputs = model(img)

# Print predictions
print('-----')
for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
    prob = torch.softmax(outputs, dim=1)[0, idx].item()
    print('{label:<75} ({p:.2f}%)'.format(label=labels_map[idx], p=prob*100))