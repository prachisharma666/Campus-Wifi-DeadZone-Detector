import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
Sequential=tf.keras.models.Sequential
Dense=tf.keras.layers.Dense
Dropout=tf.keras.layers.Dropout
Adam=tf.keras.optimizers.Adam
import pickle
import os

def load_and_preprocess(filepath,is_train=True):
    df=pd.read_csv(filepath)
    wap_cols=[col for col in df.columns if "WAP" in col]
    x=df[wap_cols].copy()
    x.replace(100,-105,inplace=True)
    #Scaling RSSI to be between 0(weak/not detected) and 1(strongest)
    x=(x+105)/105.0
    y=df["BUILDINGID"].astype(str)+"_"+df["FLOOR"].astype(str)
    return x,y,df

def build_model(input_dim,num_classes):
    model=Sequential()
    model.add(Dense(128,input_dim=input_dim,activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(64,activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(32,activation="relu"))
    model.add(Dense(num_classes,activation="softmax"))
    optimizer=Adam(learning_rate=0.001)
    model.compile(loss="sparse_categorical_crossentropy",optimizer=optimizer,metrics=["accuracy"])
    return model

if __name__=="__main__":
    print("Loading Dataset...")
    x_train_raw,y_train_raw,df_train=load_and_preprocess(r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\trainingData.csv")
    x_val_raw,y_val_raw,df_val=load_and_preprocess(r"C:\Users\Prachi\OneDrive\Desktop\FOML_Project_1\data\validationData.csv",is_train=False)
    print("Encoding Target Variables...")
    LE=LabelEncoder()
    y_train=LE.fit_transform(y_train_raw)
    y_val=LE.transform(y_val_raw)
    num_classes=len(LE.classes_)
    print("Applying PCA...")
    pca=PCA(0.95)
    x_train_pca=pca.fit_transform(x_train_raw)
    x_val_pca=pca.transform(x_val_raw)
    print(f"Reduced features from {x_train_raw.shape[1]} to {x_train_pca.shape[1]} components")
    print("Training Neural Network...")
    model=build_model(input_dim=x_train_pca.shape[1],num_classes=num_classes)
    hist=model.fit(x_train_pca,y_train,validation_data=(x_val_pca,y_val),epochs=30,batch_size=64,verbose=1)
    print("Evaluating Model on the basis of Validation Set...")
    val_predictions=np.argmax(model.predict(x_val_pca),axis=1)
    print(classification_report(y_val,val_predictions,target_names=LE.classes_))
    os.makedirs("models/",exist_ok=True)
    model.save("models/nn_localization_model.h5")
    with open("models/pca_transformer.pkl","wb") as f:
        pickle.dump(pca,f)
    with open("models/label_encoder.pkl","wb") as f:
        pickle.dump(LE,f)
    print("Pipeline Completed, all files saved in models/ directory.")