import monai 
import cv2
from monai.transforms.utility.array import AsChannelLast
import torch
from monai.transforms import (Compose, AsChannelFirst,Resize,ScaleIntensity, ToTensor,EnsureType)



class test_data(monai.data.Dataset):
    """
    Stores image data for test set of classifier network
    does no augmentation
    img_files: list of file names
    labels: list of labels
    size=512 :image size

    """
    def __init__(self, img_files,labels,  size=256):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.labels = labels
        self.img_files = img_files
        self.size=size  
        
       
    def __len__(self):
        return len(self.img_files) 

  
    def __getitem__(self, idx):
        """
        called by dataloader
        idx (int) index of image
        
        return image, label, img_file
        """  
        #load image transform
        self.trans_load_image = Compose([
             AsChannelFirst(),
             ToTensor(),
             Resize((self.size, self.size)),
             EnsureType(device=self.device),
             ])
        #read image:
        img_file =self.img_files[idx]          
        image = cv2.cvtColor(cv2.imread(img_file, 1), cv2.COLOR_BGR2RGB)
        image = self.trans_load_image(image).to(self.device)  
        image  = image.type(torch.int)
        ##rescaling:
        self.fit_network_transform = Compose([
                                ToTensor(),
                                Resize((self.size, self.size)),
                                ScaleIntensity(), 
                                EnsureType(device=self.device),])
        

        image = self.fit_network_transform(image) 
        #load label:
        label = self.labels[idx] 
    

        return image, label, img_file