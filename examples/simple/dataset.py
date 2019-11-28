import numpy as np
import torch
from torchvision import transforms
from PIL import Image

path_list = ["/newNAS/Workspaces/DRLGroup/xiangyuliu/NEW/x_0.npy",
            "/newNAS/Workspaces/DRLGroup/xiangyuliu/NEW/x_1.npy",
            "/newNAS/Workspaces/DRLGroup/xiangyuliu/NEW/x_2.npy",
            "/newNAS/Workspaces/DRLGroup/xiangyuliu/NEW/x_3.npy",
            "/newNAS/Workspaces/DRLGroup/xiangyuliu/NEW/x_4.npy"]

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, path_list, transform=None, img_size=300, model_type="five"):
        self.data = []
        self.len_array = []
        self.img_size = img_size
        self.path_list = path_list
        self.kinds = 4 if (model_type == "four" or model_type == 'univ_net') else 5
        if self.kinds == 4:
            self.path_list = self.path_list[1:]
        if transform == None:
            self.tfms = transforms.Compose([transforms.Resize(size=(img_size, img_size)),
                                            transforms.ToTensor(),
                                            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
        else:
            self.tfms = transform
        for path, i in zip(path_list, range(len(self.path_list))):
            self.data.append(np.load(path, mmap_mode="r"))
            self.len_array.append(self.data[i].shape[0] - 20)
        for i in range(len(self.len_array)):
            if i == 0:
                continue
            self.len_array[i] = self.len_array[i] + self.len_array[i - 1]
        self.test_batch, self.test_label = self._fetch_test_data()

    def __getitem__(self, item):
        pre_len = 0
        for length, i in zip(self.len_array, range(len(self.len_array))):
            if item <= length - 1:
                label = i
                index = item - pre_len
                break
            pre_len = self.len_array[i]
        img = self.data[label][index + 10]
        img = self.image_transform(img)
        return img, label

    def __len__(self):
        return self.len_array[-1]

    def _fetch_test_data(self):
        image_list = []
        label_list = []
        for label in range(self.kinds):
            for index in range(10):
                image_list.append(self.image_transform(self.data[label][index]))
                image_list.append(self.image_transform(self.data[label][-index - 1]))
                label_list.append(label)
                label_list.append(label)
        return torch.stack(image_list, dim=0), torch.tensor(np.array(label_list), dtype=torch.long)

    def image_transform(self, img):
        img = Image.fromarray(np.uint8(img))
        img = transforms.Resize(size=(self.img_size, self.img_size))(img)
        img = transforms.ToTensor()(img)
        img = transforms.Normalize([0.371813122684, 0.259104121899, 0.216585938671],
                                   [0.270264841454, 0.213204154534, 0.210561357497])(img)
        return img

    def calculate_mean_std(self):
        for i in range(len(self.data)):
            self.data[i] = np.uint8(self.data[i])
        whole_dataset = np.concatenate(tuple(self.data), axis=0)
        for i in range(3):
            print(np.mean(whole_dataset[:, :, :, i]) / 255, np.std(whole_dataset[:, :, :, i]) / 255)

    def fix_data(self):
        a = self.data[0][:, :, :, 0]
        b = self.data[0][:, :, :, 2]

        self.data[0][:, :, :, 0] = b
        self.data[0][:, :, :, 2] = a

        print("begin to save")
        np.save("/newNAS/Workspaces/DRLGroup/xiangyuliu/clahe/x_0.npy", np.uint8(self.data[0]))
        np.save("/newNAS/Workspaces/DRLGroup/xiangyuliu/clahe/x_1.npy", np.uint8(self.data[1]))
        np.save("/newNAS/Workspaces/DRLGroup/xiangyuliu/clahe/x_2.npy", np.uint8(self.data[2]))
        np.save("/newNAS/Workspaces/DRLGroup/xiangyuliu/clahe/x_3.npy", np.uint8(self.data[3]))
        np.save("/newNAS/Workspaces/DRLGroup/xiangyuliu/clahe/x_4.npy", np.uint8(self.data[4]))



if __name__ == '__main__':
    dataset = CustomDataset(path_list)
    dataset.calculate_mean_std()