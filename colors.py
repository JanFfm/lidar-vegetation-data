import numpy as np

def get_classification_color(class_number):
    if int(class_number) > 18:
        return np.array([221,160,221]) / 255
    classification_colors ={
            0: [240,255,255], # azure, never cöassified
            1:[220,220,220], # grey, unclassified
            2:[244,164,96], # brwon, ground
            3:[32,178,170], #low veg lightseagreen
            4 :[0,255,127], #med veg springgreen
            5:[0,100,0], #hig veg darkgreen
            6:[128,0,0], #building maroon
            7:[255,20,147], # noise deeppink
            8:[255,192,203], # reserved pink
            9:[0,0,255], #water blue
            10:[138,43,226], #rail blueviolet
            11:[112,128,144], #road   slategrey
            12:[255,192,203], #reserved pink
            13:[255,255,0], #wire Yellow
            14:[255,255,0], #wire Yellow
            15:[255,255,0], #transmission tower Yellow
            16:[255,255,0], # wire Yellow
            17:[112,128,144], #bridge  slategrey
            18:[255,20,147], #high noise deeppink            
        }
    return np.array(classification_colors[int(class_number)]) / 255