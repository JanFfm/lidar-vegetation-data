
import monai
import math
from monai.transforms import ( Compose,
    AsDiscrete,
    Compose,
    LoadImage,
    Resize,
    AsChannelFirst,
    ToNumpy,
    AsChannelLast, 
)
import monai.metrics 
import monai.data
import monai.networks.nets  
import monai.optimizers
import matplotlib.pyplot as plt

import classifier_train_data, classifier_test_data
import torch
from torchmetrics import Accuracy
import os
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import db_settings


"""

"""
class classifier_network:
    def __init__(self, image_files, labels, size=256, network_name="classifier", network=None, drop=0.0, weight=1, threshold=0.5): 
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #self.device='cpu'
        print(self.device)
        self.network_name = network_name     
        self.size = size
        self.weight = weight
        if self.weight == 0:
            self.weight=1
        self.threshold =threshold
        print("pos weight:", self.weight)
        self.image_files = image_files
        self.labels = labels

        self.class_number = len(np.unique(labels))
        print(self.class_number, " classes to classify")
  
        
        #https://docs.monai.io/en/latest/networks.html#classifier       
        if network == None:         
            self.net = monai.networks.nets.DenseNet121(spatial_dims=2, in_channels=3, out_channels=self.class_number, dropout_prob=drop).to(self.device)
            """
            self.net = monai.networks.nets.Classifier(            
            in_shape=(3, size,size), 
            classes=self.class_number,
            channels=(64, 128, 256, 512),
            strides = (2,2, 2),
            dropout = 0.2,
            act='PRELU',   
            kernel_size=9, 
            num_res_units=2,
            ).to(self.device)            
            """   

        else:
            self.net=network.to(self.device)        
        
        #according to https://github.com/Project-MONAI/tutorials/blob/master/2d_classification/mednist_tutorial.ipynb : 
        self.loss_fn= torch.nn.CrossEntropyLoss() 
        #different loss-fkt for validation/test because there is no weighting of loss values   
        #self.val_loss= torch.nn.CrossEntropyLoss()
        self.optimizer =torch.optim.Adam(self.net.parameters(), lr=0.001) 
        self.accuracy = Accuracy().to(self.device)   


    """
    prints network config
    """
    def get_network_config(self):
        print(self.net)
        
    def load(self,path):
        self.net.load_state_dict(torch.load(path))



    """
    loads the data-sets. 
    must be called before training
    """
    def get_data(self, batch_size=4):
        self.batch_size = batch_size

        # hier splitten:
        X_train, X_test, y_train, y_test = train_test_split(self.image_files, self.labels, test_size=0.33, random_state=42)

        l, l_num = np.unique(y_train, return_counts=True)
        print("labels train set", dict(zip(l, l_num)))

        l, l_num = np.unique(y_test, return_counts=True)
        print("labels val/test-set", dict(zip(l, l_num)))

        self.training_set  = classifier_train_data.train_data(img_files = X_train ,labels=y_train, size=self.size)
        self.val_test_set = classifier_test_data.test_data(img_files = X_test ,labels=y_test, size=self.size)

        val_size = int(len(self.val_test_set) * 0.3)
        test_size = len(self.val_test_set) - val_size
        print(val_size)
        print(test_size)

        #split testset in train and validation set
        self.validation_set, self.test_set = torch.utils.data.random_split(self.val_test_set,[val_size,test_size], generator=torch.Generator().manual_seed(98))   

        self.train_loader = monai.data.DataLoader(self.training_set, batch_size=batch_size, num_workers=0, shuffle=True )
        self.val_loader = monai.data.DataLoader(self.validation_set, batch_size=batch_size, num_workers=0, shuffle=False)
        self.test_loader = monai.data.DataLoader(self.test_set, batch_size=batch_size ,num_workers=0, shuffle=False)
        

    """
    start training
    epochs: number of training epochs
    search_treshhold=True : if true, a list of possible thresholds will be tested at each minimum validation loss
    
    """
    def train(self, epochs=5):
        ###saves scores from each epoch:
        softmax = torch.nn.Softmax(dim=1)
        losses = []
        v_losses = []
        
        acc_scores =[]
        acc_scores_test =[]
        acc_scores_test_epochs = []
     
        #for storing best f-scores
        self.best_f_score_treshhod= (0.0,0.0, math.inf)
        for e in range(epochs):
            print("epoch", e+1, " off ", epochs)
            t_meanloss = 0.0
            counter = 0
            
            self.net.train()
            #training step:
            for batch_numer, (X, y) in enumerate(self.train_loader):
                X = X.to(self.device)
                y = y.to(self.device)   
                print    



                pred = self.net(X.float()) 
                pred = softmax(pred).to(self.device)  
                y = y.type(torch.LongTensor).to(self.device)  
                #with torch.autocast(self.device):
                loss =self.loss_fn(pred,y)            
       
                # Backpropagation
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                #count losses
                t_meanloss = t_meanloss + loss.item()
                counter = counter + 1                

                ##print feedback
                if batch_numer % 40 == 0:
                    step = batch_numer * self.batch_size
                    print(f"mean loss: {loss.item():>4f} in step {step:>5d} of {len(self.train_loader.dataset):>5d}")
            t_meanloss = t_meanloss / counter
            losses.append(t_meanloss)
            print("epoch ", (e+1),"mean loss: ", t_meanloss)           
            
            #eval:
            self.net.eval()
            v_meanloss = 0.0
            v_counter = 0
    
            self.first_run = True
  
            acc_list =[]
            for batch_numer, (X, y, img_file) in enumerate(self.val_loader):
                X = X.to(self.device) 
                y = y.to(self.device)
                pred = self.net(X.float()) 
                pred = softmax(pred).to(self.device)   
                y = y.type(torch.LongTensor).to(self.device)  

                loss =self.loss_fn(pred,y)

                # count poitiv examples in validation set:
  
                v_meanloss = v_meanloss + loss.item()
                v_counter = v_counter + 1
                
                #calculating acc score:
                
                acc = float(self.accuracy(pred, y))
                acc_list.append(acc)         
             

              

            #collect metrics:
            accuracy_score = sum(acc_list) /len(acc_list)
            acc_scores.append(accuracy_score)
            v_meanloss = v_meanloss / v_counter
            v_losses.append(v_meanloss)            
   
            print("epoch ", (e+1),"mean validation loss: ", v_meanloss )
            
     
            print("accuracy: ", accuracy_score)           
            
            if (max(acc_scores) == accuracy_score):
                print("new best accuracay!")
                acc_test = self.test()
                acc_scores_test.append(acc_test)
                acc_scores_test_epochs.append(e)
                if  (max(acc_scores_test) == acc_test):
                    print("newx best acc in testset!")
                    self.save((str(acc_test)+"_in_e_" +str(e)))
        print("best accurarcy score ", str(max(acc_scores_test)))
            
    ###### plot mean losses
        x = [i for i in range(epochs)]
        plt.clf()
        plt.plot(x, losses,  label = "train_loss")
        plt.plot(x, v_losses,  label = "val_loss")
        plt.xlabel("epoch")
        plt.ylabel("mean error")
        plt.legend()        
        plot_name= self.network_name  +"_losses.png"
        plt.savefig(plot_name)  
        plt.show()
        plt.close() 
       

        #plot accurray f-score
        x = [i for i in range(epochs)]
        plt.plot(x, acc_scores, label="val_accuracy")
        plt.plot(acc_scores_test_epochs, acc_scores_test, label="test_accuracy")


        plt.xlabel("epoch")
        plt.ylabel("score")
        plt.yticks(np.arange(0, 1.1, 0.1))
        plt.legend()
        plot_name= self.network_name +"_" +str(str(max(acc_scores_test)))+"_acc.png"
        plt.savefig(plot_name)  
        plt.show()
        plt.close() 
  
    """
    run test set
    """
    def test(self):
            softmax = torch.nn.Softmax(dim=1)

            #eval:
            self.net.eval()
            test_meanloss = 0.0
            test_counter = 0
            acc_list= []
            
            self.first_run = True
            for _, (X, y, _) in enumerate(self.test_loader):
                X = X.to(self.device) #!!!!!!!
                y = y.to(self.device)
                pred = self.net(X.float()) 
                pred = softmax(pred).to(self.device)   
                y = y.type(torch.LongTensor).to(self.device)  

                #with torch.autocast( self.device):
                loss =self.loss_fn(pred,y)
                                
                acc = float(self.accuracy(pred, y))
                acc_list.append(acc)         
        
                
                test_meanloss += loss
                test_counter +=1
            accuracy_score = sum(acc_list) /len(acc_list)
            print(accuracy_score, "in test set with mean loss: ", test_meanloss/test_counter)
                


            return accuracy_score


    """
    saves network to networks/classifier/
    name: filename
    returns save_path
    
    """
    def save(self, name):
        path = self.network_name
        os.makedirs(path, exist_ok=True)
        name = path +"/" +name+ "_network"
        torch.save(self.net.state_dict(), name)
        return name

   
########################################################################################################################



    """
    Instantiates classifier_network
    reads image list from  folders before
    
    folder_list:  
 
    """
def create_network(folder_list, taxon='class', n_min=150, n_max=150,size=256, name='network', drop=0.0, network=None, weight=1, threshold=0.5, gingko_to_conifera=None):
        db =db_settings.db(autocommit=False)
        req_families = """SELECT * FROM lidar_proj.familien"""
        req_order = """SELECT * FROM lidar_proj.ordnungen"""
        req_class = """SELECT * FROM lidar_proj.klassen"""
        req_gattung = """SELECT * FROM lidar_proj.gattungen"""

        df_families = db.export_to_pandas(req_families)
        df_order = db.export_to_pandas(req_order)
        df_class = db.export_to_pandas(req_class)
        df_gattung = db.export_to_pandas(req_gattung)

        df_families.set_index("ID", drop=True, inplace=True)
        df_order.set_index("ID", drop=True, inplace=True)
        df_class.set_index("ID", drop=True, inplace=True)
        df_gattung.set_index("ID", drop=True, inplace=True)

        global dict_gattung
        global dict_families
        global dict_order
        global dict_class

        dict_gattung =df_gattung.to_dict(orient="index")

        dict_families =df_families.to_dict(orient="index")
        dict_order =df_order.to_dict(orient="index")
        dict_class =df_class.to_dict(orient="index")
        print(dict_gattung[1])

        
        try:
            image_dir = '//content/drive/MyDrive/Colab Notebooks/train_data_images_z_intensity_gelsenkirchen'
            image_files = []
            labels = []
            for i in folder_list: 
                for child in Path((image_dir +"/"+ str(i))).iterdir():
                    img = image_dir +"/"+ str(i) +"/" + child.name
                    image_files.append(img)
                    labels.append(i)
        except:
            image_dir = 'G:/Meine Ablage/Colab Notebooks/train_data_images_z_intensity'
            image_files = []
            labels = []
            for i in folder_list: 
                for child in Path((image_dir +"/"+ str(i))).iterdir():
                    img = image_dir +"/"+ str(i) +"/" + child.name
                    image_files.append(img)
                    labels.append(i)
                
                
        image_files = np.array(image_files)
        if taxon=='class':
            labels = np.array(list(map(get_class, labels)))


            if gingko_to_conifera:
                labels = np.array(list(map(lambda x: 2 if x==3 else x, labels)))
        elif taxon =='family':
            labels = np.array(list(map(get_family, labels)))
            print(labels)
        elif taxon =='order':
            labels = np.array(list(map(get_family, labels)))
            print(labels)


        l, l_num = np.unique(labels, return_counts=True)
        count_dict = dict(zip(l, l_num))
        used_labels = []
        for key in count_dict.keys():
            if count_dict[key] >= n_min:
                used_labels.append(key)
        print(count_dict)

        data = {}
        for l in used_labels:   
            data[l] = image_files[labels == l]
   


        images = []
        labels = []
        for key in data.keys():

            if len(data[key]) > n_max:
                idx = np.random.randint(len(data[key]) -1, size=n_max)
                images_downsampled =data[key][idx]  

                images +=list(images_downsampled)
                labels += [key  for i in range(n_max)]
            else:
                images +=list(data[key])
                labels += [key  for i in range(len(list(data[key])))]

        labels, _ =scale_y(labels)     
        images =np.array(images)
        labels = np.array(labels) 
        
        print(labels.shape, images.shape)

                
       

        net = classifier_network(images,labels, size, network_name=name,drop=drop, network=network, weight=weight, threshold=threshold)

        return net

def get_class(id):
    family = dict_families[dict_gattung[id]['ID_FAMILIE']]
    order = dict_order[family['ID_ORDNUNG']]
    c = order['ID_KLASSE']
    return c
def get_order(id):
    family = dict_families[dict_gattung[id]['ID_FAMILIE']]
    o = family['ID_ORDNUNG']
    return o
def get_family(id):
    f = dict_gattung[id]['ID_FAMILIE']
    return f


def scale_y(y):
    """translates a list of labels with unsorted numbers to a labeling starting with [0,1,2,...]

    Args:
        y (_type_): _description_

    Returns:
        _type_: _description_
    """
    labels = np.unique(y)
    y_new = [i for i in range(len(labels))]
    translator = {key:value for (key,value) in zip(labels, y_new)}
    re_translate = {key:value for (key,value) in zip(y_new, labels)}

    y = [translator[i] for i in y]
    return y, re_translate
        
"""label_folders = [x[0] for x in os.walk('G:/Meine Ablage/Colab Notebooks/train_data_images_z_intensity')]
folder_list = list(map(lambda x: int(x.split('\\')[-1]), label_folders[1:]))
print(folder_list)
#labels, _ = scale_y(label_folders)
#print(labels)

drop = 0.1

network_name = "Dense121_order"

network =create_network(folder_list, size=256, taxon='oder',name=network_name,drop=drop, n_min=150)
network.get_data()
network.train(300) 
"""
