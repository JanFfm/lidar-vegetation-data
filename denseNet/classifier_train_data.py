import monai 
import cv2
import pandas as pd
import numpy
import torch
from monai.transforms import (Compose, AsChannelFirst,Resize,ScaleIntensity, RandGaussianSharpen,  ToTensor,  RandScaleCrop,OneOf, RandHistogramShift,RandCoarseDropout,AddChannel,RandFlip,RandZoom, RandRotate,EnsureType,   RandAdjustContrast, RandGaussianSmooth,RandStdShiftIntensity,  RandGaussianNoise,  RandGibbsNoise)




"""
Stores image data for training set for classifier network
img_files: list if file names
labels: .csv
mask_files=None : list of file_names 
size=512 :image size
use_noise=True : If True, use intensity augmentation transform
return image, label, img_file
"""
class train_data(monai.data.Dataset):
    def __init__(self, img_files,labels,size=256):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.size = size
        self.labels = labels
        self.img_files = img_files       
      

        #transform for spatial augmentation
        self.trans_sec_aug = Compose([
                RandFlip(prob = 0.5, spatial_axis=0),
                RandRotate(range_x=0.15, prob=0.14, padding_mode="zeros"),            
                OneOf([            
                    RandScaleCrop(roi_scale=0.7, max_roi_scale=0.99),
                    RandZoom(min_zoom=0.9, max_zoom=1.2, prob=0.07, keep_size=True),                
                ], weights=[0.1, 0.9]),

        ])
                
        #tranform for resizing and intensity scale:
        self.fit_network_transform = Compose([
                                ToTensor(),
                                Resize((self.size, self.size)),
                                ScaleIntensity(), 
                                EnsureType(device=self.device),])

    def __len__(self):
        return len(self.img_files) 


    """
    called by dataloader
    idx (int) index of image
    """   
    def __getitem__(self, idx):

        #load images_
        self.trans_load_image = Compose([
             #LoadImage(image_only=True),
             AsChannelFirst(),
             ToTensor(),
             Resize((self.size, self.size)),
             EnsureType(device=self.device),
             ])
        img_file_name =self.img_files[idx]  
        #
        image = cv2.cvtColor(cv2.imread(img_file_name, 1), cv2.COLOR_BGR2RGB)
        image = self.trans_load_image(image).to(self.device)
       
        #intensity augmentation    
        image  = image.type(torch.int)           

        #spatial augmentation
        image =self.trans_sec_aug(image)
      
       

        image = self.fit_network_transform(image) 
        #load labels:
        label = self.labels[idx]   
        #label = float(label)
        #label = numpy.array([label])      
       

        return image, label